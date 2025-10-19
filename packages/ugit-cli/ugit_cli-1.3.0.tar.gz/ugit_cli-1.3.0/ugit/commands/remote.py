"""
Remote repository management for ugit.

This module handles adding, removing, listing, and showing remote repositories.
"""

import os
from typing import Any, Dict, Optional

from ..core.repository import Repository
from ..utils.config import Config


def remote(args: Any) -> None:
    """
    Handle remote command with subcommands.

    Args:
        args: Parsed command arguments
    """
    repo = Repository()

    if not repo.is_repository():
        print("Not a ugit repository")
        return

    if hasattr(args, "subcommand"):
        if args.subcommand == "add":
            add_remote(args.name, args.url)
        elif args.subcommand == "remove":
            remove_remote(args.name)
        elif args.subcommand == "show":
            show_remote(args.name)
        elif args.subcommand == "list" or args.subcommand is None:
            list_remotes(args.verbose if hasattr(args, "verbose") else False)
        else:
            print(f"Unknown remote subcommand: {args.subcommand}")
    else:
        list_remotes(args.verbose if hasattr(args, "verbose") else False)


def add_remote(name: str, url: str) -> None:
    """
    Add a new remote repository.

    Args:
        name: Remote name
        url: Remote URL
    """
    config = Config()

    # Check if remote already exists
    existing_url = config.get("remote", f"{name}.url")
    if existing_url:
        print(f"remote {name} already exists")
        return

    # Validate URL format (basic validation)
    if not _is_valid_url(url):
        print(f"Invalid URL format: {url}")
        return

    # Add remote to config
    config.set("remote", f"{name}.url", url)
    config.set("remote", f"{name}.fetch", f"+refs/heads/*:refs/remotes/{name}/*")

    print(f"Added remote '{name}' -> {url}")


def remove_remote(name: str) -> None:
    """
    Remove a remote repository.

    Args:
        name: Remote name to remove
    """
    config = Config()

    # Check if remote exists
    existing_url = config.get("remote", f"{name}.url")
    if not existing_url:
        print(f"No such remote: {name}")
        return

    # Remove from config
    config.remove("remote", f"{name}.url")
    config.remove("remote", f"{name}.fetch")

    # Remove remote refs directory
    repo = Repository()
    remote_refs_path = os.path.join(repo.ugit_dir, "refs", "remotes", name)
    if os.path.exists(remote_refs_path):
        import shutil

        shutil.rmtree(remote_refs_path)

    print(f"Removed remote '{name}'")


def list_remotes(verbose: bool = False) -> None:
    """
    List all configured remotes.

    Args:
        verbose: Show URLs as well as names
    """
    remotes = get_all_remotes()

    if not remotes:
        return

    for name in sorted(remotes.keys()):
        if verbose:
            print(f"{name}\t{remotes[name]['url']}")
            if "fetch" in remotes[name]:
                print(f"{name}\t{remotes[name]['url']} (fetch)")
            if "push" in remotes[name]:
                print(f"{name}\t{remotes[name]['push']} (push)")
            elif "url" in remotes[name]:
                print(f"{name}\t{remotes[name]['url']} (push)")
        else:
            print(name)


def show_remote(name: str) -> None:
    """
    Show detailed information about a remote.

    Args:
        name: Remote name
    """
    remotes = get_all_remotes()

    if name not in remotes:
        print(f"No such remote: {name}")
        return

    remote_info = remotes[name]
    print(f"* remote {name}")
    print(f"  Fetch URL: {remote_info['url']}")
    print(f"  Push  URL: {remote_info.get('push', remote_info['url'])}")

    # Show remote branches if they exist
    repo = Repository()
    remote_refs_path = os.path.join(repo.ugit_dir, "refs", "remotes", name)
    if os.path.exists(remote_refs_path):
        print("  Remote branches:")
        for branch_file in os.listdir(remote_refs_path):
            branch_path = os.path.join(remote_refs_path, branch_file)
            if os.path.isfile(branch_path):
                try:
                    with open(branch_path, "r") as f:
                        f.read().strip()
                    print(f"    {name}/{branch_file}")
                except (IOError, OSError):
                    pass


def get_all_remotes() -> Dict[str, Dict[str, str]]:
    """
    Get all configured remotes.

    Returns:
        Dictionary of remote configurations
    """
    config = Config()
    remotes: Dict[str, Dict[str, str]] = {}

    # Parse all remote.* configurations
    all_settings = config.get_all_settings()
    for key, value in all_settings.items():
        if key.startswith("remote."):
            parts = key.split(".", 2)
            if len(parts) == 3:
                _, remote_name, setting = parts
                if remote_name not in remotes:
                    remotes[remote_name] = {}
                remotes[remote_name][setting] = value

    return remotes


def get_remote_url(name: str) -> Optional[str]:
    """
    Get URL for a specific remote.

    Args:
        name: Remote name

    Returns:
        Remote URL or None if not found
    """
    config = Config()
    return config.get("remote", f"{name}.url")


def _is_valid_url(url: str) -> bool:
    """
    Basic URL validation.

    Args:
        url: URL to validate

    Returns:
        True if URL appears valid
    """
    # Support local paths, HTTP(S), and basic validation
    if os.path.isabs(url) or url.startswith("./") or url.startswith("../"):
        return True

    if url.startswith(("http://", "https://", "git://", "ssh://")):
        return True

    if "@" in url and ":" in url:  # SSH-style: user@host:path
        return True

    # Support relative paths - check if directory exists and has .ugit
    if os.path.isdir(url):
        ugit_path = os.path.join(url, ".ugit")
        if os.path.exists(ugit_path):
            return True

    # Support any local path format that could exist
    return True  # For now, be permissive with local paths
