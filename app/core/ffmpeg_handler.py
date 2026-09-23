"""FFmpeg auto-detection and validation utility."""

import os
import shutil
import sys
from pathlib import Path


def get_ffmpeg_path() -> str | None:
    """
    Locates the FFmpeg binary on the system or in the application directory.
    
    Returns:
        The directory containing ffmpeg or the path to ffmpeg executable, or None if not found.
    """
    # 1. Check local project root / application folder
    app_root = Path(__file__).resolve().parent.parent.parent
    local_ffmpeg_exe = app_root / "ffmpeg.exe"
    local_ffmpeg = app_root / "ffmpeg"
    
    if local_ffmpeg_exe.is_file() and os.access(str(local_ffmpeg_exe), os.X_OK | os.R_OK):
        return str(app_root)
    if local_ffmpeg.is_file() and os.access(str(local_ffmpeg), os.X_OK | os.R_OK):
        return str(app_root)

    # 2. Check system PATH
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return str(Path(system_ffmpeg).parent)

    # 3. Check common Windows / Unix paths
    common_paths = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Links",
        Path("C:/ffmpeg/bin"),
        Path("C:/Program Files/ffmpeg/bin"),
        Path("/usr/bin"),
        Path("/usr/local/bin"),
        Path("/opt/homebrew/bin"),
    ]

    for p in common_paths:
        if (p / "ffmpeg.exe").is_file() or (p / "ffmpeg").is_file():
            return str(p)

    return None


def is_ffmpeg_available() -> bool:
    """Checks whether FFmpeg is installed and accessible."""
    return get_ffmpeg_path() is not None
