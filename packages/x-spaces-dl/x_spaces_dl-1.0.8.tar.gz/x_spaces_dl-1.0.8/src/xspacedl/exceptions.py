"""
Custom exceptions for x-spaces-dl
"""


class XSpacesError(Exception):
    """Base exception for all x-spaces-dl errors"""

    pass


class AuthenticationError(XSpacesError):
    """Raised when authentication fails"""

    pass


class SpaceNotFoundError(XSpacesError):
    """Raised when a Space cannot be found or accessed"""

    pass


class DownloadError(XSpacesError):
    """Raised when download fails"""

    pass


class InvalidURLError(XSpacesError):
    """Raised when the provided URL is invalid"""

    pass


class MetadataError(XSpacesError):
    """Raised when metadata extraction fails"""

    pass


class ConversionError(XSpacesError):
    """Raised when format conversion fails"""

    pass
