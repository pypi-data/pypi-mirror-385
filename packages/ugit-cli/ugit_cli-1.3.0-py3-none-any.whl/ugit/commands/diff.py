"""
Diff command implementation for ugit.

This module handles comparing files between different states:
- Working directory vs staging area
- Staging area vs last commit
- Between two commits
"""

import difflib
import os
import sys
from typing import Dict, Optional

from ..core.objects import get_object
from ..core.repository import Index, Repository
from ..utils.helpers import (
    get_commit_data,
    get_ignored_patterns,
    get_tree_entries,
    should_ignore_file,
)


def diff(
    staged: bool = False, commit1: Optional[str] = None, commit2: Optional[str] = None
) -> None:
    """
    Show differences between files.

    Args:
        staged: Show differences between staging area and last commit
        commit1: First commit to compare (if comparing commits)
        commit2: Second commit to compare (if comparing commits)
    """
    repo = Repository()
    if not repo.is_repository():
        print("Not in a ugit repository")
        return

    if commit1 and commit2:
        _diff_commits(repo, commit1, commit2)
    elif staged:
        _diff_staged(repo)
    else:
        _diff_working_directory(repo)


def _diff_working_directory(repo: Repository) -> None:
    """Show differences between working directory and staging area."""
    # Get staged files
    staged_files = _get_staged_files(repo)

    # Get working directory files
    working_files = _get_working_files(repo)

    # Compare files
    all_files = set(staged_files.keys()) | set(working_files.keys())

    has_changes = False
    for file_path in sorted(all_files):
        staged_content = staged_files.get(file_path, "")
        working_content = working_files.get(file_path, "")

        if staged_content != working_content:
            has_changes = True
            _print_file_diff(
                file_path, staged_content, working_content, "staged", "working"
            )

    if not has_changes:
        print("No changes in working directory")


def _diff_staged(repo: Repository) -> None:
    """Show differences between staging area and last commit."""
    # Get last commit
    head_commit = repo.get_head_ref()
    if not head_commit:
        print("No commits yet")
        return

    # Get committed files
    committed_files = _get_commit_files(repo, head_commit)

    # Get staged files
    staged_files = _get_staged_files(repo)

    # Compare files
    all_files = set(committed_files.keys()) | set(staged_files.keys())

    has_changes = False
    for file_path in sorted(all_files):
        committed_content = committed_files.get(file_path, "")
        staged_content = staged_files.get(file_path, "")

        if committed_content != staged_content:
            has_changes = True
            _print_file_diff(
                file_path, committed_content, staged_content, "committed", "staged"
            )

    if not has_changes:
        print("No changes staged for commit")


def _diff_commits(repo: Repository, commit1: str, commit2: str) -> None:
    """Show differences between two commits."""
    # Get files from both commits
    try:
        files1 = _get_commit_files(repo, commit1)
        files2 = _get_commit_files(repo, commit2)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return

    # Compare files
    all_files = set(files1.keys()) | set(files2.keys())

    has_changes = False
    for file_path in sorted(all_files):
        content1 = files1.get(file_path, "")
        content2 = files2.get(file_path, "")

        if content1 != content2:
            has_changes = True
            _print_file_diff(file_path, content1, content2, commit1[:7], commit2[:7])

    if not has_changes:
        print("No differences between commits")


def _get_staged_files(repo: Repository) -> Dict[str, str]:
    """Get all staged files and their content."""
    index_data = Index(repo).read()
    staged_files: Dict[str, str] = {}

    for path, (sha, _, _) in index_data.items():
        try:
            obj_type, content = get_object(sha)
            if obj_type == "blob":
                staged_files[path] = content.decode("utf-8", errors="replace")
        except (FileNotFoundError, ValueError, UnicodeDecodeError):
            staged_files[path] = ""

    return staged_files


def _get_working_files(repo: Repository) -> Dict[str, str]:
    """Get all working directory files and their content."""
    working_files = {}
    ignored_patterns = get_ignored_patterns(repo.path)

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
                with open(file_path, "r", encoding="utf-8") as f:
                    working_files[rel_path] = f.read()
            except (IOError, OSError, UnicodeDecodeError):
                working_files[rel_path] = ""

    return working_files


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


def _print_file_diff(
    file_path: str, content1: str, content2: str, label1: str, label2: str
) -> None:
    """Print unified diff for a file."""
    lines1 = content1.splitlines(keepends=True)
    lines2 = content2.splitlines(keepends=True)

    diff = difflib.unified_diff(
        lines1,
        lines2,
        fromfile=f"{label1}/{file_path}",
        tofile=f"{label2}/{file_path}",
        lineterm="",
    )

    diff_output = list(diff)
    if diff_output:
        print(f"\n--- {file_path}")
        for line in diff_output:
            if line.startswith("+++") or line.startswith("---"):
                print(line)
            elif line.startswith("@@"):
                print(f"\033[36m{line}\033[0m")  # Cyan
            elif line.startswith("+"):
                print(f"\033[32m{line}\033[0m")  # Green
            elif line.startswith("-"):
                print(f"\033[31m{line}\033[0m")  # Red
            else:
                print(line, end="")
