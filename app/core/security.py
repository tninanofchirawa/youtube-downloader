"""Zero-Tolerance Security and Input Sanitization Module.

Protects against:
- SSRF (Server-Side Request Forgery) and local network / loopback probing
- Path traversal (e.g., ../../../) and arbitrary file overwrite
- Windows reserved device name exploitation (CON, PRN, AUX, NUL, COM*, LPT*)
- Command injection / argument injection
"""

import ipaddress
import os
import re
import urllib.parse
from pathlib import Path


class SecurityValidationError(ValueError):
    """Raised when an input fails security validation."""
    pass


# Strict whitelist of allowed YouTube domain names
ALLOWED_DOMAINS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "gaming.youtube.com",
    "youtu.be",
    "www.youtu.be",
}

# Regex for illegal filename characters on Windows and POSIX
ILLEGAL_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

# Windows reserved device names
WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
}

# YouTube video/playlist ID patterns
YT_VIDEO_ID_REGEX = re.compile(r'^[a-zA-Z0-9_-]{11}$')
YT_PLAYLIST_ID_REGEX = re.compile(r'^[a-zA-Z0-9_-]{10,50}$')


def validate_media_url(url: str) -> str:
    """
    Validates that a URL is a legitimate YouTube media URL.
    Blocks SSRF, loopbacks, internal IPs, and arbitrary protocols.
    
    Returns:
        The sanitized canonical URL string.
    
    Raises:
        SecurityValidationError: If the URL fails security checks.
    """
    if not url or not isinstance(url, str):
        raise SecurityValidationError("URL cannot be empty.")

    url = url.strip()
    if len(url) > 2048:
        raise SecurityValidationError("URL exceeds maximum permissible length.")

    parsed = urllib.parse.urlparse(url)

    # 1. Scheme Check: Only allow HTTPS (and HTTP if strictly necessary, normalized to HTTPS)
    if parsed.scheme.lower() not in ("https", "http"):
        raise SecurityValidationError(f"Forbidden URL scheme: '{parsed.scheme}'. Only HTTPS is permitted.")

    # 2. Block credentials in URL (e.g., https://user:pass@host)
    if parsed.username or parsed.password:
        raise SecurityValidationError("User credentials in URL are strictly prohibited.")

    hostname = (parsed.hostname or "").lower()
    if not hostname:
        raise SecurityValidationError("URL has no valid host.")

    # 3. Block IP addresses (Prevent SSRF / loopback / private subnet probing)
    try:
        ip = ipaddress.ip_address(hostname)
        # If it parsed as an IP address, block it immediately
        raise SecurityValidationError(f"Direct IP access is prohibited for security ({hostname}).")
    except ValueError:
        # Not a raw IP, continue to hostname checks
        pass

    # 4. Check for localhost / loopback string names
    if hostname in ("localhost", "ip6-localhost", "ip6-loopback", "local"):
        raise SecurityValidationError("Access to localhost is prohibited.")

    # 5. Whitelist Domain Validation
    if hostname not in ALLOWED_DOMAINS:
        # Check for subdomain of allowed domains
        is_subdomain = any(hostname.endswith("." + domain) for domain in ALLOWED_DOMAINS if not domain.startswith("www."))
        if not is_subdomain:
            raise SecurityValidationError(
                f"Domain '{hostname}' is not an authorized YouTube domain."
            )

    # 6. Normalize to secure HTTPS
    sanitized_url = urllib.parse.urlunparse((
        "https",
        parsed.netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        ""  # Strip fragment for safety
    ))

    return sanitized_url


def sanitize_filename(name: str, default: str = "media_download", max_length: int = 150) -> str:
    """
    Sanitizes user-provided or remote media titles for safe filesystem storage.
    
    Protects against:
    - Path traversal ('..', '/', '\\')
    - Null bytes and ASCII control characters
    - Windows forbidden characters (< > : " / \\ | ? *)
    - Windows reserved device names (CON, NUL, AUX, PRN, COM1-9, LPT1-9)
    - Trailing dots and spaces
    - Overly long filenames
    """
    if not name or not isinstance(name, str):
        return default

    # Remove null bytes and path traversal indicators
    cleaned = name.replace("\0", "").replace("..", "")
    
    # Replace path separators with underscores
    cleaned = cleaned.replace("/", "_").replace("\\", "_")

    # Remove illegal characters
    cleaned = ILLEGAL_FILENAME_CHARS.sub("_", cleaned)

    # Collapse multiple consecutive underscores or spaces
    cleaned = re.sub(r'[\s_]+', ' ', cleaned).strip()

    # Remove trailing periods and spaces (Windows issue)
    cleaned = cleaned.rstrip(". ")

    if not cleaned:
        cleaned = default

    # Check for Windows reserved names (e.g., 'CON', 'con.mp4', 'con.tar.gz', 'aux.txt')
    primary_stem = cleaned.split(".")[0].strip().upper()
    if primary_stem in WINDOWS_RESERVED_NAMES:
        cleaned = f"safe_{cleaned}"

    # Truncate to maximum length while preserving extension if present
    if len(cleaned) > max_length:
        path_obj = Path(cleaned)
        ext = path_obj.suffix
        stem = path_obj.stem
        max_stem_len = max(1, max_length - len(ext))
        cleaned = stem[:max_stem_len].rstrip(". ") + ext

    return cleaned or default


def validate_save_directory(dir_path: str) -> str:
    """
    Validates and canonicalizes a directory path.
    Ensures directory exists, is writable, and blocks system-critical root writes.
    
    Returns:
        The canonical absolute path.
    
    Raises:
        SecurityValidationError: If the path is invalid or restricted.
    """
    if not dir_path or not isinstance(dir_path, str):
        raise SecurityValidationError("Save directory must be specified.")

    # Canonicalize path
    try:
        resolved_path = Path(dir_path).resolve()
    except Exception as e:
        raise SecurityValidationError(f"Invalid directory path format: {e}")

    # Check if path points to system-critical directories
    resolved_str = str(resolved_path)
    system_root = os.environ.get("SystemRoot", r"C:\Windows")
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")

    restricted_roots = [
        Path(system_root).resolve(),
        Path(program_files).resolve(),
        Path(program_files_x86).resolve(),
    ]

    for restricted in restricted_roots:
        try:
            if resolved_path == restricted or restricted in resolved_path.parents:
                raise SecurityValidationError(
                    f"Saving files into system directory '{resolved_str}' is restricted."
                )
        except (TypeError, ValueError) as ve:
            if isinstance(ve, SecurityValidationError):
                raise


    # Ensure directory exists or can be created
    if not resolved_path.exists():
        try:
            resolved_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise SecurityValidationError(f"Cannot create save directory: {e}")

    if not resolved_path.is_dir():
        raise SecurityValidationError(f"Target path is not a directory: {resolved_str}")

    # Check write permissions
    if not os.access(resolved_str, os.W_OK):
        raise SecurityValidationError(f"Directory is not writable: {resolved_str}")

    return str(resolved_path)
