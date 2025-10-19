"""
Tests for the `status` command.
"""

import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ugit.commands.add import add
from ugit.commands.commit import commit
from ugit.commands.init import init
from ugit.commands.status import status


class TestStatusCommand(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        init()

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def capture_status_output(self) -> str:
        """Helper to capture the output of the status command."""
        f = io.StringIO()
        with redirect_stdout(f):
            status()
        return f.getvalue()

    def test_status_on_clean_repository(self):
        """Test status on a clean repository with one commit."""
        # Create, add, and commit a file
        (Path(".") / "a.txt").write_text("initial content")
        add("a.txt")
        commit("initial commit")

        # Check status
        output = self.capture_status_output()
        self.assertIn("Nothing to commit, working tree clean", output)

    def test_status_with_untracked_file(self):
        """Test status shows untracked files."""
        (Path(".") / "untracked.txt").write_text("untracked")
        output = self.capture_status_output()
        self.assertIn("Untracked files:", output)
        self.assertIn("? untracked.txt", output)

    def test_status_with_modified_file(self):
        """Test status shows modified files."""
        # Create, add, and commit a file
        (Path(".") / "a.txt").write_text("initial content")
        add("a.txt")
        commit("initial commit")

        # Modify the file
        (Path(".") / "a.txt").write_text("modified content")

        # Check status
        output = self.capture_status_output()
        self.assertIn("Changes not staged for commit:", output)
        self.assertIn("M a.txt", output)

    def test_status_with_deleted_file(self):
        """Test status shows deleted files."""
        # Create, add, and commit a file
        (Path(".") / "a.txt").write_text("initial content")
        add("a.txt")
        commit("initial commit")

        # Delete the file
        os.remove("a.txt")

        # Check status
        output = self.capture_status_output()
        self.assertIn("Deleted files:", output)
        self.assertIn("D a.txt", output)

    def test_status_with_new_staged_file(self):
        """Test status shows new files staged for commit."""
        (Path(".") / "new.txt").write_text("new file")
        add("new.txt")

        output = self.capture_status_output()
        self.assertIn("Changes to be committed:", output)
        self.assertIn("A new.txt", output)

    def test_status_with_modified_staged_file(self):
        """Test status shows modified files staged for commit."""
        # Create, add, and commit a file
        (Path(".") / "a.txt").write_text("initial content")
        add("a.txt")
        commit("initial commit")

        # Modify and stage the file
        (Path(".") / "a.txt").write_text("modified content")
        add("a.txt")

        # Check status
        output = self.capture_status_output()
        self.assertIn("Changes to be committed:", output)
        self.assertIn("M a.txt", output)
