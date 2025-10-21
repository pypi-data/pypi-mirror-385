"""
Path resolution utilities for maqet.

Provides centralized path resolution for sockets, logs, and runtime files.
Ensures consistency across all modules and supports XDG specification.
"""

import os
from pathlib import Path


def get_socket_path(vm_id: str) -> Path:
    """
    Get Unix socket path for VM runner.

    Socket location: XDG_RUNTIME_DIR/maqet/sockets/{vm_id}.sock
    Falls back to /tmp/maqet-{uid}/sockets/ if XDG_RUNTIME_DIR not available.

    This is the single source of truth for socket path resolution.

    Args:
        vm_id: VM identifier

    Returns:
        Path to Unix socket

    Example:
        >>> get_socket_path("vm1")
        PosixPath('/run/user/1000/maqet/sockets/vm1.sock')
    """
    # Get runtime directory (prefer XDG_RUNTIME_DIR)
    runtime_dir_base = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")

    if not Path(runtime_dir_base).exists():
        # Fallback to /tmp (already includes maqet-{uid})
        socket_dir = Path(f"/tmp/maqet-{os.getuid()}") / "sockets"
    else:
        # XDG_RUNTIME_DIR exists (e.g., /run/user/1000)
        socket_dir = Path(runtime_dir_base) / "maqet" / "sockets"

    # Ensure socket directory exists
    socket_dir.mkdir(parents=True, exist_ok=True)

    return socket_dir / f"{vm_id}.sock"


def get_log_path(vm_id: str) -> Path:
    """
    Get log file path for VM runner.

    Log location: XDG_DATA_HOME/maqet/logs/vm_{vm_id}.log

    Args:
        vm_id: VM identifier

    Returns:
        Path to log file
    """
    xdg_data_home = os.environ.get(
        "XDG_DATA_HOME", os.path.expanduser("~/.local/share")
    )
    log_dir = Path(xdg_data_home) / "maqet" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    return log_dir / f"vm_{vm_id}.log"


def get_runtime_dir() -> Path:
    """
    Get maqet runtime directory.

    Returns:
        Path to runtime directory
    """
    runtime_dir_base = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")

    if not Path(runtime_dir_base).exists():
        return Path(f"/tmp/maqet-{os.getuid()}")

    return Path(runtime_dir_base) / "maqet"
