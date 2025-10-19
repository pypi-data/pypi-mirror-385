"""Configuration management for ugit."""

import configparser
import os
from typing import Optional


class Config:
    """Manages ugit configuration."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.config_path = os.path.join(repo_path, ".ugit", "config")
        self._config = configparser.ConfigParser()
        self._load()

    def _load(self) -> None:
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            try:
                self._config.read(self.config_path)
            except (configparser.Error, IOError):
                pass  # Use defaults

    def get(
        self, section: str, key: str, default: Optional[str] = None
    ) -> Optional[str]:
        """Get configuration value."""
        try:
            return self._config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default

    def set(self, section: str, key: str, value: str) -> None:
        """Set configuration value."""
        if not self._config.has_section(section):
            self._config.add_section(section)
        self._config.set(section, key, value)
        self._save()

    def _save(self) -> None:
        """Save configuration to file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        try:
            with open(self.config_path, "w") as f:
                self._config.write(f)
        except (IOError, OSError):
            pass  # Fail silently

    def get_user_name(self) -> str:
        """Get configured user name."""
        return self.get("user", "name", "Your Name") or "Your Name"

    def get_user_email(self) -> str:
        """Get configured user email."""
        return self.get("user", "email", "you@example.com") or "you@example.com"

    def get_author_string(self) -> str:
        """Get formatted author string."""
        name = self.get_user_name()
        email = self.get_user_email()
        return f"{name} <{email}>"

    def remove(self, section: str, key: str) -> None:
        """Remove configuration value."""
        try:
            self._config.remove_option(section, key)
            # If section is now empty, remove it
            if not self._config.options(section):
                self._config.remove_section(section)
            self._save()
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass  # Already doesn't exist

    def get_all_settings(self) -> dict:
        """Get all configuration settings as a flat dictionary."""
        settings = {}
        for section_name in self._config.sections():
            for key, value in self._config.items(section_name):
                settings[f"{section_name}.{key}"] = value
        return settings
