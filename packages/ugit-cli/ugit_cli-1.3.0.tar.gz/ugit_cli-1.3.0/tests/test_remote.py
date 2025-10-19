"""
Tests for remote operations.
"""

import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

from ugit.commands.clone import clone
from ugit.commands.fetch import fetch
from ugit.commands.push import push
from ugit.commands.remote import add_remote, list_remotes, remove_remote, show_remote
from ugit.core.exceptions import UgitError
from ugit.core.repository import Repository
from ugit.utils.config import Config


class TestRemoteOperations(unittest.TestCase):
    """Test remote repository operations."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()

        # Create source repository
        self.source_dir = os.path.join(self.test_dir, "source")
        os.makedirs(self.source_dir)
        os.chdir(self.source_dir)

        # Initialize source repo and add some content
        self._create_test_repo()

        # Create target directory for cloning
        self.target_dir = os.path.join(self.test_dir, "target")

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def _create_test_repo(self):
        """Create a test repository with some content."""
        from ugit.commands.add import add
        from ugit.commands.commit import commit
        from ugit.commands.init import init

        # Initialize repo
        init()

        # Add test file
        with open("test.txt", "w") as f:
            f.write("Hello, World!")

        add(["test.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

        # Add another commit
        with open("test2.txt", "w") as f:
            f.write("Second file")

        add(["test2.txt"])
        commit("Second commit", "Test Author <test@example.com>")

    def test_add_remote(self):
        """Test adding a remote repository."""
        add_remote("origin", "/path/to/repo")

        config = Config()
        url = config.get("remote", "origin.url")
        fetch_spec = config.get("remote", "origin.fetch")

        self.assertEqual(url, "/path/to/repo")
        self.assertEqual(fetch_spec, "+refs/heads/*:refs/remotes/origin/*")

    def test_add_duplicate_remote(self):
        """Test adding a remote that already exists."""
        add_remote("origin", "/path/to/repo")

        with patch("builtins.print") as mock_print:
            add_remote("origin", "/another/path")
            mock_print.assert_called_with("remote origin already exists")

    def test_remove_remote(self):
        """Test removing a remote repository."""
        add_remote("origin", "/path/to/repo")
        remove_remote("origin")

        config = Config()
        url = config.get("remote", "origin.url")
        self.assertIsNone(url)

    def test_remove_nonexistent_remote(self):
        """Test removing a remote that doesn't exist."""
        with patch("builtins.print") as mock_print:
            remove_remote("nonexistent")
            mock_print.assert_called_with("No such remote: nonexistent")

    def test_list_remotes_empty(self):
        """Test listing remotes when none exist."""
        with patch("builtins.print") as mock_print:
            list_remotes()
            mock_print.assert_not_called()

    def test_list_remotes_verbose(self):
        """Test listing remotes with verbose output."""
        add_remote("origin", "/path/to/repo")
        add_remote("upstream", "/path/to/upstream")

        with patch("builtins.print") as mock_print:
            list_remotes(verbose=True)

            # Check that remotes are printed with URLs
            calls = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(
                any("origin" in call and "/path/to/repo" in call for call in calls)
            )
            self.assertTrue(
                any(
                    "upstream" in call and "/path/to/upstream" in call for call in calls
                )
            )

    def test_show_remote(self):
        """Test showing remote details."""
        add_remote("origin", "/path/to/repo")

        with patch("builtins.print") as mock_print:
            show_remote("origin")

            calls = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(any("* remote origin" in call for call in calls))
            self.assertTrue(any("/path/to/repo" in call for call in calls))

    def test_show_nonexistent_remote(self):
        """Test showing details for non-existent remote."""
        with patch("builtins.print") as mock_print:
            show_remote("nonexistent")
            mock_print.assert_called_with("No such remote: nonexistent")


