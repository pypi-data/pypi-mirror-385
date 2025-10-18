"""
Unit tests for core functionality
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from xspacesdl.config import Config
from xspacesdl.core import XSpacesDL
from xspacesdl.exceptions import InvalidURLError, SpaceNotFoundError


class TestXSpacesDL:
    """Test XSpacesDL class"""

    def test_extract_space_id_valid(self):
        """Test extracting space ID from valid URL"""
        dl = XSpacesDL()

        urls = [
            ("https://x.com/i/spaces/1234567890", "1234567890"),
            ("https://twitter.com/i/spaces/abcDEF123", "abcDEF123"),
            ("https://x.com/i/spaces/1zqKVPlQOqxJB", "1zqKVPlQOqxJB"),
        ]

        for url, expected_id in urls:
            space_id = dl._extract_space_id(url)
            assert space_id == expected_id

    def test_extract_space_id_invalid(self):
        """Test extracting space ID from invalid URL"""
        dl = XSpacesDL()

        invalid_urls = [
            "https://x.com/user/status/123",
            "https://x.com/spaces",
            "not a url",
            "",
        ]

        for url in invalid_urls:
            with pytest.raises(InvalidURLError):
                dl._extract_space_id(url)

    def test_get_guest_token(self):
        """Test dynamic guest token fetching"""
        dl = XSpacesDL()
        token = dl._get_guest_token()
        assert isinstance(token, str) and token.isdigit() and len(token) > 8
        assert dl.session.headers["x-guest-token"] == token

    def test_config_initialization(self):
        """Test initialization with config"""
        config = Config(
            output_dir="./test",
            format="mp3",
            verbose=True,
        )

        dl = XSpacesDL(config=config)
        assert dl.config.get("output_dir") == "./test"
        assert dl.config.get("format") == "mp3"
        assert dl.config.get("verbose") is True
