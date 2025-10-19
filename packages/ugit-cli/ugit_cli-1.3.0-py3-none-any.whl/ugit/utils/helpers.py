"""Utility functions for ugit."""

import fnmatch
import os
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, cast

if TYPE_CHECKING:
    from ..core.repository import Repository


def find_repository_root(path: str = ".") -> str:
    """
    Find the root of the ugit repository.

    Args:
        path: Starting path to search from

    Returns:
        Path to repository root

    Raises:
        RuntimeError: If not in a repository
    """
    current = os.path.abspath(path)

    while current != os.path.dirname(current):  # Not at filesystem root
        if os.path.exists(os.path.join(current, ".ugit")):
            return current
        current = os.path.dirname(current)

    raise RuntimeError("Not in a ugit repository")


def format_timestamp(timestamp: str) -> str:
    """Format ISO timestamp for display."""
    try:
        from datetime import datetime

        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%a %b %d %H:%M:%S %Y %z")
    except (ValueError, AttributeError):
        return timestamp


def walk_files(
    directory: str = ".", ignore_patterns: Optional[list] = None
) -> Iterator[str]:
    """
    Walk files in directory, respecting ignore patterns.

    Args:
        directory: Directory to walk
        ignore_patterns: Patterns to ignore (defaults to ['.ugit'])

    Yields:
        Relative file paths
    """
    if ignore_patterns is None:
        ignore_patterns = [".ugit"]

    for root, dirs, files in os.walk(directory):
        # Remove ignored directories
        dirs[:] = [
            d
            for d in dirs
            if not any(d.startswith(pattern) for pattern in ignore_patterns)
        ]

        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), directory)
            if not any(file_path.startswith(pattern) for pattern in ignore_patterns):
                yield file_path.replace(os.sep, "/")  # Normalize separators


