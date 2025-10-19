"""
Tests for the Repository and Index classes.
"""

import os
import shutil
import tempfile
import time
import unittest

from ugit.commands.init import init
from ugit.core.repository import Index, Repository


class TestRepository(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_is_repository(self):
        """Test the is_repository method."""
        repo = Repository()
        self.assertFalse(repo.is_repository())
        init()
        self.assertTrue(repo.is_repository())


class TestIndex(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        init()
        self.repo = Repository()
        self.index = Index(self.repo)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_read_empty__index(self):
        """Test reading a non-existent index returns an empty dict."""
        self.assertEqual(self.index.read(), {})

    def test_write_and_read_index(self):
        """Test that writing and reading the index preserves data."""
        # Create some dummy data with the new format
        mtime = time.time()
        size = 123
        index_data = {
            "file1.txt": ("a" * 40, mtime, size),
            "path/to/file2.txt": ("b" * 40, mtime, size + 10),
        }

        # Write and read the data
        self.index.write(index_data)
        read_data = self.index.read()

        # Check that the data is identical
        self.assertEqual(index_data, read_data)

    def test_read_malformed_index(self):
        """Test that reading a malformed index handles errors gracefully."""
        # Write a file with incorrect formatting
        with open(self.index.index_path, "w") as f:
            f.write("invalid line\n")
            f.write("a" * 40 + " just_sha_and_path\n")

        # Reading should return an empty dict and print warnings (not asserted here)
        read_data = self.index.read()
        self.assertEqual(read_data, {})
