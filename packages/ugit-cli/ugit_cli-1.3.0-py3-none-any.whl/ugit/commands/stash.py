"""
Stash command implementation for ugit.

This module handles stashing and restoring changes.
"""

import json
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from ..core.checkout import clear_working_directory
from ..core.objects import get_object, hash_object
from ..core.repository import Index, Repository
from ..utils.helpers import (
    ensure_repository,
    get_current_branch_name,
    get_ignored_patterns,
    should_ignore_file,
)


def stash(message: Optional[str] = None, include_untracked: bool = False) -> None:
    """
    Stash current changes in working directory and staging area.

    Args:
        message: Optional message for the stash
        include_untracked: Include untracked files in stash
    """
    repo = ensure_repository()

    # Check if there are changes to stash
    staged_files = _get_staged_files(repo)
    working_changes = _get_working_changes(repo, include_untracked)

    if not staged_files and not working_changes:
        print("No changes to stash")
        return

    # Create stash entry
    current_branch = get_current_branch_name(repo) or "detached HEAD"
    stash_data = {
        "message": message
        or f"WIP on {current_branch}: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "timestamp": time.time(),
        "staged_files": staged_files,
        "working_changes": working_changes,
        "parent_commit": repo.get_head_ref(),
    }

    # Save stash
    _save_stash(repo, stash_data)

    # Clear working directory and staging area
    clear_working_directory()
    _clear_staging_area(repo)

    print(f"Saved working directory and index state: {stash_data['message']}")


def stash_pop(stash_id: int = 0) -> None:
    """
    Apply most recent stash and remove it from stash list.

    Args:
        stash_id: Index of stash to pop (0 = most recent)
    """
    repo = ensure_repository()

    stash_data = _get_stash(repo, stash_id)
    if not stash_data:
        print(f"No stash found at index {stash_id}")
        return

    # Apply the stash
    _apply_stash_data(repo, stash_data)

    # Remove from stash list
    _remove_stash(repo, stash_id)

    print(f"Applied stash: {stash_data['message']}")


def stash_apply(stash_id: int = 0) -> None:
    """
    Apply stash without removing it from stash list.

    Args:
        stash_id: Index of stash to apply (0 = most recent)
    """
    repo = ensure_repository()

    stash_data = _get_stash(repo, stash_id)
    if not stash_data:
        print(f"No stash found at index {stash_id}")
        return

    _apply_stash_data(repo, stash_data)
    print(f"Applied stash: {stash_data['message']}")


def stash_list() -> None:
    """List all stashes."""
    repo = ensure_repository()

    stashes = _get_all_stashes(repo)
    if not stashes:
        print("No stashes found")
        return

    for i, stash_data in enumerate(stashes):
        timestamp = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(stash_data["timestamp"])
        )
        print(f"stash@{{{i}}}: {stash_data['message']} ({timestamp})")


def stash_drop(stash_id: int = 0) -> None:
    """
    Remove a stash without applying it.

    Args:
        stash_id: Index of stash to drop (0 = most recent)
    """
    repo = ensure_repository()

    stash_data = _get_stash(repo, stash_id)
    if not stash_data:
        print(f"No stash found at index {stash_id}")
        return

    _remove_stash(repo, stash_id)
    print(f"Dropped stash: {stash_data['message']}")


def stash_clear() -> None:
    """Remove all stashes."""
    repo = ensure_repository()

    stash_file = os.path.join(repo.ugit_dir, "stash")
    if os.path.exists(stash_file):
        os.remove(stash_file)
        print("Cleared all stashes")
    else:
        print("No stashes to clear")


def _get_staged_files(repo: Repository) -> Dict[str, Tuple[str, float, int]]:
    """Get all currently staged files."""
    return Index(repo).read()


