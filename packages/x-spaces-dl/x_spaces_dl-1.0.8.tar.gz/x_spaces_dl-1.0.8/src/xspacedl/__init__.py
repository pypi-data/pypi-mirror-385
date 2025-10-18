"""
x-spaces-dl: A powerful tool for downloading Twitter/X Spaces recordings
"""

__version__ = "1.0.0"
__author__ = "w3Abhishek"
__license__ = "MIT"

from .config import Config
from .core import XSpacesDL
from .exceptions import (
    AuthenticationError,
    DownloadError,
    InvalidURLError,
    SpaceNotFoundError,
    XSpacesError,
)

__all__ = [
    "XSpacesDL",
    "Config",
    "XSpacesError",
    "AuthenticationError",
    "SpaceNotFoundError",
    "DownloadError",
    "InvalidURLError",
]
