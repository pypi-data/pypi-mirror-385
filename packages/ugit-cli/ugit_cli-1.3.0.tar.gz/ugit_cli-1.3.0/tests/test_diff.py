"""
Test cases for ugit diff command.
"""

import os
import shutil
import tempfile
from unittest import TestCase

from ugit.commands.add import add
from ugit.commands.commit import commit
from ugit.commands.config import config
from ugit.commands.diff import diff
from ugit.commands.init import init


class TestDiffCommand(TestCase):
    """Test cases for diff functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Initialize repository
        init()
        config("user.name", "Test User")
        config("user.email", "test@ugit.com")

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_diff_no_changes(self):
        """Test diff with no changes."""
        # Create and commit a file
        with open("test.txt", "w") as f:
            f.write("Hello, World!")

        add(["test.txt"])
        commit("Initial commit")

        # Test that diff shows no changes
        diff()  # Should show "No changes in working directory"

    def test_diff_working_directory(self):
        """Test diff showing working directory changes."""
        # Create and commit a file
        with open("test.txt", "w") as f:
            f.write("Hello, World!")

        add(["test.txt"])
        commit("Initial commit")

        # Modify the file
        with open("test.txt", "w") as f:
            f.write("Hello, Universe!")

        diff()  # Should show changes

    def test_diff_staged_changes(self):
        """Test diff showing staged changes."""
        # Create and commit a file
        with open("test.txt", "w") as f:
            f.write("Hello, World!")

        add(["test.txt"])
        commit("Initial commit")

        # Modify and stage the file
        with open("test.txt", "w") as f:
            f.write("Hello, Universe!")

        add(["test.txt"])

        diff(staged=True)  # Should show staged changes

    def test_diff_with_ugitignore(self):
        """Test that diff respects .ugitignore."""
        # Create .ugitignore
        with open(".ugitignore", "w") as f:
            f.write("*.tmp\n")

        # Create files
        with open("test.txt", "w") as f:
            f.write("Hello, World!")

        with open("temp.tmp", "w") as f:
            f.write("Temporary file")

        add(["."])
        commit("Initial commit")

        # Modify both files
        with open("test.txt", "w") as f:
            f.write("Hello, Universe!")

        with open("temp.tmp", "w") as f:
            f.write("Modified temporary file")

        diff()  # Should only show test.txt changes, not temp.tmp
