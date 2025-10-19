"""
Pull changes from remote repositories.

This module handles fetching and merging changes from remote repositories.
"""

import os
import sys
from typing import Optional

from ..core.checkout import checkout_commit
from ..core.repository import Repository
from ..utils.helpers import get_current_branch_name, is_ancestor
from .fetch import fetch


def pull(remote_name: str = "origin", branch: Optional[str] = None) -> int:
    """
    Fetch and merge changes from a remote repository.

    Args:
        remote_name: Name of remote to pull from
        branch: Specific branch to pull (optional)

    Returns:
        0 on success, 1 on error
    """
    repo = Repository()

    if not repo.is_repository():
        print("Not a ugit repository")
        return 1

    # Get current branch
    current_branch = get_current_branch_name(repo)
    if not current_branch:
        print("fatal: You are not currently on a branch", file=sys.stderr)
        return 1

    # Use current branch if no branch specified
    if branch is None:
        branch = current_branch

    print(f"Pulling {remote_name}/{branch} into {current_branch}")

    # First, fetch the changes
    fetch_result = fetch(remote_name, branch)
    if fetch_result != 0:
        return fetch_result

    # Get the remote ref
    remote_ref_path = os.path.join(
        repo.ugit_dir, "refs", "remotes", remote_name, branch
    )
    if not os.path.exists(remote_ref_path):
        print(
            f"fatal: Couldn't find remote ref {remote_name}/{branch}", file=sys.stderr
        )
        return 1

    try:
        with open(remote_ref_path, "r") as f:
            remote_sha = f.read().strip()
    except (IOError, OSError) as e:
        print(f"fatal: Failed to read remote ref: {e}", file=sys.stderr)
        return 1

    # Get current HEAD
    current_sha = repo.get_head_ref()
    if not current_sha:
        print("fatal: No commits in current branch", file=sys.stderr)
        return 1

    # Check if we're already up to date
    if current_sha == remote_sha:
        print("Already up to date.")
        return 0

    # Check if this is a fast-forward merge
    if is_ancestor(repo, current_sha, remote_sha):
        # This is a fast-forward merge
        print("Fast-forwarding...")
        _fast_forward_merge(repo, current_branch, remote_sha)
        print("Fast-forward merge completed.")
        return 0
    else:
        # The remote has diverged. For simplicity, we'll just fail.
        print(
            "Error: Your local branch has diverged from the remote branch.",
            file=sys.stderr,
        )
        print(
            "hint: A three-way merge is required, which is not yet supported by this simplified pull command."
        )
        print("hint: You can try to merge manually:")
        print(f"hint: ugit merge {remote_name}/{branch}")
        return 1


def _get_current_branch(repo: Repository) -> Optional[str]:
    """
    Get the name of the current branch.

    Args:
        repo: Repository instance

    Returns:
        Current branch name or None if detached HEAD
    """
    head_path = os.path.join(repo.ugit_dir, "HEAD")
    if not os.path.exists(head_path):
        return None

    try:
        with open(head_path, "r") as f:
            head_content = f.read().strip()

        if head_content.startswith("ref: refs/heads/"):
            return head_content[16:]  # Remove "ref: refs/heads/"

        return None  # Detached HEAD
    except (IOError, OSError):
        return None


def _fast_forward_merge(repo: Repository, branch: str, target_sha: str) -> None:
    """
    Perform a fast-forward merge.

    Args:
        repo: Repository instance
        branch: Current branch name
        target_sha: Target commit SHA
    """
    # Update branch ref
    branch_path = os.path.join(repo.ugit_dir, "refs", "heads", branch)
    try:
        with open(branch_path, "w") as f:
            f.write(target_sha)
    except (IOError, OSError) as e:
        raise RuntimeError(f"Failed to update branch {branch}: {e}")

    # Checkout the new commit
    checkout_commit(repo, target_sha)
