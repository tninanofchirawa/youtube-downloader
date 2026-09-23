"""Group 3: 10 Minute Bugs, Edge Cases, and Combinatorial Issue Tests."""

import os
import unittest

from app.core.downloader import DownloadCancelledError, SafeDownloader
from app.core.extractor import MediaExtractor, MediaFormat
from app.core.ffmpeg_handler import get_ffmpeg_path, is_ffmpeg_available
from app.core.security import SecurityValidationError, sanitize_filename, validate_media_url
from app.utils.helpers import format_bytes, format_duration, truncate_text


class TestMinuteBugsAndEdgeCases(unittest.TestCase):
    """10 Specific Edge Cases and Minute Issue Tests."""

    def test_edge_01_duration_formatting_extremes(self):
        """Edge Test 1: Zero, negative, None, 59s, 1 hour, and multi-day duration formatting."""
        cases = [
            (None, "--:--"),
            (0, "--:--"),
            (-100, "--:--"),
            (5, "00:05"),
            (59, "00:59"),
            (60, "01:00"),
            (3599, "59:59"),
            (3600, "01:00:00"),
            (86400, "24:00:00"),      # 24 hours
            (100000, "27:46:40"),     # > 1 day
        ]
        for sec, expected in cases:
            self.assertEqual(format_duration(sec), expected, f"Failed for duration: {sec}")

    def test_edge_02_byte_formatting_boundaries(self):
        """Edge Test 2: Byte boundaries (0 B, 1 B, 1023 B, 1024 B, 1.0 MB - 1 B, 1.0 GB)."""
        cases = [
            (None, "Unknown size"),
            (0, "Unknown size"),
            (-500, "Unknown size"),
            (1, "1.0 B"),
            (1023, "1023.0 B"),
            (1024, "1.0 KB"),
            (1024 * 1024, "1.0 MB"),
            (1024 * 1024 * 1024, "1.0 GB"),
        ]
        for raw, expected in cases:
            self.assertEqual(format_bytes(raw), expected, f"Failed for bytes: {raw}")

    def test_edge_03_filename_pure_illegal_characters(self):
        """Edge Test 3: Filename composed entirely of illegal characters falls back to safe default."""
        bad_names = [
            '<<<>>>:::***???///\\\\',
            '       ',
            '.....',
            '\0\0\0',
            '???:***',
        ]
        for name in bad_names:
            clean = sanitize_filename(name, default="safe_fallback")
            self.assertEqual(clean, "safe_fallback")

    def test_edge_04_filename_trailing_dots_and_spaces(self):
        """Edge Test 4: Stripping trailing dots and spaces that cause Windows Explorer errors."""
        name = "My Favorite Song . . . . "
        clean = sanitize_filename(name)
        self.assertFalse(clean.endswith("."))
        self.assertFalse(clean.endswith(" "))
        self.assertEqual(clean, "My Favorite Song")

    def test_edge_05_corrupted_format_stream_handling(self):
        """Edge Test 5: Parsing stream lists containing None values, missing keys, and corrupted dicts."""
        corrupted_streams = [
            {},
            {"format_id": None},
            {"format_id": "1", "vcodec": "none"},  # Audio only
            {"format_id": "2", "vcodec": "avc1", "height": None},  # Missing height
            {"format_id": "3", "vcodec": "avc1", "height": 720, "fps": None, "tbr": None},
        ]
        parsed = MediaExtractor._parse_video_formats(corrupted_streams, 60)
        self.assertTrue(len(parsed) >= 1)
        self.assertIn("720p", parsed[0].label)

    def test_edge_06_audio_presets_quality_mapping(self):
        """Edge Test 6: Verifying accurate bitrate mapping and codec assignment for audio presets."""
        presets = MediaExtractor._build_audio_presets([], 120)
        preset_map = {p.format_id: p for p in presets}

        self.assertIn("audio_mp3_320", preset_map)
        self.assertEqual(preset_map["audio_mp3_320"].audio_bitrate_kbps, 320)
        self.assertEqual(preset_map["audio_mp3_320"].target_codec, "mp3")

        self.assertIn("audio_m4a_fast", preset_map)
        self.assertEqual(preset_map["audio_m4a_fast"].target_codec, "m4a")

    def test_edge_07_empty_and_whitespace_url_inputs(self):
        """Edge Test 7: Handling empty, space-only, tab, and newline URL strings."""
        empty_cases = ["", "   ", "\t", "\n\r\n", None]
        for item in empty_cases:
            with self.assertRaises(SecurityValidationError):
                validate_media_url(item)

    def test_edge_08_ffmpeg_auto_detection_resilience(self):
        """Edge Test 8: FFmpeg detector returns string or None without throwing unhandled exceptions."""
        path = get_ffmpeg_path()
        self.assertTrue(path is None or isinstance(path, str))
        avail = is_ffmpeg_available()
        self.assertTrue(isinstance(avail, bool))

    def test_edge_09_download_cancellation_exception(self):
        """Edge Test 9: SafeDownloader raises DownloadCancelledError when cancelled during download."""
        downloader = SafeDownloader()
        downloader.cancel()

        with self.assertRaises(DownloadCancelledError):
            downloader._progress_hook({"status": "downloading"})

    def test_edge_10_truncate_text_edge_cases(self):
        """Edge Test 10: Truncate text with exact lengths, zero length, None, and Unicode boundaries."""
        self.assertEqual(truncate_text("", 10), "")
        self.assertEqual(truncate_text(None, 10), "")
        self.assertEqual(truncate_text("ExactLen10", 10), "ExactLen10")
        self.assertEqual(truncate_text("ExactLen11_", 10), "ExactLe...")


if __name__ == "__main__":
    unittest.main()
