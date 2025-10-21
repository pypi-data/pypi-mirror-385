# Code Review: Utility Creation Analysis - Phase 2 Session

## Review Metrics

- **Files Modified**: 7 core files
- **Critical Issues**: 0
- **High Priority**: 2 (Utility Extraction Opportunities)
- **Medium Priority**: 1 (Consistency)
- **Suggestions**: 2

## Executive Summary

During Phase 2 implementation (commit 1d9b400), critical security and correctness issues were successfully addressed. However, **NO utility modules were created** to consolidate duplicated logic patterns across multiple files. This review identifies specific duplication patterns that violate the DRY (Don't Repeat Yourself) principle and should be extracted into utility modules.

The session focused on implementing security features rather than refactoring common utilities. This is understandable given the critical nature of security fixes, but creates technical debt that should be addressed before considering Phase 2 "complete."

---

## HIGH Priority - Utility Extraction Needed

### 1. Socket Path Resolution - Duplicated in 3 Files

**Impact**: High (Maintenance burden, potential divergence)
**Files Affected**:

- /mnt/internal/git/m4x0n/the-linux-project/maqet/maqet/process_spawner.py:289-320
- /mnt/internal/git/m4x0n/the-linux-project/maqet/maqet/vm_runner.py:479-502
- /mnt/internal/git/m4x0n/the-linux-project/maqet/maqet/ipc/runner_client.py:346-367

**Root Cause Analysis**:
The same socket path resolution logic is duplicated across three different modules. Each implementation:

1. Checks XDG_RUNTIME_DIR environment variable
2. Falls back to /run/user/{uid}
3. Falls back to /tmp/maqet-{uid}
4. Appends /maqet/sockets/{vm_id}.sock

This creates multiple points of failure if the logic needs to change. The code even includes a comment "This MUST match the socket path used in vm_runner.py!" which is a clear code smell indicating missing abstraction.

**Current Duplication Evidence**:

process_spawner.py (lines 289-320):

```python
def get_socket_path(vm_id: str) -> Path:
    """
    Get Unix socket path for VM runner.

    This MUST match the socket path used in vm_runner.py!  # CODE SMELL!
    """
    runtime_dir_base = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    if not Path(runtime_dir_base).exists():
        socket_dir = Path(f"/tmp/maqet-{os.getuid()}") / "sockets"
    else:
        runtime_dir = Path(runtime_dir_base) / "maqet"
        socket_dir = runtime_dir / "sockets"
    socket_dir.mkdir(parents=True, exist_ok=True)
    return socket_dir / f"{vm_id}.sock"
```

vm_runner.py (lines 479-502):

```python
def _get_socket_path(self) -> Path:
    """Get Unix socket path for this VM."""
    runtime_dir_base = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    if not Path(runtime_dir_base).exists():
        # Fallback to /tmp
        # [IDENTICAL LOGIC REPEATED]
```

runner_client.py (lines 346-367):

```python
def _get_socket_path(self) -> Path:
    """Get Unix socket path for this VM."""
    runtime_dir_base = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    if not Path(runtime_dir_base).exists():
        # [IDENTICAL LOGIC REPEATED AGAIN]
```

**Solution - Create maqet/utils/paths.py**:

```python
"""
Path utility functions for maqet.

Centralized path resolution for sockets, logs, and runtime directories.
"""

import os
from pathlib import Path
from typing import Optional


def get_runtime_dir() -> Path:
    """
    Get maqet runtime directory.

    Priority:
    1. $XDG_RUNTIME_DIR/maqet (if XDG_RUNTIME_DIR exists)
    2. /run/user/{uid}/maqet (if directory exists)
    3. /tmp/maqet-{uid} (fallback)

    Creates directory if it doesn't exist.

    Returns:
        Path to runtime directory

    Example:
        runtime_dir = get_runtime_dir()
        # Returns: /run/user/1000/maqet or /tmp/maqet-1000
    """
    runtime_dir_base = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")

    if Path(runtime_dir_base).exists():
        runtime_dir = Path(runtime_dir_base) / "maqet"
    else:
        runtime_dir = Path(f"/tmp/maqet-{os.getuid()}")

    runtime_dir.mkdir(parents=True, exist_ok=True)
    return runtime_dir


def get_socket_path(vm_id: str) -> Path:
    """
    Get Unix socket path for VM runner.

    Socket location: {runtime_dir}/sockets/{vm_id}.sock

    Args:
        vm_id: VM identifier

    Returns:
        Path to Unix socket

    Example:
        socket_path = get_socket_path("vm1")
        # Returns: /run/user/1000/maqet/sockets/vm1.sock
    """
    socket_dir = get_runtime_dir() / "sockets"
    socket_dir.mkdir(parents=True, exist_ok=True)
    return socket_dir / f"{vm_id}.sock"


def get_log_path(vm_id: str, log_type: str = "vm") -> Path:
    """
    Get log file path for VM.

    Args:
        vm_id: VM identifier
        log_type: Type of log ("vm", "qemu", "runner")

    Returns:
        Path to log file

    Example:
        log_path = get_log_path("vm1", "qemu")
        # Returns: /run/user/1000/maqet/logs/vm1-qemu.log
    """
    log_dir = get_runtime_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / f"{vm_id}-{log_type}.log"


def get_pid_path(vm_id: str, process_type: str = "runner") -> Path:
    """
    Get PID file path.

    Args:
        vm_id: VM identifier
        process_type: Type of process ("runner", "qemu")

    Returns:
        Path to PID file

    Example:
        pid_path = get_pid_path("vm1", "runner")
        # Returns: /run/user/1000/maqet/pids/vm1-runner.pid
    """
    pid_dir = get_runtime_dir() / "pids"
    pid_dir.mkdir(parents=True, exist_ok=True)
    return pid_dir / f"{vm_id}-{process_type}.pid"
```

**Migration Steps**:

1. Create maqet/utils/**init**.py:

```python
"""Utility modules for maqet."""

from .paths import get_runtime_dir, get_socket_path, get_log_path, get_pid_path

__all__ = ["get_runtime_dir", "get_socket_path", "get_log_path", "get_pid_path"]
```

2. Update process_spawner.py:

```python
# OLD (line 289-320):
def get_socket_path(vm_id: str) -> Path:
    # [32 lines of duplicated code]

# NEW (line 289):
from maqet.utils.paths import get_socket_path  # Import from utility module
```

3. Update vm_runner.py:

```python
# OLD (line 479-502):
def _get_socket_path(self) -> Path:
    # [24 lines of duplicated code]

# NEW (line 128):
from maqet.utils.paths import get_socket_path

# NEW (line 479):
def _get_socket_path(self) -> Path:
    """Get Unix socket path for this VM."""
    return get_socket_path(self.vm_id)
```

4. Update runner_client.py:

```python
# OLD (line 346-367):
def _get_socket_path(self) -> Path:
    # [22 lines of duplicated code]

# NEW (line 346):
def _get_socket_path(self) -> Path:
    """Get Unix socket path for this VM."""
    return get_socket_path(self.vm_id)
```

**Benefits**:

- Single source of truth for path resolution
- Easier to modify path logic (only one place to change)
- Can add get_log_path() and get_pid_path() utilities
- Eliminates "MUST match" comments (replaced with shared function)
- Reduces code by approximately 60 lines
- Makes testing easier (mock one function instead of three)

---

### 2. PID Verification Logic - Incomplete Abstraction

**Impact**: High (Security - PID reuse vulnerability)
**Files Affected**:

- /mnt/internal/git/m4x0n/the-linux-project/maqet/maqet/managers/vm_manager.py:387-483
- /mnt/internal/git/m4x0n/the-linux-project/maqet/maqet/process_spawner.py:351-411

**Root Cause Analysis**:
Phase 2 implemented excellent PID verification for QEMU processes (_verify_qemu_process) but did NOT apply the same verification to runner processes (kill_runner). This creates an asymmetric security posture where QEMU PIDs are protected but runner PIDs are vulnerable to the same PID reuse attack.

The self-review document (PHASE2_SELF_REVIEW.md:300-414) already identified this issue as "IMPORTANT" but it was not addressed in the implementation.

**Current Implementation Gap**:

vm_manager.py - QEMU verification (IMPLEMENTED):

```python
def _verify_qemu_process(self, qemu_pid: int, vm_id: str, vm_name: str) -> bool:
    """Verify PID belongs to correct QEMU process before killing."""
    if PSUTIL_AVAILABLE:
        import psutil
        try:
            process = psutil.Process(qemu_pid)

            # Check 1: Process name contains "qemu"
            process_name = process.name().lower()
            if "qemu" not in process_name:
                raise VMManagerError("PID is not QEMU process")

            # Check 2: Command line contains VM ID or name
            cmdline = " ".join(process.cmdline())
            if vm_id not in cmdline and vm_name not in cmdline:
                raise VMManagerError("PID does not match VM")

            # Check 3: Process start time warning
            create_time = process.create_time()
            if time.time() - create_time < 1.0:
                LOG.warning("PID created very recently - possible reuse")

            return True
```

process_spawner.py - Runner killing (NOT VERIFIED):

```python
def kill_runner(runner_pid: int, force: bool = False) -> bool:
    """Kill VM runner process with PID reuse protection."""  # COMMENT IS A LIE!

    if not is_runner_alive(runner_pid):  # Only checks if PID exists
        return False

    try:
        if force:
            os.kill(runner_pid, 9)  # SIGKILL - NO VERIFICATION!
        else:
            os.kill(runner_pid, 15)  # SIGTERM - NO VERIFICATION!
        return True
    except ProcessLookupError:
        return False
```

**Solution - Create maqet/utils/process_utils.py**:

```python
"""
Process utility functions for maqet.

PID verification and process management utilities.
"""

import os
import time
from pathlib import Path
from typing import Optional, Tuple

from ..logger import LOG

# Optional dependency
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class ProcessVerificationError(Exception):
    """Process verification failed - PID doesn't match expected process."""


def verify_process_identity(
    pid: int,
    expected_name_fragment: str,
    expected_cmdline_fragments: list[str],
    process_type: str = "process"
) -> bool:
    """
    Verify PID belongs to expected process before killing.

    Prevents PID reuse attacks by checking:
    1. Process name contains expected fragment
    2. Command line contains at least one expected fragment
    3. Process start time (warning for recent PIDs)

    Args:
        pid: Process ID to verify
        expected_name_fragment: Expected string in process name (e.g., "qemu", "maqet")
        expected_cmdline_fragments: List of strings, at least one must be in cmdline
        process_type: Description for error messages (e.g., "QEMU process", "runner")

    Returns:
        True if verified, False if process doesn't exist

    Raises:
        ProcessVerificationError: If PID exists but doesn't match expected process

    Example:
        # Verify QEMU process
        verify_process_identity(1234, "qemu", ["vm-test", "test-vm"], "QEMU")

        # Verify runner process
        verify_process_identity(5678, "maqet", ["vm_runner", "vm-test"], "runner")
    """
    if PSUTIL_AVAILABLE:
        return _verify_with_psutil(
            pid, expected_name_fragment, expected_cmdline_fragments, process_type
        )
    else:
        return _verify_with_proc(
            pid, expected_name_fragment, expected_cmdline_fragments, process_type
        )


def _verify_with_psutil(
    pid: int,
    expected_name_fragment: str,
    expected_cmdline_fragments: list[str],
    process_type: str
) -> bool:
    """Verify process using psutil library."""
    try:
        process = psutil.Process(pid)

        # Check 1: Process name
        process_name = process.name().lower()
        if expected_name_fragment.lower() not in process_name:
            LOG.error(
                f"PID {pid} is not a {process_type} "
                f"(name: {process.name()}). Possible PID reuse."
            )
            raise ProcessVerificationError(
                f"PID {pid} does not match expected {process_type}. "
                f"Current process: {process.name()}"
            )

        # Check 2: Command line
        cmdline = " ".join(process.cmdline()).lower()
        if not any(fragment.lower() in cmdline for fragment in expected_cmdline_fragments):
            LOG.error(
                f"PID {pid} command line does not contain expected fragments. "
                f"Possible PID reuse."
            )
            raise ProcessVerificationError(
                f"PID {pid} command line does not match expected {process_type}. "
                f"Expected one of: {expected_cmdline_fragments}"
            )

        # Check 3: Process start time warning
        create_time = process.create_time()
        age = time.time() - create_time
        if age < 1.0:
            LOG.warning(
                f"PID {pid} was created very recently ({age:.2f}s ago). "
                f"This could indicate PID reuse."
            )

        LOG.debug(f"PID {pid} verified as {process_type}")
        return True

    except psutil.NoSuchProcess:
        LOG.debug(f"PID {pid} does not exist")
        return False
    except psutil.AccessDenied:
        LOG.warning(f"PID {pid} exists but access denied (different user)")
        return False


def _verify_with_proc(
    pid: int,
    expected_name_fragment: str,
    expected_cmdline_fragments: list[str],
    process_type: str
) -> bool:
    """Verify process using /proc filesystem (fallback)."""
    try:
        # Check if process exists
        os.kill(pid, 0)

        # Read command line
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                cmdline = f.read().decode("utf-8", errors="ignore")

                # Check command line contains expected fragments
                if not any(fragment.lower() in cmdline.lower() for fragment in expected_cmdline_fragments):
                    LOG.error(
                        f"PID {pid} command line does not contain expected fragments "
                        f"(using /proc fallback). Possible PID reuse."
                    )
                    raise ProcessVerificationError(
                        f"PID {pid} does not match expected {process_type}"
                    )

                LOG.debug(f"PID {pid} verified as {process_type} (using /proc)")
                return True

        except FileNotFoundError:
            # /proc not available or process gone
            return False

    except ProcessLookupError:
        return False
    except PermissionError:
        LOG.warning(f"PID {pid} exists but permission denied")
        return False


def is_process_alive(pid: int, check_zombie: bool = True) -> bool:
    """
    Check if process is alive.

    Args:
        pid: Process ID
        check_zombie: If True, return False for zombie processes

    Returns:
        True if process exists and is not zombie, False otherwise
    """
    if pid is None or pid <= 0:
        return False

    if PSUTIL_AVAILABLE:
        try:
            process = psutil.Process(pid)
            if check_zombie:
                return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
            else:
                return process.is_running()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    else:
        # Fallback: Check /proc
        try:
            os.kill(pid, 0)
            if check_zombie:
                # Read zombie state from /proc/{pid}/stat
                with open(f"/proc/{pid}/stat", "r") as f:
                    stat = f.read()
                    state_start = stat.rfind(")") + 2
                    state = stat[state_start] if state_start < len(stat) else "?"
                    return state != "Z"
            return True
        except (ProcessLookupError, PermissionError, FileNotFoundError, IOError):
            return False
```

**Migration Steps**:

1. Create maqet/utils/**init**.py (add to existing):

```python
from .process_utils import (
    verify_process_identity,
    is_process_alive,
    ProcessVerificationError
)

__all__ = [
    # ... paths exports ...
    "verify_process_identity",
    "is_process_alive",
    "ProcessVerificationError"
]
```

2. Update vm_manager.py:

```python
from maqet.utils.process_utils import verify_process_identity, ProcessVerificationError

def _verify_qemu_process(self, qemu_pid: int, vm_id: str, vm_name: str) -> bool:
    """Verify PID belongs to correct QEMU process."""
    try:
        return verify_process_identity(
            qemu_pid,
            expected_name_fragment="qemu",
            expected_cmdline_fragments=[vm_id, vm_name],
            process_type="QEMU process"
        )
    except ProcessVerificationError as e:
        raise VMManagerError(str(e))
```

3. Update process_spawner.py (FIX THE SECURITY ISSUE):

```python
from maqet.utils.process_utils import (
    verify_process_identity,
    is_process_alive,
    ProcessVerificationError
)

def kill_runner(runner_pid: int, vm_id: str, force: bool = False) -> bool:
    """
    Kill VM runner process with PID reuse protection.

    Args:
        runner_pid: PID of runner process
        vm_id: VM identifier (for verification)
        force: If True, use SIGKILL. If False, use SIGTERM
    """
    # Verify this is actually a runner process (SECURITY FIX!)
    try:
        verified = verify_process_identity(
            runner_pid,
            expected_name_fragment="maqet",
            expected_cmdline_fragments=["vm_runner", vm_id],
            process_type="VM runner"
        )
        if not verified:
            LOG.warning(f"Runner PID {runner_pid} no longer exists")
            return False
    except ProcessVerificationError as e:
        LOG.error(f"Runner PID verification failed: {e}")
        raise RunnerSpawnError(
            f"Refusing to kill PID {runner_pid} - verification failed: {e}"
        )

    # Now safe to kill
    try:
        signal_num = 9 if force else 15
        os.kill(runner_pid, signal_num)
        LOG.info(f"Sent signal {signal_num} to runner PID {runner_pid}")
        return True
    except ProcessLookupError:
        return False
    except PermissionError as e:
        raise RunnerSpawnError(f"Permission denied killing runner: {e}")
```

**Benefits**:

- Fixes critical security vulnerability (PID reuse in kill_runner)
- Centralizes PID verification logic
- Consistent verification across QEMU and runner processes
- Reduces duplication (approximately 80 lines)
- Makes verification logic testable in isolation
- Can reuse for future process verification needs

---

## MEDIUM Priority - Consistency Issues

### 3. TYPE_CHECKING Import Pattern - Inconsistent Usage

**Impact**: Medium (Code quality, import performance)
**Files Affected**:

- /mnt/internal/git/m4x0n/the-linux-project/maqet/maqet/process_spawner.py:29-31
- /mnt/internal/git/m4x0n/the-linux-project/maqet/maqet/config/parser.py:12-14
- /mnt/internal/git/m4x0n/the-linux-project/maqet/maqet/machine.py:15-29

**Root Cause**:
The TYPE_CHECKING pattern is used to avoid circular imports and improve runtime performance by only importing types during static type checking. However, it's only used in 3 files out of the entire codebase, indicating inconsistent application of this best practice.

**Current Usage**:

process_spawner.py:

```python
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..state import StateManager  # Only imported for type checking
```

machine.py:

```python
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

if TYPE_CHECKING:
    from .maqet import Maqet
```

**Most files do NOT use this pattern**:

```python
# Direct import (potential circular dependency)
from ..state import StateManager
```

**Solution**:
Either:

1. Standardize on using TYPE_CHECKING everywhere for cross-module type hints
2. Document when to use it (e.g., "only for circular import avoidance")
3. Add to CONTRIBUTING.md or style guide

**Recommendation**:

```python
# Add to pyproject.toml or CONTRIBUTING.md

# Use TYPE_CHECKING pattern when:
# 1. Import would create circular dependency
# 2. Import is ONLY needed for type hints (not runtime)
# 3. Module is large and rarely used

# Example:
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .large_module import ExpensiveClass  # Only for type hints

def process(obj: "ExpensiveClass") -> None:  # Forward reference
    pass
```

---

## Suggestions

### 4. Message Framing Protocol - Could Be Utility Function

**Impact**: Low (Code clarity)
**Current State**: Protocol is now consistent (newline framing) but inline

**Files Using Protocol**:

- maqet/ipc/unix_socket_server.py:166-175 (reading)
- maqet/ipc/unix_socket_server.py:297-305 (writing)
- maqet/ipc/runner_client.py:244-264 (reading/writing)

**Current Implementation** (repeated 3 times):

```python
# Sending
request_data = (json.dumps(request) + "\n").encode("utf-8")
writer.write(request_data)

# Receiving
response_data = await reader.readuntil(b'\n')
response = json.loads(response_data.decode("utf-8").strip())
```

**Potential Utility** (maqet/utils/ipc_protocol.py):

```python
"""IPC protocol utilities."""

import asyncio
import json
from typing import Any, Dict


class IPCProtocolError(Exception):
    """IPC protocol errors."""


async def send_json_message(writer: asyncio.StreamWriter, message: Dict[str, Any]) -> None:
    """
    Send JSON message with newline framing.

    Args:
        writer: asyncio StreamWriter
        message: Message to send (will be JSON serialized)
    """
    data = (json.dumps(message) + "\n").encode("utf-8")
    writer.write(data)
    await writer.drain()


async def receive_json_message(
    reader: asyncio.StreamReader,
    timeout: float = 5.0
) -> Dict[str, Any]:
    """
    Receive JSON message with newline framing.

    Args:
        reader: asyncio StreamReader
        timeout: Timeout in seconds

    Returns:
        Parsed JSON message

    Raises:
        IPCProtocolError: On protocol errors
        asyncio.TimeoutError: On timeout
    """
    try:
        data = await asyncio.wait_for(reader.readuntil(b'\n'), timeout=timeout)
    except asyncio.LimitOverrunError:
        raise IPCProtocolError("Message too large or missing newline delimiter")

    if not data:
        raise IPCProtocolError("Empty message received")

    try:
        return json.loads(data.decode("utf-8").strip())
    except json.JSONDecodeError as e:
        raise IPCProtocolError(f"Invalid JSON: {e}")
```

**Recommendation**: Consider this if IPC protocol becomes more complex (e.g., adding message length prefix, compression, etc.). For now, inline implementation is acceptable.

---

### 5. Authentication HMAC Computation - Potential Utility

**Impact**: Low (Single use case currently)
**Current State**: Challenge-response authentication implemented correctly but inline

**Files**:

- maqet/ipc/runner_client.py:167-172 (client computes response)
- maqet/ipc/unix_socket_server.py:277 (server verifies with hmac.compare_digest)

**Current Implementation**:

```python
# Client
response_hash = hmac.new(
    self.auth_secret.encode("utf-8"),
    challenge.encode("utf-8"),
    hashlib.sha256
).hexdigest()

# Server
expected_response = hmac.new(
    auth_secret.encode("utf-8"),
    challenge.encode("utf-8"),
    hashlib.sha256
).hexdigest()
verified = hmac.compare_digest(response_hash, expected_response)
```

**Recommendation**: Keep inline unless authentication becomes more complex or is reused in other contexts.

---

## Summary of Findings

### What Was NOT Created (But Should Be)

1. **maqet/utils/paths.py** - Socket, log, PID path resolution
   - Eliminates ~60 lines of duplication
   - Removes "MUST match" code smell comments
   - Creates single source of truth

2. **maqet/utils/process_utils.py** - PID verification and process management
   - Eliminates ~80 lines of duplication
   - **FIXES CRITICAL SECURITY ISSUE** (kill_runner PID verification)
   - Consistent verification across all process types

### Evaluation Against DRY Principle

**FAILED** - Significant duplication remains:

- Socket path resolution: 3 identical implementations
- PID verification: Asymmetric (QEMU protected, runner vulnerable)
- Process liveness checks: Partially duplicated

### Was Utility Extraction In Scope?

**DEBATABLE**:

- Phase 2 focused on security fixes (authentication, TOCTOU, thread-safety)
- Creating utilities would have been good practice
- The self-review document identified kill_runner() issue but didn't fix it
- Time constraints may have prioritized security features over refactoring

### Should Utilities Be Created Before "Complete"?

**YES - STRONGLY RECOMMENDED**:

1. **Security Fix** (kill_runner PID verification) is CRITICAL
   - Same PID reuse vulnerability Phase 2 was supposed to fix
   - Currently only QEMU is protected, runner is vulnerable
   - This is a regression from stated goals

2. **Maintenance Burden**:
   - 3 copies of socket path logic will diverge over time
   - Already has "MUST match" comment indicating brittleness
   - Future bugs will need fixing in multiple places

3. **Testing Impact**:
   - Can't test path resolution logic without running all 3 modules
   - Can't test PID verification without vm_manager or process_spawner

---

## Recommendations

### IMMEDIATE (Before Phase 2 Complete)

1. **Create maqet/utils/process_utils.py** and fix kill_runner() PID verification
   - Priority: CRITICAL
   - Impact: Security vulnerability
   - Effort: 2-3 hours

2. **Create maqet/utils/paths.py** and consolidate socket path logic
   - Priority: HIGH
   - Impact: Maintainability
   - Effort: 1-2 hours

### SHORT TERM (Next Sprint)

3. **Add unit tests for utility modules**
   - Test path resolution with various XDG_RUNTIME_DIR scenarios
   - Test PID verification with mocked psutil and /proc
   - Test process liveness checks

4. **Document TYPE_CHECKING usage policy**
   - Add to CONTRIBUTING.md
   - Standardize across codebase

### LONG TERM (Technical Debt)

5. **Consider IPC protocol utilities** if protocol becomes more complex
6. **Evaluate other duplication patterns** across codebase

---

## Conclusion

Phase 2 implementation successfully addressed critical security issues (authentication, TOCTOU protection, thread-safety) but **did not create utility modules** to consolidate duplicated logic patterns.

**Key Findings**:

- Socket path resolution duplicated in 3 files (~60 lines)
- PID verification incomplete (security gap in kill_runner)
- TYPE_CHECKING pattern inconsistently applied

**Should utilities be created?** **YES** - Especially process_utils.py to fix the kill_runner security issue.

**Is work complete?** **NO** - Critical PID verification gap remains, creating same vulnerability Phase 2 was meant to fix.

**Next Steps**:

1. Create maqet/utils/process_utils.py (CRITICAL)
2. Create maqet/utils/paths.py (HIGH)
3. Add unit tests for utilities
4. Update Phase 2 completion checklist

---

## File References (Absolute Paths)

All paths relative to: /mnt/internal/git/m4x0n/the-linux-project/maqet/

**Files with socket path duplication**:

- maqet/process_spawner.py:289-320
- maqet/vm_runner.py:479-502
- maqet/ipc/runner_client.py:346-367

**Files with PID verification**:

- maqet/managers/vm_manager.py:387-483 (_verify_qemu_process - COMPLETE)
- maqet/process_spawner.py:351-411 (is_runner_alive, kill_runner - INCOMPLETE)

**Files with TYPE_CHECKING**:

- maqet/process_spawner.py:29-31
- maqet/config/parser.py:12-14
- maqet/machine.py:15-29

**Self-review document**:

- PHASE2_SELF_REVIEW.md (identifies kill_runner issue on line 300-414)
