#!/usr/bin/env python3
"""
Command-line interface for ugit.
"""

import argparse
import sys
from typing import List, Optional

from .commands import (
    add,
    branch,
    checkout,
    clone,
    commit,
    config,
    diff,
    fetch,
    init,
    log,
    merge,
    pull,
    push,
    remote,
    reset,
    serve,
    stash,
    stash_apply,
    stash_drop,
    stash_list,
    stash_pop,
    status,
)
from .core.exceptions import UgitError


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for ugit CLI."""
    parser = argparse.ArgumentParser(
        prog="ugit",
        description="A minimal Git implementation in Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ugit init                     Initialize a new repository
  ugit add file.txt             Add file to staging area
  ugit add .                    Add all files to staging area
  ugit commit -m "message"      Create a commit
  ugit status                   Show repository status
  ugit log                      Show commit history
  ugit log --oneline            Show compact commit history
  ugit log --graph              Show commit graph
  ugit checkout <commit>        Checkout a specific commit
  ugit checkout <branch>        Switch to a branch
  ugit checkout -b <branch>     Create and switch to a branch
  ugit branch                   List branches
  ugit branch <name>            Create a branch
  ugit branch -d <name>         Delete a branch
  ugit merge <branch>           Merge a branch
  ugit diff                     Show changes in working directory
  ugit diff --staged            Show staged changes
  ugit diff <commit1> <commit2> Compare two commits
  ugit reset                    Unstage all files
  ugit reset --hard <commit>    Reset to commit (destructive)
  ugit stash                    Stash current changes
  ugit stash pop                Apply and remove most recent stash
  ugit stash list               List all stashes
  ugit clone <url> [dir]        Clone a repository
  ugit remote add <name> <url>  Add a remote repository
  ugit remote -v                List remotes with URLs
  ugit fetch [remote]           Fetch changes from remote
  ugit pull [remote] [branch]   Fetch and merge from remote
  ugit push [remote] [branch]   Push changes to remote
        """,
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    subparsers.add_parser("init", help="Initialize a new repository")

    # add command
    add_parser = subparsers.add_parser("add", help="Add files to staging area")
    add_parser.add_argument("paths", nargs="+", help="Files or directories to add")

    # commit command
    commit_parser = subparsers.add_parser("commit", help="Create a commit")
    commit_parser.add_argument("-m", "--message", required=True, help="Commit message")
    commit_parser.add_argument("--author", help="Author information")

    # status command
    subparsers.add_parser("status", help="Show repository status")

    # config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument(
        "--list", action="store_true", help="List all configuration options"
    )
    config_parser.add_argument(
        "key", nargs="?", help="Configuration key (section.option)"
    )
    config_parser.add_argument("value", nargs="?", help="Configuration value")

    # log command
    log_parser = subparsers.add_parser("log", help="Show commit history")
    log_parser.add_argument(
        "-n", "--max-count", type=int, help="Limit number of commits to show"
    )
    log_parser.add_argument(
        "--oneline", action="store_true", help="Show each commit on one line"
    )
    log_parser.add_argument("--graph", action="store_true", help="Show ASCII graph")
    log_parser.add_argument("--since", help="Show commits since date")
    log_parser.add_argument("--until", help="Show commits until date")

    # checkout command
    checkout_parser = subparsers.add_parser(
        "checkout", help="Checkout a commit or switch to a branch"
    )
    checkout_parser.add_argument("target", help="Commit SHA or branch name to checkout")
    checkout_parser.add_argument(
        "-b", "--branch", action="store_true", help="Create new branch"
    )

    # branch command
    branch_parser = subparsers.add_parser(
        "branch", help="List, create, or delete branches"
    )
    branch_parser.add_argument("name", nargs="?", help="Branch name to create")
    branch_parser.add_argument(
        "-l", "--list", action="store_true", help="List branches"
    )
    branch_parser.add_argument("-d", "--delete", help="Delete a branch")

    # merge command
    merge_parser = subparsers.add_parser(
        "merge", help="Merge a branch into current branch"
    )
    merge_parser.add_argument("branch", help="Branch name to merge")
    merge_parser.add_argument("--no-ff", action="store_true", help="Force merge commit")

    # diff command
    diff_parser = subparsers.add_parser("diff", help="Show changes between files")
    diff_parser.add_argument(
        "--staged", action="store_true", help="Show staged changes"
    )
    diff_parser.add_argument("commit1", nargs="?", help="First commit to compare")
    diff_parser.add_argument("commit2", nargs="?", help="Second commit to compare")

    # reset command
    reset_parser = subparsers.add_parser(
        "reset", help="Reset current HEAD to specified state"
    )
    reset_parser.add_argument(
        "target", nargs="?", help="Commit SHA or branch to reset to"
    )
    reset_parser.add_argument(
        "--hard", action="store_true", help="Reset working directory and staging area"
    )
    reset_parser.add_argument("--soft", action="store_true", help="Only move HEAD")

    # stash command
    stash_parser = subparsers.add_parser(
        "stash", help="Stash changes in working directory"
    )
    stash_subparsers = stash_parser.add_subparsers(
        dest="stash_command", help="Stash commands"
    )

    # stash (default - save)
    stash_save = stash_subparsers.add_parser("save", help="Save changes to stash")
    stash_save.add_argument("message", nargs="?", help="Stash message")
    stash_save.add_argument(
        "-u", "--include-untracked", action="store_true", help="Include untracked files"
    )

    # stash pop
    stash_pop_parser = stash_subparsers.add_parser(
        "pop", help="Apply and remove most recent stash"
    )
    stash_pop_parser.add_argument(
        "stash_id", nargs="?", type=int, default=0, help="Stash index"
    )

    # stash list
    stash_subparsers.add_parser("list", help="List all stashes")

    # stash apply
    stash_apply_parser = stash_subparsers.add_parser(
        "apply", help="Apply stash without removing it"
    )
    stash_apply_parser.add_argument(
        "stash_id", nargs="?", type=int, default=0, help="Stash index"
    )

    # stash drop
    stash_drop_parser = stash_subparsers.add_parser(
        "drop", help="Remove stash without applying"
    )
    stash_drop_parser.add_argument(
        "stash_id", nargs="?", type=int, default=0, help="Stash index"
    )

    # clone command
    clone_parser = subparsers.add_parser("clone", help="Clone a repository")
    clone_parser.add_argument("url", help="Repository URL to clone")
    clone_parser.add_argument("directory", nargs="?", help="Directory name (optional)")

    # remote command
    remote_parser = subparsers.add_parser("remote", help="Manage remote repositories")
    remote_parser.add_argument("-v", "--verbose", action="store_true", help="Show URLs")
    remote_subparsers = remote_parser.add_subparsers(
        dest="subcommand", help="Remote commands"
    )

    # remote add
    remote_add = remote_subparsers.add_parser("add", help="Add a remote")
    remote_add.add_argument("name", help="Remote name")
    remote_add.add_argument("url", help="Remote URL")

    # remote remove
    remote_remove = remote_subparsers.add_parser("remove", help="Remove a remote")
    remote_remove.add_argument("name", help="Remote name")

    # remote show
    remote_show = remote_subparsers.add_parser("show", help="Show remote details")
    remote_show.add_argument("name", help="Remote name")

    # remote list (default)
    remote_list = remote_subparsers.add_parser("list", help="List remotes")
    remote_list.add_argument("-v", "--verbose", action="store_true", help="Show URLs")

    # fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch from remote repository")
    fetch_parser.add_argument("remote", nargs="?", default="origin", help="Remote name")
    fetch_parser.add_argument("branch", nargs="?", help="Branch name")

    # pull command
    pull_parser = subparsers.add_parser("pull", help="Fetch and merge from remote")
    pull_parser.add_argument("remote", nargs="?", default="origin", help="Remote name")
    pull_parser.add_argument("branch", nargs="?", help="Branch name")

    # push command
    push_parser = subparsers.add_parser("push", help="Push to remote repository")
    push_parser.add_argument("remote", nargs="?", default="origin", help="Remote name")
    push_parser.add_argument("branch", nargs="?", help="Branch name")
    push_parser.add_argument("-f", "--force", action="store_true", help="Force push")

    # serve command
    serve_parser = subparsers.add_parser("serve", help="Start web interface server")
    serve_parser.add_argument(
        "--port", type=int, default=8000, help="Port to run server on (default: 8000)"
    )
    serve_parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)"
    )
    serve_parser.add_argument(
        "--no-browser", action="store_true", help="Don't open browser automatically"
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the ugit CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    try:
        result: Optional[int] = 0

        if args.command == "init":
            init()
        elif args.command == "add":
            add(args.paths)
        elif args.command == "commit":
            commit(args.message, args.author)
        elif args.command == "config":
            result = config(args.key, args.value, args.list)
        elif args.command == "status":
            status()
        elif args.command == "log":
            log(args.max_count, args.oneline, args.graph, args.since, args.until)
        elif args.command == "checkout":
            checkout(args.target, args.branch)
        elif args.command == "branch":
            branch(args.name, args.list, args.delete)
        elif args.command == "merge":
            merge(args.branch, args.no_ff)
        elif args.command == "diff":
            if args.commit1 and args.commit2:
                diff(commit1=args.commit1, commit2=args.commit2)
            else:
                diff(staged=args.staged)
        elif args.command == "reset":
            reset(args.target, args.hard, args.soft)
        elif args.command == "stash":
            if args.stash_command == "pop":
                stash_pop(args.stash_id)
            elif args.stash_command == "list":
                stash_list()
            elif args.stash_command == "apply":
                stash_apply(args.stash_id)
            elif args.stash_command == "drop":
                stash_drop(args.stash_id)
            elif args.stash_command == "save" or args.stash_command is None:
                message = getattr(args, "message", None)
                include_untracked = getattr(args, "include_untracked", False)
                stash(message, include_untracked)
            else:
                sys.stderr.write(f"Unknown stash command: {args.stash_command}\n")
                return 1
        elif args.command == "clone":
            clone(args.url, args.directory)
        elif args.command == "remote":
            remote(args)
        elif args.command == "fetch":
            result = fetch(args.remote, args.branch)
        elif args.command == "pull":
            result = pull(args.remote, args.branch)
        elif args.command == "push":
            result = push(args.remote, args.branch, args.force)
        elif args.command == "serve":
            result = serve(args.port, args.host, not args.no_browser)
        else:
            sys.stderr.write(f"Unknown command: {args.command}\n")
            return 1

        return result if result is not None else 0

    except UgitError as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except Exception as e:
        sys.stderr.write(f"An unexpected error occurred: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
