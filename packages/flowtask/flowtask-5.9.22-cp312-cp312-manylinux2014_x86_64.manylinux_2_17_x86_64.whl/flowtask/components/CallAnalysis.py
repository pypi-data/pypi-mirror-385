from collections.abc import Callable
import asyncio
import pandas as pd
from ..interfaces.ParrotBot import ParrotBot
from .flow import FlowComponent


class CallAnalysis(ParrotBot, FlowComponent):
    """
        CallAnalysis.

        Overview

            The CallAnalysis class is a component for interacting with an IA Agent for making Call Analysis.
            It extends the FlowComponent class and adds functionality to load file content from paths.

        .. table:: Properties
        :widths: auto

            +------------------+----------+--------------------------------------------------------------------------------------------------+
            | Name             | Required | Description                                                                                      |
            +------------------+----------+--------------------------------------------------------------------------------------------------+
            | output_column    |   Yes    | Column for saving the Call Analysis information.                                                 |
            +------------------+----------+--------------------------------------------------------------------------------------------------+
            | use_dataframe    |   No     | If True (default), use dataframe mode with file_path_column. If False, use directory/pattern.   |
            +------------------+----------+--------------------------------------------------------------------------------------------------+
            | use_bytes_input  |   No     | If True, read content from BytesIO objects instead of file paths. Defaults to False.            |
            +------------------+----------+--------------------------------------------------------------------------------------------------+
            | bytes_column     |   No     | Column containing BytesIO objects (used when use_bytes_input is True).                          |
            +------------------+----------+--------------------------------------------------------------------------------------------------+
            | file_path_column |   No     | Column containing file paths to load content from (dataframe mode).                             |
            +------------------+----------+--------------------------------------------------------------------------------------------------+
            | directory        |   No     | Directory path to search for files (file mode).                                                 |
            +------------------+----------+--------------------------------------------------------------------------------------------------+
            | pattern          |   No     | Glob pattern to match files (file mode).                                                        |
            +------------------+----------+--------------------------------------------------------------------------------------------------+
            | content_column   |   No     | Column to store loaded file content (defaults to 'content').                                   |
            +------------------+----------+--------------------------------------------------------------------------------------------------+
            | as_text          |   No     | Whether to read files as text (True) or bytes (False). Defaults to True.                      |
            +------------------+----------+--------------------------------------------------------------------------------------------------+
            | group_analysis   |   No     | If True, group rows by description_column before analysis. Defaults to auto-detection.         |
            +------------------+----------+--------------------------------------------------------------------------------------------------+
        Return

            A Pandas Dataframe with the Call Analysis statistics.

        Example Configuration (Dataframe Mode - Default):

        .. code-block:: yaml

            - CallAnalysis:
                prompt_file: prompt.txt
                llm:
                    llm: google
                    model: gemini-2.5-flash
                    temperature: 0.4
                    max_tokens: 4096
                use_dataframe: true
                description_column: call_id
                file_path_column: srt_file_path
                content_column: transcript_content
                output_column: call_analysis
                as_text: true
                columns:
                    - call_id
                    - customer_name
                    - agent_name
                    - duration
                    - call_date
                    - srt_file_path

        Example Configuration (File Mode):

        .. code-block:: yaml

            - CallAnalysis:
                prompt_file: prompt.txt
                llm:
                    llm: google
                    model: gemini-2.5-flash
                    temperature: 0.4
                    max_tokens: 4096
                use_dataframe: false
                directory: /home/ubuntu/symbits/placerai/traffic/{day_six}/
                pattern: "*.srt"
                description_column: filename
                content_column: transcript_content
                output_column: call_analysis
                as_text: true

        Example Configuration (BytesIO Mode):

        .. code-block:: yaml

            - CallAnalysis:
                prompt_file: prompt.txt
                llm:
                  llm: google
                  model: gemini-2.5-flash
                  temperature: 0.4
                  max_tokens: 4096
                use_dataframe: true
                use_bytes_input: true
                bytes_column: transcript_srt_bytesio
                content_column: transcript_content
                description_column: call_id
                output_column: call_analysis
                as_text: true
                columns:
                  - call_id
                  - customer_name

    """ # noqa

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        # Set default goal for call analysis
        kwargs.setdefault(
            'goal',
            'Your task is to analyze call recordings and provide detailed sentiment analysis'
        )

        super().__init__(
            loop=loop, job=job, stat=stat, **kwargs
        )

        # File handling parameters
        self.use_dataframe: bool = kwargs.get('use_dataframe', True)
        self.file_path_column: str = kwargs.get('file_path_column')
        self.directory: str = kwargs.get('directory')
        self.pattern: str = kwargs.get('pattern')
        self.content_column: str = kwargs.get('content_column', 'content')
        self.as_text: bool = kwargs.get('as_text', True)
        self.group_analysis: bool = kwargs.get('group_analysis', None)

        # BytesIO input parameters
        self.use_bytes_input: bool = kwargs.get('use_bytes_input', False)
        self.bytes_column: str = kwargs.get('bytes_column')

        # Columns to preserve in the result (required by ParrotBot)
        self.columns: list = kwargs.get('columns', [])

        # Set survey mode to True to avoid rating column dependency
        self._survey_mode: bool = True  # Force survey mode to avoid rating column

        # Override goal if not provided
        self._goal: str = kwargs.get(
            'goal',
            'Your task is to analyze call recordings and provide detailed sentiment analysis'
        )

    def load_from_file(
        self,
        df: pd.DataFrame,
        field: str,
        column: str = None,
        as_text: bool = True
    ) -> pd.DataFrame:
        """
        Loads the content of a file specified as a path in `column` into `field`.

        Args:
            df: pandas DataFrame with a column containing file paths.
            field: name of the new column to store the file content.
            column: name of the column with file paths (defaults to `field`).
            as_text: if True, read file as text; otherwise, read as bytes.
        """
        if column is None:
            column = field

        def read_file_content(path: str) -> str | bytes | None:
            if not isinstance(path, str):
                self._logger.warning(f"Invalid path type: {type(path)}, expected string")
                return None
            if pd.isna(path) or path.strip() == '':
                self._logger.warning("Empty or NaN path found")
                return None
            try:
                with open(path, 'r' if as_text else 'rb') as f:
                    content = f.read()
                    self._logger.debug(f"Successfully loaded content from {path}")
                    return content
            except FileNotFoundError:
                self._logger.error(f"File not found: {path}")
                return None
            except PermissionError:
                self._logger.error(f"Permission denied reading file: {path}")
                return None
            except Exception as e:
                self._logger.error(f"Error reading {path}: {e}")
                return None

        df[field] = df[column].apply(read_file_content)
        return df

    def load_from_bytesio(
        self,
        df: pd.DataFrame,
        field: str,
        column: str = None,
        as_text: bool = True
    ) -> pd.DataFrame:
        """
        Loads content from BytesIO objects in a column into a new field.

        Args:
            df: pandas DataFrame with a column containing BytesIO objects.
            field: name of the new column to store the content.
            column: name of the column with BytesIO objects (defaults to `field`).
            as_text: if True, decode bytes to text; otherwise, return bytes.
        """
        if column is None:
            column = field

        def read_bytesio_content(bytesio_obj) -> str | bytes | None:
            from io import BytesIO

            if not isinstance(bytesio_obj, BytesIO):
                self._logger.warning(f"Invalid type: {type(bytesio_obj)}, expected BytesIO")
                return None
            if pd.isna(bytesio_obj) or bytesio_obj is None:
                self._logger.warning("Empty or NaN BytesIO object found")
                return None
            try:
                # Read content from BytesIO
                bytesio_obj.seek(0)  # Ensure we're at the beginning
                content = bytesio_obj.read()

                # Convert to text if requested
                if as_text and isinstance(content, bytes):
                    try:
                        content = content.decode('utf-8')
                    except UnicodeDecodeError:
                        self._logger.warning("Failed to decode bytes as UTF-8, returning raw bytes")

                self._logger.debug(f"Successfully loaded content from BytesIO object")
                return content
            except Exception as e:
                self._logger.error(f"Error reading BytesIO object: {e}")
                return None

        df[field] = df[column].apply(read_bytesio_content)
        return df

    async def start(self, **kwargs):
        """
        start

        Overview

            The start method is a method for starting the CallAnalysis component.
            Validates required parameters and loads file content.

        Parameters

            kwargs: dict
                A dictionary containing the parameters for the CallAnalysis component.

        Return

            True if the CallAnalysis component started successfully.

        """
        if self.previous:
            self.data = self.input
        # Check if we're in dataframe mode or file mode
        if not self.use_dataframe:
            # File mode - use directory and pattern like FileList
            self._logger.info("Using file mode with directory and pattern")

            # Validate required parameters for file mode
            if not self.directory:
                from ..exceptions import ConfigError
                raise ConfigError(
                    f"{self._bot_name.lower()}: directory is required when use_dataframe is false"
                )

            if not self.pattern:
                from ..exceptions import ConfigError
                raise ConfigError(
                    f"{self._bot_name.lower()}: pattern is required when use_dataframe is false"
                )

            # Process directory with mask replacement
            if isinstance(self.directory, str) and "{" in self.directory:
                self.directory = self.mask_replacement(self.directory)
                self._logger.info(f"Directory after mask replacement: {self.directory}")

            # Check if directory exists
            from pathlib import Path
            dir_path = Path(self.directory)
            if not dir_path.exists() or not dir_path.is_dir():
                from ..exceptions import ComponentError
                raise ComponentError(f"Directory doesn't exist: {self.directory}")

            # Find files matching pattern
            import glob
            pattern_path = dir_path / self.pattern
            matching_files = glob.glob(str(pattern_path))

            if not matching_files:
                from ..exceptions import ComponentError
                raise ComponentError(f"No files found matching pattern: {pattern_path}")

            # Create dataframe with found files
            import pandas as pd
            data = []
            for file_path in matching_files:
                path_obj = Path(file_path)
                data.append({
                    self._desc_column: path_obj.stem,  # filename without extension
                    'file_path': str(file_path),
                    'full_filename': path_obj.name  # Keep full filename with extension
                })

            self.data = pd.DataFrame(data)
            self.file_path_column = 'file_path'  # Set the column name for file paths
            self._logger.info(
                f"Found {len(self.data)} files matching pattern '{self.pattern}' in directory '{self.directory}'"
            )

            # Set up columns for ParrotBot (include description_column and file_path)
            if not self.columns:
                self.columns = [self._desc_column, 'file_path', 'full_filename']
            else:
                # Ensure description_column is in columns
                if self._desc_column not in self.columns:
                    self.columns.append(self._desc_column)
                if 'file_path' not in self.columns:
                    self.columns.append('file_path')
                if 'full_filename' not in self.columns:
                    self.columns.append('full_filename')

            # Set up the data for ParrotBot (bypass the previous component check)
            self.input = self.data
            self._component = self  # Set _component to self to satisfy ParrotBot's previous check

            # Call parent start method for file mode
            await super().start(**kwargs)

        else:
            # Dataframe mode - first call parent start to initialize self.data
            if self.use_bytes_input:
                self._logger.info("Using dataframe mode with BytesIO input")
            else:
                self._logger.info("Using dataframe mode with file path input")

            # Call parent start method FIRST to initialize self.data from previous component
            await super().start(**kwargs)

            # NOW validate required parameters based on input mode
            if self.use_bytes_input:
                # BytesIO mode - validate bytes_column parameter
                if not self.bytes_column:
                    from ..exceptions import ConfigError
                    raise ConfigError(
                        f"{self._bot_name.lower()}: bytes_column is required when use_bytes_input is true"
                    )

                # Check if bytes_column exists in the data (NOW self.data is initialized)
                if self.bytes_column not in self.data.columns:
                    from ..exceptions import ComponentError
                    raise ComponentError(
                        f"{self._bot_name.lower()}: bytes_column '{self.bytes_column}' not found in data columns: {list(self.data.columns)}"
                    )

                # Set up columns for ParrotBot
                if not self.columns:
                    # Default columns: include description_column and bytes_column
                    self.columns = [self._desc_column, self.bytes_column]
                else:
                    # Ensure required columns are in the list
                    if self._desc_column not in self.columns:
                        self.columns.append(self._desc_column)
                    if self.bytes_column not in self.columns:
                        self.columns.append(self.bytes_column)

            else:
                # File path mode - validate file_path_column parameter
                if not self.file_path_column:
                    from ..exceptions import ConfigError
                    raise ConfigError(
                        f"{self._bot_name.lower()}: file_path_column is required when use_dataframe is true and use_bytes_input is false"
                    )

                # Check if file_path_column exists in the data (NOW self.data is initialized)
                if self.file_path_column not in self.data.columns:
                    from ..exceptions import ComponentError
                    raise ComponentError(
                        f"{self._bot_name.lower()}: file_path_column '{self.file_path_column}' not found in data columns: {list(self.data.columns)}"  # noqa
                    )

                # In dataframe mode with file paths, preserve ALL original columns by default
                if not self.columns:
                    # By default, preserve all columns from the input dataframe
                    self.columns = list(self.data.columns)
                else:
                    # Ensure required columns are in the list
                    if self._desc_column not in self.columns:
                        self.columns.append(self._desc_column)
                    if self.file_path_column not in self.columns:
                        self.columns.append(self.file_path_column)

                self._logger.info(f"Using dataframe mode with {len(self.data)} rows")
                self._logger.info(f"Preserving columns: {self.columns}")

        # Load content into the dataframe based on input mode
        if self.use_bytes_input:
            # Load from BytesIO objects
            self._logger.info(f"Loading content from BytesIO column '{self.bytes_column}' into '{self.content_column}'")
            self.data = self.load_from_bytesio(
                df=self.data,
                field=self.content_column,
                column=self.bytes_column,
                as_text=self.as_text
            )
        else:
            # Load from file paths
            self._logger.info(f"Loading file content from column '{self.file_path_column}' into '{self.content_column}'")
            self.data = self.load_from_file(
                df=self.data,
                field=self.content_column,
                column=self.file_path_column,
                as_text=self.as_text
            )

        # Set eval_column to the content column for bot processing
        self._eval_column = self.content_column

        # Log statistics
        content_loaded = self.data[self.content_column].notna().sum()
        total_records = len(self.data)
        source_type = "BytesIO objects" if self.use_bytes_input else "files"
        self._logger.info(f"Successfully loaded content from {content_loaded}/{total_records} {source_type}")

        return True

    def format_question(self, call_identifier, transcripts, row=None):
        """
        Format the question for call analysis.

        Args:
            call_identifier: identifier for the call (from description_column)
            transcripts: list of transcript content
            row: optional row data for additional context

        Returns:
            str: formatted question for the AI bot
        """
        # Combine all transcripts for this call identifier
        combined_transcript = "\n\n".join([
            transcript.strip() if transcript and len(transcript) < 10000
            else (transcript[:10000] + "..." if transcript else "")
            for transcript in transcripts
        ])

        question = f"""
        Call ID: {call_identifier}

        Please analyze the following call transcript and provide a detailed sentiment analysis:

        TRANSCRIPT:
        {combined_transcript}

        Please provide your analysis in the specified JSON format.
        """

        return question

    async def bot_evaluation(self):
        """
        bot_evaluation

        Overview

            Custom bot evaluation for call analysis that doesn't require rating column.

        Return

            A Pandas Dataframe with the Call Analysis results.

        """
        # Determine if we should group the data or process row by row
        should_group = self.group_analysis

        if should_group is None:
            # Auto-detect: check if we have duplicate description values
            unique_desc_values = self.data[self._desc_column].nunique()
            total_rows = len(self.data)
            should_group = unique_desc_values < total_rows

            if should_group:
                self._logger.info(
                    f"Auto-detected grouping: {total_rows} rows {unique_desc_values} unique {self._desc_column} values"
                )
            else:
                self._logger.info(
                    f"Auto-detected row-by-row mode: {total_rows} unique rows"
                )

        if should_group:
            # Group mode: combine transcripts with same description_column value
            grouped = self.data.groupby(self._desc_column)[self._eval_column].apply(list).reset_index()
            _evaluation = {}

            for _, row in grouped.iterrows():
                call_identifier = row[self._desc_column]
                transcripts = row[self._eval_column]

                # Skip if all transcripts are empty
                valid_transcripts = [t for t in transcripts if t and not pd.isna(t)]
                if not valid_transcripts:
                    self._logger.warning(f"No valid transcripts for {call_identifier}, skipping")
                    continue

                # Use our custom format_question method
                formatted_question = self.format_question(call_identifier, valid_transcripts, row)

                try:
                    result = await self._bot.invoke(
                        question=formatted_question,
                    )
                    _evaluation[call_identifier] = result.output
                except Exception as e:
                    self._logger.error(f"Error analyzing {call_identifier}: {e}")
                    _evaluation[call_identifier] = None

            # For grouped mode, create result by taking first row of each group
            # and preserving columns specified in self.columns
            result_df = self.data.groupby(self._desc_column, as_index=False).first()

            # Keep only the columns we want to preserve
            columns_to_keep = [col for col in self.columns if col in result_df.columns]
            result_df = result_df[columns_to_keep]

            # Add the Call Analysis column
            result_df[self.output_column] = result_df[self._desc_column].map(
                lambda x: _evaluation.get(x)
            )

        else:
            # Row-by-row mode: process each row individually
            # Create a copy of the original dataframe to preserve all columns
            result_df = self.data[self.columns].copy() if self.columns else self.data.copy()

            # Process each row individually
            analysis_results = []
            for idx, row in self.data.iterrows():
                call_identifier = row[self._desc_column]
                transcript = row[self._eval_column]

                # Skip if no content
                if pd.isna(transcript) or not transcript:
                    self._logger.warning(f"No content for row {idx} ({call_identifier}), skipping analysis")
                    analysis_results.append(None)
                    continue

                # Format question with single transcript
                formatted_question = self.format_question(call_identifier, [transcript], row)

                try:
                    result = await self._bot.invoke(
                        question=formatted_question,
                    )
                    analysis_results.append(result.output)
                except Exception as e:
                    self._logger.error(f"Error analyzing row {idx} ({call_identifier}): {e}")
                    analysis_results.append(None)

            # Add the analysis results as a new column
            result_df[self.output_column] = analysis_results

        # Clean up JSON formatting in the output column if present
        if self.output_column in result_df.columns and not result_df[self.output_column].isna().all():
            import re
            result_df[self.output_column] = result_df[self.output_column].apply(
                lambda x: re.sub(r'^```json\s*|\s*```$', '', str(x), flags=re.MULTILINE) if x else None
            )

        # Log summary
        total_analyzed = result_df[self.output_column].notna().sum()
        self._logger.info(f"Analysis complete: {total_analyzed}/{len(result_df)} rows analyzed successfully")

        return result_df

    async def run(self):
        """
        Run the CallAnalysis component.

        Returns:
            pandas.DataFrame: DataFrame with call analysis results
        """
        self._result = await self.bot_evaluation()
        self._print_data_(self._result, 'CallAnalysis')
        return self._result

    async def close(self):
        """
        Close the CallAnalysis component.
        """
        pass
