"""
Create commits from staged changes.
"""

import json
import os
import sys
from datetime import datetime
from typing import Optional

from ..core.objects import hash_object
from ..core.repository import Index, Repository
from ..utils.config import Config
from ..utils.helpers import ensure_repository


def commit(message: str, author: Optional[str] = None) -> None:
    """
    Create a commit from staged changes.

    Args:
        message: Commit message
        author: Author information (uses config if not provided)
    """
    repo = ensure_repository()

    if not message.strip():
        print("Error: Commit message cannot be empty")
        return

    # Get author from config if not provided
    if author is None:
        config = Config(repo.path)
        author = config.get_author_string()

    # Create tree from current index
    tree_sha = _write_tree(repo)
    if not tree_sha:
        print("Nothing to commit")
        return

    # Get parent commit
    parent = repo.get_head_ref()

    # Create commit object
    commit_data = {
        "tree": tree_sha,
        "parent": parent,
        "author": author,
        "timestamp": datetime.now().isoformat(),
        "message": message.strip(),
    }

    commit_bytes = json.dumps(commit_data, indent=2).encode()
    commit_sha = hash_object(commit_bytes, "commit")

    # Update current branch pointer
    _update_current_branch(repo, commit_sha)

    print(f"Committed {commit_sha[:7]} - {message}")


def _write_tree(repo: Repository) -> Optional[str]:
    """
    Create a tree object from the current index.

    Args:
        repo: Repository instance

    Returns:
        SHA of the tree object, or None if index is empty
    """
    index = Index(repo)
    index_data = index.read()

    if not index_data:
        return None

    # Convert index to tree entries (sorted for consistency)
    tree_entries = []
    for path, (sha, _, _) in sorted(index_data.items()):
        tree_entries.append([path, sha])  # Use list for JSON serialization

    tree_data = json.dumps(tree_entries, indent=2).encode()
    return hash_object(tree_data, "tree")


def _update_current_branch(repo: Repository, commit_sha: str) -> None:
    """Update the current branch to point to the new commit."""
    head_path = os.path.join(repo.ugit_dir, "HEAD")

    if not os.path.exists(head_path):
        # No HEAD file, default to main
        repo.set_head_ref(commit_sha, "main")
        return

    try:
        with open(head_path, "r", encoding="utf-8") as f:
            head_content = f.read().strip()

        if head_content.startswith("ref: refs/heads/"):
            # We're on a branch, update that branch
            branch_name = head_content[16:]  # Remove "ref: refs/heads/" prefix
            repo.set_head_ref(commit_sha, branch_name)
        else:
            # Detached HEAD, just update the HEAD file directly
            with open(head_path, "w", encoding="utf-8") as f:
                f.write(commit_sha)

    except (IOError, OSError) as e:
        sys.stderr.write(f"Error updating branch: {e}\n")
        # Fallback to updating main
        repo.set_head_ref(commit_sha, "main")
