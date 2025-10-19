"""
Branch command implementation for ugit.

This module handles branch creation, listing, switching, and deletion.
"""

import os
from typing import Optional

from ..core.exceptions import BranchExistsError, BranchNotFoundError
from ..core.repository import Repository
from ..utils.helpers import ensure_repository, get_current_branch_name


def branch(
    branch_name: Optional[str] = None,
    list_branches: bool = False,
    delete: Optional[str] = None,
    create: bool = False,
) -> None:
    """
    Handle branch operations.

    Args:
        branch_name: Name of branch to create or switch to
        list_branches: List all branches
        delete: Branch name to delete
        create: Create new branch
    """
    repo = ensure_repository()

    if list_branches:
        _list_branches(repo)
    elif delete:
        _delete_branch(repo, delete)
    elif create and branch_name:
        _create_branch(repo, branch_name)
    elif branch_name:
        _create_branch(repo, branch_name)
    else:
        _list_branches(repo)


def _list_branches(repo: Repository) -> None:
    """List all branches."""
    heads_dir = os.path.join(repo.ugit_dir, "refs", "heads")
    current_branch = get_current_branch_name(repo)
    if os.path.exists(heads_dir):
        for branch_name in sorted(os.listdir(heads_dir)):
            if branch_name == current_branch:
                print(f"* {branch_name}")
            else:
                print(f"  {branch_name}")


def _create_branch(repo: Repository, branch_name: str) -> None:
    """Create a new branch."""
    if not _is_valid_branch_name(branch_name):
        raise ValueError(f"Invalid branch name: '{branch_name}'")

    branch_path = os.path.join(repo.ugit_dir, "refs", "heads", branch_name)
    if os.path.exists(branch_path):
        raise BranchExistsError(f"Branch '{branch_name}' already exists")

    current_commit = repo.get_head_ref()
    if not current_commit:
        raise ValueError("No commits yet - cannot create branch")

    os.makedirs(os.path.dirname(branch_path), exist_ok=True)
    with open(branch_path, "w", encoding="utf-8") as f:
        f.write(current_commit)
    print(f"Created branch '{branch_name}'")


def _delete_branch(repo: Repository, branch_name: str) -> None:
    """Delete a branch."""
    current_branch = get_current_branch_name(repo)

    if branch_name == current_branch:
        raise ValueError(f"Cannot delete current branch '{branch_name}'")

    branch_path = os.path.join(repo.ugit_dir, "refs", "heads", branch_name)

    if not os.path.exists(branch_path):
        raise BranchNotFoundError(f"Branch '{branch_name}' does not exist")

    os.remove(branch_path)
    print(f"Deleted branch '{branch_name}'")


def _is_valid_branch_name(name: str) -> bool:
    """Check if branch name is valid."""
    if not name or name.strip() != name:
        return False

    # Basic validation - no spaces, no special characters that cause issues
    invalid_chars = [" ", "\t", "\n", "..", "~", "^", ":", "?", "*", "[", "\\]"]
    for char in invalid_chars:
        if char in name:
            return False

    # Cannot start with . or -
    if name.startswith(".") or name.startswith("-"):
        return False

    return True
