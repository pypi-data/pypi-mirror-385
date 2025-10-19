"""Tests for config command."""

import os
import shutil
import tempfile

from ugit.commands.config import config
from ugit.commands.init import init
from ugit.utils.config import Config


class TestConfigCommand:
    """Test the config command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        init()  # Initialize a repository for the tests

    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_set_and_get_config(self, capsys):
        """Test setting and getting configuration values."""
        config("user.name", "John Doe")
        captured = capsys.readouterr()
        assert "Set user.name = John Doe" in captured.out

        config("user.name")
        captured = capsys.readouterr()
        assert "John Doe" in captured.out

    def test_list_config(self, capsys):
        """Test listing all configuration."""
        config("user.name", "John Doe")
        config("user.email", "john@example.com")

        config(list_all=True)
        captured = capsys.readouterr()
        assert "user.name=John Doe" in captured.out
        assert "user.email=john@example.com" in captured.out

    def test_config_help(self, capsys):
        """Test config help display."""
        config()
        captured = capsys.readouterr()
        assert "Usage:" in captured.out

    def test_invalid_key_format(self, capsys):
        """Test error handling for invalid key format."""
        result = config("invalidkey", "value")
        assert result == 1

    def test_get_nonexistent_key(self, capsys):
        """Test getting a non-existent configuration key."""
        result = config("user.nonexistent")
        assert result == 1

    def test_config_persistence(self, capsys):
        """Test that configuration persists across operations."""
        # Set config
        config("test.value", "persistent")

        # Create new config instance to test persistence
        new_config = Config(self.test_dir)
        value = new_config.get("test", "value")
        assert value == "persistent"

    def test_empty_config_list(self, capsys):
        """Test listing when no config exists."""
        config(list_all=True)
        captured = capsys.readouterr()
        assert "No configuration found" in captured.out

    def test_config_with_special_characters(self, capsys):
        """Test config with special characters in values."""
        special_value = "Name with spaces & symbols!"
        config("user.name", special_value)
        captured = capsys.readouterr()
        assert f"Set user.name = {special_value}" in captured.out

        # Verify it can be retrieved
        config("user.name")
        captured = capsys.readouterr()
        assert special_value in captured.out

    def test_multiple_sections(self, capsys):
        """Test configuration with multiple sections."""
        config("user.name", "John")
        config("core.editor", "vim")
        config("user.email", "john@example.com")

        config(list_all=True)
        captured = capsys.readouterr()
        output = captured.out

        assert "user.name=John" in output
        assert "user.email=john@example.com" in output
        assert "core.editor=vim" in output

    def test_config_overwrite(self, capsys):
        """Test overwriting existing configuration."""
        # Set initial value
        config("user.name", "Initial Name")
        config("user.name")
        captured = capsys.readouterr()
        assert "Initial Name" in captured.out

        # Overwrite with new value
        config("user.name", "New Name")
        config("user.name")
        captured = capsys.readouterr()
        assert "New Name" in captured.out

    def test_config_case_sensitivity(self, capsys):
        """Test that config keys are case sensitive."""
        config("user.name", "lowercase")
        config("User.Name", "mixedcase")

        config("user.name")
        captured = capsys.readouterr()
        assert "lowercase" in captured.out

        config("User.Name")
        captured = capsys.readouterr()
        assert "mixedcase" in captured.out
