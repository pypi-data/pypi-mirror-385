"""Tests for core object storage functionality."""

import os
import tempfile

from ugit.core.objects import get_object, hash_object, object_exists


class TestObjectStorage:
    """Test object storage operations."""

    def test_hash_object_blob_without_writing(self):
        """Test hashing a blob without writing to disk."""
        data = b"hello world"
        sha = hash_object(data, "blob", write=False)

        # Should be 40-character SHA-1 hash
        assert len(sha) == 40
        assert isinstance(sha, str)

        # Should be deterministic
        sha2 = hash_object(data, "blob", write=False)
        assert sha == sha2

    def test_hash_object_with_writing(self):
        """Test hashing and writing object to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            # Create .ugit directory structure
            os.makedirs(".ugit/objects", exist_ok=True)

            try:
                data = b"test content"
                sha = hash_object(data, "blob", write=True)

                # Object file should exist
                assert object_exists(sha)

                # Should be able to retrieve the object
                obj_type, content = get_object(sha)
                assert obj_type == "blob"
                assert content == data

            finally:
                os.chdir(old_cwd)

    def test_get_object_nonexistent(self):
        """Test retrieving non-existent object raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Should raise FileNotFoundError for non-existent object
                import pytest

                with pytest.raises(FileNotFoundError):
                    get_object("1234567890abcdef1234567890abcdef12345678")

            except ImportError:
                # If pytest not available, check manually
                try:
                    get_object("1234567890abcdef1234567890abcdef12345678")
                    assert False, "Should have raised FileNotFoundError"
                except FileNotFoundError:
                    pass
            finally:
                os.chdir(old_cwd)

    def test_object_exists(self):
        """Test object existence checking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            os.makedirs(".ugit/objects", exist_ok=True)

            try:
                # Non-existent object
                assert not object_exists("nonexistent")

                # Create and check existing object
                data = b"test"
                sha = hash_object(data, "blob", write=True)
                assert object_exists(sha)

            finally:
                os.chdir(old_cwd)


def test_different_object_types():
    """Test hashing different object types produces different hashes."""
    data = b"same content"

    blob_sha = hash_object(data, "blob", write=False)
    tree_sha = hash_object(data, "tree", write=False)
    commit_sha = hash_object(data, "commit", write=False)

    # Different types should produce different hashes
    assert blob_sha != tree_sha
    assert blob_sha != commit_sha
    assert tree_sha != commit_sha
