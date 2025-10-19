"""
Merge command implementation for ugit.

This module handles merging branches.
"""

import json
import os
import sys
import time
from typing import Dict, Optional, Set

from ..core.checkout import checkout_commit
from ..core.exceptions import BranchNotFoundError, MergeConflictError, UgitError
from ..core.objects import get_object, hash_object
from ..core.repository import Repository
from ..utils.config import Config
from ..utils.helpers import (
    ensure_repository,
    get_commit_data,
    get_current_branch_name,
    get_tree_entries,
    is_ancestor,
)


def merge(branch_name: str, no_ff: bool = False) -> None:
    """
    Merge a branch into the current branch.

    Args:
        branch_name: Name of branch to merge
        no_ff: Force a merge commit even for fast-forward merges
    """
    repo = ensure_repository()

    # Get current branch
    current_branch = get_current_branch_name(repo)
    if not current_branch:
        raise UgitError("Not on any branch - cannot merge")

    if branch_name == current_branch:
        raise UgitError(f"Cannot merge branch '{branch_name}' into itself")

    # Check if target branch exists
    branch_path = os.path.join(repo.ugit_dir, "refs", "heads", branch_name)
    if not os.path.exists(branch_path):
        raise BranchNotFoundError(f"Branch '{branch_name}' does not exist")

    # Get commit SHAs
    with open(branch_path, "r", encoding="utf-8") as f:
        merge_commit = f.read().strip()

    current_commit = repo.get_head_ref()
    if not current_commit:
        raise UgitError("No current commit to merge into")

    # Check if it's a fast-forward merge
    if is_ancestor(repo, current_commit, merge_commit):
        if no_ff:
            _create_merge_commit(repo, current_commit, merge_commit, branch_name)
        else:
            _fast_forward_merge(repo, merge_commit, branch_name)
    else:
        # Need to create a merge commit
        _three_way_merge(repo, current_commit, merge_commit, branch_name)


def _fast_forward_merge(repo: Repository, target_commit: str, branch_name: str) -> None:
    """Perform a fast-forward merge."""
    # Update current branch to point to target commit
    current_branch = get_current_branch_name(repo)
    if current_branch is None:
        raise UgitError("Not on a branch (detached HEAD)")
    current_branch_path = os.path.join(repo.ugit_dir, "refs", "heads", current_branch)

    with open(current_branch_path, "w", encoding="utf-8") as f:
        f.write(target_commit)

    # Checkout the target commit
    checkout_commit(repo, target_commit)

    print(f"Fast-forward merge of '{branch_name}' into '{current_branch}'")
    print(f"Updated {current_branch} to {target_commit[:7]}")


def _create_merge_commit(
    repo: Repository, parent1: str, parent2: str, branch_name: str
) -> None:
    """Create a merge commit with two parents."""
    current_branch = get_current_branch_name(repo)
    if current_branch is None:
        raise UgitError("Not on a branch (detached HEAD)")

    config = Config(repo.path)
    author = config.get_author_string()

    # Create merge commit
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    commit_data = {
        "tree": _get_commit_tree(repo, parent2),  # Use the merged branch's tree
        "parent": parent1,
        "parent2": parent2,  # Second parent for merge
        "author": author,
        "timestamp": timestamp,
        "message": f"Merge branch '{branch_name}' into {current_branch}",
    }

    commit_json = json.dumps(commit_data, separators=(",", ":")).encode()
    commit_sha = hash_object(commit_json, "commit")

    # Update current branch
    current_branch_path = os.path.join(repo.ugit_dir, "refs", "heads", current_branch)
    with open(current_branch_path, "w", encoding="utf-8") as f:
        f.write(commit_sha)

    # Checkout the merged files
    checkout_commit(repo, parent2, update_head=False)

    print(f"Merge commit created: {commit_sha[:7]}")


def _three_way_merge(
    repo: Repository, current_commit: str, merge_commit: str, branch_name: str
) -> None:
    """Perform a three-way merge."""
    # Find common ancestor
    common_ancestor = _find_common_ancestor(repo, current_commit, merge_commit)

    if not common_ancestor:
        raise UgitError("No common ancestor found - cannot merge")

    # Get file trees for three-way merge
    try:
        ancestor_files = _get_commit_files(repo, common_ancestor)
        current_files = _get_commit_files(repo, current_commit)
        merge_files = _get_commit_files(repo, merge_commit)
    except ValueError as e:
        raise UgitError(f"Error during merge: {e}")

    # Perform merge
    merged_files, conflicts = _merge_files(ancestor_files, current_files, merge_files)

    # Always write merged files to working directory (including conflict markers)
    _write_merged_files(merged_files)

    if conflicts:
        raise MergeConflictError("Merge conflicts detected", conflicts=conflicts)

    # Create merge commit only if no conflicts
    merged_tree_sha = _create_tree_from_files(merged_files)
    _create_merge_commit_with_tree(
        repo, current_commit, merge_commit, branch_name, merged_tree_sha
    )


def _find_common_ancestor(
    repo: Repository, commit1: str, commit2: str
) -> Optional[str]:
    """Find the common ancestor of two commits."""
    # Get all ancestors of commit1
    ancestors1 = _get_all_ancestors(repo, commit1)

    # Walk through ancestors of commit2 until we find one that's also in ancestors1
    current: Optional[str] = commit2
    while current:
        if current in ancestors1:
            return current

        try:
            commit_type, commit_data = get_object(current)
            if commit_type != "commit":
                break

            commit = json.loads(commit_data.decode())
            current = commit.get("parent")
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            break

    return None


