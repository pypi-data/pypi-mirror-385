"""
Input validation for security-sensitive parameters.

This module provides centralized validation to prevent:
- Command injection (shell metacharacters)
- Argument injection (leading hyphens)
- Path traversal (.. sequences)
- Resource exhaustion (length limits)
- Encoding attacks (non-ASCII)
"""

import re
from pathlib import Path
from typing import Pattern, Optional, List


class ValidationError(ValueError):
    """Input validation error."""
    pass


class InputValidator:
    """Centralized input validation for security-sensitive inputs."""

    # Validation patterns
    VM_ID_PATTERN: Pattern = re.compile(r'^[a-zA-Z0-9_\-]{1,64}$')
    VM_NAME_PATTERN: Pattern = re.compile(r'^[a-zA-Z0-9_\-\.]{1,255}$')
    SOCKET_NAME_PATTERN: Pattern = re.compile(r'^[a-zA-Z0-9_\-\.]{1,100}$')

    # Dangerous characters
    SHELL_METACHARACTERS = frozenset({';', '&', '|', '`', '$', '(', ')', '<', '>', '\n', '\r'})
    PATH_TRAVERSAL_SEQUENCES = frozenset({'..', '~'})

    @classmethod
    def validate_vm_id(cls, vm_id: str) -> str:
        """
        Validate VM ID for security and correctness.

        Requirements:
        - 1-64 characters
        - Alphanumeric, underscore, hyphen only
        - Cannot start with hyphen (argument injection)
        - Cannot contain .. (path traversal)

        Args:
            vm_id: VM identifier from user input

        Returns:
            Validated vm_id (unchanged if valid)

        Raises:
            ValidationError: If vm_id is invalid
        """
        if not vm_id:
            raise ValidationError("VM ID cannot be empty")

        if not isinstance(vm_id, str):
            raise ValidationError(
                f"VM ID must be string, got {type(vm_id).__name__}"
            )

        # Check pattern
        if not cls.VM_ID_PATTERN.match(vm_id):
            raise ValidationError(
                f"Invalid VM ID '{vm_id}'. "
                f"Must contain only alphanumeric, underscore, hyphen (1-64 chars)"
            )

        # Prevent argument injection
        if vm_id.startswith('-'):
            raise ValidationError(
                f"VM ID cannot start with hyphen: '{vm_id}' "
                f"(argument injection risk)"
            )

        # Prevent path traversal
        if '..' in vm_id:
            raise ValidationError(
                f"VM ID cannot contain '..': '{vm_id}' "
                f"(path traversal risk)"
            )

        return vm_id

    @classmethod
    def validate_vm_name(cls, vm_name: str) -> str:
        """
        Validate VM name (more permissive than ID).

        Allows dots for domain-like names (e.g., "web.prod.example").
        """
        if not vm_name:
            raise ValidationError("VM name cannot be empty")

        if not cls.VM_NAME_PATTERN.match(vm_name):
            raise ValidationError(
                f"Invalid VM name '{vm_name}'. "
                f"Must contain only alphanumeric, underscore, hyphen, dot (1-255 chars)"
            )

        if vm_name.startswith('-'):
            raise ValidationError(
                f"VM name cannot start with hyphen: '{vm_name}'"
            )

        # Check for consecutive dots or path traversal
        if '..' in vm_name:
            raise ValidationError(
                f"VM name cannot contain '..': '{vm_name}'"
            )

        return vm_name

    @classmethod
    def validate_path(
        cls,
        path: Path,
        must_exist: bool = False,
        must_be_absolute: bool = False,
        allowed_prefixes: Optional[List[Path]] = None,
        description: str = "Path"
    ) -> Path:
        """
        Validate filesystem path for security.

        Args:
            path: Path to validate
            must_exist: If True, path must exist
            must_be_absolute: If True, path must be absolute
            allowed_prefixes: If provided, path must be under one of these
            description: Human-readable description for error messages

        Returns:
            Resolved absolute path

        Raises:
            ValidationError: If path is invalid or unsafe
        """
        if not path:
            raise ValidationError(f"{description} cannot be empty")

        # Convert to Path object
        if isinstance(path, str):
            path = Path(path)

        # Check for null bytes (path injection)
        path_str = str(path)
        if '\0' in path_str:
            raise ValidationError(
                f"{description} contains null byte: {path_str}"
            )

        # Check for shell metacharacters (if used in commands)
        for metachar in cls.SHELL_METACHARACTERS:
            if metachar in path_str:
                raise ValidationError(
                    f"{description} contains shell metacharacter '{metachar}': {path_str}"
                )

        # Check absolute requirement
        if must_be_absolute and not path.is_absolute():
            raise ValidationError(
                f"{description} must be absolute: {path}"
            )

        # Resolve path (follow symlinks, remove ..)
        try:
            resolved_path = path.resolve(strict=must_exist)
        except (OSError, RuntimeError) as e:
            raise ValidationError(
                f"Cannot resolve {description} '{path}': {e}"
            )

        # Check existence
        if must_exist and not resolved_path.exists():
            raise ValidationError(
                f"{description} does not exist: {resolved_path}"
            )

        # Check allowed prefixes
        if allowed_prefixes:
            is_allowed = any(
                resolved_path.is_relative_to(prefix.resolve())
                for prefix in allowed_prefixes
            )
            if not is_allowed:
                raise ValidationError(
                    f"{description} not under allowed prefixes: {resolved_path}. "
                    f"Allowed: {[str(p) for p in allowed_prefixes]}"
                )

        return resolved_path

    @classmethod
    def validate_binary_path(cls, binary_path: Path) -> Path:
        """
        Validate executable binary path.

        Checks:
        - Path exists and is a file
        - File is executable
        - File is not world-writable (security)

        Returns:
            Validated binary path

        Raises:
            ValidationError: If binary is invalid or insecure
        """
        import os
        import stat

        binary_path = cls.validate_path(
            binary_path,
            must_exist=True,
            description="Binary path"
        )

        # Check is file
        if not binary_path.is_file():
            raise ValidationError(
                f"Binary is not a file: {binary_path}"
            )

        # Check executable
        if not os.access(binary_path, os.X_OK):
            raise ValidationError(
                f"Binary is not executable: {binary_path}"
            )

        # Check not world-writable (security risk)
        stat_info = binary_path.stat()
        if stat_info.st_mode & stat.S_IWOTH:
            raise ValidationError(
                f"Binary is world-writable (insecure): {binary_path}"
            )

        return binary_path
