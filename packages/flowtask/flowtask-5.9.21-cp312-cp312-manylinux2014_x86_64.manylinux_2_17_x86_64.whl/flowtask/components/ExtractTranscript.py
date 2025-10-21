import asyncio
import tempfile
import logging
import sys
import glob
from io import StringIO
from typing import List, Optional
from collections.abc import Callable
from pathlib import Path, PurePath
from io import BytesIO
import pandas as pd
from tqdm import tqdm
from parrot.loaders.audio import AudioLoader
from .flow import FlowComponent
from ..interfaces.Boto3Client import Boto3Client
from ..exceptions import ConfigError, ComponentError


class ExtractTranscript(Boto3Client, FlowComponent):
    """
    ExtractTranscript Component

    **Overview**

    This component extracts audio transcripts, VTT subtitles, SRT files with speaker diarization,
    and AI-generated summaries from audio files specified in a DataFrame. It uses Parrot's
    AudioLoader which leverages WhisperX for high-quality transcription with word-level timestamps.

    The component processes audio files in batch from a pandas DataFrame and generates multiple
    output formats for each audio file, returning an enhanced DataFrame with paths to all
    generated files.

    .. table:: Properties
       :widths: auto

    +----------------------------+----------+----------------------------------------------------------------------------------------------+
    |   Name                     | Required | Summary                                                                                      |
    +----------------------------+----------+----------------------------------------------------------------------------------------------+
    |   audio_column             | Yes*     | Name of DataFrame column containing audio file paths. Default: `"audio_path"`.              |
    |                            |          | The DataFrame must contain this column with valid paths to audio files.                     |
    |                            |          | *Not required if `use_bytes_input` is `true`.                                               |
    +----------------------------+----------+----------------------------------------------------------------------------------------------+
    |   use_bytes_input          | No       | Enable BytesIO input mode for in-memory audio data. Default: `false`.                      |
    |                            |          | When `true`, reads audio from BytesIO objects instead of file paths.                        |
    +----------------------------+----------+----------------------------------------------------------------------------------------------+
    |   bytes_column             | No       | Name of DataFrame column containing BytesIO audio data. Default: `"file_data"`.             |
    |                            |          | Only used when `use_bytes_input` is `true`.                                                 |
    +----------------------------+----------+----------------------------------------------------------------------------------------------+
    |   filename_column          | No       | Name of DataFrame column containing original filenames. Default: `"downloaded_filename"`.   |
    |                            |          | Only used when `use_bytes_input` is `true`. Used for naming temporary files.               |
    +----------------------------+----------+----------------------------------------------------------------------------------------------+
    |   language                 | No       | Language code for transcription. Accepts language codes like `"en"`, `"es"`, `"fr"`, etc.   |
    |                            |          | Default: `"en"`. Used to improve transcription accuracy.                                    |
    +----------------------------+----------+----------------------------------------------------------------------------------------------+
    |   model_size               | No       | Whisper model size for transcription. Accepts `"tiny"`, `"small"`, `"medium"`, `"large"`.   |
    |                            |          | Default: `"small"`. Larger models provide better accuracy but require more resources.       |
    +----------------------------+----------+----------------------------------------------------------------------------------------------+
    |   diarization              | No       | Enable speaker diarization to identify different speakers in the audio.                     |
    |                            |          | Default: `false`. When enabled, generates SRT files with speaker labels.                    |
    +----------------------------+----------+----------------------------------------------------------------------------------------------+
    |   summarization            | No       | Enable AI-generated summaries of the transcripts.                                          |
    |                            |          | Default: `true`. Generates summary files using LLM models.                                 |
    +----------------------------+----------+----------------------------------------------------------------------------------------------+
    |   device                   | No       | Device to use for processing. Accepts `"cpu"`, `"cuda"`, or `"mps"`.                       |
    |                            |          | Default: `"cpu"`. Use `"cuda"` for GPU acceleration (10-20x faster).                       |
    +----------------------------+----------+----------------------------------------------------------------------------------------------+
    |   skip_errors              | No       | Continue processing if a file fails. Default: `true`.                                      |
    |                            |          | When `false`, the first error stops the entire workflow.                                   |
    +----------------------------+----------+----------------------------------------------------------------------------------------------+

    **Returns**

    This component returns a pandas DataFrame containing the original data plus additional
    columns with transcription results. The structure includes:

    - **Original DataFrame columns**: All columns from the input DataFrame are preserved.
    - **transcript_success**: Boolean indicating if processing succeeded for each file.
    - **transcript_error**: Error message if processing failed (None if successful).
    - **transcript_vtt_path**: Path to generated WebVTT file with timestamps.
    - **transcript_transcript_path**: Path to plain text transcript file.
    - **transcript_srt_path**: Path to SRT subtitle file (if diarization enabled).
    - **transcript_summary_path**: Path to AI-generated summary file.
    - **transcript_summary**: Summary text content.
    - **transcript_language**: Detected or specified language.

    **Example**

    ```yaml
    ExtractTranscript:
      audio_column: audio_path
      language: en
      model_size: small
      diarization: false
      summarization: true
      device: cuda
      cuda_number: 0
      skip_errors: true
    ```

    """  # noqa

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        """Initialize ExtractTranscript component.

        Args:
            audio_column: Name of DataFrame column containing audio file paths (default: 'audio_path')
            use_bytes_input: Enable BytesIO input mode (default: False)
            bytes_column: Name of DataFrame column containing BytesIO audio data (default: 'file_data')
            filename_column: Name of DataFrame column containing original filenames (default: 'downloaded_filename')
            language: Language code for transcription (default: 'en')
            model_size: Whisper model size: tiny, small, medium, large (default: 'small')
            model_name: Explicit model name (optional, overrides model_size)
            diarization: Enable speaker diarization (default: False)
            summarization: Enable summary generation (default: True)
            device: Device to use: cpu, cuda, mps (default: 'cpu')
            cuda_number: CUDA device number if multiple GPUs (default: 0)
            source_type: Source type for metadata (default: 'AUDIO')
            batch_size: Batch size for processing (default: 1)
            skip_errors: Continue processing if a file fails (default: True)
        """
        # Input mode configuration
        self.use_bytes_input: bool = kwargs.pop('use_bytes_input', False)
        self.bytes_column: str = kwargs.pop('bytes_column', 'file_data')
        self.filename_column: str = kwargs.pop('filename_column', 'downloaded_filename')

        # Audio processing configuration
        self.audio_column: str = kwargs.pop('audio_column', 'audio_path')
        self.language: str = kwargs.pop('language', 'en')
        self.model_size: str = kwargs.pop('model_size', 'small')
        self.model_name: Optional[str] = kwargs.pop('model_name', None)
        self.diarization: bool = kwargs.pop('diarization', True)
        self.summarization: bool = kwargs.pop('summarization', True)
        self.source_type: str = kwargs.pop('source_type', 'AUDIO')
        self.do_summarization: bool = kwargs.pop('summarization', False)

        # Device configuration
        self._device: str = kwargs.pop('device', 'cpu')
        self._cuda_number: int = kwargs.pop('cuda_number', 0)

        # Processing configuration
        self.batch_size: int = kwargs.pop('batch_size', 1)
        self.skip_errors: bool = kwargs.pop('skip_errors', True)

        # S3 upload configuration
        self.save_s3: bool = kwargs.pop('save_s3', False)
        self._s3_config: str = kwargs.pop('s3_config', 'default')
        self.s3_directory: str = kwargs.pop('directory', 'transcripts/')
        self.generate_presigned_url: bool = kwargs.pop('generate_presigned_url', False)
        self.url_expiration: int = kwargs.pop('url_expiration', 3600)

        # Pass config to Boto3Client if S3 is enabled
        if self.save_s3:
            kwargs['config'] = self._s3_config

        super().__init__(
            loop=loop, job=job, stat=stat, **kwargs
        )

        # AudioLoader instance (initialized in start)
        self._audio_loader: Optional[AudioLoader] = None

    async def start(self, **kwargs):
        """Initialize the component and validate configuration."""
        await super().start(**kwargs)

        # Validate that we have input from previous component
        if self.previous is None or self.input is None:
            raise ConfigError(
                "ExtractTranscript requires input from a previous component (e.g., DataFrame)"
            )

        # Validate input is a DataFrame
        if not isinstance(self.input, pd.DataFrame):
            raise ComponentError(
                f"ExtractTranscript expects a DataFrame as input, got {type(self.input)}"
            )

        # Validate columns based on input mode
        if self.use_bytes_input:
            # Validate BytesIO columns exist
            if self.bytes_column not in self.input.columns:
                raise ConfigError(
                    f"Column '{self.bytes_column}' not found in input DataFrame. "
                    f"Available columns: {list(self.input.columns)}"
                )
            if self.filename_column not in self.input.columns:
                raise ConfigError(
                    f"Column '{self.filename_column}' not found in input DataFrame. "
                    f"Available columns: {list(self.input.columns)}"
                )
        else:
            # Validate audio_column exists in DataFrame
            if self.audio_column not in self.input.columns:
                raise ConfigError(
                    f"Column '{self.audio_column}' not found in input DataFrame. "
                    f"Available columns: {list(self.input.columns)}"
                )

        # Initialize AudioLoader with configuration
        self._audio_loader = AudioLoader(
            source=None,  # We'll pass source per file
            language=self.language,
            source_type=self.source_type,
            diarization=self.diarization,
            model_size=self.model_size,
            model_name=self.model_name,
            device=self._device,
            cuda_number=self._cuda_number,
            use_summary_pipeline=self.do_summarization,
            video_path=None,  # Not needed for audio-only processing
        )

        # Initialize S3 connection if save_s3 is enabled
        if self.save_s3:
            # Process credentials (similar to UploadToS3)
            self.processing_credentials()

            # Ensure directory has trailing slash
            if self.s3_directory and not self.s3_directory.endswith("/"):
                self.s3_directory += "/"

            # Open S3 connection
            await self.open()

    async def close(self):
        """Clean up resources."""
        if self._audio_loader:
            # Clear any CUDA cache if used
            if hasattr(self._audio_loader, 'clear_cuda'):
                self._audio_loader.clear_cuda()
        await super().close()

    async def _generate_presigned_url(self, s3_key: str) -> str:
        """Generate a presigned URL for the S3 object."""
        try:
            url = self._connection.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': s3_key},
                ExpiresIn=self.url_expiration
            )
            return url
        except Exception as e:
            self._logger.error(f"Error generating presigned URL for {s3_key}: {e}")
            return None

    async def _upload_to_s3(self, metadata: dict, base_filename: str) -> dict:
        """
        Upload all files (audio + transcripts) to S3 and generate presigned URLs.

        Args:
            metadata: Dict containing BytesIO objects and file info
            base_filename: Base filename for S3 keys (e.g., "recording.mp3")

        Returns:
            Dict with S3 keys and URLs for each file type
        """
        s3_info = {}

        # Determine base name without extension for transcript files
        base_name = Path(base_filename).stem

        # Determine audio content type based on file extension
        audio_ext = Path(base_filename).suffix.lower()
        audio_content_type = 'audio/wav' if audio_ext == '.wav' else 'audio/mpeg'

        # Files to upload: (metadata_key, s3_suffix, content_type)
        files_to_upload = [
            ('audio_bytesio', base_filename, audio_content_type),
            ('transcript_bytesio', f'{base_name}.txt', 'text/plain'),
            ('vtt_bytesio', f'{base_name}.vtt', 'text/vtt'),
            ('summary_bytesio', f'{base_name}.summary', 'text/plain'),
            ('srt_bytesio', f'{base_name}.srt', 'application/x-subrip'),
        ]

        for bytesio_key, s3_filename, content_type in files_to_upload:
            if bytesio_key in metadata and metadata[bytesio_key]:
                file_data = metadata[bytesio_key]
                s3_key = f"{self.s3_directory}{s3_filename}"

                try:
                    # Upload to S3
                    file_data.seek(0)
                    content = file_data.read()

                    response = self._connection.put_object(
                        Bucket=self.bucket,
                        Key=s3_key,
                        Body=content,
                        ContentType=content_type,
                    )

                    status_code = response["ResponseMetadata"]["HTTPStatusCode"]

                    if status_code == 200:
                        # Determine the type from bytesio_key (e.g., 'audio_bytesio' -> 'audio')
                        file_type = bytesio_key.replace('_bytesio', '')

                        # Store S3 key
                        s3_info[f'{file_type}_s3_key'] = s3_key

                        # Generate presigned URL if enabled
                        if self.generate_presigned_url:
                            presigned_url = await self._generate_presigned_url(s3_key)
                            if presigned_url:
                                s3_info[f'{file_type}_s3_url'] = presigned_url
                    else:
                        self._logger.error(f"Failed to upload {s3_filename} to S3: {response}")

                except Exception as e:
                    self._logger.error(f"Error uploading {s3_filename} to S3: {e}")

        return s3_info

    async def _process_audio_file(
        self,
        audio_input,
        row_idx: int,
        filename: str = None,
        is_bytes: bool = False
    ) -> dict:
        """Process a single audio file and extract transcripts.

        Args:
            audio_input: Either a file path (str) or BytesIO object
            row_idx: Row index for logging
            filename: Original filename (used when is_bytes=True)
            is_bytes: Whether audio_input is a BytesIO object

        Returns:
            Dictionary with extracted metadata and file paths
        """
        temp_file = None
        files_to_delete = []  # Track all temporary files for cleanup
        try:
            if is_bytes:
                # Handle BytesIO input - create temporary file
                if not isinstance(audio_input, BytesIO):
                    raise ComponentError(f"Expected BytesIO object, got {type(audio_input)}")

                # Determine file extension from filename
                file_ext = Path(filename).suffix if filename else '.wav'
                if not file_ext:
                    file_ext = '.wav'

                # Create temporary file with appropriate extension
                temp_file = tempfile.NamedTemporaryFile(
                    mode='wb',
                    suffix=file_ext,
                    delete=False,
                    prefix='extract_transcript_'
                )

                # Write BytesIO content to temporary file
                audio_input.seek(0)  # Ensure we're at the beginning
                temp_file.write(audio_input.read())
                temp_file.flush()
                temp_file.close()

                # Use the temporary file path
                path = Path(temp_file.name)
                display_name = filename or path.name

            else:
                # Handle file path input (original behavior)
                path = Path(audio_input).resolve()

                if not path.exists():
                    raise FileNotFoundError(f"Audio file not found: {path}")

                display_name = path.name

            # Extract audio using Parrot's AudioLoader (suppress verbose output)
            # Redirect stdout/stderr to suppress print() statements from Parrot
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = StringIO()
            sys.stderr = StringIO()

            try:
                metadata = await self._audio_loader.extract_audio(path)
            finally:
                # Restore stdout/stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr

            # Add success flag
            metadata['success'] = True
            metadata['error'] = None

            # If BytesIO mode, read generated files and convert to BytesIO
            if is_bytes:
                # Get the base name (without extension) of the temp file
                temp_base = path.stem  # e.g., "extract_transcript_e8sjit72"
                temp_dir = path.parent  # e.g., "/tmp"

                # Find ALL files with the same base name using glob
                # This captures all files generated by AudioLoader, including intermediates
                pattern = str(temp_dir / f"{temp_base}.*")
                all_generated_files = glob.glob(pattern)

                # Find and read the .wav file generated by AudioLoader
                wav_file = None
                for file_str in all_generated_files:
                    if file_str.endswith('.wav'):
                        wav_file = Path(file_str)
                        break

                # Use .wav file if found, otherwise use original audio
                if wav_file and wav_file.exists():
                    try:
                        # Read wav file and convert to BytesIO
                        with open(wav_file, 'rb') as f:
                            wav_content = f.read()

                        wav_bytesio = BytesIO(wav_content)
                        wav_bytesio.seek(0)
                        metadata['audio_bytesio'] = wav_bytesio

                        # Update filename to .wav extension
                        base_name = Path(filename).stem
                        metadata['original_filename'] = f"{base_name}.wav"
                    except Exception as e:
                        self._logger.warning(f"Failed to read wav file {wav_file}, using original: {e}")
                        audio_input.seek(0)
                        metadata['audio_bytesio'] = audio_input
                        metadata['original_filename'] = filename
                else:
                    # Fallback to original audio if no wav found
                    audio_input.seek(0)
                    metadata['audio_bytesio'] = audio_input
                    metadata['original_filename'] = filename

                # Read generated files and create BytesIO objects
                files_to_read = {
                    'transcript_path': 'transcript_bytesio',
                    'vtt_path': 'vtt_bytesio',
                    'summary_path': 'summary_bytesio',
                    'srt_path': 'srt_bytesio',
                }

                for path_key, bytesio_key in files_to_read.items():
                    if path_key in metadata and metadata[path_key]:
                        file_path = Path(metadata[path_key])

                        # Try to read and convert to BytesIO
                        if file_path.exists():
                            try:
                                # Read file content
                                with open(file_path, 'rb') as f:
                                    content = f.read()

                                # Create BytesIO object
                                file_bytesio = BytesIO(content)
                                file_bytesio.seek(0)
                                metadata[bytesio_key] = file_bytesio
                            except Exception as e:
                                self._logger.warning(f"Failed to read {file_path}: {e}")
                                metadata[bytesio_key] = None
                        else:
                            metadata[bytesio_key] = None
                    else:
                        metadata[bytesio_key] = None

                # Mark ALL generated files for deletion (including intermediates like .wav)
                for file_str in all_generated_files:
                    file_path = Path(file_str)
                    if file_path.exists() and file_path not in files_to_delete:
                        files_to_delete.append(file_path)

            else:
                # File path mode - log completion (only if not using tqdm to avoid conflicts)
                self._logger.debug(f"✓ Completed: {path.name}")
                if 'transcript_path' in metadata:
                    self._logger.debug(f"  - Transcript: {metadata['transcript_path']}")
                if 'vtt_path' in metadata:
                    self._logger.debug(f"  - VTT: {metadata['vtt_path']}")
                if metadata.get('summary'):
                    self._logger.debug("  - Summary generated")

            return metadata

        except Exception as e:
            error_msg = f"Error processing {filename if is_bytes else audio_input}: {str(e)}"

            if self.skip_errors:
                # Return error metadata
                return {
                    'success': False,
                    'error': str(e),
                    'source': filename if is_bytes else audio_input,
                    'vtt_path': None,
                    'transcript_path': None,
                    'srt_path': None,
                    'summary_path': None,
                    'summary': None,
                    'language': None,
                }
            else:
                raise ComponentError(error_msg) from e

        finally:
            # Clean up ALL temporary files (silently to avoid breaking tqdm)
            cleanup_errors = []

            # Delete all files marked for deletion
            if is_bytes and files_to_delete:
                for file_path in files_to_delete:
                    try:
                        if file_path.exists():
                            file_path.unlink()
                    except Exception as e:
                        cleanup_errors.append(f"{file_path.name}: {e}")

            # Log cleanup errors only if any occurred (to avoid breaking tqdm)
            if cleanup_errors:
                self._logger.warning(
                    f"Failed to delete {len(cleanup_errors)} temporary file(s): {', '.join(cleanup_errors)}"
                )

    async def run(self):
        """Process all audio files in the DataFrame."""
        df = self.input.copy()

        # Suppress verbose logging from external libraries to keep tqdm clean
        logging.getLogger('parrot').setLevel(logging.ERROR)
        logging.getLogger('whisperx').setLevel(logging.ERROR)
        logging.getLogger('pyannote').setLevel(logging.ERROR)
        logging.getLogger('pytorch_lightning').setLevel(logging.ERROR)
        logging.getLogger('pytorch_lightning.utilities').setLevel(logging.ERROR)
        logging.getLogger('pytorch_lightning.utilities.migration').setLevel(logging.ERROR)
        logging.getLogger('fsspec').setLevel(logging.ERROR)
        logging.getLogger('speechbrain').setLevel(logging.ERROR)
        logging.getLogger('speechbrain.utils').setLevel(logging.ERROR)
        logging.getLogger('torio').setLevel(logging.ERROR)
        logging.getLogger('torio._extension').setLevel(logging.ERROR)

        # Process each audio file with progress bar
        results = []

        with tqdm(total=len(df), desc="🎙️ Transcribing audio", unit="files", colour="cyan") as pbar:
            for idx, row in df.iterrows():
                if self.use_bytes_input:
                    # Process BytesIO input
                    audio_data = row[self.bytes_column]
                    filename = row.get(self.filename_column, f"audio_{idx}")

                    # Skip if data is None or empty
                    if pd.isna(audio_data) or audio_data is None:
                        empty_metadata = {
                            'success': False,
                            'error': 'No audio data provided',
                            'source': filename,
                            'vtt_path': None,
                            'transcript_path': None,
                            'srt_path': None,
                            'summary_path': None,
                            'summary': None,
                            'language': None,
                        }
                        results.append(empty_metadata)
                        self._update_dataframe_row(df, idx, empty_metadata)
                        pbar.update(1)
                        continue

                    # Process the audio from BytesIO
                    result = await self._process_audio_file(
                        audio_data,
                        idx,
                        filename=filename,
                        is_bytes=True
                    )

                    # Upload to S3 if enabled and processing was successful
                    if self.save_s3 and result.get('success'):
                        # Use the updated filename (now .wav instead of .mp3)
                        upload_filename = result.get('original_filename', filename)
                        s3_info = await self._upload_to_s3(result, upload_filename)
                        # Merge S3 info into result
                        result.update(s3_info)

                    results.append(result)
                    self._update_dataframe_row(df, idx, result)

                else:
                    # Process file path input (original behavior)
                    audio_path = row[self.audio_column]

                    # Skip if path is None or empty
                    if pd.isna(audio_path) or not audio_path:
                        empty_metadata = {
                            'success': False,
                            'error': 'No audio path provided',
                            'source': None,
                            'vtt_path': None,
                            'transcript_path': None,
                            'srt_path': None,
                            'summary_path': None,
                            'summary': None,
                            'language': None,
                        }
                        results.append(empty_metadata)
                        self._update_dataframe_row(df, idx, empty_metadata)
                        pbar.update(1)
                        continue

                    # Process the audio file
                    result = await self._process_audio_file(
                        audio_path,
                        idx,
                        is_bytes=False
                    )
                    results.append(result)
                    self._update_dataframe_row(df, idx, result)

                pbar.update(1)

        # Calculate metrics
        success_count = sum(1 for r in results if r.get('success', False))
        error_count = len(results) - success_count

        self.add_metric('TOTAL_FILES', len(results))
        self.add_metric('SUCCESS_COUNT', success_count)
        self.add_metric('ERROR_COUNT', error_count)

        # Calculate S3 upload metrics if enabled
        if self.save_s3:
            s3_uploaded_count = sum(1 for r in results if r.get('audio_s3_key'))
            self.add_metric('S3_UPLOADED_COUNT', s3_uploaded_count)
            if self.generate_presigned_url:
                self.add_metric('S3_PRESIGNED_URLS', True)

        print(f"\n{'='*60}")
        print("Extraction complete:")
        print(f"  - Total files: {len(results)}")
        print(f"  - Successful: {success_count}")
        print(f"  - Errors: {error_count}")
        if self.save_s3:
            s3_uploaded_count = sum(1 for r in results if r.get('audio_s3_key'))
            print(f"  - Uploaded to S3: {s3_uploaded_count}")
            if self.generate_presigned_url:
                print(f"  - Presigned URLs generated: Yes")
        print(f"{'='*60}\n")

        # Set result as the enhanced DataFrame
        self._result = df

        return True

    def _update_dataframe_row(self, df: pd.DataFrame, row_idx: int, metadata: dict) -> None:
        """Persist AudioLoader metadata into the original DataFrame."""
        prefix = 'transcript_'

        def _normalize(value):
            """Convert metadata values into DataFrame-friendly objects."""
            if isinstance(value, pd.Series):
                return value.to_dict()
            if isinstance(value, pd.DataFrame):
                return value.to_dict(orient='list')
            if isinstance(value, (Path, PurePath)):
                return str(value)
            return value

        for key, value in metadata.items():
            column_name = f"{prefix}{key}"

            if column_name not in df.columns:
                df[column_name] = None

            df.at[row_idx, column_name] = _normalize(value)
