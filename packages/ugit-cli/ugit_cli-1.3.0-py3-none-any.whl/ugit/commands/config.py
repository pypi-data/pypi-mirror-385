"""Configuration command for ugit."""

import sys
from typing import Optional

from ..core.exceptions import NotInRepositoryError
from ..utils.config import Config


def config(
    key: Optional[str] = None, value: Optional[str] = None, list_all: bool = False
) -> int:
    """
    Manage ugit configuration.

    Args:
        key: Configuration key (section.option)
        value: Configuration value
        list_all: List all configuration options

    Returns:
        0 on success, 1 on error
    """
    try:
        # Try to use repository config if available
        from ..utils.helpers import ensure_repository

        repo = ensure_repository()
        config_obj = Config(repo.path)
    except NotInRepositoryError:
        # Not in a repository - use config in current directory as a fallback
        config_obj = Config(".")

    if list_all:
        _list_all_config(config_obj)
        return 0
    elif key is None and value is None:
        _show_help()
        return 0
    elif value is None:
        if key is None:
            raise ValueError("Key cannot be None when getting config value")
        return _get_config(config_obj, key)
    else:
        if key is None:
            raise ValueError("Key cannot be None when setting config value")
        return _set_config(config_obj, key, value)


def _show_help() -> None:
    """Show config command help."""
    print("Usage:")
    print("  ugit config <key> <value>     # Set configuration value")
    print("  ugit config <key>             # Get configuration value")
    print("  ugit config --list            # List all configuration")
    print()
    print("Examples:")
    print("  ugit config user.name 'Your Name'")
    print("  ugit config user.email 'you@example.com'")
    print("  ugit config --list")


def _set_config(config_obj: Config, key: str, value: str) -> int:
    """Set a configuration value."""
    if "." not in key:
        print(
            "Error: Configuration key must be in 'section.option' format",
            file=sys.stderr,
        )
        return 1

    section, option = key.split(".", 1)
    config_obj.set(section, option, value)
    print(f"Set {key} = {value}")
    return 0


def _get_config(config_obj: Config, key: str) -> int:
    """Get a configuration value."""
    if "." not in key:
        print(
            "Error: Configuration key must be in 'section.option' format",
            file=sys.stderr,
        )
        return 1

    section, option = key.split(".", 1)
    value = config_obj.get(section, option)
    if value is None:
        print(f"Configuration key '{key}' not found", file=sys.stderr)
        return 1
    else:
        print(value)
        return 0


def _list_all_config(config_obj: Config) -> None:
    """List all configuration values."""
    if not hasattr(config_obj, "_config"):
        print("No configuration found")
        return

    found_any = False
    for section_name in config_obj._config.sections():
        for option_name, value in config_obj._config.items(section_name):
            print(f"{section_name}.{option_name}={value}")
            found_any = True

    if not found_any:
        print("No configuration found")
