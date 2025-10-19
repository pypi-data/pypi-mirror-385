"""
Integration tests for ugit functionality.
"""

import os
import shutil
import tempfile
from unittest import TestCase

from ugit.commands.add import add
from ugit.commands.branch import branch
from ugit.commands.checkout import checkout
from ugit.commands.commit import commit
from ugit.commands.config import config
from ugit.commands.diff import diff
from ugit.commands.init import init
from ugit.commands.stash import stash, stash_pop
from ugit.core.exceptions import InvalidRefError, NotInRepositoryError


class TestUgitIntegration(TestCase):
    """Integration tests for ugit workflow."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        init()
        config("user.name", "Test User")
        config("user.email", "test@example.com")

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_complete_workflow(self):
        """Test a complete ugit workflow."""
        # Create initial file and commit
        with open("README.md", "w") as f:
            f.write("# My Project\n\nThis is a test project.")

        add(["README.md"])
        commit("Initial commit")

        # Create a feature branch
        branch("feature/add-docs")
        checkout("feature/add-docs")

        # Add documentation
        with open("docs.md", "w") as f:
            f.write("# Documentation\n\nThis is the documentation.")

        add(["docs.md"])
        commit("Add documentation")

        # Switch back to main branch (assuming it exists)
        checkout("main")

        # Make changes on main
        with open("README.md", "w") as f:
            f.write(
                "# My Project\n\nThis is a test project.\n\nUpdated on main branch."
            )

        add(["README.md"])
        commit("Update README on main")

        # Test stash functionality
        with open("temp.txt", "w") as f:
            f.write("Temporary changes")

        stash("Temporary work")
        stash_pop()

        # Test diff functionality
        diff()

    def test_ignore_functionality(self):
        """Test .ugitignore functionality."""
        # Create .ugitignore
        with open(".ugitignore", "w") as f:
            f.write("*.tmp\n__pycache__/\n*.log")

        # Create files (some should be ignored)
        with open("important.txt", "w") as f:
            f.write("Important file")

        with open("temp.tmp", "w") as f:
            f.write("Temporary file")

        os.makedirs("__pycache__", exist_ok=True)
        with open("__pycache__/cache.py", "w") as f:
            f.write("# Cache file")

        with open("app.log", "w") as f:
            f.write("Log entry")

        # Add all files - should respect ignore patterns
        add(["."])

        commit("Initial commit with ignores")

    def test_error_handling(self):
        """Test error handling for invalid operations."""
        # Initialize a separate directory for this test to avoid conflicts
        error_dir = tempfile.mkdtemp()
        os.chdir(error_dir)

        # Try operations without a repository
        with self.assertRaises(NotInRepositoryError):
            add(["nonexistent.txt"])

        # Initialize repository
        init()

        # Try to add non-existent file
        add(["nonexistent.txt"])

        # Try to checkout non-existent branch
        with self.assertRaises(InvalidRefError):
            checkout("nonexistent-branch")
