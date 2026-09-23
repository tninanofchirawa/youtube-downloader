"""Unit tests for formatting helpers and extractor logic."""

import unittest

from app.core.extractor import MediaExtractor, MediaFormat
from app.utils.helpers import format_bytes, format_duration, truncate_text


class TestHelpersAndExtractor(unittest.TestCase):
    """Tests utility helpers and media format models."""

    def test_format_bytes(self):
        self.assertEqual(format_bytes(None), "Unknown size")
        self.assertEqual(format_bytes(0), "Unknown size")
        self.assertEqual(format_bytes(500), "500.0 B")
        self.assertEqual(format_bytes(1024), "1.0 KB")
        self.assertEqual(format_bytes(1024 * 1024 * 15), "15.0 MB")
        self.assertEqual(format_bytes(1024 * 1024 * 1024 * 2.5), "2.5 GB")

    def test_format_duration(self):
        self.assertEqual(format_duration(None), "--:--")
        self.assertEqual(format_duration(0), "--:--")
        self.assertEqual(format_duration(45), "00:45")
        self.assertEqual(format_duration(125), "02:05")
        self.assertEqual(format_duration(3665), "01:01:05")

    def test_truncate_text(self):
        self.assertEqual(truncate_text("Hello World", 20), "Hello World")
        self.assertEqual(truncate_text("This is a very long string that should be truncated", 15), "This is a ve...")

    def test_audio_presets_generation(self):
        presets = MediaExtractor._build_audio_presets([], 0)
        self.assertTrue(len(presets) >= 2)
        labels = [p.label for p in presets]
        self.assertTrue(any("320 kbps" in l for l in labels))
        self.assertTrue(any("M4A" in l for l in labels))

    def test_video_formats_parsing(self):
        sample_formats = [
            {"format_id": "137", "vcodec": "avc1.640028", "height": 1080, "fps": 30, "ext": "mp4", "filesize": 50000000},
            {"format_id": "248", "vcodec": "vp9", "height": 1080, "fps": 30, "ext": "webm", "filesize": 40000000},
            {"format_id": "136", "vcodec": "avc1.4d401f", "height": 720, "fps": 60, "ext": "mp4", "filesize": 25000000},
        ]
        parsed = MediaExtractor._parse_video_formats(sample_formats, 100)
        self.assertTrue(len(parsed) >= 2)
        self.assertIn("1080p", parsed[0].label)


if __name__ == "__main__":
    unittest.main()
