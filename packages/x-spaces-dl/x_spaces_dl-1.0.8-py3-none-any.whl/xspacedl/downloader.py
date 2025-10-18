"""
Download functionality for x-spaces-dl
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests
from tqdm import tqdm

from .exceptions import ConversionError, DownloadError
from .utils import check_ffmpeg


class Downloader:
    """Handles downloading and format conversion"""

    def __init__(self, config=None, logger=None):
        """Initialize downloader"""
        self.config = config
        self.logger = logger
        self.has_ffmpeg = check_ffmpeg()

        if not self.has_ffmpeg and logger:
            logger.warning("ffmpeg not found - using slower Python fallback")

    def download(
        self,
        m3u8_url: str,
        output_file: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Download M3U8 stream

        Args:
            m3u8_url: URL of M3U8 playlist
            output_file: Output file path
            metadata: Optional metadata dict

        Returns:
            True if successful
        """
        # Check for resume
        if Path(output_file).exists():
            if self.config and not self.config.get("no_resume"):
                if self.logger:
                    self.logger.info(f"File exists: {output_file}")
                response = input("Overwrite? (y/n): ").lower()
                if response != "y":
                    if self.logger:
                        self.logger.info("Skipping download")
                    return True

        # Use ffmpeg if available
        if self.has_ffmpeg:
            return self._download_with_ffmpeg(m3u8_url, output_file)
        else:
            return self._download_with_python(m3u8_url, output_file)

    def _download_with_ffmpeg(self, m3u8_url: str, output_file: str) -> bool:
        """Download using ffmpeg"""
        cmd = [
            "ffmpeg",
            "-i",
            m3u8_url,
            "-c",
            "copy",
            "-bsf:a",
            "aac_adtstoasc",
            "-y",  # Overwrite without asking
            output_file,
        ]

        # Suppress ffmpeg output unless verbose
        if self.config and self.config.get("verbose"):
            ffmpeg_stdout = None
            ffmpeg_stderr = None
        elif self.config and self.config.get("quiet"):
            cmd.extend(["-loglevel", "error"])
            ffmpeg_stdout = subprocess.DEVNULL
            ffmpeg_stderr = subprocess.DEVNULL
        else:
            cmd.extend(["-loglevel", "warning"])
            ffmpeg_stdout = subprocess.DEVNULL
            ffmpeg_stderr = subprocess.DEVNULL

        try:
            subprocess.run(cmd, check=True, stdout=ffmpeg_stdout, stderr=ffmpeg_stderr)
            return True
        except subprocess.CalledProcessError as e:
            raise DownloadError(f"FFmpeg download failed: {str(e)}")
        except FileNotFoundError:
            raise DownloadError("FFmpeg not found in PATH")

    def _download_with_python(self, m3u8_url: str, output_file: str) -> bool:
        """Download using pure Python (fallback)"""
        if self.logger:
            self.logger.info("Downloading with Python fallback method...")

        try:
            # Download playlist
            response = requests.get(m3u8_url, timeout=30)
            response.raise_for_status()
            playlist = response.text

            # Parse segments
            base_url = m3u8_url.rsplit("/", 1)[0] + "/"
            segments = []
            for line in playlist.split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    segment_url = urljoin(base_url, line)
                    segments.append(segment_url)

            if not segments:
                raise DownloadError("No segments found in playlist")

            if self.logger:
                self.logger.info(f"Found {len(segments)} segments")

            # Download segments with progress bar
            with open(output_file, "wb") as outfile:
                with tqdm(
                    total=len(segments),
                    desc="Downloading",
                    disable=self.config and self.config.get("quiet"),
                    unit="segment",
                ) as pbar:
                    for segment_url in segments:
                        try:
                            seg_response = requests.get(segment_url, timeout=30)
                            seg_response.raise_for_status()
                            outfile.write(seg_response.content)
                            pbar.update(1)
                        except Exception as e:
                            raise DownloadError(f"Segment download failed: {str(e)}")

            return True

        except Exception as e:
            # Cleanup partial file
            if Path(output_file).exists():
                Path(output_file).unlink()
            raise DownloadError(f"Python download failed: {str(e)}")

    def convert_format(self, input_file: str, output_format: str) -> str:
        """
        Convert audio file to different format

        Args:
            input_file: Input file path
            output_format: Target format (mp3, aac, wav, etc.)

        Returns:
            Path to converted file
        """
        if not self.has_ffmpeg:
            raise ConversionError("ffmpeg required for format conversion")

        output_file = str(Path(input_file).with_suffix(f".{output_format}"))

        cmd = ["ffmpeg", "-i", input_file, "-y"]

        # Format-specific options
        if output_format == "mp3":
            cmd.extend(["-codec:a", "libmp3lame", "-qscale:a", "2"])
        elif output_format == "wav":
            cmd.extend(["-codec:a", "pcm_s16le"])
        elif output_format == "aac":
            cmd.extend(["-codec:a", "aac", "-b:a", "192k"])

        cmd.append(output_file)

        # Suppress ffmpeg output unless verbose
        if self.config and self.config.get("verbose"):
            ffmpeg_stdout = None
            ffmpeg_stderr = None
        elif self.config and self.config.get("quiet"):
            cmd.extend(["-loglevel", "error"])
            ffmpeg_stdout = subprocess.DEVNULL
            ffmpeg_stderr = subprocess.DEVNULL
        else:
            cmd.extend(["-loglevel", "warning"])
            ffmpeg_stdout = subprocess.DEVNULL
            ffmpeg_stderr = subprocess.DEVNULL

        try:
            subprocess.run(cmd, check=True, stdout=ffmpeg_stdout, stderr=ffmpeg_stderr)

            # Remove original file
            Path(input_file).unlink()

            return output_file
        except subprocess.CalledProcessError as e:
            raise ConversionError(f"Format conversion failed: {str(e)}")
