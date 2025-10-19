"""
Fetch objects and refs from remote repositories.

This module handles fetching changes from remote repositories without merging them.
"""

import os
import shutil
import sys
from typing import Dict, Optional, Set

from ..core.objects import get_object, object_exists
from ..core.repository import Repository
from ..utils.helpers import is_local_path
from .remote import get_remote_url


def fetch(remote_name: str = "origin", branch: Optional[str] = None) -> int:
    """
    Fetch objects and refs from a remote repository.

    Args:
        remote_name: Name of remote to fetch from
        branch: Specific branch to fetch (optional)

    Returns:
        0 on success, 1 on error
    """
    repo = Repository()

    if not repo.is_repository():
        print("Not a ugit repository")
        return 1

    # Get remote URL
    remote_url = get_remote_url(remote_name)
    if not remote_url:
        print(
            f"fatal: '{remote_name}' does not appear to be a ugit repository",
            file=sys.stderr,
        )
        return 1

    print(f"From {remote_url}")

    try:
        if is_local_path(remote_url):
            _fetch_local(repo, remote_name, remote_url, branch)
        else:
            print(
                f"fatal: remote protocols not yet supported: {remote_url}",
                file=sys.stderr,
            )
            return 1

    except Exception as e:
        print(f"fatal: failed to fetch from '{remote_name}': {e}", file=sys.stderr)
        return 1

    return 0


def _fetch_local(
    repo: Repository, remote_name: str, remote_url: str, branch: Optional[str]
) -> None:
    """
    Fetch from a local repository.

    Args:
        repo: Local repository
        remote_name: Remote name
        remote_url: Remote repository path
        branch: Specific branch to fetch
    """
    # Check if remote repository exists
    remote_ugit_dir = os.path.join(remote_url, ".ugit")
    if not os.path.exists(remote_ugit_dir):
        raise ValueError(f"not a ugit repository: {remote_url}")

    # Get remote refs
    remote_refs = _get_remote_refs(remote_url, branch)
    if not remote_refs:
        print("No refs to fetch")
        return

    # Ensure remote refs directory exists
    local_remote_refs_dir = os.path.join(repo.ugit_dir, "refs", "remotes", remote_name)
    os.makedirs(local_remote_refs_dir, exist_ok=True)

    # Track what we need to fetch
    commits_to_fetch = set()
    any_changes = False

    for branch_name, commit_sha in remote_refs.items():
        # Check if we need to fetch this commit
        if not object_exists(commit_sha, repo=repo):
            commits_to_fetch.add(commit_sha)

        # Update local remote ref
        local_remote_ref_path = os.path.join(local_remote_refs_dir, branch_name)

        # Check if ref changed
        old_sha = None
        if os.path.exists(local_remote_ref_path):
            try:
                with open(local_remote_ref_path, "r") as f:
                    old_sha = f.read().strip()
            except (IOError, OSError):
                pass

        if old_sha != commit_sha:
            any_changes = True
            # Write new ref
            with open(local_remote_ref_path, "w") as f:
                f.write(commit_sha)

            # Show update status
            if old_sha:
                print(f" * {old_sha[:8]}..{commit_sha[:8]} {remote_name}/{branch_name}")
            else:
                print(
                    f" * [new branch] {remote_name}/{branch_name} -> {remote_name}/{branch_name}"
                )

    # If no changes, say so
    if not any_changes:
        print("No refs to fetch")
        return

    # Fetch missing objects
    if commits_to_fetch:
        _fetch_objects(repo, remote_url, commits_to_fetch)


def _get_remote_refs(
    remote_url: str, branch_filter: Optional[str] = None
) -> Dict[str, str]:
    """
    Get refs from remote repository.

    Args:
        remote_url: Remote repository path
        branch_filter: Only fetch this branch if specified

    Returns:
        Dictionary of branch names to commit SHAs
    """
    refs: Dict[str, str] = {}
    remote_heads_dir = os.path.join(remote_url, ".ugit", "refs", "heads")

    if not os.path.exists(remote_heads_dir):
        return refs

    for branch_file in os.listdir(remote_heads_dir):
        if branch_filter and branch_file != branch_filter:
            continue

        branch_path = os.path.join(remote_heads_dir, branch_file)
        if os.path.isfile(branch_path):
            try:
                with open(branch_path, "r") as f:
                    commit_sha = f.read().strip()
                    if len(commit_sha) == 40:  # Valid SHA
                        refs[branch_file] = commit_sha
            except (IOError, OSError):
                continue

    return refs


def _fetch_objects(repo: Repository, remote_url: str, commits: Set[str]) -> None:
    """
    Fetch all objects needed for the given commits.

    Args:
        repo: Local repository
        remote_url: Remote repository path
        commits: Set of commit SHAs to fetch
    """
    remote_objects_dir = os.path.join(remote_url, ".ugit", "objects")
    local_objects_dir = os.path.join(repo.ugit_dir, "objects")

    # Track all objects we need to fetch
    objects_to_fetch = set(commits)
    fetched_objects = set()

    while objects_to_fetch:
        sha = objects_to_fetch.pop()

        if sha in fetched_objects or object_exists(sha, repo=repo):
            continue

        # Copy object from remote
        if _copy_object(remote_objects_dir, local_objects_dir, sha):
            fetched_objects.add(sha)

            # Find dependencies of this object
            try:
                obj_type, obj_content = get_object(sha, repo=repo)

                if obj_type == "commit":
                    # Parse JSON commit to find tree and parents
                    import json

                    commit_data = json.loads(obj_content.decode("utf-8"))

                    if "tree" in commit_data:
                        objects_to_fetch.add(commit_data["tree"])

                    if "parent" in commit_data:
                        parent = commit_data["parent"]
                        # Only fetch if it's a real parent SHA (not a ref)
                        if not parent.startswith("ref: refs/heads/"):
                            objects_to_fetch.add(parent)

                elif obj_type == "tree":
                    # Parse JSON tree to find blobs and subtrees
                    import json

                    tree_data = json.loads(obj_content.decode("utf-8"))

                    # Tree is a list of [filename, sha] pairs
                    for entry in tree_data:
                        if len(entry) >= 2:
                            objects_to_fetch.add(entry[1])

            except (ValueError, IndexError, UnicodeDecodeError):
                # If we can't parse the object, that's ok - skip it
                continue


def _copy_object(remote_objects_dir: str, local_objects_dir: str, sha: str) -> bool:
    """
    Copy an object from remote to local repository.

    Args:
        remote_objects_dir: Remote objects directory
        local_objects_dir: Local objects directory
        sha: Object SHA to copy

    Returns:
        True if object was copied successfully
    """
    # Try both old flat and new hierarchical formats
    remote_paths = [
        os.path.join(remote_objects_dir, sha),  # Old flat
        os.path.join(remote_objects_dir, sha[:2], sha[2:]),  # New hierarchical
    ]

    for remote_path in remote_paths:
        if os.path.exists(remote_path):
            # Copy to hierarchical format in local
            local_dir = os.path.join(local_objects_dir, sha[:2])
            local_path = os.path.join(local_dir, sha[2:])

            os.makedirs(local_dir, exist_ok=True)

            try:
                shutil.copy2(remote_path, local_path)
                return True
            except (IOError, OSError):
                continue

    return False
