"""Helper functions for formatting and string manipulations."""

def format_bytes(size: float | int | None) -> str:
    """Converts raw byte counts into human-readable format (B, KB, MB, GB, TB)."""
    import math
    if size is None or size <= 0 or math.isinf(size) or math.isnan(size):
        return "Unknown size"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    current_size = float(size)
    for unit in units:
        if current_size < 1024.0 or unit == units[-1]:
            return f"{current_size:.1f} {unit}"
        current_size /= 1024.0
    return f"{current_size:.1f} TB"


def format_duration(seconds: int | float | None) -> str:
    """Converts duration in seconds to HH:MM:SS or MM:SS."""
    if not seconds or seconds <= 0:
        return "--:--"
    
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncates text safely with ellipsis."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
