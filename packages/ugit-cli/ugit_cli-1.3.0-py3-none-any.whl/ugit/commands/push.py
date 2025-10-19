"""
Push changes to remote repositories.

This module handles uploading local changes to remote repositories.
"""

import os
import shutil
from typing import Optional, Set

from ..core.exceptions import NonFastForwardError, UgitError
from ..core.objects import get_object
from ..core.repository import Repository
from ..utils.helpers import get_current_branch_name, is_local_path
from .remote import get_remote_url


def push(
    remote_name: str = "origin", branch: Optional[str] = None, force: bool = False
) -> int:
    """
    Push local changes to a remote repository.

    Args:
        remote_name: Name of remote to push to
        branch: Specific branch to push (optional)
        force: Force push even if not fast-forward

    Returns:
        0 on success, 1 on error
    """
    repo = Repository()

    if not repo.is_repository():
        raise UgitError("Not a ugit repository")

    # Get remote URL
    remote_url = get_remote_url(remote_name)
    if not remote_url:
        raise UgitError(
            f"fatal: '{remote_name}' does not appear to be a ugit repository"
        )

    # Get current branch if none specified
    if branch is None:
        branch = get_current_branch_name(repo)
        if not branch:
            raise UgitError("fatal: You are not currently on a branch")

    # Get local branch ref
    local_branch_path = os.path.join(repo.ugit_dir, "refs", "heads", branch)
    if not os.path.exists(local_branch_path):
        raise UgitError(f"fatal: src refspec {branch} does not match any")

    try:
        with open(local_branch_path, "r") as f:
            local_sha = f.read().strip()
    except (IOError, OSError) as e:
        raise UgitError(f"fatal: Failed to read local ref: {e}")

    print(f"Pushing to {remote_url}")

    try:
        if is_local_path(remote_url):
            _push_local(repo, remote_name, remote_url, branch, local_sha, force)
        else:
            raise UgitError(f"fatal: remote protocols not yet supported: {remote_url}")

    except Exception as e:
        raise UgitError(f"fatal: failed to push to '{remote_name}': {e}")

    return 0


def _push_local(
    repo: Repository,
    remote_name: str,
    remote_url: str,
    branch: str,
    local_sha: str,
    force: bool,
) -> None:
    """
    Push to a local repository.

    Args:
        repo: Local repository
        remote_name: Remote name
        remote_url: Remote repository path
        branch: Branch to push
        local_sha: Local commit SHA
        force: Force push
    """
    # Check if remote repository exists
    remote_ugit_dir = os.path.join(remote_url, ".ugit")
    if not os.path.exists(remote_ugit_dir):
        raise ValueError(f"not a ugit repository: {remote_url}")

    # Check remote branch status
    remote_branch_path = os.path.join(remote_ugit_dir, "refs", "heads", branch)
    remote_sha = None

    if os.path.exists(remote_branch_path):
        try:
            with open(remote_branch_path, "r") as f:
                remote_sha = f.read().strip()
        except (IOError, OSError):
            pass

    # Check if this is a fast-forward push
    if remote_sha and not force:
        if not _is_fast_forward(repo, remote_sha, local_sha):
            raise NonFastForwardError(
                f"! [rejected] {branch} -> {branch} (non-fast-forward)\n"
                "hint: Updates were rejected because the tip of your current branch is behind\n"
                "hint: its remote counterpart. Integrate the remote changes (e.g.\n"
                "hint: 'ugit pull ...') before pushing again."
            )

    # Push objects
    objects_pushed = _push_objects(repo, remote_url, local_sha)

    # Update remote ref
    os.makedirs(os.path.dirname(remote_branch_path), exist_ok=True)
    try:
        with open(remote_branch_path, "w") as f:
            f.write(local_sha)
    except (IOError, OSError) as e:
        raise RuntimeError(f"Failed to update remote branch {branch}: {e}")

    # Show status
    if remote_sha:
        if force and not _is_fast_forward(repo, remote_sha, local_sha):
            print(
                f" + {remote_sha[:8]}...{local_sha[:8]} {branch} -> {branch} (forced update)"
            )
        else:
            print(f"   {remote_sha[:8]}..{local_sha[:8]}  {branch} -> {branch}")
    else:
        print(f"* [new branch] {branch} -> {branch}")

    if objects_pushed:
        print(f"Pushed {objects_pushed} objects")


