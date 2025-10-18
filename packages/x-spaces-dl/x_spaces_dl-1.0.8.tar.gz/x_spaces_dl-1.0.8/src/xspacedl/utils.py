"""
Utility functions for x-spaces-dl
"""

import logging
import re
import subprocess
from datetime import datetime
from typing import Any, Dict


def check_ffmpeg() -> bool:
    """Check if ffmpeg is available"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', "", filename)

    # Replace multiple spaces with single space and remove leading/trailing spaces
    filename = re.sub(r"\s+", " ", filename).strip()

    # Remove leading/trailing dots
    filename = filename.strip(".")

    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:200] + (f".{ext}" if ext else "")

    return filename or "space"


def format_filename(template: str, metadata: Dict[str, Any]) -> str:
    """
    Format filename using template and metadata

    Args:
        template: Filename template
        metadata: Metadata dictionary

    Returns:
        Formatted filename
    """
    # Extract date and time from started_date or created_date
    date_str = "unknown_date"
    time_str = "unknown_time"

    date_field = metadata.get("started_date") or metadata.get("created_date")
    if date_field:
        try:
            dt = datetime.fromisoformat(date_field.replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H-%M-%S")
        except Exception:
            pass

    # Build replacement dict
    replacements = {
        "space_id": metadata.get("space_id", "unknown"),
        "title": metadata.get("title", "untitled"),
        "host": metadata.get("host", "unknown"),
        "date": date_str,
        "time": time_str,
    }

    # Replace template variables
    filename = template
    for key, value in replacements.items():
        filename = filename.replace(f"{{{key}}}", str(value))

    return sanitize_filename(filename)


def setup_logger(verbose: bool = False, quiet: bool = False) -> logging.Logger:
    """
    Setup logger with appropriate level

    Args:
        verbose: Enable verbose logging
        quiet: Enable quiet mode (errors only)

    Returns:
        Configured logger
    """
    logger = logging.getLogger("xspacesdl")

    # Remove existing handlers
    logger.handlers = []

    # Set level
    if quiet:
        logger.setLevel(logging.ERROR)
    elif verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Create handler
    handler = logging.StreamHandler()
    handler.setLevel(logger.level)

    # Create formatter
    if verbose:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    else:
        formatter = logging.Formatter("%(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def format_size(bytes: int) -> str:
    """Format bytes to human readable size"""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} TB"


def format_duration(seconds: int) -> str:
    """Format seconds to human readable duration"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"
