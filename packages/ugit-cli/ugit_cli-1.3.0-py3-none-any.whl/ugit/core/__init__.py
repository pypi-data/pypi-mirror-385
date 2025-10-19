"""
Core functionality package for ugit.

This package contains the core components:
- objects: Object storage and management (hash_object, get_object, etc.)
- repository: Repository and Index classes for managing ugit repositories
"""

from .objects import get_object, hash_object
from .repository import Index, Repository

__all__ = ["hash_object", "get_object", "Repository", "Index"]