def _get_working_changes(
    repo: Repository, include_untracked: bool = False
) -> Dict[str, str]:
    """Get all working directory changes."""
    ignored_patterns = get_ignored_patterns(repo.path)
    working_changes = {}

    # Get staged files for comparison
    staged_files = _get_staged_files(repo)

    for root, dirs, files in os.walk(repo.path):
        # Skip .ugit directory
        if ".ugit" in dirs:
            dirs.remove(".ugit")

        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, repo.path)

            # Skip ignored files
            if should_ignore_file(rel_path, ignored_patterns):
                continue

            try:
                with open(file_path, "rb") as f:
                    content = f.read()

                current_sha = hash_object(content, "blob", write=False)
                staged_entry = staged_files.get(rel_path)
                staged_sha = staged_entry[0] if staged_entry else None

                # Include if modified or untracked and include_untracked is True
                if staged_sha != current_sha:
                    if staged_sha or include_untracked:
                        working_changes[rel_path] = current_sha
                        # Actually store the content for later restoration
                        hash_object(content, "blob", write=True)

            except (IOError, OSError, UnicodeDecodeError):
                pass

    return working_changes


def _save_stash(repo: Repository, stash_data: Dict) -> str:
    """Save stash data to disk."""
    stash_file = os.path.join(repo.ugit_dir, "stash")
    stashes = []

    # Load existing stashes
    if os.path.exists(stash_file):
        try:
            with open(stash_file, "r", encoding="utf-8") as f:
                stashes = json.load(f)
        except (json.JSONDecodeError, IOError):
            stashes = []

    # Add new stash at the beginning (most recent first)
    stashes.insert(0, stash_data)

    # Save back to file
    with open(stash_file, "w", encoding="utf-8") as f:
        json.dump(stashes, f, indent=2)

    return "stash@{0}"


def _get_stash(repo: Repository, stash_id: int) -> Optional[Dict]:
    """Get a specific stash by ID."""
    stashes = _get_all_stashes(repo)
    if 0 <= stash_id < len(stashes):
        return stashes[stash_id]
    return None


def _get_all_stashes(repo: Repository) -> List[Dict[str, Any]]:
    """Get all stashes."""
    stash_file = os.path.join(repo.ugit_dir, "stash")

    if not os.path.exists(stash_file):
        return []

    try:
        with open(stash_file, "r", encoding="utf-8") as f:
            result = json.load(f)
            return result if isinstance(result, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def _apply_stash_data(repo: Repository, stash_data: Dict) -> None:
    """Apply stash data to working directory and staging area."""
    index = Index(repo)

    # Restore staged files
    if stash_data["staged_files"]:
        index.write(stash_data["staged_files"])

        # Also restore to working directory
        for file_path, (sha, _, _) in stash_data["staged_files"].items():
            try:
                obj_type, content = get_object(sha)
                if obj_type == "blob":
                    # Create directory if needed
                    dir_path = os.path.dirname(file_path)
                    if dir_path:
                        os.makedirs(dir_path, exist_ok=True)

                    # Write file
                    with open(file_path, "wb") as f_out:
                        f_out.write(content)
            except (FileNotFoundError, IOError):
                sys.stderr.write(
                    f"Warning: Could not restore staged file {file_path}\n"
                )

    # Restore working directory files
    for file_path, sha in stash_data["working_changes"].items():
        try:
            obj_type, content = get_object(sha)
            if obj_type == "blob":
                # Create directory if needed
                dir_path = os.path.dirname(file_path)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)

                # Write file
                with open(file_path, "wb") as f:
                    f.write(content)
        except (FileNotFoundError, IOError):
            sys.stderr.write(f"Warning: Could not restore {file_path}\n")


def _remove_stash(repo: Repository, stash_id: int) -> None:
    """Remove a stash from the list."""
    stashes = _get_all_stashes(repo)

    if 0 <= stash_id < len(stashes):
        stashes.pop(stash_id)

        stash_file = os.path.join(repo.ugit_dir, "stash")
        if stashes:
            with open(stash_file, "w", encoding="utf-8") as f:
                json.dump(stashes, f, indent=2)
        else:
            os.remove(stash_file)


def _clear_staging_area(repo: Repository) -> None:
    """Clear the staging area."""
    index_path = os.path.join(repo.ugit_dir, "index")
    if os.path.exists(index_path):
        os.remove(index_path)
