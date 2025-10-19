"""
Custom exceptions for the kcleaner package.
"""


class KcleanerError(Exception):
    """Base exception for all dotflow errors."""

    pass


class ValidationError(KcleanerError):
    """Raised when validation fails."""

    pass


class SystemPermissionError(KcleanerError):
    """
    Raised when user cannot acess to system reasource due to insuficient permissions.
    Eg command execusion
    """

    pass


class FileSystemError(KcleanerError):
    """
    Raises when there is file/folder ie FileSystem acess error not related to permissions.
    ie write error
    """

    pass


class AuthorizationError(KcleanerError):
    """
    Raised when there is an *Explicit* file/dir/resource access denial.
        When priviledge elevelation is required.
    """

    pass


class ConfigurationError(KcleanerError):
    """Raised when invalid configuration."""

    pass
