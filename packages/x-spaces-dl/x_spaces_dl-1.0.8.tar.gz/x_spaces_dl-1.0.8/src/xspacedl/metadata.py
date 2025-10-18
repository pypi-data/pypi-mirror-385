"""
Metadata handling for x-spaces-dl
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from dateutil import parser as date_parser

try:
    from mutagen.easyid3 import EasyID3
    from mutagen.flac import FLAC
    from mutagen.mp3 import MP3
    from mutagen.mp4 import MP4

    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

from .exceptions import MetadataError


class MetadataManager:
    """Manages space metadata extraction and embedding"""

    def __init__(self, logger=None):
        """Initialize metadata manager"""
        self.logger = logger

    def parse_metadata(self, raw_data: Dict[str, Any], space_id: str) -> Dict[str, Any]:
        """
        Parse raw API response into structured metadata

        Args:
            raw_data: Raw API response
            space_id: Space ID

        Returns:
            Parsed metadata dictionary
        """
        try:
            audio_space = raw_data.get("data", {}).get("audioSpace", {})
            metadata_raw = audio_space.get("metadata", {})

            # Extract basic info
            title = metadata_raw.get("title", "Untitled Space")
            state = metadata_raw.get("state", "UNKNOWN")
            created_at = metadata_raw.get("created_at")
            started_at = metadata_raw.get("started_at")
            ended_at = metadata_raw.get("ended_at")

            # Parse dates
            created_date = self._parse_timestamp(created_at) if created_at else None
            started_date = self._parse_timestamp(started_at) if started_at else None
            ended_date = self._parse_timestamp(ended_at) if ended_at else None

            # Get host/creator info
            participants = audio_space.get("participants", {})
            admins = participants.get("admins", [])
            host = admins[0].get("twitter_screen_name", "Unknown") if admins else "Unknown"
            host_display_name = admins[0].get("display_name", host) if admins else host

            # Get participant count
            total_participants = participants.get("total", 0)

            # Build metadata dict
            metadata = {
                "space_id": space_id,
                "title": title,
                "host": host,
                "host_display_name": host_display_name,
                "state": state,
                "created_at": created_at,
                "started_at": started_at,
                "ended_at": ended_at,
                "created_date": created_date,
                "started_date": started_date,
                "ended_date": ended_date,
                "total_participants": total_participants,
                "admins": admins,
                "url": f"https://x.com/i/spaces/{space_id}",
            }

            return metadata

        except Exception as e:
            if self.logger:
                self.logger.warning(f"Metadata parsing failed: {str(e)}")
            return {
                "space_id": space_id,
                "title": "Unknown",
                "host": "Unknown",
            }

    def _parse_timestamp(self, timestamp: Any) -> Optional[str]:
        """Parse timestamp to ISO format"""
        try:
            if isinstance(timestamp, int):
                # Unix timestamp in milliseconds
                dt = datetime.fromtimestamp(timestamp / 1000)
            else:
                # String timestamp
                dt = date_parser.parse(str(timestamp))
            return dt.isoformat()
        except Exception:
            return None

    def embed_metadata(self, audio_file: str, metadata: Dict[str, Any]):
        """
        Embed metadata into audio file

        Args:
            audio_file: Path to audio file
            metadata: Metadata dictionary
        """
        if not MUTAGEN_AVAILABLE:
            if self.logger:
                self.logger.warning("mutagen not available - skipping metadata embedding")
            return

        try:
            path = Path(audio_file)
            suffix = path.suffix.lower()

            if suffix == ".mp3":
                self._embed_mp3(audio_file, metadata)
            elif suffix in [".m4a", ".mp4"]:
                self._embed_m4a(audio_file, metadata)
            elif suffix == ".flac":
                self._embed_flac(audio_file, metadata)
            else:
                if self.logger:
                    self.logger.warning(f"Metadata embedding not supported for {suffix}")

        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to embed metadata: {str(e)}")

    def _embed_mp3(self, audio_file: str, metadata: Dict[str, Any]):
        """Embed metadata into MP3 file"""
        audio = MP3(audio_file, ID3=EasyID3)
        audio["title"] = metadata.get("title", "")
        audio["artist"] = metadata.get("host_display_name", metadata.get("host", ""))
        audio["album"] = "X Space"
        if metadata.get("started_date"):
            audio["date"] = metadata["started_date"][:10]  # YYYY-MM-DD
        audio["comment"] = metadata.get("url", "")
        audio.save()

    def _embed_m4a(self, audio_file: str, metadata: Dict[str, Any]):
        """Embed metadata into M4A/MP4 file"""
        audio = MP4(audio_file)
        audio["\xa9nam"] = metadata.get("title", "")  # Title
        audio["\xa9ART"] = metadata.get("host_display_name", metadata.get("host", ""))  # Artist
        audio["\xa9alb"] = "X Space"  # Album
        if metadata.get("started_date"):
            audio["\xa9day"] = metadata["started_date"][:10]  # Date
        audio["\xa9cmt"] = metadata.get("url", "")  # Comment
        audio.save()

    def _embed_flac(self, audio_file: str, metadata: Dict[str, Any]):
        """Embed metadata into FLAC file"""
        audio = FLAC(audio_file)
        audio["title"] = metadata.get("title", "")
        audio["artist"] = metadata.get("host_display_name", metadata.get("host", ""))
        audio["album"] = "X Space"
        if metadata.get("started_date"):
            audio["date"] = metadata["started_date"][:10]
        audio["comment"] = metadata.get("url", "")
        audio.save()

    def save_metadata(self, metadata: Dict[str, Any], output_file: str):
        """
        Save metadata to JSON file

        Args:
            metadata: Metadata dictionary
            output_file: Output JSON file path
        """
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise MetadataError(f"Failed to save metadata: {str(e)}")
