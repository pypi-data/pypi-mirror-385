"""
Initialize a new ugit repository.
"""

import os

from ..core.repository import Repository


def init() -> None:
    """Initialize a new ugit repository in the current directory."""
    repo = Repository()

    if repo.is_repository():
        print("Already a ugit repository")
        return

    # Create directory structure
    os.mkdir(repo.ugit_dir)
    os.makedirs(os.path.join(repo.ugit_dir, "objects"))
    os.makedirs(os.path.join(repo.ugit_dir, "refs", "heads"))

    # Initialize HEAD to point to main branch
    with open(os.path.join(repo.ugit_dir, "HEAD"), "w") as f:
        f.write("ref: refs/heads/main")

    print("Initialized empty ugit repository")
