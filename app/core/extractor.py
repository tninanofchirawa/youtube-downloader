"""Simplified, High-Definition Media Metadata and Format Extraction Engine."""

from dataclasses import dataclass, field
from typing import List, Optional
import yt_dlp

from ..utils.helpers import format_bytes, format_duration
from .security import validate_media_url


@dataclass
class MediaFormat:
    """Represents a clean selectable video or audio format."""
    format_id: str
    label: str
    extension: str
    resolution: str
    filesize_display: str = "Estimated"
    is_audio_only: bool = False
    format_selector: str = "best"
    audio_bitrate_kbps: Optional[int] = None
    target_codec: Optional[str] = None


@dataclass
class VideoMetadata:
    """Clean metadata extracted from a YouTube video."""
    url: str
    title: str
    uploader: str
    duration_seconds: int
    duration_display: str
    view_count: int
    thumbnail_url: str
    video_formats: List[MediaFormat] = field(default_factory=list)
    audio_formats: List[MediaFormat] = field(default_factory=list)


class MediaExtractor:
    """Extracts streamlined, simplified video and audio options."""

    @staticmethod
    def get_ydl_base_opts() -> dict:
        return {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "no_color": True,
            "no_config": True,
            "allowed_extractors": ["youtube", "youtube:*"],
            "socket_timeout": 15,
        }

    @classmethod
    def fetch_metadata(cls, raw_url: str) -> VideoMetadata:
        clean_url = validate_media_url(raw_url)
        opts = cls.get_ydl_base_opts()

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            if not info:
                raise ValueError("Could not retrieve media information.")

        duration = info.get("duration") or 0
        formats = info.get("formats", [])

        # Streamlined Video Formats (1080p, 720p, 480p, 360p, 240p MP4)
        video_formats = cls._parse_video_formats(formats, duration)

        # Streamlined Audio Formats (MP3 320k, M4A)
        audio_formats = cls._build_audio_presets(formats, duration)

        return VideoMetadata(
            url=clean_url,
            title=info.get("title", "Untitled Video"),
            uploader=info.get("uploader", "Unknown Creator"),
            duration_seconds=duration,
            duration_display=format_duration(duration),
            view_count=info.get("view_count", 0),
            thumbnail_url=info.get("thumbnail", ""),
            video_formats=video_formats,
            audio_formats=audio_formats,
        )

    @classmethod
    def _parse_video_formats(cls, formats: list, duration: int) -> List[MediaFormat]:
        """Builds clean, standard MP4 resolution choices (1080p, 720p, 480p, 360p, 240p)."""
        available_heights = set()
        height_sizes = {}

        for f in formats:
            h = f.get("height")
            if h and f.get("vcodec") and f.get("vcodec") != "none":
                available_heights.add(h)
                size = f.get("filesize") or f.get("filesize_approx")
                if size and (h not in height_sizes or size > height_sizes[h]):
                    height_sizes[h] = size
                elif duration > 0 and f.get("tbr") and h not in height_sizes:
                    height_sizes[h] = int(((f.get("tbr") + 128) * 1024 / 8) * duration)

        standard_tiers = [
            (1080, "1080p Full HD (MP4)", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"),
            (720, "720p HD (MP4)", "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]/best"),
            (480, "480p SD (MP4)", "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best[height<=480]/best"),
            (360, "360p Standard (MP4)", "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=360]+bestaudio/best[height<=360]/best"),
            (240, "240p Low (MP4)", "bestvideo[height<=240][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=240]+bestaudio/best[height<=240]/best"),
        ]

        parsed: List[MediaFormat] = []

        for h, label, selector in standard_tiers:
            # Check if this resolution or higher is available
            is_avail = any(avail_h >= h for avail_h in available_heights) if available_heights else True
            if is_avail:
                size_str = format_bytes(height_sizes.get(h)) if h in height_sizes else "Estimated"
                parsed.append(MediaFormat(
                    format_id=f"video_{h}p",
                    label=f"🎬 {label} — ~{size_str}",
                    extension="mp4",
                    resolution=f"{h}p",
                    filesize_display=size_str,
                    is_audio_only=False,
                    format_selector=selector,
                ))

        # Fallback Best if none matched
        if not parsed:
            parsed.append(MediaFormat(
                format_id="video_best",
                label="🎬 Best Available Quality (MP4)",
                extension="mp4",
                resolution="Auto Best",
                filesize_display="Best",
                is_audio_only=False,
                format_selector="bestvideo+bestaudio/best",
            ))

        return parsed

    @classmethod
    def _build_audio_presets(cls, formats: list, duration: int) -> List[MediaFormat]:
        """Builds clean, high-definition audio options."""
        return [
            MediaFormat(
                format_id="audio_mp3_320",
                label="🎵 MP3 Audio — Ultra Quality (320 kbps)",
                extension="mp3",
                resolution="Audio",
                filesize_display="High Quality",
                is_audio_only=True,
                format_selector="bestaudio/best",
                audio_bitrate_kbps=320,
                target_codec="mp3",
            ),
            MediaFormat(
                format_id="audio_m4a_fast",
                label="🎧 M4A / AAC — Original Stream (Fastest)",
                extension="m4a",
                resolution="Audio",
                filesize_display="Direct Stream",
                is_audio_only=True,
                format_selector="bestaudio[ext=m4a]/bestaudio/best",
                target_codec="m4a",
            ),
        ]
