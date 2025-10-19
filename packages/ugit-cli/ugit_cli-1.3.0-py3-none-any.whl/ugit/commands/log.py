"""
Display commit history.
"""

import json
import sys
from datetime import datetime
from typing import Optional

from ..core.objects import get_object
from ..utils.helpers import ensure_repository, format_timestamp


def log(
    max_commits: Optional[int] = None,
    oneline: bool = False,
    graph: bool = False,
    since: Optional[str] = None,
    until: Optional[str] = None,
) -> None:
    """
    Display commit history.

    Args:
        max_commits: Maximum number of commits to show (None for all)
        oneline: Show each commit on a single line
        graph: Show ASCII graph of branches and merges
        since: Show commits since date
        until: Show commits until date
    """
    repo = ensure_repository()

    current = repo.get_head_ref()
    if not current:
        print("No commits yet")
        return

    count = 0
    while current and (max_commits is None or count < max_commits):
        try:
            type_, data = get_object(current)
            if type_ != "commit":
                print(f"Error: Expected commit object, got {type_}", file=sys.stderr)
                break

            commit = json.loads(data.decode())

            # Check date filters
            if since or until:
                commit_time = commit.get("timestamp", "")
                if not _is_commit_in_date_range(commit_time, since, until):
                    parent = commit.get("parent")
                    if parent and not parent.startswith("ref: refs/heads/"):
                        current = parent
                    else:
                        current = None
                    continue

            if oneline:
                _print_oneline_commit(current, commit)
            elif graph:
                _print_graph_commit(current, commit, count == 0)
            else:
                _print_full_commit(current, commit)

            parent = commit.get("parent")
            if parent and not parent.startswith("ref: refs/heads/"):
                current = parent
            else:
                current = None  # No more parents to follow
            count += 1

        except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
            print(f"Error reading commit {current}: {e}", file=sys.stderr)
            break


def _print_full_commit(commit_sha: str, commit: dict) -> None:
    """Print commit in full format."""
    print(f"commit {commit_sha}")
    print(f"Author: {commit['author']}")

    # Try to format timestamp nicely
    timestamp = commit.get("timestamp", "")
    formatted_time = format_timestamp(timestamp)
    print(f"Date:   {formatted_time}")

    # Display commit message with proper indentation
    message_lines = commit["message"].strip().split("\n")
    print()
    for line in message_lines:
        print(f"    {line}")
    print()


def _print_oneline_commit(commit_sha: str, commit: dict) -> None:
    """Print commit in oneline format."""
    short_sha = commit_sha[:7]
    message = commit["message"].strip().split("\n")[0]  # First line only
    print(f"{short_sha} {message}")


def _print_graph_commit(commit_sha: str, commit: dict, is_first: bool) -> None:
    """Print commit with ASCII graph."""
    prefix = "* " if is_first else "* "
    short_sha = commit_sha[:7]
    message = commit["message"].strip().split("\n")[0]
    print(f"{prefix}{short_sha} {message}")

    if commit.get("parent"):
        print("| ")


def _is_commit_in_date_range(
    commit_time: str, since: Optional[str] = None, until: Optional[str] = None
) -> bool:
    """Check if commit is within date range."""
    if not since and not until:
        return True

    try:
        from datetime import datetime

        if commit_time:
            commit_dt = datetime.fromisoformat(commit_time.replace("Z", "+00:00"))
            now = datetime.now(commit_dt.tzinfo)

            if since:
                since_dt = _parse_relative_date(since, now)
                if since_dt and commit_dt < since_dt:
                    return False

            if until:
                until_dt = _parse_relative_date(until, now)
                if until_dt and commit_dt > until_dt:
                    return False

    except (ValueError, AttributeError):
        pass

    return True


def _parse_relative_date(date_str: str, now: datetime) -> Optional[datetime]:
    """Parse relative dates like '2 days ago', '1 week ago'."""
    try:
        from datetime import datetime, timedelta

        if "ago" in date_str.lower():
            parts = date_str.lower().replace("ago", "").strip().split()
            if len(parts) == 2:
                value_str, unit = parts
                value = int(value_str)

                if unit.startswith("day"):
                    return now - timedelta(days=value)
                elif unit.startswith("week"):
                    return now - timedelta(weeks=value)
                elif unit.startswith("month"):
                    return now - timedelta(days=value * 30)  # Approximate
                elif unit.startswith("year"):
                    return now - timedelta(days=value * 365)  # Approximate
                elif unit.startswith("hour"):
                    return now - timedelta(hours=value)
                elif unit.startswith("minute"):
                    return now - timedelta(minutes=value)

        # Try parsing as ISO date
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))

    except (ValueError, AttributeError):
        return None