def safe_read_file(path: str) -> bytes:
    """
    Safely read file contents.

    Args:
        path: File path to read

    Returns:
        File contents as bytes

    Raises:
        FileNotFoundError: If file doesn't exist
        RuntimeError: If file cannot be read
    """
    try:
        with open(path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except (IOError, OSError) as e:
        raise RuntimeError(f"Cannot read file {path}: {e}")


def ensure_repository() -> "Repository":
    """
    Ensure we're in a repository and return Repository instance.

    Returns:
        Repository instance

    Raises:
        NotInRepositoryError: If not in a repository
    """
    from ..core.exceptions import NotInRepositoryError
    from ..core.repository import Repository

    repo = Repository()
    if not repo.is_repository():
        raise NotInRepositoryError()
    return repo


def get_ignored_patterns(repo_path: str = ".") -> list:
    """
    Get ignore patterns from .ugitignore file.

    Args:
        repo_path: Path to repository root

    Returns:
        List of ignore patterns
    """
    patterns = [".ugit"]  # Always ignore .ugit directory
    ignore_file = os.path.join(repo_path, ".ugitignore")

    if os.path.exists(ignore_file):
        try:
            with open(ignore_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except (IOError, OSError):
            pass

    return patterns


def get_commit_data(
    commit_sha: str, repo: Optional["Repository"] = None
) -> Dict[str, Any]:
    """
    Get commit data from SHA.

    Args:
        commit_sha: SHA of the commit
        repo: Repository instance (optional, defaults to current repo)

    Returns:
        Parsed commit data

    Raises:
        ValueError: If not a valid commit
    """
    import json

    from ..core.objects import get_object
    from ..core.repository import Repository

    if repo is None:
        repo = Repository()

    try:
        type_, data = get_object(commit_sha, repo=repo)
        if type_ != "commit":
            raise ValueError(f"Expected commit object, got {type_}")
        try:
            return cast(Dict[str, Any], json.loads(data.decode()))
        except (json.JSONDecodeError, UnicodeDecodeError):
            commit: Dict[str, Any] = {}
            lines = data.decode().splitlines()
            for i, line in enumerate(lines):
                if not line:
                    commit["message"] = "\n".join(lines[i + 1 :])
                    break
                key, value = line.split(" ", 1)
                if key == "tree":
                    commit["tree"] = value
                elif key == "parent":
                    if "parent" in commit:
                        if "parents" not in commit:
                            commit["parents"] = [commit["parent"]]
                        commit["parents"].append(value)
                    else:
                        commit["parent"] = value
                elif key == "author":
                    commit["author"] = value
                elif key == "committer":
                    commit["committer"] = value
            return commit
    except (json.JSONDecodeError, FileNotFoundError) as e:
        raise ValueError(f"Invalid commit {commit_sha}: {e}")


def get_tree_entries(
    tree_sha: str, repo: Optional["Repository"] = None
) -> List[tuple[str, str, str]]:
    """Get entries from a tree object, supporting both JSON and Git binary formats."""
    import json

    from ..core.objects import get_object
    from ..core.repository import Repository

    if repo is None:
        repo = Repository()

    try:
        tree_type, tree_content = get_object(tree_sha, repo=repo)
        if tree_type != "tree":
            raise ValueError(f"Object {tree_sha} is not a tree")

        try:
            # JSON format: list of [path, sha]
            entries_json = json.loads(tree_content.decode())
            entries = []
            for path, sha in entries_json:
                obj_type, _ = get_object(sha, repo=repo)
                mode = "40000" if obj_type == "tree" else "100644"
                entries.append((mode, path, sha))
            return entries
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ValueError(f"Invalid tree format in {tree_sha}") from e
    except (FileNotFoundError, ValueError) as e:
        raise ValueError(f"Invalid tree {tree_sha}: {e}")


def should_ignore_file(file_path: str, ignored_patterns: List[str]) -> bool:
    """Check if a file should be ignored based on patterns."""
    for pattern in ignored_patterns:
        # Check full path and just filename
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(
            os.path.basename(file_path), pattern
        ):
            return True

        # Handle directory patterns (ending with /)
        if pattern.endswith("/"):
            dir_pattern = pattern[:-1]  # Remove trailing slash
            path_parts = file_path.split(os.sep)
            for part in path_parts[:-1]:  # Exclude the filename itself
                if fnmatch.fnmatch(part, dir_pattern):
                    return True
        else:
            # Check if any parent directory matches the pattern
            path_parts = file_path.split(os.sep)
            for part in path_parts[:-1]:  # Exclude the filename itself
                if fnmatch.fnmatch(part, pattern):
                    return True

    return False


def _get_current_branch(repo: "Repository") -> Optional[str]:
    """Get the name of the current branch."""
    head_path = os.path.join(repo.ugit_dir, "HEAD")

    if not os.path.exists(head_path):
        return None

    try:
        with open(head_path, "r", encoding="utf-8") as f:
            head_content = f.read().strip()

        if head_content.startswith("ref: refs/heads/"):
            return head_content[16:]  # Remove "ref: refs/heads/" prefix

        return None  # Detached HEAD
    except (IOError, OSError):
        return None


def get_current_branch_name(repo: Optional["Repository"] = None) -> Optional[str]:
    """Get current branch name (utility function for other modules)."""
    from ..core.repository import Repository

    if repo is None:
        repo = Repository()
        if not repo.is_repository():
            return None

    return _get_current_branch(repo)


def is_local_path(url: str) -> bool:
    """
    Check if a URL represents a local file path.

    Args:
        url: URL or path to check

    Returns:
        True if URL is a local path
    """
    if url.startswith(("http://", "https://", "ssh://", "git://", "git@")):
        return False
    return os.path.exists(url) or os.path.isabs(url)


def is_ancestor(repo: "Repository", ancestor_sha: str, descendant_sha: str) -> bool:
    """
    Check if ancestor_sha is an ancestor of descendant_sha.

    Args:
        repo: Repository instance
        ancestor_sha: Potential ancestor commit SHA
        descendant_sha: Potential descendant commit SHA

    Returns:
        True if ancestor_sha is an ancestor of descendant_sha
    """
    if ancestor_sha == descendant_sha:
        return True

    visited = set()
    stack = [descendant_sha]

    while stack:
        current = stack.pop()
        if current is None or current in visited:
            continue
        if current == ancestor_sha:
            return True

        visited.add(current)

        try:
            commit_data = get_commit_data(current, repo=repo)
            # Handle both single parent and multiple parents
            if "parent" in commit_data and commit_data["parent"] is not None:
                stack.append(commit_data["parent"])
            if "parents" in commit_data:
                stack.extend(p for p in commit_data["parents"] if p is not None)
        except (FileNotFoundError, ValueError):
            continue

    return False
