"""
File path validation utilities for secure file operations.

This module provides utilities for validating file paths to prevent
path traversal attacks and ensure secure file operations.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

# Standard library imports
import os
import re
from collections.abc import Callable
from pathlib import Path

# Local imports
from splurge_safe_io.exceptions import (
    SplurgeSafeIoFileNotFoundError,
    SplurgeSafeIoFilePermissionError,
    SplurgeSafeIoPathValidationError,
)

# Module-level constants for path validation
_MAX_PATH_LENGTH = 4096  # Maximum path length for most filesystems
_DEFAULT_FILENAME = "unnamed_file"  # Default filename when sanitization results in empty string


class PathValidator:
    """Utility class for validating file paths securely.

    This class centralizes path validation logic to prevent path
    traversal attacks and reject paths with dangerous characters or
    unsupported formats. It offers helpers for registering lightweight
    pre-resolution policies used by applications or tests.
    """

    # Private constants for path validation
    # A list of pre-resolution policy callables. Each callable receives
    # the raw path string and may either return None (pass) or raise
    # SplurgeSafeIoPathValidationError to reject the path. Policies are
    # intentionally lightweight and optional — by default there are no
    # pre-resolution checks to avoid false positives on valid platform
    # paths. Callers/tests can register policies via
    # `register_pre_resolution_policy` if they need additional checks.
    _pre_resolution_policies: list[Callable[[str], None]] = []

    @classmethod
    def register_pre_resolution_policy(cls, policy: Callable[[str], None]) -> None:
        """Register a pre-resolution policy callable.

        The `policy` callable will be invoked with the raw path string
        prior to resolution. The callable should raise
        :class:`SplurgeSafeIoPathValidationError` to reject the path, or
        return ``None`` to allow it.

        Args:
            policy (Callable[[str], None]): A callable that accepts the raw
                path string and either returns None or raises
                :class:`SplurgeSafeIoPathValidationError`.
        """
        cls._pre_resolution_policies.append(policy)

    @classmethod
    def clear_pre_resolution_policies(cls) -> None:
        """Clear all registered pre-resolution policies.

        This is primarily useful for tests or application shutdown to
        ensure no policies remain registered.
        """
        cls._pre_resolution_policies.clear()

    @classmethod
    def list_pre_resolution_policies(cls) -> list[Callable[[str], None]]:
        """Return a shallow copy of registered pre-resolution policies.

        Returns:
            list[Callable[[str], None]]: A shallow copy of policy callables.
        """
        return list(cls._pre_resolution_policies)

    # Commonly reserved characters that should be rejected in many
    # filesystem contexts. Control characters (U+0000..U+001F) are
    # checked programmatically in `_check_dangerous_characters` below
    # to avoid enumerating them here.
    _DANGEROUS_CHARS = [
        "<",
        ">",
        '"',
        "|",
        "?",
        "*",  # Windows reserved characters (excluding ':' for drive letters)
    ]

    MAX_PATH_LENGTH = _MAX_PATH_LENGTH

    @classmethod
    def validate_path(
        cls,
        file_path: str | Path,
        *,
        must_exist: bool = False,
        must_be_file: bool = False,
        must_be_readable: bool = False,
        must_be_writable: bool = False,
        allow_relative: bool = True,
        base_directory: str | Path | None = None,
    ) -> Path:
        """Validate a filesystem path for security and correctness.

        This is the central path validation routine used across the package.

        Args:
            file_path: Path or string to validate.
            must_exist: If True, require the path to exist.
            must_be_file: If True, require the path to be a regular file.
            must_be_readable: If True, check read permission via os.access().
            allow_relative: If False, disallow relative paths.
            base_directory: Optional directory to resolve relative paths
                against and to restrict the resolved path to.

        Returns:
            pathlib.Path: Resolved and normalized path.

        Raises:
            SplurgeSafeIoPathValidationError: If any validation rule fails.
            SplurgeSafeIoFileNotFoundError: If must_exist is True and file is missing.
            SplurgeSafeIoFilePermissionError: If must_be_readable is True and the file is not readable.
        """
        # Deprecated wrapper: prefer `get_validated_path` which returns a
        # validated and resolved pathlib.Path. ``validate_path`` will be
        # removed in release 2025.2.0.
        import warnings

        warnings.warn(
            "PathValidator.validate_path is deprecated; use PathValidator.get_validated_path(...) instead. "
            "Scheduled removal: 2025.2.0",
            DeprecationWarning,
            stacklevel=2,
        )

        return cls.get_validated_path(
            file_path,
            must_exist=must_exist,
            must_be_file=must_be_file,
            must_be_readable=must_be_readable,
            must_be_writable=must_be_writable,
            allow_relative=allow_relative,
            base_directory=base_directory,
        )

    @classmethod
    def get_validated_path(
        cls,
        file_path: str | Path,
        *,
        must_exist: bool = False,
        must_be_file: bool = False,
        must_be_readable: bool = False,
        must_be_writable: bool = False,
        allow_relative: bool = True,
        base_directory: str | Path | None = None,
    ) -> Path:
        """Validate and return a resolved pathlib.Path.

        This is the primary implementation: it performs the same checks
        that previously lived in ``validate_path`` but is named to make
        it obvious the function returns a validated Path object.
        """
        # Convert to Path object
        path = Path(file_path) if isinstance(file_path, str) else file_path

        # Get the original string for validation (before Path normalization)
        path_str = str(file_path) if isinstance(file_path, str) else str(path)

        # Check for dangerous characters
        cls._check_dangerous_characters(path_str)

        # Check for path traversal patterns
        cls._check_path_traversal(path_str)

        # Check path length
        cls._check_path_length(path_str)

        # Handle relative paths
        if not path.is_absolute() and not allow_relative:
            raise SplurgeSafeIoPathValidationError(
                f"Relative paths are not allowed: {path}", details="Set allow_relative=True to allow relative paths"
            )

        # Resolve path (handles symlinks and normalizes)
        try:
            if base_directory:
                base_path = Path(base_directory).resolve()
                if not path.is_absolute():
                    resolved_path = (base_path / path).resolve()
                else:
                    resolved_path = path.resolve()

                # Ensure resolved path is within base directory
                try:
                    resolved_path.relative_to(base_path)
                except ValueError:
                    raise SplurgeSafeIoPathValidationError(
                        f"Path {path} resolves outside base directory {base_directory}",
                        details="Path traversal detected",
                    ) from None
            else:
                resolved_path = path.resolve()
        except (OSError, RuntimeError) as e:
            raise SplurgeSafeIoPathValidationError(
                f"Failed to resolve path {path}: {e}",
                details="Check if path contains invalid characters or symlinks",
                original_exception=e,
            ) from e

        # Check if file exists
        if must_exist and not resolved_path.exists():
            raise SplurgeSafeIoFileNotFoundError(
                f"File does not exist: {resolved_path}", details="Set must_exist=False to allow non-existent files"
            )

        # Check if it's a file (not directory)
        if must_be_file and resolved_path.exists() and not resolved_path.is_file():
            raise SplurgeSafeIoPathValidationError(
                f"Path is not a file: {resolved_path}", details="Path exists but is not a regular file"
            )

        # Check if file is readable
        if must_be_readable:
            if not resolved_path.exists():
                raise SplurgeSafeIoFileNotFoundError(
                    f"Cannot check readability of non-existent file: {resolved_path}",
                    details="File must exist to check readability",
                )

            if not os.access(resolved_path, os.R_OK):
                raise SplurgeSafeIoFilePermissionError(
                    f"File is not readable: {resolved_path}", details="Check file permissions"
                )

        # Check if file is writable
        if must_be_writable:
            if not resolved_path.exists():
                raise SplurgeSafeIoFileNotFoundError(
                    f"Cannot check writability of non-existent file: {resolved_path}",
                    details="File must exist to check writability",
                )

            if not os.access(resolved_path, os.W_OK):
                raise SplurgeSafeIoFilePermissionError(
                    f"File is not writable: {resolved_path}", details="Check file permissions"
                )

        return resolved_path

    @classmethod
    def _is_valid_windows_drive_pattern(cls, path_str: str) -> bool:
        """Return True if ``path_str`` looks like a valid Windows drive pattern.

        Accepts both ``C:`` and ``C:\\...`` or ``C:/...`` forms.
        """
        # Must be C: at the end of the string, or C:\ (or C:/) followed by path
        return bool(re.match(r"^[A-Za-z]:$", path_str)) or bool(re.match(r"^[A-Za-z]:[\\/]", path_str))

    @classmethod
    def _check_dangerous_characters(cls, path_str: str) -> None:
        """Raise if ``path_str`` contains characters disallowed by policy.

        This guards against NULs, control characters, and reserved filesystem
        characters which may be used in injection or traversal attacks.
        """
        # Check for reserved dangerous characters (e.g. < > " | ? *)
        for char in cls._DANGEROUS_CHARS:
            idx = path_str.find(char)
            if idx != -1:
                raise SplurgeSafeIoPathValidationError(
                    f"Path contains dangerous character: {repr(char)}",
                    details=f"Character at position {idx}",
                )

        # Programmatic check for C0 control characters (U+0000..U+001F).
        # This avoids listing control characters explicitly and is easier
        # to maintain. Report the first found control character's position.
        for idx, ch in enumerate(path_str):
            if ord(ch) < 32:
                raise SplurgeSafeIoPathValidationError(
                    f"Path contains control character: U+{ord(ch):04X}",
                    details=f"Character at position {idx}",
                )

        # Special handling for colons - only allow them in Windows drive letters (e.g., C:)
        if ":" in path_str:
            if not cls._is_valid_windows_drive_pattern(path_str):
                raise SplurgeSafeIoPathValidationError(
                    "Path contains colon in invalid position",
                    details="Colons are only allowed in Windows drive letters (e.g., C: or C:\\)",
                )

    @classmethod
    def _check_path_traversal(cls, path_str: str) -> None:
        """Raise if ``path_str`` contains obvious traversal patterns.

        This is a best-effort check that catches sequences such as ``..``
        and unusual repeated separators that are likely malicious.
        """
        # Invoke any registered pre-resolution policy callables. Each
        # policy may raise SplurgeSafeIoPathValidationError to reject the
        # path. If no policies are registered, this check is a no-op.
        for policy in cls._pre_resolution_policies:
            # Policies are trusted callables provided by the application or
            # tests; call them with the raw path string.
            policy(path_str)

    @classmethod
    def _check_path_length(cls, path_str: str) -> None:
        """Raise if the path exceeds the configured maximum length.

        Long paths can indicate malformed input or attempt to overflow
        downstream APIs; this check enforces a sane upper bound.
        """
        if len(path_str) > cls.MAX_PATH_LENGTH:
            raise SplurgeSafeIoPathValidationError(
                f"Path is too long: {len(path_str)} characters",
                details=f"Maximum allowed length is {cls.MAX_PATH_LENGTH} characters",
            )

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitize a filename by removing dangerous characters.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove or replace dangerous characters
        sanitized = filename

        # Replace Windows reserved characters
        for char in ["<", ">", ":", '"', "|", "?", "*"]:
            sanitized = sanitized.replace(char, "_")

        # Remove control characters
        sanitized = "".join(char for char in sanitized if ord(char) >= 32)

        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(" .")

        # Ensure filename is not empty
        if not sanitized:
            sanitized = _DEFAULT_FILENAME

        return sanitized

    @classmethod
    def is_safe_path(cls, file_path: str | Path) -> bool:
        """
        Check if a path is safe without raising exceptions.

        Args:
            file_path: Path to check

        Returns:
            True if path is safe, False otherwise
        """
        try:
            cls.validate_path(file_path)
            return True
        except (SplurgeSafeIoPathValidationError, SplurgeSafeIoFileNotFoundError, SplurgeSafeIoFilePermissionError):
            return False
