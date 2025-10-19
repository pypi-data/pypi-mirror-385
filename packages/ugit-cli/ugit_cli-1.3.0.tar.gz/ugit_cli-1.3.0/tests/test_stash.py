"""
Test cases for ugit stash command.
"""

import os
import shutil
import tempfile
from unittest import TestCase

from ugit.commands.add import add
from ugit.commands.commit import commit
from ugit.commands.init import init
from ugit.commands.stash import stash, stash_apply, stash_drop, stash_list, stash_pop
from ugit.core.repository import Repository


class TestStashCommand(TestCase):
    """Test cases for stash functionality."""

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

    def test_stash_changes(self):
        """Test stashing changes."""
        # Modify file and stage changes
        with open("test.txt", "w") as f:
            f.write("Modified content")
        add(["test.txt"])

        # Create unstaged changes
        with open("test2.txt", "w") as f:
            f.write("Unstaged file")

        try:
            stash("Test stash message")
        except SystemExit:
            pass

        # Check that stash was created
        repo = Repository()
        stash_file = os.path.join(repo.ugit_dir, "stash")
        self.assertTrue(os.path.exists(stash_file))

    def test_stash_pop(self):
        """Test popping stash."""
        # Create changes and stash them
        with open("test.txt", "w") as f:
            f.write("Stashed content")
        add(["test.txt"])

        try:
            stash("Test stash")
            stash_pop()
        except SystemExit:
            pass

        # Check that changes are restored
        with open("test.txt", "r") as f:
            content = f.read()
        self.assertEqual(content, "Stashed content")

    def test_stash_list(self):
        """Test listing stashes."""
        # Create multiple stashes
        with open("test.txt", "w") as f:
            f.write("Content 1")
        add(["test.txt"])

        try:
            stash("First stash")
        except SystemExit:
            pass

        with open("test.txt", "w") as f:
            f.write("Content 2")
        add(["test.txt"])

        try:
            stash("Second stash")
            stash_list()  # Should show both stashes
        except SystemExit:
            pass

    def test_stash_apply(self):
        """Test applying stash without removing it."""
        # Create changes and stash them
        with open("test.txt", "w") as f:
            f.write("Applied content")
        add(["test.txt"])

        try:
            stash("Test apply")
            stash_apply()
        except SystemExit:
            pass

        # Check that stash still exists
        repo = Repository()
        stash_file = os.path.join(repo.ugit_dir, "stash")
        self.assertTrue(os.path.exists(stash_file))

    def test_stash_drop(self):
        """Test dropping stash without applying."""
        # Create changes and stash them
        with open("test.txt", "w") as f:
            f.write("Dropped content")
        add(["test.txt"])

        try:
            stash("Test drop")
            stash_drop()
        except SystemExit:
            pass

        # Check that stash was removed
        repo = Repository()
        stash_file = os.path.join(repo.ugit_dir, "stash")
        self.assertFalse(os.path.exists(stash_file))
