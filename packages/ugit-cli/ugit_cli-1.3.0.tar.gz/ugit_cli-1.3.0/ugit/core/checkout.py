"""
Core checkout functionality for ugit.
"""

import os
import shutil
import sys
from typing import TYPE_CHECKING

from ..utils.helpers import get_commit_data, get_tree_entries
from .objects import get_object

if TYPE_CHECKING:
    from .repository import Repository


def checkout_commit(
    repo: "Repository", commit_sha: str, update_head: bool = True
) -> None:
    """Checkout files from a specific commit."""
    try:
        clear_working_directory()
        commit = get_commit_data(commit_sha, repo=repo)
        tree_sha = commit.get("tree")
        if tree_sha:
            checkout_tree(repo, tree_sha, ".")

        if update_head:
            head_path = os.path.join(repo.ugit_dir, "HEAD")
            with open(head_path, "w", encoding="utf-8") as f:
                f.write(commit_sha)
            print(f"Checked out commit {commit_sha[:7]}")

    except (ValueError, FileNotFoundError) as e:
        print(f"Error checking out commit {commit_sha}: {e}", file=sys.stderr)


def checkout_tree(repo: "Repository", tree_sha: str, path: str) -> None:
    """Recursively checkout a tree object."""
    try:
        entries = get_tree_entries(tree_sha, repo=repo)
        for mode, name, sha in entries:
            entry_path = os.path.join(path, name)
            if mode.startswith("10"):  # File
                dirname = os.path.dirname(entry_path)
                if dirname:
                    os.makedirs(dirname, exist_ok=True)
                type_, content = get_object(sha, repo=repo)
                with open(entry_path, "wb") as f:
                    f.write(content)
            elif mode.startswith("40"):  # Directory
                os.makedirs(entry_path, exist_ok=True)
                checkout_tree(repo, sha, entry_path)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error checking out tree {tree_sha}: {e}", file=sys.stderr)


def clear_working_directory() -> None:
    """Clear working directory of all files and directories, except .ugit."""
    for entry in os.listdir("."):
        if entry == ".ugit":
            continue
        path = os.path.join(".", entry)
        if os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass
        elif os.path.isdir(path):
            try:
                shutil.rmtree(path)
            except OSError:
                pass
