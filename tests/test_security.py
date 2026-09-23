"""Unit tests for the Zero-Tolerance Security layer."""

import os
import tempfile
import unittest

from app.core.security import (
    SecurityValidationError,
    sanitize_filename,
    validate_media_url,
    validate_save_directory,
)


class TestSecurityValidation(unittest.TestCase):
    """Verifies that all attack vectors and malicious inputs are neutralized."""

    def test_valid_youtube_urls(self):
        """Standard valid YouTube links must pass and normalize to HTTPS."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://music.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/playlist?list=PL1234567890ABCDEF",
        ]
        for url in valid_urls:
            sanitized = validate_media_url(url)
            self.assertTrue(sanitized.startswith("https://"))

    def test_reject_ssrf_and_ip_addresses(self):
        """Direct IP addresses, localhost, and loopbacks must be blocked."""
        malicious_urls = [
            "http://127.0.0.1/video.mp4",
            "https://127.0.0.1:8000/test",
            "http://localhost/watch?v=test",
            "http://169.254.169.254/latest/meta-data/",
            "http://192.168.1.1/admin",
            "http://10.0.0.1/",
            "http://0.0.0.0/",
            "http://[::1]/",
        ]
        for url in malicious_urls:
            with self.assertRaises(SecurityValidationError, msg=f"Failed to block: {url}"):
                validate_media_url(url)

    def test_reject_forbidden_schemes(self):
        """Protocols other than HTTP/HTTPS must be rejected."""
        schemes = [
            "file:///C:/Windows/System32/cmd.exe",
            "file:///etc/passwd",
            "ftp://ftp.example.com/file",
            "javascript:alert(1)",
            "data:text/html;base64,PHNjcmlwdD4=",
            "gopher://gopher.floodgap.com/",
        ]
        for url in schemes:
            with self.assertRaises(SecurityValidationError):
                validate_media_url(url)

    def test_reject_unauthorized_domains(self):
        """Arbitrary external domains must be blocked."""
        unauthorized = [
            "https://attacker.com/malware.exe",
            "https://evil-youtube.com/watch?v=123",
            "https://youtube.com.attacker.com/watch?v=123",
            "https://phishing-site.org",
        ]
        for url in unauthorized:
            with self.assertRaises(SecurityValidationError):
                validate_media_url(url)

    def test_reject_credentials_in_url(self):
        """Embedded authentication credentials must be blocked."""
        with self.assertRaises(SecurityValidationError):
            validate_media_url("https://admin:password@www.youtube.com/watch?v=123")

    def test_sanitize_filename_traversal(self):
        """Directory traversal sequences and forbidden characters must be removed."""
        bad_names = [
            ("../../../Windows/System32/calc.exe", "Windows_System32_calc.exe"),
            ("..\\..\\malicious", "malicious"),
            ("video<title>:with*illegal?chars|and\"quotes", "video_title_with_illegal_chars_and_quotes"),
            ("test\0nullbyte.mp4", "testnullbyte.mp4"),
            ("trailing.dots....", "trailing.dots"),
        ]
        for raw, expected_sub in bad_names:
            sanitized = sanitize_filename(raw)
            self.assertNotIn("..", sanitized)
            self.assertNotIn("/", sanitized)
            self.assertNotIn("\\", sanitized)
            self.assertNotIn(":", sanitized)
            self.assertNotIn("*", sanitized)
            self.assertNotIn("?", sanitized)
            self.assertNotIn("<", sanitized)
            self.assertNotIn(">", sanitized)
            self.assertNotIn("|", sanitized)

    def test_sanitize_filename_windows_reserved(self):
        """Windows reserved device names must be safely prefixed."""
        reserved_names = ["CON", "con.mp4", "PRN", "AUX", "NUL", "COM1", "lpt2.m4a"]
        for name in reserved_names:
            sanitized = sanitize_filename(name)
            self.assertTrue(sanitized.startswith("safe_"), f"Failed for reserved name: {name}")

    def test_validate_save_directory(self):
        """Valid local directories must pass, while restricted system paths must fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            validated = validate_save_directory(tmpdir)
            self.assertTrue(os.path.isdir(validated))

        # Check blocking system directory
        system_dir = os.environ.get("SystemRoot", r"C:\Windows")
        with self.assertRaises(SecurityValidationError):
            validate_save_directory(system_dir)


if __name__ == "__main__":
    unittest.main()
