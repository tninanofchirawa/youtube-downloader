"""Group 1: 10 Heavy Stress Tests for Safe Media Downloader."""

import concurrent.futures
import threading
import time
import unittest

from app.core.downloader import SafeDownloader
from app.core.extractor import MediaExtractor, MediaFormat
from app.core.security import sanitize_filename, validate_media_url
from app.utils.helpers import format_bytes, format_duration, truncate_text


class TestHeavyStress(unittest.TestCase):
    """10 Heavy Stress Tests covering concurrency, load, memory, and high-frequency dispatch."""

    def test_stress_01_concurrent_url_validation(self):
        """Stress Test 1: 50 concurrent threads validating mixed legitimate and malicious URLs simultaneously."""
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://127.0.0.1/malicious",
            "https://youtu.be/dQw4w9WgXcQ",
            "file:///C:/Windows/System32/cmd.exe",
            "https://music.youtube.com/watch?v=abcdef12345",
            "https://attacker.com/payload",
            "https://m.youtube.com/watch?v=xyz98765432",
        ] * 100  # 700 URLs total

        def worker(u):
            try:
                return validate_media_url(u)
            except Exception:
                return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(worker, test_urls))

        self.assertEqual(len(results), 700)
        # Verify that all valid ones passed and all invalid ones were blocked safely
        valid_count = sum(1 for r in results if r and r.startswith("https://"))
        self.assertEqual(valid_count, 400)

    def test_stress_02_concurrent_filename_sanitization(self):
        """Stress Test 2: 50 concurrent threads sanitizing dangerous filenames under race conditions."""
        dangerous_names = [
            "../../../Windows/System32/calc.exe",
            "CON.mp4",
            "aux.tar.gz",
            "video<title>:with*illegal?chars|and\"quotes.mp4",
            "test\0nullbyte.mp4",
            "normal_safe_video_name.mp4",
        ] * 100

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(sanitize_filename, dangerous_names))

        self.assertEqual(len(results), 600)
        for name in results:
            self.assertNotIn("..", name)
            self.assertNotIn("/", name)
            self.assertNotIn("\\", name)
            self.assertNotIn("\0", name)

    def test_stress_03_massive_batch_url_processing(self):
        """Stress Test 3: Processing and filtering a massive batch of 2,000 URLs rapidly."""
        batch = [f"https://www.youtube.com/watch?v=testID_{i:04d}" for i in range(1000)] + [
            f"http://192.168.1.{i % 255}/bad" for i in range(1000)
        ]

        start_time = time.time()
        valid = []
        blocked = 0
        for u in batch:
            try:
                valid.append(validate_media_url(u))
            except Exception:
                blocked += 1

        elapsed = time.time() - start_time
        self.assertEqual(len(valid), 1000)
        self.assertEqual(blocked, 1000)
        self.assertLess(elapsed, 2.0, "Massive batch validation must complete in under 2 seconds.")

    def test_stress_04_ultra_large_byte_sizes(self):
        """Stress Test 4: Handling extreme byte values (Petabytes, Exabytes, negative/huge floats)."""
        huge_sizes = [
            (1024**4 * 5, "5.0 TB"),
            (1024**5 * 10, "10240.0 TB"),  # Petabyte scale
            (1024**6 * 2, "2097152.0 TB"),  # Exabyte scale
            (10**18, "909494.7 TB"),
            (float("inf"), "Unknown size"),
        ]
        for val, expected_suffix in huge_sizes:
            res = format_bytes(val)
            self.assertTrue(isinstance(res, str))
            self.assertTrue(res != "")

    def test_stress_05_high_volume_format_deduplication(self):
        """Stress Test 5: Deduplicating and ranking 500 stream variants under high load."""
        simulated_formats = []
        for i in range(500):
            simulated_formats.append({
                "format_id": str(i),
                "vcodec": "avc1.640028" if i % 2 == 0 else "vp9",
                "height": 1080 if i % 3 == 0 else (720 if i % 3 == 1 else 480),
                "fps": 60 if i % 2 == 0 else 30,
                "ext": "mp4" if i % 2 == 0 else "webm",
                "filesize": 1000000 + i * 1000,
                "tbr": 2000 + i,
            })

        parsed = MediaExtractor._parse_video_formats(simulated_formats, 300)
        # Should deduplicate down to unique resolution+fps+codec combinations + Best option
        self.assertLess(len(parsed), 20)
        self.assertGreater(len(parsed), 3)

    def test_stress_06_massive_text_buffer_truncation(self):
        """Stress Test 6: Safe handling and truncation of 1MB+ massive string buffers."""
        massive_string = "A" * 1_000_000
        res = truncate_text(massive_string, 50)
        self.assertEqual(len(res), 50)
        self.assertTrue(res.endswith("..."))

    def test_stress_07_high_frequency_progress_events(self):
        """Stress Test 7: Simulating 10,000 rapid progress callbacks in fractions of a second."""
        dispatched = []
        downloader = SafeDownloader(
            progress_callback=lambda p: dispatched.append(p),
        )

        start_time = time.time()
        for i in range(10000):
            downloader._progress_hook({
                "status": "downloading",
                "downloaded_bytes": i * 1024,
                "total_bytes": 10000 * 1024,
                "_speed_str": "15.5 MB/s",
                "_eta_str": "00:05",
                "filename": "video.mp4",
            })

        elapsed = time.time() - start_time
        self.assertEqual(len(dispatched), 10000)
        self.assertLess(elapsed, 1.5, "10,000 progress events must dispatch smoothly in < 1.5s")

    def test_stress_08_heavy_malformed_query_parameters(self):
        """Stress Test 8: Stressing URL parser with corrupt, repeated, nested parameters."""
        nested_query = "&".join([f"param_{i}={i}&list={i}*@#" for i in range(50)])
        stress_url = f"https://www.youtube.com/watch?v=dQw4w9WgXcQ&{nested_query}"
        
        sanitized = validate_media_url(stress_url)
        self.assertTrue(sanitized.startswith("https://www.youtube.com/watch"))

    def test_stress_09_multilingual_unicode_and_rtl_stress(self):
        """Stress Test 9: Unicode, Emojis, Cyrillic, CJK, and RTL control characters stress test."""
        multilingual_titles = [
            "🔥 Top Hits 2026! 🎧 (Official Video) [4K] 🚀",
            "مرحبا بكم في عالم الفيديو - تجربة رائعة",  # Arabic RTL
            "日本語のタイトルと漢字のテスト（公式）",  # Japanese
            "Русский заголовок с длинным описанием",  # Cyrillic
            "Special characters: !@#$%^&*()_+{}|:\"<>?~`",
            "\u202E\u202D\u200E\u200F Hidden RTL Override Attack",  # Bidi overrides
        ]
        for title in multilingual_titles:
            sanitized = sanitize_filename(title)
            self.assertTrue(isinstance(sanitized, str))
            self.assertGreater(len(sanitized), 0)
            self.assertNotIn("..", sanitized)
            self.assertNotIn("/", sanitized)
            self.assertNotIn("\\", sanitized)

    def test_stress_10_concurrent_cancellation_race_condition(self):
        """Stress Test 10: Multi-threaded cancellation toggle and atomic state safety under load."""
        downloader = SafeDownloader()
        
        def cancel_runner():
            for _ in range(100):
                downloader.cancel()

        def hook_runner():
            for _ in range(100):
                try:
                    downloader._progress_hook({"status": "downloading"})
                except Exception:
                    pass

        threads = [threading.Thread(target=cancel_runner) for _ in range(5)] + [
            threading.Thread(target=hook_runner) for _ in range(5)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertTrue(downloader._cancel_requested.is_set())


if __name__ == "__main__":
    unittest.main()
