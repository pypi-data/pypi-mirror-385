import asyncio
import base64
import urllib.parse
from collections.abc import Callable
from typing import Optional, Dict, Any, List
from pathlib import Path
from io import BytesIO
import pandas as pd
import httpx
from tqdm import tqdm
from .flow import FlowComponent
from ..interfaces.http import HTTPService
from ..interfaces.cache import CacheSupport
from ..exceptions import ComponentError
from ..conf import (
    ZOOM_ACCOUNT_ID,
    ZOOM_CLIENT_ID,
    ZOOM_CLIENT_SECRET,
)


class Zoom(HTTPService, CacheSupport, FlowComponent):
    """
    Zoom Component

    Retrieves call logs and, for those that are recorded (recording_status=recorded),
    gets recording metadata and downloads:
      - audio/video files
      - transcripts, using the recordingId

    .. table:: Properties
       :widths: auto

    +-------------------------+----------+---------------------------------------------------------------------+
    | Name                    | Required | Summary                                                             |
    +-------------------------+----------+---------------------------------------------------------------------+
    | from_date               | Yes      | Start date (YYYY-MM-DD) for call logs                               |
    +-------------------------+----------+---------------------------------------------------------------------+
    | to_date                 | Yes      | End date (YYYY-MM-DD) for call logs                                 |
    +-------------------------+----------+---------------------------------------------------------------------+
    | save_path               | No       | Folder for recordings (default: /tmp/zoom/recordings)               |
    +-------------------------+----------+---------------------------------------------------------------------+
    | transcripts_path        | No       | Folder for transcripts (default: /tmp/zoom/transcripts)             |
    +-------------------------+----------+---------------------------------------------------------------------+
    | download                | No       | Download recordings (bool, default: True)                           |
    +-------------------------+----------+---------------------------------------------------------------------+
    | download_transcripts    | No       | Download transcripts (bool, default: True)                          |
    +-------------------------+----------+---------------------------------------------------------------------+
    | max_pages               | No       | Page limit for testing/debug                                         |
    +-------------------------+----------+---------------------------------------------------------------------+
    | base_path               | No       | Base path for all downloads (default: /tmp/zoom)                    |
    +-------------------------+----------+---------------------------------------------------------------------+
    | extension_column        | No       | DataFrame column name containing extensions to filter                |
    +-------------------------+----------+---------------------------------------------------------------------+
    | as_bytes                | No       | Store recordings/transcripts in memory as BytesIO (default: False)   |
    +-------------------------+----------+---------------------------------------------------------------------+
    | content_type            | No       | Default content type for recordings (default: 'audio/mpeg')          |
    +-------------------------+----------+---------------------------------------------------------------------+

    Returns:
        pandas.DataFrame with call logs and download information.
    """

    accept: str = "application/json"
    BASE_URL = "https://api.zoom.us/v2"
    AUTH_URL = "https://zoom.us/oauth/token"
    CACHE_KEY = "_zoom_authentication"

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        # ETL inputs
        self.from_date: str = kwargs.get("from_date")
        self.to_date: str = kwargs.get("to_date")

        base_path = Path(kwargs.get("base_path", "/tmp/zoom"))
        self.save_path: Path = Path(kwargs.get("save_path", base_path / "recordings"))
        self.transcripts_path: Path = Path(kwargs.get("transcripts_path", base_path / "transcripts"))

        self.download_recordings: bool = bool(kwargs.get("download", True))
        self.download_transcripts: bool = bool(kwargs.get("download_transcripts", True))
        self.max_pages: Optional[int] = kwargs.get("max_pages")

        # DataFrame filtering
        self.extension_column: Optional[str] = kwargs.get("extension_column", None)
        self._extensions_filter: List[str] = []

        # Memory storage options
        self.as_bytes: bool = kwargs.get("as_bytes", False)
        self.content_type: str = kwargs.get("content_type", "audio/mpeg")

        # State
        self._access_token: Optional[str] = None

        # Ensure folders exist (only if not using as_bytes)
        if not self.as_bytes:
            self.save_path.mkdir(parents=True, exist_ok=True)
            self.transcripts_path.mkdir(parents=True, exist_ok=True)

        super().__init__(loop=loop, job=job, stat=stat, **kwargs)

    # =========================
    # Auth
    # =========================
    async def get_cached_token(self) -> Optional[str]:
        """
        Try to get the OAuth Access Token from cache (Redis).
        """
        try:
            async with self as cache:
                token = await cache._redis.get(self.CACHE_KEY)
                if isinstance(token, bytes):
                    token = token.decode('utf-8', errors='ignore')
                if token and isinstance(token, str) and len(token) > 10:
                    self._logger.info(f"Using cached Zoom token: {token[:10]}...")
                    return token
                else:
                    self._logger.debug(f"Invalid or no token in cache: {token!r}")
        except Exception as e:
            self._logger.warning(f"Error getting cached token: {str(e)}")
        return None

    def set_auth_headers(self, token: str) -> None:
        """
        Set Bearer token in headers and keep it in memory.
        """
        self._access_token = token
        if not isinstance(self.headers, dict):
            self.headers = {}
        self.headers["Authorization"] = f"Bearer {token}"

    def _ensure_paths(self):
        """Force save_path and transcripts_path to be pathlib.Path and ensure dirs exist."""
        if not isinstance(self.save_path, Path):
            self.save_path = Path(self.save_path)
        if not isinstance(self.transcripts_path, Path):
            self.transcripts_path = Path(self.transcripts_path)
        self.save_path.mkdir(parents=True, exist_ok=True)
        self.transcripts_path.mkdir(parents=True, exist_ok=True)


    @staticmethod
    def _basic_header_value(client_id: str, client_secret: str) -> str:
        """
        Build the HTTP Basic header for OAuth token request.
        """
        creds = f"{client_id}:{client_secret}".encode("utf-8")
        return "Basic " + base64.b64encode(creds).decode("utf-8")

    async def _fetch_token(self) -> tuple[str, int]:
        """
        Get a fresh OAuth Access Token via Server-to-Server OAuth.
        Returns: (token, expires_in)
        """
        if not (ZOOM_ACCOUNT_ID and ZOOM_CLIENT_ID and ZOOM_CLIENT_SECRET):
            raise ComponentError("Missing Zoom S2S OAuth credentials")

        params = {
            "grant_type": "account_credentials",
            "account_id": ZOOM_ACCOUNT_ID,
        }
        headers = {
            "Accept": "application/json",
            "Authorization": self._basic_header_value(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET),
        }
        resp = await self._post(
            url=self.AUTH_URL,
            params=params,
            headers=headers,
            cookies=None,
            follow_redirects=True,
            raise_for_status=True,
            use_proxy=False,
        )
        data = resp.json()
        token = data.get("access_token")
        if not token:
            raise ComponentError("No access_token in Zoom OAuth response")
        return token, int(data.get("expires_in", 3600))

    async def start(self, **kwargs):
        """
        Ensure we have a valid token: try cache, else fetch and cache.
        Also process input DataFrame if provided.
        """
        # Apply masks to date attributes (masks are already processed by _mask_processing in __init__)
        if hasattr(self, "masks"):
            for mask, replace in self._mask.items():
                if self.from_date:
                    self.from_date = self.from_date.replace(mask, str(replace))
                if self.to_date:
                    self.to_date = self.to_date.replace(mask, str(replace))

        self._logger.info("🔐 Starting Zoom authentication...")
        token = await self.get_cached_token()
        if not token:
            self._logger.info("📡 Fetching new OAuth token from Zoom...")
            token, expires_in = await self._fetch_token()
            try:
                async with self as cache:
                    await cache.setex(self.CACHE_KEY, token, timeout=f"{expires_in}s")
                self._logger.info(f"💾 Token cached for {expires_in} seconds")
            except Exception as e:
                self._logger.warning(f"Couldn't cache token: {e}")
        self.set_auth_headers(token)
        if not self._access_token or "Authorization" not in self.headers:
            raise ComponentError("Authentication headers not properly set")
        self._logger.info("✅ Successfully authenticated with Zoom API")

        # Process input DataFrame if provided
        if self.previous and hasattr(self, 'input') and self.input is not None:
            if hasattr(self.input, 'empty'):  # It's a DataFrame
                if not self.input.empty:
                    self._logger.info(f"📊 Received input DataFrame with {len(self.input)} rows")
                    self._process_input_dataframe()

        return True

    async def _ensure_token(self):
        """
        Make sure we have an access token in memory and headers.
        If not, try cache; if still not, fetch a new one.
        """
        if self._access_token and "Authorization" in self.headers:
            return
        token = await self.get_cached_token()
        if not token:
            token, expires_in = await self._fetch_token()
            try:
                async with self as cache:
                    await cache.setex(self.CACHE_KEY, token, timeout=f"{expires_in}s")
            except Exception as e:
                self._logger.warning(f"Couldn't cache token: {e}")
        self.set_auth_headers(token)

    async def _refresh_token(self):
        """
        Force-refresh the token and update cache + headers.
        """
        token, expires_in = await self._fetch_token()
        try:
            async with self as cache:
                await cache.setex(self.CACHE_KEY, token, timeout=f"{expires_in}s")
        except Exception as e:
            self._logger.warning(f"Couldn't cache token: {e}")
        self.set_auth_headers(token)

    async def _authed_api_get(self, url: str, *, params=None, extra_headers: dict = None, use_http2=True):
        """
        Do a GET with auth guard + one retry on 401.
        """
        await self._ensure_token()
        headers = {**self.headers, "Accept": "application/json", **(extra_headers or {})}
        try:
            return await self.api_get(
                url=url,
                params=params,
                headers=headers,
                use_proxy=False,
                use_http2=use_http2
            )
        except Exception as e:
            msg = str(e).lower()
            if "401" in msg or "unauthorized" in msg:
                self._logger.warning("401 Unauthorized. Refreshing Zoom token and retrying once...")
                await self._refresh_token()
                headers = {**self.headers, "Accept": "application/json", **(extra_headers or {})}
                return await self.api_get(
                    url=url,
                    params=params,
                    headers=headers,
                    use_proxy=False,
                    use_http2=use_http2
                )
            raise

    # =========================
    # API helpers
    # =========================
    def _clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean column names by replacing dots with underscores for all columns.
        This handles nested JSON fields that get flattened with dots.
        """
        if df.empty:
            return df

        # Create mapping for all columns that contain dots
        column_mapping = {}
        for col in df.columns:
            if '.' in col:
                new_col = col.replace('.', '_')
                column_mapping[col] = new_col

        # Rename columns if any were found
        if column_mapping:
            df_renamed = df.rename(columns=column_mapping)
            self._logger.info(f"🔄 Renamed {len(column_mapping)} columns with dots to underscores")
            self._logger.debug(f"Column mappings: {column_mapping}")
            return df_renamed

        return df

    def _process_input_dataframe(self):
        """
        Process input DataFrame to extract extensions for filtering.
        Similar to ScrapTool's DataFrame processing.
        """
        if not self.extension_column:
            self._logger.debug("No extension_column specified, skipping extension filtering")
            return

        if self.extension_column not in self.input.columns:
            self._logger.warning(
                f"Extension column '{self.extension_column}' not found in input DataFrame. "
                f"Available columns: {list(self.input.columns)}"
            )
            return

        # Extract unique extensions from the column
        extensions = self.input[self.extension_column].dropna().astype(str).unique().tolist()
        self._extensions_filter = [ext.strip() for ext in extensions if ext.strip()]

        if self._extensions_filter:
            self._logger.info(
                f"🔍 Extracted {len(self._extensions_filter)} extensions from column '{self.extension_column}': "
                f"{', '.join(self._extensions_filter[:5])}"
                f"{' ...' if len(self._extensions_filter) > 5 else ''}"
            )
        else:
            self._logger.warning(f"No valid extensions found in column '{self.extension_column}'")

    async def call_logs(self) -> pd.DataFrame:
        """
        GET /phone/call_logs?from=...&to=... with pagination.
        """
        if not self.from_date or not self.to_date:
            raise ComponentError("from_date/to_date are required")

        self._logger.info(f"📞 Fetching call logs from {self.from_date} to {self.to_date}...")
        url = f"{self.BASE_URL}/phone/call_logs"
        params = {"from": self.from_date, "to": self.to_date, "page_size": 100}

        all_logs: List[Dict[str, Any]] = []
        next_page = None
        page = 0

        while True:
            if next_page:
                params["next_page_token"] = next_page
            self._logger.info(f"📄 Fetching page {page + 1} of call logs...")
            data = await self._authed_api_get(url, params=params)
            items = data.get("call_logs", [])
            all_logs.extend(items)
            self._logger.info(f"📊 Retrieved {len(items)} call logs from page {page + 1}")

            next_page = data.get("next_page_token")
            page += 1
            if self.max_pages and page >= self.max_pages:
                self._logger.warning(f"Reached max_pages={self.max_pages}, stopping pagination early.")
                break
            if not next_page:
                break

        total_logs = len(all_logs)
        self._logger.info(f"✅ Total call logs retrieved: {total_logs}")

        # Create DataFrame and clean column names
        df = pd.json_normalize(all_logs) if all_logs else pd.DataFrame()
        df = self._clean_column_names(df)

        # Filter by extensions if provided
        if self._extensions_filter and not df.empty:
            self._logger.info(f"🔍 Filtering call logs by {len(self._extensions_filter)} extensions...")

            # Try different possible extension field names from Zoom API
            extension_fields = [
                'owner_extension_number'
            ]
            filter_applied = False

            for field in extension_fields:
                if field in df.columns:
                    before_count = len(df)
                    df = df[df[field].astype(str).isin(self._extensions_filter)]
                    after_count = len(df)
                    self._logger.info(
                        f"✅ Filtered by '{field}': {before_count} → {after_count} calls "
                        f"({after_count} matching extensions)"
                    )
                    filter_applied = True
                    break

            if not filter_applied:
                self._logger.warning(
                    f"⚠️ Could not filter by extensions. Extension fields not found in DataFrame. "
                    f"Available columns: {list(df.columns)}"
                )

        return df

    async def recordings_meta(self, call_id: str) -> Dict[str, Any]:
        """
        GET /phone/call_logs/{id}/recordings
        Returns list of recordings with their ids and download_url.
        """
        url = f"{self.BASE_URL}/phone/call_logs/{call_id}/recordings"
        return await self._authed_api_get(url)

    async def _download_file(self, url: str, filename: Path = None, return_bytes: bool = False) -> Optional[tuple]:
        """
        Downloads a binary resource using HTTPService._get.

        Args:
            url: URL to download from
            filename: Path for disk storage (ignored if return_bytes=True)
            return_bytes: If True, returns (BytesIO, content_type, filename_str) instead of saving to disk

        Returns:
            If return_bytes=True: (BytesIO object, content_type, filename_str) or None on error
            If return_bytes=False: Path object or None on error
        """
        try:
            # Perform the GET with redirects enabled (important for zoom.us -> file.zoom.us endpoints)
            resp = await self._get(
                url=url,
                cookies=None,
                params=None,
                headers=self.headers,
                use_proxy=False,
                free_proxy=False,
                connect_timeout=10.0,
                read_timeout=120.0,
                write_timeout=10.0,
                pool_timeout=30.0,
                num_retries=2
            )
            # Raise if a 4xx/5xx status is returned
            resp.raise_for_status()

            # 1) Determine the final filename
            content_disposition = resp.headers.get("content-disposition") or resp.headers.get("Content-Disposition")
            content_type = resp.headers.get("Content-Type", self.content_type)
            server_name: Optional[str] = None

            if content_disposition:
                # Examples: attachment; filename="foo.mp3"
                from email.message import Message
                msg = Message()
                msg["Content-Disposition"] = content_disposition
                server_name = msg.get_param("filename", header="Content-Disposition")
                utf8_filename = msg.get_param("filename*", header="Content-Disposition")
                if utf8_filename:
                    # RFC 5987: filename*=UTF-8''<url-encoded>
                    _, enc_name = utf8_filename.split("''", 1)
                    server_name = urllib.parse.unquote(enc_name)

            # If the name comes from the URL (e.g., ?filename=call_recording_...mp3) and there was no header, use it
            if not server_name:
                try:
                    from urllib.parse import urlparse, parse_qs
                    q = parse_qs(urlparse(str(resp.request.url)).query)
                    if "filename" in q and q["filename"]:
                        server_name = q["filename"][0]
                except Exception:
                    pass

            # Get content
            content = resp.content  # already bytes in httpx

            # Return bytes if requested
            if return_bytes:
                file_data = BytesIO()
                file_data.write(content)
                file_data.seek(0)
                final_filename = server_name or (str(filename.name) if filename else "recording")
                return (file_data, content_type, final_filename)

            # Otherwise save to disk
            if "{filename}" in str(filename) and server_name:
                final_path = Path(str(filename).format(filename=server_name))
            else:
                final_path = Path(filename) if filename else Path(server_name or "recording")

            # Create destination folder
            final_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to disk
            with open(final_path, "wb") as fp:
                fp.write(content)

            return final_path

        except Exception as e:
            self._logger.error(f"Download failed from {url}: {e}")
            return None

    async def _download_recording(self, download_url: str, call_id: str, recording_id: str):
        """
        Downloads a recording.

        Returns:
            If as_bytes=True: (BytesIO, content_type, filename) or None
            If as_bytes=False: Path or None
        """
        if self.as_bytes:
            # Return bytes instead of saving to disk
            result = await self._download_file(download_url, return_bytes=True)
            return result
        else:
            # Attempt 1: let the server define the name
            p = await self._download_file(download_url, self.save_path / "{filename}", return_bytes=False)
            if p:
                return p
            # Fallback in case Content-Disposition doesn't come
            fallback_path = self.save_path / f"{call_id}_{recording_id}.mp4"
            p = await self._download_file(download_url, fallback_path, return_bytes=False)
            return p

    async def _download_transcript(self, recording_id: str, call_id: str):
        """
        Downloads transcript by recordingId:
          GET /phone/recording_transcript/download/{recordingId}

        Returns:
            If as_bytes=True: (BytesIO, content_type, filename) or None
            If as_bytes=False: Path or None
        """
        url = f"{self.BASE_URL}/phone/recording_transcript/download/{recording_id}"

        if self.as_bytes:
            # Return bytes instead of saving to disk
            result = await self._download_file(url, return_bytes=True)
            return result
        else:
            # Attempt 1: trust Content-Disposition
            p = await self._download_file(url, self.transcripts_path / "{filename}", return_bytes=False)
            if p:
                return p
            # Fallback (we don't know exact extension: could be .txt/.vtt/.srt)
            fallback_path = self.transcripts_path / f"{call_id}_{recording_id}.txt"
            p = await self._download_file(url, fallback_path, return_bytes=False)
            return p

    # =========================
    # Flow entrypoint
    # =========================
    async def run(self):
        import time
        t0 = time.time()

        self._logger.info("🚀 Starting Zoom Interface processing...")
        self._logger.info(f"📅 Date range: {self.from_date} to {self.to_date}")
        self._logger.info(f"📁 Recordings path: {self.save_path}")
        self._logger.info(f"📄 Transcripts path: {self.transcripts_path}")
        self._logger.info(f"⬇️ Download recordings: {self.download_recordings}")
        self._logger.info(f"📝 Download transcripts: {self.download_transcripts}")

        # Process input DataFrame BEFORE calling Zoom API (to extract extensions for filtering)
        if self.previous and hasattr(self, 'input') and self.input is not None:
            if hasattr(self.input, 'empty') and not self.input.empty:
                self._logger.info(f"📊 Received input DataFrame with {len(self.input)} rows")
                self._process_input_dataframe()

        # Ensure paths exist
        self._ensure_paths()

        # Call logs
        self._logger.info("📞 Fetching call logs...")
        df = await self.call_logs()
        
        # Log available columns for debugging
        if not df.empty:
            self._logger.info(f"📋 Available columns: {list(df.columns)}")

        # If no rows, basic metrics and exit
        if df.empty:
            self._logger.warning("⚠️ No call logs found in the specified date range")
            self.add_metric("NUMROWS", 0)
            self.add_metric("NUMCOLS", 0)
            self.add_metric("RECORDED_COUNT", 0)
            self.add_metric("DOWNLOADED_COUNT", 0)
            self.add_metric("TRANSCRIPTS_DOWNLOADED", 0)
            self.add_metric("SAVE_PATH", str(self.save_path))
            self.add_metric("TRANSCRIPTS_PATH", str(self.transcripts_path))
            self.add_metric("DURATION_SEC", round(time.time() - t0, 3))
            self._result = df
            return self._result

        self._logger.info(f"📊 Total call logs retrieved: {len(df)}")

        # Output columns based on storage mode
        if self.as_bytes:
            # For memory storage: file_data, content_type, downloaded_filename
            for col in ("file_data", "content_type", "downloaded_filename", "transcript_data", "transcript_filename"):
                if col not in df.columns:
                    df[col] = None
        else:
            # For disk storage: local_path (full path), recording_filename (filename only), transcript_paths, transcript_filename
            for col in ("local_path", "recording_filename", "transcript_paths", "transcript_filename"):
                if col not in df.columns:
                    df[col] = None  # None instead of an empty string

        # Filter recorded using Zoom Phone fields
        self._logger.info("🔍 Filtering recorded calls...")
        if "recording_status" in df.columns:
            # In case that field appears for a tenant
            recorded_mask = df["recording_status"].astype(str).str.lower().eq("recorded")
            recorded_df = df[recorded_mask]
            self._logger.info(f"📹 Found {len(recorded_df)} calls with recording_status='recorded'")
        else:
            # Robust fallback using has_recording / recording_id / recording_type
            has_rec = pd.Series(False, index=df.index)
            if "has_recording" in df.columns:
                has_rec = df["has_recording"].astype(str).str.lower().isin(["true", "1", "yes"])
                self._logger.info(f"📹 Found {has_rec.sum()} calls with has_recording=True")
            by_rec_id = df["recording_id"].notna() if "recording_id" in df.columns else False
            if "recording_id" in df.columns:
                self._logger.info(f"🆔 Found {by_rec_id.sum()} calls with recording_id")
            by_rec_type = df["recording_type"].notna() if "recording_type" in df.columns else False
            if "recording_type" in df.columns:
                self._logger.info(f"📋 Found {by_rec_type.sum()} calls with recording_type")
            recorded_df = df[has_rec | by_rec_id | by_rec_type]

        recorded_count = int(recorded_df.shape[0])
        if recorded_count == 0:
            self._logger.warning(
                "⚠️ No recorded calls found using has_recording/recording_id/recording_type. "
                "If you expected recordings, verify Zoom Phone recording settings/scopes."
            )
        else:
            self._logger.info(f"🎯 Processing {recorded_count} recorded calls...")

        downloaded = 0
        transcripts_downloaded = 0

        # Prepare separate lists for recordings and transcripts
        recordings_to_download = []
        transcripts_to_download = []
        calls_with_recordings = set()  # Track unique calls with recordings
        calls_with_transcripts = set()  # Track unique calls with transcripts
        
        # Global deduplicators per run
        seen_recording_keys = set()     # (call_id, recording_id) or (call_id, url) if there is no id
        seen_transcript_keys = set()    # (call_id, recording_id)
        
        for _, row in recorded_df.iterrows():
            call_short = str(row.get("call_id", "") or "").strip()
            call_uuid = str(row.get("id", "") or "").strip()
            call_ref = call_short or call_uuid
            if not call_ref:
                continue

            try:
                meta = await self.recordings_meta(call_ref)
                
                # === RECORDINGS (prefer download_url and fall back to file_url) ===
                if self.download_recordings:
                    rec_entries: List[tuple[str, str]] = []  # (url, recording_id)

                    recs = meta.get("recordings")
                    if isinstance(recs, list) and recs:
                        for rec in recs:
                            url = rec.get("download_url") or rec.get("file_url")
                            if not url:
                                continue
                            rec_id = str(rec.get("id") or rec.get("recording_id") or "").strip()
                            # If there is no id, still add it; use the URL for deduplication
                            rec_entries.append((url, rec_id))
                    else:
                        # Flat object without a list
                        url = meta.get("download_url") or meta.get("file_url")
                        if url:
                            rec_id = str(meta.get("id") or meta.get("recording_id") or "").strip()
                            rec_entries.append((url, rec_id))

                    # Deduplicate by (call_id, recording_id) or (call_id, url) if there is no id
                    for url, rec_id in rec_entries:
                        key = (call_ref, rec_id or url)
                        if key in seen_recording_keys:
                            continue
                        seen_recording_keys.add(key)

                        recordings_to_download.append({
                            'url': url,
                            'call_id': call_ref,
                            # Use the real recording_id if it exists; otherwise use a readable fallback
                            'recording_id': rec_id or "rec"
                        })

                # === TRANSCRIPTS (by real recording_id) ===
                if self.download_transcripts:
                    transcript_ids: List[str] = []

                    recs = meta.get("recordings")
                    if isinstance(recs, list) and recs:
                        for rec in recs:
                            rid = str(rec.get("id") or rec.get("recording_id") or "").strip()
                            if rid:
                                transcript_ids.append(rid)
                    else:
                        rid = str(meta.get("id") or meta.get("recording_id") or "").strip()
                        if rid:
                            transcript_ids.append(rid)

                    # Deduplicate by (call_id, recording_id)
                    for rid in transcript_ids:
                        key = (call_ref, rid)
                        if key in seen_transcript_keys:
                            continue
                        seen_transcript_keys.add(key)

                        transcripts_to_download.append({
                            'recording_id': rid,
                            'call_id': call_ref
                        })
                        
            except Exception as e:
                self._logger.warning(f"Failed to get metadata for call {call_ref}: {e}")

        # STEP 1: Download recordings
        if recordings_to_download:
            total_recordings = len(recordings_to_download)
            self._logger.info(f"🎥 Starting download of {total_recordings} recording files...")

            if self.as_bytes:
                # Store in memory as BytesIO
                with tqdm(total=total_recordings, desc="🎥 Downloading recordings", unit="files", colour="blue") as pbar:
                    for recording_info in recordings_to_download:
                        try:
                            result = await self._download_recording(
                                recording_info['url'],
                                recording_info['call_id'],
                                recording_info['recording_id']
                            )
                            if result:
                                file_data, content_type, filename = result
                                calls_with_recordings.add(recording_info['call_id'])

                                # Update DataFrame with BytesIO data
                                # Use .at for single cell assignment (BytesIO objects don't support len())
                                call_id = recording_info['call_id']
                                mask = (df['call_id'] == call_id) | (df['id'] == call_id)
                                indices = df.index[mask].tolist()
                                for idx in indices:
                                    df.at[idx, 'file_data'] = file_data
                                    df.at[idx, 'content_type'] = content_type
                                    df.at[idx, 'downloaded_filename'] = filename

                        except Exception as e:
                            self._logger.error(f"❌ Recording download error: {str(e)}")

                        pbar.update(1)
            else:
                # Save to disk (original behavior)
                local_path_by_call = {}
                filenames_by_call = {}

                with tqdm(total=total_recordings, desc="🎥 Downloading recordings", unit="files", colour="blue") as pbar:
                    for recording_info in recordings_to_download:
                        try:
                            saved = await self._download_recording(
                                recording_info['url'],
                                recording_info['call_id'],
                                recording_info['recording_id']
                            )
                            if saved:
                                calls_with_recordings.add(recording_info['call_id'])
                                # Store the local path for this call_id
                                call_id = recording_info['call_id']
                                if call_id not in local_path_by_call:
                                    local_path_by_call[call_id] = []
                                    filenames_by_call[call_id] = []

                                local_path_by_call[call_id].append(str(saved))
                                # Extract just the filename from the full path
                                filenames_by_call[call_id].append(Path(saved).name)

                        except Exception as e:
                            self._logger.error(f"❌ Recording download error: {str(e)}")

                        pbar.update(1)

                # Update the DataFrame with the local paths and filenames
                for call_id, paths in local_path_by_call.items():
                    # Find the corresponding row in the DataFrame
                    mask = (df['call_id'] == call_id) | (df['id'] == call_id)
                    if mask.any() and paths:  # Only update if there are actual paths
                        # Join the paths with a semicolon
                        df.loc[mask, 'local_path'] = '; '.join(paths)
                        # Also store just the filenames
                        df.loc[mask, 'recording_filename'] = '; '.join(filenames_by_call[call_id])
        else:
            self._logger.info("🎥 No recordings to download")

        # STEP 2: Download transcripts (only if enabled)
        if transcripts_to_download:
            total_transcripts = len(transcripts_to_download)
            self._logger.info(f"📝 Starting download of {total_transcripts} transcript files...")

            if self.as_bytes:
                # Store in memory as BytesIO
                with tqdm(total=total_transcripts, desc="📝 Downloading transcripts", unit="files", colour="green") as pbar:
                    for transcript_info in transcripts_to_download:
                        try:
                            result = await self._download_transcript(
                                transcript_info['recording_id'],
                                transcript_info['call_id']
                            )
                            if result:
                                file_data, content_type, filename = result
                                calls_with_transcripts.add(transcript_info['call_id'])
                                transcripts_downloaded += 1

                                # Update DataFrame with BytesIO data
                                # Use .at for single cell assignment (BytesIO objects don't support len())
                                call_id = transcript_info['call_id']
                                mask = (df['call_id'] == call_id) | (df['id'] == call_id)
                                indices = df.index[mask].tolist()
                                for idx in indices:
                                    df.at[idx, 'transcript_data'] = file_data
                                    df.at[idx, 'transcript_filename'] = filename

                        except Exception as e:
                            self._logger.error(f"❌ Transcript download error: {str(e)}")

                        pbar.update(1)
            else:
                # Save to disk (original behavior)
                transcript_paths_by_call = {}
                transcript_filenames_by_call = {}

                with tqdm(total=total_transcripts, desc="📝 Downloading transcripts", unit="files", colour="green") as pbar:
                    for transcript_info in transcripts_to_download:
                        try:
                            saved = await self._download_transcript(
                                transcript_info['recording_id'],
                                transcript_info['call_id']
                            )
                            if saved:
                                calls_with_transcripts.add(transcript_info['call_id'])
                                transcripts_downloaded += 1
                                # Store the local path for this call_id
                                call_id = transcript_info['call_id']
                                if call_id not in transcript_paths_by_call:
                                    transcript_paths_by_call[call_id] = []
                                    transcript_filenames_by_call[call_id] = []

                                transcript_paths_by_call[call_id].append(str(saved))
                                # Extract just the filename from the full path
                                transcript_filenames_by_call[call_id].append(Path(saved).name)

                        except Exception as e:
                            self._logger.error(f"❌ Transcript download error: {str(e)}")

                        pbar.update(1)

                # Update the DataFrame with the transcript paths and filenames
                for call_id, paths in transcript_paths_by_call.items():
                    # Find the corresponding row in the DataFrame
                    mask = (df['call_id'] == call_id) | (df['id'] == call_id)
                    if mask.any() and paths:  # Only update if there are actual paths
                        # Join the paths with a semicolon
                        df.loc[mask, 'transcript_paths'] = '; '.join(paths)
                        # Also store just the filenames
                        df.loc[mask, 'transcript_filename'] = '; '.join(transcript_filenames_by_call[call_id])
        else:
            self._logger.info("📝 No transcripts to download")

        # Calculate unique calls with successful downloads
        downloaded = len(calls_with_recordings)

        # Final summary
        self._logger.info("�� Processing Summary:")
        self._logger.info(f"   �� Total call logs: {len(df)}")
        self._logger.info(f"   📹 Recorded calls: {recorded_count}")
        self._logger.info(f"   🎥 Calls with recordings downloaded: {downloaded}")
        self._logger.info(f"   📝 Transcripts downloaded: {transcripts_downloaded}")

        if self.as_bytes:
            self._logger.info("   💾 Storage mode: In-memory (BytesIO objects)")
            self._logger.info("   📊 DataFrame columns: file_data, content_type, downloaded_filename")
        else:
            self._logger.info("   💾 Storage mode: Disk")
            self._logger.info(f"   📁 Recordings path: {self.save_path}")
            self._logger.info(f"   📄 Transcripts path: {self.transcripts_path}")
            self._logger.info("   📊 DataFrame columns: local_path (full path), recording_filename (filename only)")

        # Metrics
        self.add_metric("NUMROWS", int(df.shape[0]))
        self.add_metric("NUMCOLS", int(df.shape[1]))
        self.add_metric("RECORDED_COUNT", recorded_count)
        self.add_metric("DOWNLOADED_COUNT", downloaded)
        self.add_metric("TRANSCRIPTS_DOWNLOADED", transcripts_downloaded)
        self.add_metric("SAVE_PATH", str(self.save_path))
        self.add_metric("TRANSCRIPTS_PATH", str(self.transcripts_path))
        self.add_metric("DURATION_SEC", round(time.time() - t0, 3))

        # Preview in debug mode
        if self._debug:
            print("\n=== DataFrame Preview ===")
            try:
                print(df.head(10))
            except Exception:
                print(df.head())
            print("\n=== Column dtypes ===")
            for column, dtype in df.dtypes.items():
                sample = None
                if not df.empty:
                    try:
                        sample = df[column].iloc[0]
                    except Exception:
                        sample = "N/A"
                print(f"{column} -> {dtype} -> {sample}")

        duration = round(time.time() - t0, 3)
        self._logger.info(f"🎉 Zoom Interface processing completed in {duration} seconds")
        self._result = df
        return self._result

    async def close(self):
        """
        Cleanup.
        """
        self._access_token = None
        return True