def _is_fast_forward(repo: Repository, base_sha: str, target_sha: str) -> bool:
    """
    Check if target_sha is a fast-forward from base_sha.

    Args:
        repo: Repository instance
        base_sha: Base commit SHA
        target_sha: Target commit SHA

    Returns:
        True if target_sha is a fast-forward from base_sha
    """
    if base_sha == target_sha:
        return True

    # Check if base_sha is an ancestor of target_sha
    visited = set()
    to_check = [target_sha]

    while to_check:
        current_sha = to_check.pop()

        if current_sha in visited:
            continue
        visited.add(current_sha)

        if current_sha == base_sha:
            return True

        try:
            commit_type, commit_content = get_object(current_sha, repo=repo)
            if commit_type != "commit":
                continue

            # Parse JSON commit to find parents
            import json

            commit_data = json.loads(commit_content.decode("utf-8"))

            if "parent" in commit_data:
                parent = commit_data["parent"]
                # Handle both direct SHA and ref format
                if parent.startswith("ref: refs/heads/"):
                    # This is the initial commit, no parent
                    continue
                else:
                    # Direct parent SHA
                    to_check.append(parent)

        except (FileNotFoundError, UnicodeDecodeError, IOError):
            # Skip commits that can't be read or decoded
            continue

    return False


def _push_objects(repo: Repository, remote_url: str, start_sha: str) -> int:
    """
    Push all objects needed for the given commit to remote.

    Args:
        repo: Local repository
        remote_url: Remote repository path
        start_sha: Starting commit SHA

    Returns:
        Number of objects pushed
    """
    remote_objects_dir = os.path.join(remote_url, ".ugit", "objects")
    local_objects_dir = os.path.join(repo.ugit_dir, "objects")

    # Find all objects we need to push
    objects_to_push: Set[str] = set()
    _collect_objects(start_sha, objects_to_push, set(), remote_url, repo)

    # Push objects
    pushed_count = 0
    for sha in objects_to_push:
        if _copy_object_to_remote(local_objects_dir, remote_objects_dir, sha):
            pushed_count += 1

    return pushed_count


def _collect_objects(
    sha: str, to_push: Set[str], visited: Set[str], remote_url: str, repo: Repository
) -> None:
    """
    Recursively collect all objects that need to be pushed.

    Args:
        sha: Object SHA to start from
        to_push: Set to add objects to
        visited: Set of already visited objects
        remote_url: Remote repository path
        repo: Local repository instance
    """
    if sha in visited:
        return
    visited.add(sha)

    # Check if remote already has this object
    if _remote_has_object(remote_url, sha):
        return

    to_push.add(sha)

    try:
        obj_type, obj_content = get_object(sha, repo=repo)

        if obj_type == "commit":
            # Parse JSON commit to find tree and parents
            import json

            commit_data = json.loads(obj_content.decode("utf-8"))

            if "tree" in commit_data:
                _collect_objects(
                    commit_data["tree"], to_push, visited, remote_url, repo
                )

            if "parent" in commit_data:
                parent = commit_data["parent"]
                # Only collect if it's a real parent SHA (not a ref)
                if parent is not None and not parent.startswith("ref: refs/heads/"):
                    _collect_objects(parent, to_push, visited, remote_url, repo)

        elif obj_type == "tree":
            # Parse JSON tree to find blobs and subtrees
            import json

            tree_data = json.loads(obj_content.decode("utf-8"))

            # Tree is a list of [filename, sha] pairs
            for entry in tree_data:
                if len(entry) >= 2:
                    _collect_objects(entry[1], to_push, visited, remote_url, repo)

    except (FileNotFoundError, ValueError, IndexError):
        # Skip objects that can't be read or parsed
        return


def _remote_has_object(remote_url: str, sha: str) -> bool:
    """
    Check if remote repository has an object.

    Args:
        remote_url: Remote repository path
        sha: Object SHA to check

    Returns:
        True if remote has the object
    """
    remote_objects_dir = os.path.join(remote_url, ".ugit", "objects")

    # Check both formats
    paths = [
        os.path.join(remote_objects_dir, sha),  # Old flat
        os.path.join(remote_objects_dir, sha[:2], sha[2:]),  # New hierarchical
    ]

    return any(os.path.exists(path) for path in paths)


def _copy_object_to_remote(
    local_objects_dir: str, remote_objects_dir: str, sha: str
) -> bool:
    """
    Copy an object from local to remote repository.

    Args:
        local_objects_dir: Local objects directory
        remote_objects_dir: Remote objects directory
        sha: Object SHA to copy

    Returns:
        True if object was copied successfully
    """
    # Try both formats for source
    local_paths = [
        os.path.join(local_objects_dir, sha),  # Old flat
        os.path.join(local_objects_dir, sha[:2], sha[2:]),  # New hierarchical
    ]

    for local_path in local_paths:
        if os.path.exists(local_path):
            # Copy to hierarchical format in remote
            remote_dir = os.path.join(remote_objects_dir, sha[:2])
            remote_path = os.path.join(remote_dir, sha[2:])

            os.makedirs(remote_dir, exist_ok=True)

            try:
                shutil.copy2(local_path, remote_path)
                return True
            except (IOError, OSError):
                continue

    return False
