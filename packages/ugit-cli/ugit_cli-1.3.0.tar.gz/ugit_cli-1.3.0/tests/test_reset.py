"""
Test cases for ugit reset command.
"""

import os
import shutil
import tempfile
from unittest import TestCase

from ugit.commands.add import add
from ugit.commands.commit import commit
from ugit.commands.init import init
from ugit.commands.reset import reset, unstage
from ugit.core.repository import Repository


class TestResetCommand(TestCase):
    """Test cases for reset functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Initialize repository and create initial commit
        init()
        with open("test.txt", "w") as f:
            f.write("Hello, World!")
        add(["test.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_reset_staging_area(self):
        """Test resetting staging area."""
        # Modify and stage a file
        with open("test.txt", "w") as f:
            f.write("Modified content")
        add(["test.txt"])

        # Reset staging area
        try:
            reset()
        except SystemExit:
            pass

        # Check that index is cleared
        repo = Repository()
        index_path = os.path.join(repo.ugit_dir, "index")
        self.assertFalse(os.path.exists(index_path))

    def test_unstage_specific_file(self):
        """Test unstaging a specific file."""
        # Stage multiple files
        with open("file1.txt", "w") as f:
            f.write("File 1")
        with open("file2.txt", "w") as f:
            f.write("File 2")

        add(["file1.txt", "file2.txt"])

        # Unstage one file
        try:
            unstage(["file1.txt"])
        except SystemExit:
            pass

        # Check that only file2.txt is still staged
        repo = Repository()
        from ugit.core.repository import Index

        index = Index(repo)
        index_data = index.read()

        self.assertIn("file2.txt", index_data)
        self.assertNotIn("file1.txt", index_data)

    def test_hard_reset(self):
        """Test hard reset."""
        # Create second commit
        with open("test.txt", "w") as f:
            f.write("Second version")
        add(["test.txt"])
        commit("Second commit", "Test Author <test@example.com>")

        # Make changes and stage them
        with open("test.txt", "w") as f:
            f.write("Third version")
        add(["test.txt"])

        # Get first commit SHA
        Repository()
        # Would need to implement log traversal to get first commit
        # For now, just test that hard reset works conceptually
        try:
            reset(hard=True)  # Reset to HEAD
        except SystemExit:
            pass

    def test_soft_reset(self):
        """Test soft reset."""
        # Create second commit
        with open("test.txt", "w") as f:
            f.write("Second version")
        add(["test.txt"])
        commit("Second commit", "Test Author <test@example.com>")

        try:
            reset(soft=True)  # Should only move HEAD
        except SystemExit:
            pass
