"""Custom exceptions for ugit."""

from typing import List, Optional


class UgitError(Exception):
    """Base class for all ugit errors."""

    pass


class NotInRepositoryError(UgitError):
    """Raised when an operation requires a repository but is not in one."""

    def __init__(self, message: str = "Not a ugit repository") -> None:
        super().__init__(message)


class BranchExistsError(UgitError):
    """Raised when trying to create a branch that already exists."""

    pass


class BranchNotFoundError(UgitError):
    """Raised when a specified branch cannot be found."""

    pass


class MergeConflictError(UgitError):
    """Raised when a merge results in conflicts."""

    def __init__(
        self,
        message: str = "Merge conflicts detected",
        conflicts: Optional[List[str]] = None,
    ) -> None:
        super().__init__(message)
        self.conflicts = conflicts or []


class InvalidRefError(UgitError):
    """Raised for invalid references (commits, branches, etc.)."""

    pass


class RemoteNotFoundError(UgitError):
    """Raised when a specified remote cannot be found."""

    pass


class NonFastForwardError(UgitError):
    """Raised on a rejected non-fast-forward push."""

    pass