class TestCloneOperations(unittest.TestCase):
    """Test clone operations."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()

        # Create source repository
        self.source_dir = os.path.join(self.test_dir, "source")
        os.makedirs(self.source_dir)
        os.chdir(self.source_dir)

        # Initialize source repo and add some content
        self._create_test_repo()

        # Go back to test dir for cloning
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def _create_test_repo(self):
        """Create a test repository with some content."""
        from ugit.commands.add import add
        from ugit.commands.commit import commit
        from ugit.commands.init import init

        # Initialize repo
        init()

        # Add test file
        with open("test.txt", "w") as f:
            f.write("Hello, World!")

        add(["test.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

    def test_clone_local_repo(self):
        """Test cloning a local repository."""
        clone(self.source_dir, "cloned")

        # Check that directory was created
        self.assertTrue(os.path.exists("cloned"))

        # Check that it's a valid ugit repo
        os.chdir("cloned")
        repo = Repository()
        self.assertTrue(repo.is_repository())

        # Check that files were checked out
        self.assertTrue(os.path.exists("test.txt"))
        with open("test.txt", "r") as f:
            self.assertEqual(f.read(), "Hello, World!")

        # Check that origin remote was added
        config = Config()
        origin_url = config.get("remote", "origin.url")
        self.assertEqual(origin_url, self.source_dir)

    def test_clone_existing_directory(self):
        """Test cloning to an existing directory."""
        os.makedirs("existing")

        with self.assertRaises(UgitError) as context:
            clone(self.source_dir, "existing")
        self.assertIn("already exists", str(context.exception))

    def test_clone_invalid_source(self):
        """Test cloning from invalid source."""
        with self.assertRaises(UgitError) as context:
            clone("/nonexistent/path", "cloned")
        self.assertIn(
            "does not exist or is not a valid ugit repository", str(context.exception)
        )


class TestFetchOperations(unittest.TestCase):
    """Test fetch operations."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()

        # Create source and target repositories
        self.source_dir = os.path.join(self.test_dir, "source")
        os.makedirs(self.source_dir)
        os.chdir(self.source_dir)
        self._create_test_repo()

        # Clone to create target repo
        os.chdir(self.test_dir)
        with patch("sys.exit") as mock_exit:  # Mock sys.exit during clone in setUp
            clone(self.source_dir, "target")
            # If clone exits, it means it failed, so we should not proceed with chdir
            if mock_exit.called:
                raise Exception(
                    "Clone failed in setUp"
                )  # Raise an exception to stop setUp
        self.target_dir = os.path.join(
            self.test_dir, "target"
        )  # Ensure target_dir is set
        os.chdir(self.target_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def _create_test_repo(self):
        """Create a test repository with some content."""
        from ugit.commands.add import add
        from ugit.commands.commit import commit
        from ugit.commands.init import init

        init()

        with open("test.txt", "w") as f:
            f.write("Hello, World!")

        add(["test.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

    def test_fetch_no_changes(self):
        """Test fetching when no changes exist."""
        with patch("builtins.print") as mock_print:
            fetch("origin")
            mock_print.assert_called_with("No refs to fetch")

    def test_fetch_with_new_commits(self):
        """Test fetching when new commits exist."""
        # Add new commit to source
        os.chdir(self.source_dir)
        with open("new_file.txt", "w") as f:
            f.write("New content")

        from ugit.commands.add import add
        from ugit.commands.commit import commit

        add(["new_file.txt"])
        commit("New commit", "Test Author <test@example.com>")

        # Fetch from target
        os.chdir(self.target_dir)
        with patch("builtins.print") as mock_print:
            fetch("origin")

            # Should show fetch progress
            calls = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(any("origin/main" in str(call) for call in calls))

    def test_fetch_nonexistent_remote(self):
        """Test fetching from non-existent remote."""
        with patch("builtins.print") as mock_print:
            result = fetch("nonexistent")
            self.assertEqual(result, 1)
            mock_print.assert_called_with(
                "fatal: 'nonexistent' does not appear to be a ugit repository",
                file=sys.stderr,
            )


class TestPushOperations(unittest.TestCase):
    """Test push operations."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()

        # Create source and target repositories
        self.source_dir = os.path.join(self.test_dir, "source")
        os.makedirs(self.source_dir)
        os.chdir(self.source_dir)
        self._create_test_repo()
        # Create bare target repo
        self.target_dir = os.path.join(self.test_dir, "target")
        os.makedirs(self.target_dir)
        os.chdir(self.target_dir)
        from ugit.commands.init import init

        init()

        # Go back to source and add remote
        os.chdir(self.source_dir)
        add_remote("origin", self.target_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def _create_test_repo(self):
        """Create a test repository with some content."""
        from ugit.commands.add import add
        from ugit.commands.commit import commit
        from ugit.commands.init import init

        init()

        with open("test.txt", "w") as f:
            f.write("Hello, World!")

        add(["test.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

    def test_push_new_branch(self):
        """Test pushing to a new branch."""
        with patch("builtins.print") as mock_print:
            push("origin", "main")

            calls = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(any("[new branch]" in str(call) for call in calls))

    def test_push_nonexistent_remote(self):
        """Test pushing to non-existent remote."""
        with self.assertRaises(UgitError):
            push("nonexistent")


if __name__ == "__main__":
    unittest.main()
