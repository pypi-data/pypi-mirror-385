"""
Checkout files from a specific commit or switch to a branch.
"""

import os

from ..core.checkout import checkout_commit
from ..core.exceptions import InvalidRefError, UgitError
from ..core.repository import Repository
from ..utils.helpers import ensure_repository


def checkout(target: str, create_branch: bool = False) -> None:
    """
    Checkout files from a specific commit or switch to a branch.

    Args:
        target: Commit SHA or branch name to checkout
        create_branch: Create new branch if target is a branch name
    """
    repo = ensure_repository()

    # Check if target is a branch name
    branch_path = os.path.join(repo.ugit_dir, "refs", "heads", target)

    if os.path.exists(branch_path):
        # It's a branch - switch to it
        _switch_to_branch(repo, target)
    elif create_branch:
        # Create new branch and switch to it
        _create_and_switch_branch(repo, target)
    else:
        # Assume it's a commit SHA, but verify it exists
        from ..core.objects import object_exists

        if not object_exists(target):
            raise InvalidRefError(f"Invalid reference '{target}'")
        checkout_commit(repo, target)


def _switch_to_branch(repo: Repository, branch_name: str) -> None:
    """Switch to an existing branch."""
    branch_path = os.path.join(repo.ugit_dir, "refs", "heads", branch_name)

    # Get the commit that the branch points to
    with open(branch_path, "r", encoding="utf-8") as f:
        commit_sha = f.read().strip()

    # Update HEAD to point to the branch
    head_path = os.path.join(repo.ugit_dir, "HEAD")
    with open(head_path, "w", encoding="utf-8") as f:
        f.write(f"ref: refs/heads/{branch_name}")

    # Checkout the commit without updating HEAD again
    checkout_commit(repo, commit_sha, update_head=False)
    print(f"Switched to branch '{branch_name}'")


def _create_and_switch_branch(repo: Repository, branch_name: str) -> None:
    """Create a new branch and switch to it."""
    # Get current HEAD commit
    current_commit = repo.get_head_ref()
    if not current_commit:
        raise UgitError("No commits yet - cannot create branch")

    # Create refs/heads directory if it doesn't exist
    refs_heads_dir = os.path.join(repo.ugit_dir, "refs", "heads")
    os.makedirs(refs_heads_dir, exist_ok=True)

    # Create branch file pointing to current commit
    branch_path = os.path.join(refs_heads_dir, branch_name)
    with open(branch_path, "w", encoding="utf-8") as f:
        f.write(current_commit)

    # Switch to the new branch
    _switch_to_branch(repo, branch_name)
    print(f"Created and switched to branch '{branch_name}'")
