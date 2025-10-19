"""
Test cases for ugit branch command.
"""

import os
import shutil
import tempfile
from unittest import TestCase

import pytest

from ugit.commands.add import add
from ugit.commands.branch import branch
from ugit.commands.checkout import checkout
from ugit.commands.commit import commit
from ugit.commands.config import config
from ugit.commands.init import init
from ugit.core.exceptions import BranchNotFoundError
from ugit.core.repository import Repository


class TestBranchCommand(TestCase):
    """Test cases for branch functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Initialize repository and create initial commit
        init()
        config("user.name", "Test User")
        config("user.email", "test@ugit.com")
        with open("test.txt", "w") as f:
            f.write("Hello, World!")
        add(["test.txt"])
        commit("Initial commit")

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_create_branch(self):
        """Test creating a new branch."""
        branch("feature-branch")

        # Check that branch was created
        repo = Repository()
        branch_path = os.path.join(repo.ugit_dir, "refs", "heads", "feature-branch")
        self.assertTrue(os.path.exists(branch_path))

    def test_list_branches(self):
        """Test listing branches."""
        # Create some branches
        branch("feature1")
        branch("feature2")
        branch(list_branches=True)  # Should list all branches

    def test_delete_branch(self):
        """Test deleting a branch."""
        # Create a branch
        branch("temp-branch")
        branch(delete="temp-branch")

        # Check that branch was deleted
        repo = Repository()
        branch_path = os.path.join(repo.ugit_dir, "refs", "heads", "temp-branch")
        self.assertFalse(os.path.exists(branch_path))

    def test_delete_nonexistent_branch(self):
        """Test deleting a non-existent branch."""
        with pytest.raises(BranchNotFoundError):
            branch(delete="nonexistent-branch")

    def test_checkout_branch(self):
        """Test switching to a branch."""
        # Create a branch
        branch("test-branch")
        checkout("test-branch")

        # Check that HEAD points to the branch
        repo = Repository()
        head_path = os.path.join(repo.ugit_dir, "HEAD")
        with open(head_path, "r") as f:
            head_content = f.read().strip()

        self.assertEqual(head_content, "ref: refs/heads/test-branch")

    def test_create_and_checkout_branch(self):
        """Test creating and checking out a branch in one operation."""
        checkout("new-branch", create_branch=True)

        # Check that branch exists and is checked out
        repo = Repository()
        branch_path = os.path.join(repo.ugit_dir, "refs", "heads", "new-branch")
        self.assertTrue(os.path.exists(branch_path))

        head_path = os.path.join(repo.ugit_dir, "HEAD")
        with open(head_path, "r") as f:
            head_content = f.read().strip()

        self.assertEqual(head_content, "ref: refs/heads/new-branch")
