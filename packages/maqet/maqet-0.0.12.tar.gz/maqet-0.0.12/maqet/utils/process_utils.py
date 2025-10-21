"""
Process management utilities.

Provides PID verification, process token management, and safe process operations.
"""

import os
import stat
import secrets
from typing import Optional, List
from pathlib import Path
from dataclasses import dataclass

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from maqet.logger import LOG


@dataclass
class ProcessVerification:
    """Result of process verification."""
    pid: int
    is_verified: bool
    process_name: str
    cmdline: str
    error: Optional[str] = None


def verify_process(
    pid: int,
    expected_names: List[str],
    expected_cmdline_tokens: List[str],
    warn_recent: float = 1.0
) -> ProcessVerification:
    """
    Verify process identity with PID reuse protection.

    Performs multi-layer verification:
    1. Process name matches expected names
    2. Command line contains expected tokens
    3. (Optional) Warns if process very recently created

    Args:
        pid: Process ID to verify
        expected_names: List of acceptable process names (e.g., ["python", "python3"])
        expected_cmdline_tokens: Tokens that must appear in cmdline (e.g., ["maqet", "vm_runner"])
        warn_recent: Warn if process created within this many seconds (default 1.0)

    Returns:
        ProcessVerification with verification result

    Raises:
        ValueError: If process exists but doesn't match verification criteria

    Example:
        # Verify QEMU process
        result = verify_process(
            qemu_pid,
            expected_names=["qemu-system-x86_64", "qemu"],
            expected_cmdline_tokens=[vm_id, vm_name]
        )

        # Verify runner process
        result = verify_process(
            runner_pid,
            expected_names=["python", "python3"],
            expected_cmdline_tokens=["maqet", "vm_runner"]
        )
    """
    if PSUTIL_AVAILABLE:
        try:
            import psutil
            process = psutil.Process(pid)

            # Check 1: Process name matches
            process_name = process.name().lower()
            name_match = any(name.lower() in process_name for name in expected_names)

            if not name_match:
                error = (
                    f"PID {pid} process name '{process.name()}' does not match "
                    f"expected names {expected_names}. Possible PID reuse."
                )
                LOG.error(error)
                raise ValueError(error)

            # Check 2: Command line contains expected tokens
            cmdline = process.cmdline()
            cmdline_str = " ".join(cmdline)

            tokens_found = [
                token for token in expected_cmdline_tokens
                if token.lower() in cmdline_str.lower()
            ]

            if not tokens_found:
                error = (
                    f"PID {pid} cmdline does not contain expected tokens {expected_cmdline_tokens}. "
                    f"Command: {' '.join(cmdline[:3])}... Possible PID reuse."
                )
                LOG.error(error)
                raise ValueError(error)

            # Check 3: Recent creation warning
            if warn_recent > 0:
                import time
                create_time = process.create_time()
                if time.time() - create_time < warn_recent:
                    LOG.warning(
                        f"PID {pid} created very recently ({time.time() - create_time:.2f}s ago). "
                        f"Possible PID reuse - verify this is correct process."
                    )

            LOG.debug(f"Verified PID {pid} matches expected process")

            return ProcessVerification(
                pid=pid,
                is_verified=True,
                process_name=process.name(),
                cmdline=cmdline_str
            )

        except psutil.NoSuchProcess:
            raise ValueError(f"PID {pid} does not exist")

        except psutil.AccessDenied:
            raise ValueError(f"Access denied when checking PID {pid}")

    else:
        # Fallback: Check /proc/{pid}/cmdline
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                cmdline_bytes = f.read()
                cmdline = cmdline_bytes.decode("utf-8", errors="ignore")

            # Check name (approximate - cmdline has first arg)
            name_match = any(name.lower() in cmdline.lower() for name in expected_names)
            if not name_match:
                error = f"PID {pid} cmdline does not match expected names {expected_names}"
                LOG.error(error)
                raise ValueError(error)

            # Check tokens
            tokens_found = [
                token for token in expected_cmdline_tokens
                if token.lower() in cmdline.lower()
            ]

            if not tokens_found:
                error = f"PID {pid} cmdline does not contain expected tokens {expected_cmdline_tokens}"
                LOG.error(error)
                raise ValueError(error)

            LOG.debug(f"Verified PID {pid} matches expected process (via /proc)")

            return ProcessVerification(
                pid=pid,
                is_verified=True,
                process_name=cmdline.split('\0')[0] if '\0' in cmdline else cmdline[:50],
                cmdline=cmdline
            )

        except FileNotFoundError:
            raise ValueError(f"PID {pid} does not exist")
