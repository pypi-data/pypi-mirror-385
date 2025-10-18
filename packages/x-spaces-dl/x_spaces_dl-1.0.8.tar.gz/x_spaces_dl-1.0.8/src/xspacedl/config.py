"""
Configuration management for x-spaces-dl
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class Config:
    """Configuration manager for x-spaces-dl"""

    DEFAULT_CONFIG_PATHS = [
        Path.home() / ".config" / "xspacesdl" / "config.yaml",
        Path.home() / ".xspacesdl" / "config.yaml",
        Path.cwd() / "xspacesdl.yaml",
    ]

    DEFAULT_CONFIG = {
        "output_dir": ".",
        "format": "mp3",
        "embed_metadata": False,
        "save_metadata": False,
        "retry_attempts": 3,
        "template": "{space_id}",
        "guest_mode": True,
        "cookies_file": None,
        "verbose": False,
        "quiet": False,
    }

    def __init__(self, config_file: Optional[str] = None, **kwargs):
        """
        Initialize configuration

        Args:
            config_file: Path to configuration file
            **kwargs: Override configuration options
        """
        self.config = self.DEFAULT_CONFIG.copy()

        # Load from file if exists
        if config_file:
            self.load_from_file(config_file)
        else:
            self.load_from_default_paths()

        # Override with kwargs
        for key, value in kwargs.items():
            if value is not None:
                self.config[key] = value

    def load_from_file(self, filepath: str):
        """Load configuration from a YAML file"""
        path = Path(filepath)
        if path.exists():
            try:
                with open(path, "r") as f:
                    file_config = yaml.safe_load(f) or {}
                    self.config.update(file_config)
            except Exception:
                # Silently fail if config file is invalid
                pass

    def load_from_default_paths(self):
        """Try loading config from default paths"""
        for path in self.DEFAULT_CONFIG_PATHS:
            if path.exists():
                self.load_from_file(str(path))
                break

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return self.config.copy()

    @classmethod
    def create_default_config(cls, filepath: str):
        """Create a default configuration file"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        config_content = """# x-spaces-dl Configuration File

# Output directory for downloaded spaces
output_dir: ~/Downloads/Spaces

# Default output format (m4a, mp3, aac, wav)
format: m4a

# Embed metadata into audio file
embed_metadata: true

# Save metadata to separate JSON file
save_metadata: false

# Number of retry attempts for failed downloads
retry_attempts: 3

# Filename template
# Available variables: {space_id}, {title}, {host}, {date}, {time}
template: "{date}_{host}_{title}"

# Use guest mode by default (no authentication)
guest_mode: true

# Path to cookies.txt file for authentication
# cookies_file: ~/cookies.txt

# Logging
verbose: false
quiet: false
"""
        with open(path, "w") as f:
            f.write(config_content)
