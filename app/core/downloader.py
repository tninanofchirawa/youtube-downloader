"""Safe Download Engine managing secure yt-dlp executions."""

import os
import threading
from typing import Callable, Optional
import yt_dlp

from .ffmpeg_handler import get_ffmpeg_path
from .extractor import MediaFormat
from .security import sanitize_filename, validate_media_url, validate_save_directory


class DownloadCancelledError(Exception):
    """Raised when the user cancels an ongoing download."""
    pass


class SafeDownloader:
    """Executes sandboxed media downloads with live progress reporting."""

    def __init__(
        self,
        progress_callback: Optional[Callable[[dict], None]] = None,
        status_callback: Optional[Callable[[str], None]] = None,
    ):
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self._cancel_requested = threading.Event()

    def cancel(self):
        """Requests cancellation of any running download."""
        self._cancel_requested.set()

    def _progress_hook(self, d: dict):
        """Internal progress hook translating yt-dlp status events."""
        if self._cancel_requested.is_set():
            raise DownloadCancelledError("Download was cancelled by user.")

        status = d.get("status", "")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            percent = (downloaded / total * 100.0) if total > 0 else 0.0
            
            speed = d.get("speed")
            eta = d.get("eta")
            speed_str = d.get("_speed_str", "").strip() or "-- MB/s"
            eta_str = d.get("_eta_str", "").strip() or "--:--"

            if self.progress_callback:
                self.progress_callback({
                    "status": "downloading",
                    "percent": percent,
                    "downloaded_bytes": downloaded,
                    "total_bytes": total,
                    "speed_str": speed_str,
                    "eta_str": eta_str,
                    "filename": d.get("filename", ""),
                })
        elif status == "finished":
            if self.status_callback:
                self.status_callback("Processing and finalising output...")
            if self.progress_callback:
                self.progress_callback({
                    "status": "processing",
                    "percent": 100.0,
                    "speed_str": "Finalizing",
                    "eta_str": "00:00",
                })

    def download(
        self,
        raw_url: str,
        media_format: MediaFormat,
        save_dir: str,
        custom_name: Optional[str] = None,
    ) -> str:
        """
        Executes a secure media download.
        
        Returns:
            The output destination directory.
        """
        self._cancel_requested.clear()

        # 1. Security validation
        clean_url = validate_media_url(raw_url)
        safe_save_dir = validate_save_directory(save_dir)

        # 2. Filename formatting
        if custom_name and custom_name.strip():
            safe_title = sanitize_filename(custom_name.strip())
            outtmpl = os.path.join(safe_save_dir, f"{safe_title}.%(ext)s")
        else:
            outtmpl = os.path.join(safe_save_dir, "%(title).120B.%(ext)s")

        # 3. Base yt-dlp options
        ydl_opts = {
            "format": media_format.format_selector,
            "outtmpl": outtmpl,
            "progress_hooks": [self._progress_hook],
            "quiet": True,
            "no_warnings": True,
            "no_color": True,
            "no_config": True,
            "restrictfilenames": True,
            "windowsfilenames": True,
            "allowed_extractors": ["youtube", "youtube:*"],
            "socket_timeout": 30,
            "retries": 5,
        }

        # 4. Attach FFmpeg path if available
        ffmpeg_dir = get_ffmpeg_path()
        if ffmpeg_dir:
            ydl_opts["ffmpeg_location"] = ffmpeg_dir

        # 5. Audio vs Video post-processing configuration
        if media_format.is_audio_only:
            target_codec = media_format.target_codec or "mp3"
            if target_codec == "mp3":
                bitrate = str(media_format.audio_bitrate_kbps or 192)
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": bitrate,
                }]
            elif target_codec == "wav":
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                }]
            elif target_codec == "m4a":
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                }]
        else:
            # Video: Merge into standard MP4 container
            ydl_opts["merge_output_format"] = "mp4"

        # 6. Execute download
        if self.status_callback:
            self.status_callback("Initiating secure download...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([clean_url])

        if self.status_callback:
            self.status_callback("Download completed successfully!")

        return safe_save_dir
