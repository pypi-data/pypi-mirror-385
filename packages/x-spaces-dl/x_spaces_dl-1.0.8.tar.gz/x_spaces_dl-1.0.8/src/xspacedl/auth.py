"""
Authentication handling for x-spaces-dl
"""

import http.cookiejar
from pathlib import Path
from typing import Optional

import requests

from .exceptions import AuthenticationError


class AuthManager:
    """Manages authentication for X/Twitter API"""

    def __init__(self, cookies_file: Optional[str] = None):
        """
        Initialize authentication manager

        Args:
            cookies_file: Path to Netscape format cookies file
        """
        self.cookies_file = cookies_file
        self.cookies: Optional[http.cookiejar.CookieJar] = None
        self.csrf_token: Optional[str] = None
        self.auth_token: Optional[str] = None

        if cookies_file:
            self.load_cookies()

    def load_cookies(self):
        """Load cookies from file"""
        if not self.cookies_file:
            return

        path = Path(self.cookies_file)
        if not path.exists():
            raise AuthenticationError(f"Cookies file not found: {self.cookies_file}")

        try:
            self.cookies = http.cookiejar.MozillaCookieJar(str(path))
            self.cookies.load(ignore_discard=True, ignore_expires=True)

            # Extract important tokens
            for cookie in self.cookies:
                if cookie.name == "ct0":
                    self.csrf_token = cookie.value
                elif cookie.name == "auth_token":
                    self.auth_token = cookie.value

        except Exception as e:
            raise AuthenticationError(f"Failed to load cookies: {str(e)}")

    def get_authenticated_session(self) -> requests.Session:
        """
        Create an authenticated requests session

        Returns:
            Configured requests.Session with authentication
        """
        session = requests.Session()

        if self.cookies:
            # Add cookies to session
            for cookie in self.cookies:
                session.cookies.set(cookie.name, cookie.value, domain=cookie.domain)

        # Add CSRF token if available
        if self.csrf_token:
            session.headers["x-csrf-token"] = self.csrf_token

        return session

    def is_authenticated(self) -> bool:
        """Check if we have valid authentication"""
        return bool(self.auth_token and self.csrf_token)

    def validate_auth(self, session: requests.Session) -> bool:
        """
        Validate authentication by making a test request

        Args:
            session: Requests session to test

        Returns:
            True if authentication is valid
        """
        try:
            # Test with account verification endpoint
            response = session.get(
                "https://api.x.com/1.1/account/verify_credentials.json", timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
