"""
Tests for merge command functionality.
"""

import os
import tempfile
import unittest

import pytest

from ugit.commands.add import add
from ugit.commands.branch import branch
from ugit.commands.checkout import checkout
from ugit.commands.commit import commit
from ugit.commands.init import init
from ugit.commands.merge import merge
from ugit.core.exceptions import MergeConflictError, UgitError
from ugit.core.repository import Repository


class TestMergeCommand(unittest.TestCase):
    """Test cases for merge command."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil

        shutil.rmtree(self.test_dir)

    def test_merge_fast_forward(self):
        """Test fast-forward merge."""
        # Initialize repository
        init()

        # Create initial commit on main
        with open("main.txt", "w") as f:
            f.write("Main content")
        add(["main.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

        # Create feature branch
        branch("feature")
        checkout("feature")

        # Add commits to feature branch
        with open("feature.txt", "w") as f:
            f.write("Feature content")
        add(["feature.txt"])
        commit("Feature commit", "Test Author <test@example.com>")

        # Switch back to main
        checkout("main")

        # Merge feature branch (should be fast-forward)
        merge("feature")

        # Check that feature.txt exists in main
        self.assertTrue(os.path.exists("feature.txt"))

    def test_merge_no_ff(self):
        """Test merge with --no-ff flag."""
        # Initialize repository
        init()

        # Create initial commit
        with open("base.txt", "w") as f:
            f.write("Base content")
        add(["base.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

        # Create feature branch
        branch("feature")
        checkout("feature")

        # Add commit to feature
        with open("feature.txt", "w") as f:
            f.write("Feature content")
        add(["feature.txt"])
        commit("Feature commit", "Test Author <test@example.com>")

        # Switch back to main
        checkout("main")

        # Merge with no-ff
        merge("feature", no_ff=True)

        # Check that feature content is merged
        self.assertTrue(os.path.exists("feature.txt"))

    def test_merge_three_way(self):
        """Test three-way merge when branches have diverged."""
        # Initialize repository
        init()

        # Create initial commit
        with open("shared.txt", "w") as f:
            f.write("Shared content")
        add(["shared.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

        # Create and switch to feature branch
        branch("feature")
        checkout("feature")

        # Add commit to feature branch
        with open("feature.txt", "w") as f:
            f.write("Feature content")
        add(["feature.txt"])
        commit("Feature commit", "Test Author <test@example.com>")

        # Switch back to main and add different commit
        checkout("main")

        with open("main.txt", "w") as f:
            f.write("Main content")
        add(["main.txt"])
        commit("Main commit", "Test Author <test@example.com>")

        # Merge feature branch
        merge("feature")

        # Check that both files exist
        self.assertTrue(os.path.exists("feature.txt"))
        self.assertTrue(os.path.exists("main.txt"))
        self.assertTrue(os.path.exists("shared.txt"))

    def test_merge_conflict_detection(self):
        """Test that merge conflicts are detected."""
        # Initialize repository
        init()

        # Create initial commit with conflicting file
        with open("conflict.txt", "w") as f:
            f.write("Original content")
        add(["conflict.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

        # Create feature branch and modify file
        branch("feature")
        checkout("feature")

        with open("conflict.txt", "w") as f:
            f.write("Feature content")
        add(["conflict.txt"])
        commit("Feature commit", "Test Author <test@example.com>")

        # Switch to main and modify same file differently
        checkout("main")

        with open("conflict.txt", "w") as f:
            f.write("Main content")
        add(["conflict.txt"])
        commit("Main commit", "Test Author <test@example.com>")

        # Attempt merge - should detect conflict
        with pytest.raises(MergeConflictError):
            merge("feature")

        # Check that conflict markers exist
        with open("conflict.txt", "r") as f:
            content = f.read()
        self.assertIn("<<<<<<< HEAD", content)
        self.assertIn(">>>>>>> feature", content)
        self.assertIn("Main content", content)
        self.assertIn("Feature content", content)

    def test_merge_nonexistent_branch(self):
        """Test merge with non-existent branch."""
        init()

        # Create initial commit
        with open("test.txt", "w") as f:
            f.write("Test")
        add(["test.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

        # Try to merge non-existent branch
        with pytest.raises(UgitError):
            merge("nonexistent")

    def test_merge_into_same_branch(self):
        """Test merge branch into itself."""
        init()

        # Create initial commit
        with open("test.txt", "w") as f:
            f.write("Test")
        add(["test.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

        # Create branch and switch to it
        branch("feature")
        checkout("feature")

        # Try to merge branch into itself
        with pytest.raises(UgitError):
            merge("feature")

    def test_merge_when_not_on_branch(self):
        """Test merge when HEAD is detached."""
        init()

        # Create initial commit
        with open("test.txt", "w") as f:
            f.write("Test")
        add(["test.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

        # Get commit SHA and checkout directly (detached HEAD)
        repo = Repository()
        commit_sha = repo.get_head_ref()

        checkout(commit_sha)  # Detached HEAD

        # Create branch to merge
        branch("feature")

        # Try to merge while detached
        with pytest.raises(UgitError):
            merge("feature")

    def test_merge_preserves_history(self):
        """Test that merge commits preserve both parent histories."""
        init()

        # Create initial commit
        with open("base.txt", "w") as f:
            f.write("Base")
        add(["base.txt"])
        commit("Base commit", "Test Author <test@example.com>")

        # Create feature branch
        branch("feature")
        checkout("feature")

        with open("feature.txt", "w") as f:
            f.write("Feature")
        add(["feature.txt"])
        commit("Feature commit", "Test Author <test@example.com>")

        # Switch to main and add commit
        checkout("main")

        with open("main.txt", "w") as f:
            f.write("Main")
        add(["main.txt"])
        commit("Main commit", "Test Author <test@example.com>")

        # Merge feature
        merge("feature")

        # Verify all files are present
        self.assertTrue(os.path.exists("base.txt"))
        self.assertTrue(os.path.exists("feature.txt"))
        self.assertTrue(os.path.exists("main.txt"))


if __name__ == "__main__":
    unittest.main()
