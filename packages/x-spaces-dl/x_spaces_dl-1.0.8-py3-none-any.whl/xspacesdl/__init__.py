"""
x-spaces-dl: A powerful tool for downloading Twitter/X Spaces recordings
"""

__version__ = "1.0.0"
__author__ = "w3Abhishek"
__license__ = "MIT"

from .core import XSpacesDL
from .exceptions import (
    XSpacesError,
    AuthenticationError,
    SpaceNotFoundError,
    DownloadError,
    InvalidURLError,
)
from .config import Config

__all__ = [
    "XSpacesDL",
    "Config",
    "XSpacesError",
    "AuthenticationError",
    "SpaceNotFoundError",
    "DownloadError",
    "InvalidURLError",
]
