"""
Core functionality for x-spaces-dl
"""

import re
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from .auth import AuthManager
from .config import Config
from .downloader import Downloader
from .exceptions import (
    AuthenticationError,
    DownloadError,
    InvalidURLError,
    SpaceNotFoundError,
)
from .metadata import MetadataManager
from .utils import format_filename, sanitize_filename, setup_logger


class XSpacesDL:
    """Main class for downloading X/Twitter Spaces"""

    BASE_URL = "https://api.x.com"
    AUTH_TOKEN = (
        "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
        "%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
    )

    def __init__(
        self,
        config: Optional[Config] = None,
        cookies_file: Optional[str] = None,
        guest_mode: bool = True,
    ):
        """
        Initialize XSpacesDL

        Args:
            config: Configuration object
            cookies_file: Path to cookies file for authentication
            guest_mode: Whether to prefer guest mode (will fall back to auth if available)
        """
        self.config = config or Config()
        self.guest_mode = guest_mode
        self.logger = setup_logger(
            verbose=self.config.get("verbose", False),
            quiet=self.config.get("quiet", False),
        )

        # Authentication
        self.auth_manager = None
        if cookies_file or self.config.get("cookies_file"):
            self.auth_manager = AuthManager(cookies_file or self.config.get("cookies_file"))

        # Components
        self.downloader = Downloader(config=self.config, logger=self.logger)
        self.metadata_manager = MetadataManager(logger=self.logger)

        # Session
        self.session = self._create_session()

    def _create_session(self, use_auth: bool = False) -> requests.Session:
        """Create a requests session"""
        if use_auth and self.auth_manager:
            session = self.auth_manager.get_authenticated_session()
            self.logger.info("Using authenticated session")
        else:
            session = requests.Session()
            self.logger.info("Using guest session")

        session.headers.update(
            {
                "Authorization": self.AUTH_TOKEN,
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
                ),
                "Accept": "*/*",
                "accept-language": "en-US,en;q=0.8",
                "content-type": "application/json",
                "Referer": "https://x.com/",
                "Origin": "https://x.com",
                "x-twitter-active-user": "yes",
                "x-twitter-client-language": "en",
            }
        )

        return session

    def _get_guest_token(self) -> str:
        """Dynamically fetch a guest token using the Bearer token."""
        url = f"{self.BASE_URL}/1.1/guest/activate.json"
        headers = self.session.headers.copy()
        # Only Bearer token is hardcoded
        headers["Authorization"] = self.AUTH_TOKEN
        try:
            r = requests.post(url, headers=headers, timeout=10)
            r.raise_for_status()
            token = r.json().get("guest_token")
            if token:
                self.session.headers["x-guest-token"] = token
                self.logger.debug(f"Guest token acquired: {token}")
                return token
            raise AuthenticationError("Failed to get guest token")
        except Exception as e:
            raise AuthenticationError(f"Guest token generation failed: {str(e)}")

    def _extract_space_id(self, url: str) -> str:
        """Extract the Space ID from an X Space URL"""
        match = re.search(r"/spaces/([a-zA-Z0-9]+)", url)
        if not match:
            raise InvalidURLError(f"Invalid X Space URL: {url}")
        return match.group(1)

    def _get_audio_space_metadata(self, space_id: str, retry: int = 0) -> Dict[str, Any]:
        """Fetch metadata for the given space ID using robust feature flags."""
        import json
        variables = {
            "id": space_id,
            "isMetatagsQuery": False,
            "withReplays": True,
            "withListeners": True,
        }
        features = {
            "spaces_2022_h2_spaces_communities": True,
            "spaces_2022_h2_clipping": True,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "payments_enabled": False,
            "profile_label_improvements_pcf_label_in_post_enabled": True,
            "responsive_web_profile_redirect_enabled": False,
            "rweb_tipjar_consumption_enabled": True,
            "verified_phone_label_enabled": True,
            "premium_content_api_read_enabled": False,
            "communities_web_enable_tweet_community_results_fetch": True,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": False,
            "responsive_web_grok_analysis_button_from_backend": False,
            "responsive_web_grok_community_note_auto_translation_is_enabled": False,
            "responsive_web_grok_image_annotation_enabled": False,
            "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
            "responsive_web_grok_imagine_annotation_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": False,
            "responsive_web_grok_analyze_post_followups_enabled": False,
            "responsive_web_grok_show_grok_translated_post": False,
            "longform_notetweets_inline_media_enabled": False,
            "longform_notetweets_rich_text_read_enabled": False,
            "responsive_web_grok_share_attachment_enabled": False,
            "articles_preview_enabled": False,
            "responsive_web_enhance_cards_enabled": False,
            "responsive_web_jetfuel_frame": False,
            "creator_subscriptions_quote_tweet_preview_enabled": False,
        }
        params = {
            "variables": json.dumps(variables, separators=(",", ":"), ensure_ascii=False),
            "features": json.dumps(features, separators=(",", ":"), ensure_ascii=False),
        }
        url = f"{self.BASE_URL}/graphql/iY0kOPlaSUig-Dy7rK7G7w/AudioSpaceById"
        try:
            r = self.session.get(url, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            if not data.get("data", {}).get("audioSpace"):
                raise SpaceNotFoundError(f"Space not found: {space_id}")
            return data
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401 and retry < 1 and self.auth_manager:
                self.logger.info("Guest mode failed, trying authenticated mode...")
                self.session = self._create_session(use_auth=True)
                return self._get_audio_space_metadata(space_id, retry + 1)
            raise SpaceNotFoundError(f"Failed to fetch space metadata: {str(e)}")
        except Exception as e:
            raise SpaceNotFoundError(f"Error fetching metadata: {str(e)}")

    def _get_m3u8_url(self, media_key: str) -> Optional[str]:
        """Fetch the .m3u8 stream URL using the media key"""
        params = {
            "client": "web",
            "use_syndication_guest_id": "false",
            "cookie_set_host": "x.com",
        }
        url = f"{self.BASE_URL}/1.1/live_video_stream/status/{media_key}"

        try:
            r = self.session.get(url, params=params, timeout=15)
            r.raise_for_status()
            location = r.json().get("source", {}).get("location")
            if not location:
                self.logger.warning("No stream URL found - replay may not be available")
            return location
        except Exception as e:
            raise DownloadError(f"Failed to get stream URL: {str(e)}")

    def get_stream_url(self, space_url: str) -> Optional[str]:
        """
        Get the M3U8 stream URL for a Space

        Args:
            space_url: URL of the Space

        Returns:
            M3U8 stream URL or None if not available
        """
        # Try guest mode first
        if self.guest_mode or not self.auth_manager:
            try:
                self._get_guest_token()
            except AuthenticationError as e:
                if not self.auth_manager:
                    raise
                self.logger.warning(f"Guest mode failed: {e}")
                self.session = self._create_session(use_auth=True)

        # Extract Space ID
        space_id = self._extract_space_id(space_url)
        self.logger.info(f"Space ID: {space_id}")

        # Fetch metadata
        metadata = self._get_audio_space_metadata(space_id)
        media_key = metadata["data"]["audioSpace"]["metadata"]["media_key"]
        self.logger.info(f"Media key: {media_key}")

        # Get stream URL
        m3u8_url = self._get_m3u8_url(media_key)
        if m3u8_url:
            self.logger.info(f"Stream URL: {m3u8_url}")

        return m3u8_url

    def get_space_metadata(self, space_url: str) -> Dict[str, Any]:
        """
        Get metadata for a Space

        Args:
            space_url: URL of the Space

        Returns:
            Dictionary containing space metadata
        """
        # Setup session
        if self.guest_mode or not self.auth_manager:
            try:
                self._get_guest_token()
            except AuthenticationError:
                if self.auth_manager:
                    self.session = self._create_session(use_auth=True)

        space_id = self._extract_space_id(space_url)
        raw_metadata = self._get_audio_space_metadata(space_id)

        # Parse metadata
        return self.metadata_manager.parse_metadata(raw_metadata, space_id)

    def download_space(
        self,
        space_url: str,
        output_file: Optional[str] = None,
        format: Optional[str] = None,
        embed_metadata: Optional[bool] = None,
        save_metadata: Optional[bool] = None,
    ) -> bool:
        """
        Download a Space recording

        Args:
            space_url: URL of the Space
            output_file: Output filename (optional)
            format: Output format (optional, uses config default)
            embed_metadata: Whether to embed metadata (optional)
            save_metadata: Whether to save metadata to JSON (optional)

        Returns:
            True if download successful
        """
        try:
            # Get metadata
            self.logger.info("Fetching space information...")
            metadata = self.get_space_metadata(space_url)

            # Get stream URL
            m3u8_url = self.get_stream_url(space_url)
            if not m3u8_url:
                self.logger.error("Replay not available for this space")
                return False

            # Determine output file
            if not output_file:
                template = self.config.get("template", "{space_id}")
                output_file = format_filename(template, metadata)
                output_file = sanitize_filename(output_file)

            # Always download as m4a, then convert if needed
            output_format = format or self.config.get("format", "mp3")
            base_name = output_file.rsplit(".", 1)[0] if output_file else format_filename(self.config.get("template", "{space_id}"), metadata)
            base_name = sanitize_filename(base_name)
            m4a_file = f"{base_name}.m4a"
            output_dir = self.config.get("output_dir", ".")
            m4a_path = Path(output_dir) / m4a_file
            m4a_path.parent.mkdir(parents=True, exist_ok=True)

            self.logger.info(f"Downloading to: {m4a_path}")
            success = self.downloader.download(
                m3u8_url,
                str(m4a_path),
                metadata=metadata,
            )
            if not success:
                return False

            # Convert to target format if needed
            final_path = m4a_path
            if output_format != "m4a":
                self.logger.info(f"Converting to {output_format}...")
                final_path = self.downloader.convert_format(str(m4a_path), output_format)

            # If user specified a custom output filename, rename to match and ensure extension
            if output_file:
                expected_ext = f'.{output_format}'
                if not output_file.endswith(expected_ext):
                    output_file = f'{output_file}{expected_ext}'
                custom_path = Path(output_dir) / output_file
                if Path(final_path) != custom_path:
                    Path(final_path).rename(custom_path)
                    final_path = custom_path


            # Embed metadata
            if embed_metadata or self.config.get("embed_metadata"):
                self.logger.info("Embedding metadata...")
                self.metadata_manager.embed_metadata(str(final_path), metadata)

            # Save metadata to JSON
            if save_metadata or self.config.get("save_metadata"):
                metadata_file = str(final_path).rsplit(".", 1)[0] + ".json"
                self.logger.info(f"Saving metadata to: {metadata_file}")
                self.metadata_manager.save_metadata(metadata, metadata_file)

            self.logger.info(f"✅ Download complete: {final_path}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Download failed: {str(e)}")
            if self.config.get("verbose"):
                import traceback

                traceback.print_exc()
            return False

    def download_batch(self, urls_file: str) -> Dict[str, bool]:
        """
        Download multiple spaces from a file

        Args:
            urls_file: Path to file containing Space URLs (one per line)

        Returns:
            Dictionary mapping URLs to success status
        """
        results = {}

        try:
            with open(urls_file, "r") as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

            self.logger.info(f"Found {len(urls)} spaces to download")

            for i, url in enumerate(urls, 1):
                self.logger.info(f"\n[{i}/{len(urls)}] Processing: {url}")
                try:
                    success = self.download_space(url)
                    results[url] = success
                except Exception as e:
                    self.logger.error(f"Failed: {str(e)}")
                    results[url] = False

                # Small delay between downloads
                if i < len(urls):
                    time.sleep(2)

            # Summary
            successful = sum(1 for v in results.values() if v)
            self.logger.info("\n" + "=" * 50)
            self.logger.info(f"Download Summary: {successful}/{len(urls)} successful")
            self.logger.info("=" * 50)

        except FileNotFoundError:
            self.logger.error(f"File not found: {urls_file}")
        except Exception as e:
            self.logger.error(f"Batch download failed: {str(e)}")

        return results
