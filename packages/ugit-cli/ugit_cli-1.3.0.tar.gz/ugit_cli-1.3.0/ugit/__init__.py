"""
ugit - A minimal Git implementation in Python

ugit is a simplified version control system that demonstrates the core concepts
of Git including object storage, staging, committing, and basic history.
"""

__version__ = "1.3.0"
__author__ = "night-slayer18"

# Core functionality is available but not auto-imported to avoid circular imports
# Import modules explicitly when needed:
# from ugit.core.repository import Repository
# from ugit.core.objects import hash_object, get_object
# from ugit.commands import init, add, commit, log, checkout, status

__all__ = ["__version__", "__author__"]
