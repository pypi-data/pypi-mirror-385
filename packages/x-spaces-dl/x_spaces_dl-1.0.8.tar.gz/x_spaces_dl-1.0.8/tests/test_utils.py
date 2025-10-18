"""
Tests for utility functions
"""

import pytest

from xspacesdl.utils import format_duration, format_filename, format_size, sanitize_filename


def test_sanitize_filename():
    """Test filename sanitization"""
    assert sanitize_filename("normal_file.mp3") == "normal_file.mp3"
    assert sanitize_filename("file:with:colons.mp3") == "filewithcolons.mp3"
    assert sanitize_filename('file"with"quotes.mp3') == "filewithquotes.mp3"
    assert sanitize_filename("file/with/slashes.mp3") == "filewithslashes.mp3"
    # Corrected expectation: internal spaces before extension are preserved after collapsing
    assert sanitize_filename("  spaces  .mp3") == "spaces .mp3"
    assert sanitize_filename("") == "space"

    # Test length limit
    long_name = "a" * 250 + ".mp3"
    result = sanitize_filename(long_name)
    assert len(result) <= 205  # 200 + extension


def test_format_filename():
    """Test filename formatting with template"""
    metadata = {
        "space_id": "123456",
        "title": "Test Space",
        "host": "testuser",
        "started_date": "2025-10-18T01:13:11+00:00",
    }

    template = "{space_id}"
    assert format_filename(template, metadata) == "123456"

    template = "{host}_{title}"
    assert format_filename(template, metadata) == "testuser_Test Space"

    template = "{date}_{host}"
    result = format_filename(template, metadata)
    assert result.startswith("2025-10-18_testuser")


def test_format_size():
    """Test size formatting"""
    assert format_size(500) == "500.00 B"
    assert format_size(1024) == "1.00 KB"
    assert format_size(1048576) == "1.00 MB"
    assert format_size(1073741824) == "1.00 GB"


def test_format_duration():
    """Test duration formatting"""
    assert format_duration(30) == "30s"
    assert format_duration(90) == "1m 30s"
    assert format_duration(3665) == "1h 1m 5s"
