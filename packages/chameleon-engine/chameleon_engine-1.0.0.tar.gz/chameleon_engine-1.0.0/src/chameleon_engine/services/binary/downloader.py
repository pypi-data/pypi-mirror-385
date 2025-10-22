"""
Binary download utilities.

This module provides functionality for downloading browser binaries from
various sources with progress tracking, resume support, and retry logic.
"""

import asyncio
import aiofiles
import aiohttp
import os
import tempfile
import zipfile
import tarfile
import gzip
from pathlib import Path
from typing import Dict, Any, Optional, Callable, AsyncGenerator, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import hashlib
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class DownloadStatus(Enum):
    """Download status values."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DownloadProgress:
    """Download progress information."""
    status: DownloadStatus
    url: str
    file_path: Path
    total_size: int = 0
    downloaded_size: int = 0
    speed: float = 0.0  # bytes per second
    eta: Optional[float] = None  # estimated time remaining in seconds
    start_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    error: Optional[str] = None
    retry_count: int = 0

    @property
    def progress_percentage(self) -> float:
        """Get progress as percentage."""
        if self.total_size == 0:
            return 0.0
        return (self.downloaded_size / self.total_size) * 100

    @property
    def downloaded_mb(self) -> float:
        """Get downloaded size in MB."""
        return self.downloaded_size / (1024 * 1024)

    @property
    def total_mb(self) -> float:
        """Get total size in MB."""
        return self.total_size / (1024 * 1024)

    @property
    def speed_mb_per_sec(self) -> float:
        """Get speed in MB per second."""
        return self.speed / (1024 * 1024)


@dataclass
class DownloadTask:
    """Download task configuration."""
    url: str
    file_path: Path
    expected_size: Optional[int] = None
    expected_checksum: Optional[str] = None
    checksum_type: str = "sha256"
    headers: Optional[Dict[str, str]] = None
    timeout: int = 300
    chunk_size: int = 8192
    max_retries: int = 3
    retry_delay: float = 1.0
    resume: bool = True

    def __post_init__(self):
        """Initialize task."""
        if self.headers is None:
            self.headers = {}

        # Ensure parent directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)


class BinaryDownloader:
    """Downloader for browser binaries."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the binary downloader.

        Args:
            config: Download configuration
        """
        self.config = config or {}
        self.max_concurrent_downloads = self.config.get('max_concurrent_downloads', 3)
        self.default_timeout = self.config.get('download_timeout', 300)
        self.default_chunk_size = self.config.get('chunk_size', 8192)
        self.default_retry_attempts = self.config.get('retry_attempts', 3)
        self.default_retry_delay = self.config.get('retry_delay', 1.0)
        self.temp_dir = Path(self.config.get('temp_directory', './temp'))
        self.cache_dir = Path(self.config.get('cache_directory', './cache'))

        # Ensure directories exist
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Active downloads
        self._active_downloads: Dict[str, DownloadProgress] = {}
        self._download_semaphore = asyncio.Semaphore(self.max_concurrent_downloads)

    async def download(self, task: DownloadTask) -> DownloadProgress:
        """
        Download a binary file.

        Args:
            task: Download task configuration

        Returns:
            DownloadProgress with final status
        """
        download_id = f"{task.url}_{datetime.now().timestamp()}"

        # Initialize progress
        progress = DownloadProgress(
            status=DownloadStatus.PENDING,
            url=task.url,
            file_path=task.file_path,
            start_time=datetime.now()
        )

        self._active_downloads[download_id] = progress

        try:
            async with self._download_semaphore:
                await self._download_file(task, progress)

        except Exception as e:
            logger.error(f"Download failed for {task.url}: {str(e)}")
            progress.status = DownloadStatus.FAILED
            progress.error = str(e)

        finally:
            # Clean up
            if download_id in self._active_downloads:
                del self._active_downloads[download_id]

        return progress

    async def _download_file(self, task: DownloadTask, progress: DownloadProgress):
        """
        Download file with retry logic and resume support.

        Args:
            task: Download task
            progress: Progress tracking object
        """
        retry_count = 0
        last_error = None

        while retry_count <= task.max_retries:
            try:
                # Check if we can resume
                resume_pos = 0
                if task.resume and task.file_path.exists():
                    resume_pos = task.file_path.stat().st_size
                    progress.downloaded_size = resume_pos

                    # Add Range header for resume
                    headers = task.headers.copy()
                    headers['Range'] = f'bytes={resume_pos}-'
                else:
                    headers = task.headers

                progress.status = DownloadStatus.DOWNLOADING
                progress.update_time = datetime.now()

                # Perform download
                await self._perform_download(task, progress, headers, resume_pos)

                # Verify download if checksum provided
                if task.expected_checksum:
                    if not await self._verify_checksum(task.file_path, task.expected_checksum, task.checksum_type):
                        raise ValueError("Checksum verification failed")

                progress.status = DownloadStatus.COMPLETED
                logger.info(f"Successfully downloaded {task.url} to {task.file_path}")
                return

            except Exception as e:
                last_error = e
                retry_count += 1
                progress.retry_count = retry_count

                if retry_count <= task.max_retries:
                    logger.warning(f"Download attempt {retry_count} failed for {task.url}: {str(e)}")
                    await asyncio.sleep(task.retry_delay * retry_count)  # Exponential backoff
                else:
                    raise

        # All retries failed
        raise last_error

    async def _perform_download(
        self,
        task: DownloadTask,
        progress: DownloadProgress,
        headers: Dict[str, str],
        resume_pos: int
    ):
        """
        Perform the actual download.

        Args:
            task: Download task
            progress: Progress tracking
            headers: HTTP headers
            resume_pos: Position to resume from
        """
        timeout = aiohttp.ClientTimeout(total=task.timeout)
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)

        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            async with session.get(task.url, headers=headers) as response:
                # Check response status
                if response.status not in [200, 206]:  # 200 OK, 206 Partial Content
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=f"HTTP {response.status}: {response.reason}"
                    )

                # Get total size
                content_length = response.headers.get('content-length')
                if content_length:
                    progress.total_size = int(content_length) + resume_pos
                elif task.expected_size:
                    progress.total_size = task.expected_size + resume_pos

                # Open file for writing
                mode = 'ab' if resume_pos > 0 else 'wb'
                async with aiofiles.open(task.file_path, mode) as file:
                    start_time = datetime.now()
                    last_update_time = start_time
                    last_downloaded = resume_pos

                    # Download chunks
                    async for chunk in response.content.iter_chunked(task.chunk_size):
                        await file.write(chunk)
                        progress.downloaded_size += len(chunk)

                        # Update progress stats
                        current_time = datetime.now()
                        time_delta = (current_time - last_update_time).total_seconds()

                        if time_delta >= 1.0:  # Update every second
                            # Calculate speed
                            bytes_downloaded = progress.downloaded_size - last_downloaded
                            progress.speed = bytes_downloaded / time_delta

                            # Calculate ETA
                            if progress.speed > 0 and progress.total_size > 0:
                                remaining_bytes = progress.total_size - progress.downloaded_size
                                progress.eta = remaining_bytes / progress.speed

                            progress.update_time = current_time
                            last_update_time = current_time
                            last_downloaded = progress.downloaded_size

                            logger.debug(
                                f"Downloading {task.url}: {progress.progress_percentage:.1f}% "
                                f"({progress.downloaded_mb:.1f}/{progress.total_mb:.1f} MB, "
                                f"{progress.speed_mb_per_sec:.1f} MB/s)"
                            )

    async def _verify_checksum(self, file_path: Path, expected_checksum: str, checksum_type: str) -> bool:
        """
        Verify file checksum.

        Args:
            file_path: Path to file
            expected_checksum: Expected checksum
            checksum_type: Type of checksum

        Returns:
            True if checksum matches
        """
        try:
            if checksum_type.lower() == "sha256":
                hasher = hashlib.sha256()
            elif checksum_type.lower() == "sha1":
                hasher = hashlib.sha1()
            elif checksum_type.lower() == "md5":
                hasher = hashlib.md5()
            else:
                raise ValueError(f"Unsupported checksum type: {checksum_type}")

            async with aiofiles.open(file_path, 'rb') as file:
                while chunk := await file.read(8192):
                    hasher.update(chunk)

            actual_checksum = hasher.hexdigest()
            return actual_checksum.lower() == expected_checksum.lower()

        except Exception as e:
            logger.error(f"Checksum verification failed: {str(e)}")
            return False

    async def download_and_extract(
        self,
        task: DownloadTask,
        extract_to: Optional[Path] = None,
        delete_after_extract: bool = True
    ) -> DownloadProgress:
        """
        Download and extract archive file.

        Args:
            task: Download task
            extract_to: Directory to extract to (default: same directory as file)
            delete_after_extract: Whether to delete archive after extraction

        Returns:
            DownloadProgress with final status
        """
        # Download file
        progress = await self.download(task)

        if progress.status != DownloadStatus.COMPLETED:
            return progress

        # Determine extraction directory
        if extract_to is None:
            extract_to = task.file_path.parent

        try:
            # Extract archive
            await self._extract_archive(task.file_path, extract_to)

            # Delete archive if requested
            if delete_after_extract:
                task.file_path.unlink()

            logger.info(f"Successfully extracted {task.file_path} to {extract_to}")

        except Exception as e:
            logger.error(f"Extraction failed for {task.file_path}: {str(e)}")
            progress.status = DownloadStatus.FAILED
            progress.error = f"Extraction failed: {str(e)}"

        return progress

    async def _extract_archive(self, archive_path: Path, extract_to: Path):
        """
        Extract archive file.

        Args:
            archive_path: Path to archive
            extract_to: Directory to extract to
        """
        extract_to.mkdir(parents=True, exist_ok=True)

        # Determine archive type and extract
        suffix = archive_path.suffix.lower()

        if suffix == '.zip':
            await self._extract_zip(archive_path, extract_to)
        elif suffix in ['.tar', '.gz', '.bz2', '.xz']:
            await self._extract_tar(archive_path, extract_to)
        elif suffix == '.gz' and archive_path.name != '.gz':  # Single .gz file
            await self._extract_gzip(archive_path, extract_to)
        else:
            raise ValueError(f"Unsupported archive format: {suffix}")

    async def _extract_zip(self, zip_path: Path, extract_to: Path):
        """Extract ZIP archive."""
        def extract():
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                zip_file.extractall(extract_to)

        await asyncio.get_event_loop().run_in_executor(None, extract)

    async def _extract_tar(self, tar_path: Path, extract_to: Path):
        """Extract TAR archive."""
        def extract():
            with tarfile.open(tar_path, 'r:*') as tar_file:
                tar_file.extractall(extract_to)

        await asyncio.get_event_loop().run_in_executor(None, extract)

    async def _extract_gzip(self, gz_path: Path, extract_to: Path):
        """Extract single GZIP file."""
        output_path = extract_to / gz_path.stem

        async with aiofiles.open(gz_path, 'rb') as src_file:
            gzip_content = await src_file.read()

        # Decompress
        decompressed = gzip.decompress(gzip_content)

        async with aiofiles.open(output_path, 'wb') as dst_file:
            await dst_file.write(decompressed)

    async def get_download_info(self, url: str) -> Dict[str, Any]:
        """
        Get information about a downloadable file without downloading it.

        Args:
            url: URL to check

        Returns:
            Dictionary with file information
        """
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(limit=5)

        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            async with session.head(url) as response:
                headers = response.headers

                return {
                    'url': url,
                    'status_code': response.status,
                    'content_type': headers.get('content-type'),
                    'content_length': int(headers.get('content-length', 0)),
                    'last_modified': headers.get('last-modified'),
                    'etag': headers.get('etag'),
                    'accept_ranges': headers.get('accept-ranges') == 'bytes'
                }

    async def batch_download(
        self,
        tasks: List[DownloadTask],
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None
    ) -> List[DownloadProgress]:
        """
        Download multiple files concurrently.

        Args:
            tasks: List of download tasks
            progress_callback: Optional callback for progress updates

        Returns:
            List of download progress results
        """
        # Create download coroutines
        coroutines = []
        for task in tasks:
            coro = self.download(task)
            if progress_callback:
                coro = self._wrap_with_callback(coro, progress_callback)
            coroutines.append(coro)

        # Execute concurrently
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        # Process results
        progress_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Download {i} failed: {str(result)}")
                error_progress = DownloadProgress(
                    status=DownloadStatus.FAILED,
                    url=tasks[i].url,
                    file_path=tasks[i].file_path,
                    error=str(result)
                )
                progress_results.append(error_progress)
            else:
                progress_results.append(result)

        return progress_results

    async def _wrap_with_callback(
        self,
        coro,
        callback: Callable[[DownloadProgress], None]
    ):
        """Wrap download coroutine with progress callback."""
        progress = await coro
        callback(progress)
        return progress

    def get_active_downloads(self) -> List[DownloadProgress]:
        """Get list of active downloads."""
        return list(self._active_downloads.values())

    def get_download_progress(self, download_id: str) -> Optional[DownloadProgress]:
        """Get progress for specific download."""
        return self._active_downloads.get(download_id)

    async def cancel_download(self, download_id: str) -> bool:
        """
        Cancel an active download.

        Args:
            download_id: Download ID to cancel

        Returns:
            True if download was cancelled
        """
        if download_id in self._active_downloads:
            progress = self._active_downloads[download_id]
            progress.status = DownloadStatus.CANCELLED
            del self._active_downloads[download_id]
            return True
        return False

    async def cleanup_temp_files(self):
        """Clean up temporary files."""
        try:
            for temp_file in self.temp_dir.glob("*"):
                if temp_file.is_file():
                    # Check if file is older than 24 hours
                    age = datetime.now().timestamp() - temp_file.stat().st_mtime
                    if age > 86400:  # 24 hours
                        temp_file.unlink()
                        logger.debug(f"Cleaned up temp file: {temp_file}")

        except Exception as e:
            logger.error(f"Failed to cleanup temp files: {str(e)}")

    async def get_download_history(self) -> List[Dict[str, Any]]:
        """
        Get download history from cache.

        Returns:
            List of download history entries
        """
        history_file = self.cache_dir / "download_history.json"

        if not history_file.exists():
            return []

        try:
            async with aiofiles.open(history_file, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to load download history: {str(e)}")
            return []

    async def save_download_history(self, progress: DownloadProgress):
        """
        Save download progress to history.

        Args:
            progress: Download progress to save
        """
        history_file = self.cache_dir / "download_history.json"

        try:
            # Load existing history
            history = await self.get_download_history()

            # Add new entry
            history.append({
                'url': progress.url,
                'file_path': str(progress.file_path),
                'status': progress.status.value,
                'total_size': progress.total_size,
                'downloaded_size': progress.downloaded_size,
                'start_time': progress.start_time.isoformat() if progress.start_time else None,
                'update_time': progress.update_time.isoformat() if progress.update_time else None,
                'error': progress.error,
                'retry_count': progress.retry_count
            })

            # Keep only last 100 entries
            history = history[-100:]

            # Save history
            async with aiofiles.open(history_file, 'w') as f:
                await f.write(json.dumps(history, indent=2))

        except Exception as e:
            logger.error(f"Failed to save download history: {str(e)}")