def _get_all_ancestors(repo: Repository, commit_sha: str) -> Set[str]:
    """Get all ancestors of a commit."""
    ancestors = set()
    current: Optional[str] = commit_sha

    while current:
        ancestors.add(current)

        try:
            commit_type, commit_data = get_object(current)
            if commit_type != "commit":
                break

            commit = json.loads(commit_data.decode())
            current = commit.get("parent")
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            break

    return ancestors


def _get_commit_files(repo: Repository, commit_sha: str) -> Dict[str, str]:
    """Get all files from a specific commit."""
    try:
        commit = get_commit_data(commit_sha, repo=repo)
        tree_sha = commit["tree"]
        return _get_tree_files(repo, tree_sha)
    except ValueError as e:
        raise ValueError(f"Invalid commit {commit_sha}: {e}")


def _get_tree_files(
    repo: Repository, tree_sha: str, prefix: str = ""
) -> Dict[str, str]:
    """Recursively get all files from a tree object."""
    files = {}
    try:
        entries = get_tree_entries(tree_sha, repo=repo)
        for mode, path, sha in entries:
            full_path = os.path.join(prefix, path) if prefix else path
            if mode.startswith("10"):  # File
                try:
                    type_, content = get_object(sha, repo=repo)
                    if type_ == "blob":
                        files[full_path] = content.decode("utf-8", errors="replace")
                except (FileNotFoundError, ValueError, UnicodeDecodeError):
                    files[full_path] = ""
            elif mode.startswith("40"):  # Tree
                subfiles = _get_tree_files(repo, sha, full_path)
                files.update(subfiles)
    except ValueError as e:
        raise ValueError(f"Invalid tree {tree_sha}: {e}")
    return files


def _merge_files(
    ancestor_files: Dict[str, str],
    current_files: Dict[str, str],
    merge_files: Dict[str, str],
) -> tuple:
    """Perform three-way merge on file contents."""
    all_files = (
        set(ancestor_files.keys()) | set(current_files.keys()) | set(merge_files.keys())
    )
    merged_files = {}
    conflicts = []

    for file_path in all_files:
        ancestor_content = ancestor_files.get(file_path, "")
        current_content = current_files.get(file_path, "")
        merge_content = merge_files.get(file_path, "")

        if current_content == merge_content:
            # No conflict - both sides have same content
            merged_files[file_path] = current_content
        elif ancestor_content == current_content:
            # Current side unchanged, use merge side
            merged_files[file_path] = merge_content
        elif ancestor_content == merge_content:
            # Merge side unchanged, use current side
            merged_files[file_path] = current_content
        else:
            # Both sides changed - conflict
            conflicts.append(file_path)
            merged_files[file_path] = _create_conflict_marker(
                file_path, current_content, merge_content
            )

    return merged_files, conflicts


def _create_conflict_marker(
    file_path: str, current_content: str, merge_content: str
) -> str:
    """Create conflict markers in file content."""
    return f"""<<<<<<< HEAD
{current_content}=======
{merge_content}>>>>>>> feature
"""


def _write_merged_files(merged_files: Dict[str, str]) -> None:
    """Write merged files to working directory."""
    for file_path, content in merged_files.items():
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)


def _create_tree_from_files(files: Dict[str, str]) -> str:
    """Create a tree object from files."""
    tree_data = {}

    for file_path, content in files.items():
        blob_sha = hash_object(content.encode(), "blob")
        tree_data[file_path] = blob_sha

    tree_json = json.dumps(tree_data, separators=(",", ":")).encode()
    return hash_object(tree_json, "tree")


def _create_merge_commit_with_tree(
    repo: Repository, parent1: str, parent2: str, branch_name: str, tree_sha: str
) -> None:
    """Create merge commit with specific tree."""
    current_branch = get_current_branch_name(repo)
    if current_branch is None:
        raise UgitError("Not on a branch (detached HEAD)")

    config = Config(repo.path)
    author = config.get_author_string()

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    commit_data = {
        "tree": tree_sha,
        "parent": parent1,
        "parent2": parent2,
        "author": author,
        "timestamp": timestamp,
        "message": f"Merge branch '{branch_name}' into {current_branch}",
    }

    commit_json = json.dumps(commit_data, separators=(",", ":")).encode()
    commit_sha = hash_object(commit_json, "commit")

    # Update current branch
    current_branch_path = os.path.join(repo.ugit_dir, "refs", "heads", current_branch)
    with open(current_branch_path, "w", encoding="utf-8") as f:
        f.write(commit_sha)

    print(f"Merge completed: {commit_sha[:7]}")


def _get_commit_tree(repo: Repository, commit_sha: str) -> str:
    """Get tree SHA from commit."""
    try:
        commit_type, commit_data = get_object(commit_sha)
        if commit_type != "commit":
            raise ValueError(f"Not a commit: {commit_sha}")

        commit = json.loads(commit_data.decode())
        tree_sha: str = commit["tree"]
        return tree_sha

    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Invalid commit {commit_sha}: {e}")
