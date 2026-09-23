"""Core logic module for security, extraction, and downloading."""

from .security import validate_media_url, sanitize_filename, validate_save_directory
from .ffmpeg_handler import get_ffmpeg_path, is_ffmpeg_available
from .extractor import MediaExtractor, VideoMetadata, MediaFormat
from .downloader import SafeDownloader

__all__ = [
    "validate_media_url",
    "sanitize_filename",
    "validate_save_directory",
    "get_ffmpeg_path",
    "is_ffmpeg_available",
    "MediaExtractor",
    "VideoMetadata",
    "MediaFormat",
    "SafeDownloader",
]
