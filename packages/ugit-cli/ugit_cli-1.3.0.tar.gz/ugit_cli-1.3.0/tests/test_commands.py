"""Tests for command implementations."""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ugit.commands import add, commit, init, status
from ugit.core.repository import Index, Repository


class TestInitCommand:
    """Test repository initialization."""

    def test_init_creates_repository_structure(self):
        """Test that init creates proper repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                init()

                # Check that .ugit directory and subdirectories exist
                assert os.path.exists(".ugit")
                assert os.path.exists(".ugit/objects")
                assert os.path.exists(".ugit/refs/heads")
                assert os.path.exists(".ugit/HEAD")

                # Check HEAD content
                with open(".ugit/HEAD", "r") as f:
                    head_content = f.read()
                assert head_content == "ref: refs/heads/main"

            finally:
                os.chdir(old_cwd)

    def test_init_in_existing_repository(self):
        """Test init in already initialized repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Initialize once
                init()

                # Initialize again - should detect existing repo
                # This would normally print "Already a ugit repository"
                init()  # Should not raise an error

            finally:
                os.chdir(old_cwd)


class TestAddCommand(unittest.TestCase):
    """Test file staging."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        init()
        self.repo = Repository()
        self.index = Index(self.repo)

    def tearDown(self):
        os.chdir(self.original_cwd)
        import shutil

        shutil.rmtree(self.test_dir)

    def test_add_single_file(self):
        """Test adding a single file to staging area."""
        test_file = Path("test.txt")
        test_file.write_text("Hello, World!")
        add("test.txt")
        index_data = self.index.read()
        self.assertIn("test.txt", index_data)

    def test_add_nonexistent_file(self):
        """Test adding non-existent file."""
        add("nonexistent.txt")
        index_data = self.index.read()
        self.assertEqual(len(index_data), 0)

    def test_add_stages_deletion(self):
        """Test that add stages a file deletion."""
        # Create, add, and commit a file
        test_file = Path("a.txt")
        test_file.write_text("initial content")
        add("a.txt")
        commit("initial commit")

        # Delete the file
        os.remove("a.txt")

        # Run `add .` to stage the deletion
        add(".")

        # Check that the file is no longer in the index
        index_data = self.index.read()
        self.assertNotIn("a.txt", index_data)

    def test_add_does_not_restage_unmodified(self):
        """Test that add does not re-stage an unmodified file."""
        # Create, add, and commit a file
        test_file = Path("a.txt")
        test_file.write_text("initial content")
        add("a.txt")
        commit("initial commit")

        # Run `add .` again
        f = io.StringIO()
        with redirect_stdout(f):
            add(".")
        output = f.getvalue()

        # Check that no "Staged" message was printed
        self.assertNotIn("Staged a.txt", output)


class TestCommitCommand:
    """Test commit creation."""

    def test_commit_with_staged_files(self):
        """Test creating a commit with staged files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                init()

                # Create and add a file
                test_file = Path("test.txt")
                test_file.write_text("Initial content")
                add("test.txt")

                # Create commit
                commit("Initial commit")

                # Check that commit was created
                repo = Repository()
                head_sha = repo.get_head_ref()
                assert head_sha is not None
                assert len(head_sha) == 40  # SHA-1 length

            finally:
                os.chdir(old_cwd)

    def test_commit_with_empty_index(self):
        """Test committing with no staged files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                init()

                # Try to commit without staging anything
                commit("Empty commit")  # Should handle gracefully

            finally:
                os.chdir(old_cwd)


class TestStatusCommand:
    """Test status reporting."""

    def test_status_clean_repository(self):
        """Test status on clean repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                init()
                status()  # Should not raise errors

            finally:
                os.chdir(old_cwd)

    def test_status_with_untracked_files(self):
        """Test status with untracked files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                init()

                # Create untracked file
                test_file = Path("untracked.txt")
                test_file.write_text("Untracked content")

                status()  # Should detect untracked file

            finally:
                os.chdir(old_cwd)
