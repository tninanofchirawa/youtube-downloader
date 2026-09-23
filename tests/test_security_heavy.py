"""Group 2: 10 Heavy Security Bug and Attack Vector Tests."""

import os
import unittest

from app.core.downloader import SafeDownloader
from app.core.extractor import MediaExtractor
from app.core.security import (
    SecurityValidationError,
    sanitize_filename,
    validate_media_url,
    validate_save_directory,
)


class TestHeavySecurityBugs(unittest.TestCase):
    """10 Heavy Security Tests covering SSRF, injections, traversals, and sandbox integrity."""

    def test_security_01_ssrf_ipv6_and_hex_decimal_ip_bypasses(self):
        """Security Test 1: Blocks advanced SSRF vectors including IPv6, hex, decimal, and loopback aliases."""
        malicious_ssrf = [
            "http://127.0.0.1:8080/exploit",
            "https://127.0.0.1/",
            "http://0.0.0.0:80/",
            "http://[::1]/secret",
            "http://[::ffff:127.0.0.1]/",
            "http://2130706433/",  # Decimal representation of 127.0.0.1
            "http://localhost:5000/api",
            "http://ip6-localhost/test",
            "http://169.254.169.254/latest/meta-data/",  # Cloud metadata endpoint
            "http://10.255.255.1/",
            "http://172.16.0.1/",
            "http://192.168.0.1/",
        ]
        for url in malicious_ssrf:
            with self.assertRaises(SecurityValidationError, msg=f"Should block SSRF vector: {url}"):
                validate_media_url(url)

    def test_security_02_dns_rebinding_and_dotless_domains(self):
        """Security Test 2: Blocks DNS rebinding, spoofed domains, and user-at-host confusion."""
        spoofed = [
            "https://youtube.com@evil-attacker.com/payload",
            "https://evil-attacker.com#youtube.com",
            "https://youtube.com.attacker.com/watch?v=123",
            "https://www.youtube.com.phishing.org/",
            "https://notyoutube.com/watch?v=123",
            "https://myoutube.com/",
            "https://youtube.co/",
        ]
        for url in spoofed:
            with self.assertRaises(SecurityValidationError, msg=f"Should block domain spoof: {url}"):
                validate_media_url(url)

    def test_security_03_deep_directory_traversal_escapes(self):
        """Security Test 3: Neutralizes deep, nested, and alternate directory traversal patterns."""
        traversals = [
            ("../../../../../../../../Windows/System32/drivers/etc/hosts", "Windows_System32_drivers_etc_hosts"),
            ("....//....//....//etc/passwd", "etc_passwd"),
            ("..\\..\\..\\..\\boot.ini", "boot.ini"),
            ("/var/log/../../etc/shadow", "_var_log_etc_shadow"),
            (".%2e/.%2e/secret.txt", ".%2e_.%2e_secret.txt"),
        ]
        for raw, _ in traversals:
            clean = sanitize_filename(raw)
            self.assertNotIn("..", clean)
            self.assertNotIn("/", clean)
            self.assertNotIn("\\", clean)

    def test_security_04_windows_reserved_device_names_with_extensions(self):
        """Security Test 4: Prevents Windows system crash/lockup by safely prefixing reserved device names."""
        reserved = [
            "CON", "CON.mp4", "con.tar.gz",
            "PRN", "prn.txt",
            "AUX", "aux.mp3",
            "NUL", "nul.iso",
            "COM1", "COM1.exe", "com9.flac",
            "LPT1", "lpt5.wav",
        ]
        for name in reserved:
            clean = sanitize_filename(name)
            self.assertTrue(clean.startswith("safe_"), f"Must prefix reserved device name: {name} -> {clean}")

    def test_security_05_null_byte_and_crlf_injections(self):
        """Security Test 5: Strips null bytes, CRLF newlines, and ASCII control characters."""
        injections = [
            "malicious\0title.mp4",
            "video\r\nHeader-Injection: true",
            "test\x00\x01\x02\x1f\x7fcontrol.mp4",
        ]
        for raw in injections:
            clean = sanitize_filename(raw)
            self.assertNotIn("\0", clean)
            self.assertNotIn("\r", clean)
            self.assertNotIn("\n", clean)

    def test_security_06_dangerous_uri_schemes_and_xss(self):
        """Security Test 6: Rejects dangerous protocol schemes (file, ftp, javascript, data, blob)."""
        schemes = [
            "file:///C:/Windows/System32/cmd.exe",
            "ftp://ftp.example.com/malware",
            "javascript:alert(document.domain)",
            "data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==",
            "blob:https://www.youtube.com/uuid-here",
            "vbscript:msgbox(1)",
            "ws://127.0.0.1:8080",
        ]
        for url in schemes:
            with self.assertRaises(SecurityValidationError, msg=f"Should reject scheme: {url}"):
                validate_media_url(url)

    def test_security_07_credential_embedding_and_auth_bypass(self):
        """Security Test 7: Rejects URLs with embedded user:password credentials."""
        credential_urls = [
            "https://admin:password123@www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://user:@www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://:pass@youtu.be/dQw4w9WgXcQ",
        ]
        for url in credential_urls:
            with self.assertRaises(SecurityValidationError):
                validate_media_url(url)

    def test_security_08_restricted_system_directories_defense(self):
        """Security Test 8: Blocks saving files into critical system roots (Windows, Program Files)."""
        system_dir = os.environ.get("SystemRoot", r"C:\Windows")
        prog_dir = os.environ.get("ProgramFiles", r"C:\Program Files")

        with self.assertRaises(SecurityValidationError):
            validate_save_directory(system_dir)
        with self.assertRaises(SecurityValidationError):
            validate_save_directory(prog_dir)

    def test_security_09_buffer_overflow_and_max_length_attacks(self):
        """Security Test 9: Defends against buffer overflow via extreme URL and filename lengths."""
        # 1. Extreme URL length (>2048 chars)
        huge_url = "https://www.youtube.com/watch?v=" + ("A" * 3000)
        with self.assertRaises(SecurityValidationError):
            validate_media_url(huge_url)

        # 2. Extreme filename length (>10,000 chars)
        huge_name = ("SafeVideo_" * 1000) + ".mp4"
        clean = sanitize_filename(huge_name, max_length=150)
        self.assertLessEqual(len(clean), 150)
        self.assertTrue(clean.endswith(".mp4"))

    def test_security_10_ytdlp_sandbox_and_extractor_locking(self):
        """Security Test 10: Ensures yt-dlp runs strictly locked down without external configs."""
        opts = MediaExtractor.get_ydl_base_opts()
        self.assertTrue(opts.get("quiet"))
        self.assertTrue(opts.get("no_config"))
        self.assertTrue(opts.get("skip_download"))
        self.assertEqual(opts.get("allowed_extractors"), ["youtube", "youtube:*"])


if __name__ == "__main__":
    unittest.main()
