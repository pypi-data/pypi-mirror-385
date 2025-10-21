# MAQET

**Warning:** Most of the code was written using AI. This product is a work in progress and should not be used in production environments under any circumstances.

**MAQET** (M4x0n's QEMU Tool) is a VM management system that implements unified API generation. Methods decorated with `@api_method` automatically become CLI commands, Python API methods, and configuration-driven calls.

## Quick Start

### Installation

```bash
pip install maqet
```

**Optional Dependencies:**

- `psutil` - Enhanced process management and validation (recommended)

  ```bash
  pip install psutil
  ```

  Without psutil, basic PID tracking still works but ownership validation is skipped.

## Breaking Changes

### v0.0.8+: QEMU Vendoring

MAQET v0.0.8+ vendors QEMU Python bindings internally for reliable installation.

**Before** (v0.0.7 and earlier):

```bash
pip install maqet[qemu]  # DON'T USE ANYMORE
```

**Now** (v0.0.8+):

```bash
pip install maqet  # QEMU bindings included automatically
```

**Why?** The official `qemu.qmp` PyPI package had packaging issues. Vendoring ensures reliable installation across all platforms.

**For existing users**: Simply run `pip install --upgrade maqet`. No code changes needed if you use MAQET's API methods.

### v0.0.11: License Change

MAQET changed from MIT to GPL-2.0-only due to vendored QEMU code (GPL-2.0).

**Impact**:

- CLI usage: No impact
- Library usage in GPL-compatible projects: No impact
- Library usage in proprietary/MIT projects: May require license review

See [Migration Guide](docs/MIGRATION.md) for details.

### v0.0.11: Security Improvements

**Automatic** - no action required:

- Unix socket permissions: Now 0600 (user-only access)
- Path traversal protection: System directories blocked
- Database performance: 100x faster with 100+ VMs

**Action required** if your config uses system directories:

```yaml
# Before (blocked in v0.0.11):
storage:
  - file: /etc/disk.qcow2  # ValueError

# After (use user directories):
storage:
  - file: ~/vms/disk.qcow2  # OK
```

See [CHANGELOG](CHANGELOG.md) for complete details.

### Core Concept

Write once, use everywhere. A single method becomes a CLI command, Python API, and configuration option:

```python
@api_method(cli_name="start", description="Start a virtual machine", category="vm")
def start(self, vm_id: str, detach: bool = False):
    """Start a virtual machine."""
    # Single implementation
```

This automatically creates:

- **CLI**: `maqet start myvm --detach`
- **Python API**: `maqet.start("myvm", detach=True)`
- **Config**: VM settings only (no commands in YAML)

## Usage

### Command Line Interface

```bash
# Create a VM
maqet add --config config.yaml --name myvm

# Start VM
maqet start myvm

# List all VMs
maqet ls

# Check VM status
maqet status myvm

# Execute QMP command
maqet qmp myvm system_powerdown

# Remove VM
maqet rm myvm --force
```

### Python API

```python
from maqet import Maqet

maqet = Maqet()

# Create and start VM
vm_id = maqet.add(name='myvm', memory='4G', cpu=2)
maqet.start(vm_id)

# Manage VM
status = maqet.status(vm_id)
maqet.qmp(vm_id, 'system_powerdown')
maqet.rm(vm_id, force=True)
```

### Configuration Files

```yaml
# config.yaml - VM configuration only
name: myvm
binary: /usr/bin/qemu-system-x86_64
memory: 4G
cpu: 2
storage:
  - name: hdd
    size: 20G
    type: qcow2
    interface: virtio
```

```bash
# Use configuration file
maqet add --config config.yaml
maqet start myvm --detach
```

**Configuration Features:**

- Deep-merge multiple config files
- Lists are concatenated (storage, network)
- Command-line args override config values
- Full QEMU argument support

See [Configuration Guide](docs/user-guide/configuration.md) for details.

## Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `add` | Create new VM | `maqet add --config config.yaml --name myvm` |
| `start` | Start VM | `maqet start myvm` |
| `stop` | Stop VM | `maqet stop myvm --force` |
| `rm` | Remove VM | `maqet rm myvm --force` |
| `ls` | List VMs | `maqet ls --status running` |
| `status` | Show VM status | `maqet status myvm` |
| `apply` | Apply configuration | `maqet apply myvm --memory 8G` |
| `snapshot` | Manage snapshots | `maqet snapshot myvm create hdd snap1` |

### QMP Commands

| Command | Description | Example |
|---------|-------------|---------|
| `qmp keys` | Send key combination | `maqet qmp keys myvm ctrl alt f2` |
| `qmp type` | Type text to VM | `maqet qmp type myvm "hello world"` |
| `qmp screendump` | Take screenshot | `maqet qmp screendump myvm screenshot.ppm` |
| `qmp pause` | Pause VM | `maqet qmp pause myvm` |
| `qmp resume` | Resume VM | `maqet qmp resume myvm` |
| `qmp device-add` | Hot-plug device | `maqet qmp device-add myvm usb-storage` |
| `qmp device-del` | Hot-unplug device | `maqet qmp device-del myvm usb1` |

### Global Options

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Increase verbosity: -v=warnings, -vv=info, -vvv=debug (default: errors only) |
| `--data-dir` | Override data directory |
| `--log-file` | Enable file logging |

## Documentation

### Full Documentation

- **[Documentation Index](docs/README.md)** - Complete documentation portal
- **[Architecture](docs/architecture/)** - Internal architecture and design
- **[Development](docs/development/)** - Contributing and development guides
- **[Deployment](docs/deployment/)** - Production deployment
- **[Reference](docs/reference/)** - Technical references

### Architecture

- **Unified API System** - Single methods generate CLI, Python API, and config
- **State Management** - SQLite backend with XDG compliance
- **QEMU Integration** - Full QMP protocol support
- **Storage System** - QCOW2, Raw, VirtFS support with snapshots

See [QEMU Internal Architecture](docs/architecture/QEMU_INTERNAL_ARCHITECTURE.md) for details.

### Development

#### Running Tests

Maqet uses pytest with parallel execution support for fast testing.

**Quick Commands:**

```bash
# Run all tests in parallel (recommended) - ~54 seconds
pytest -n auto

# Run all tests serially (for debugging) - ~120 seconds
pytest

# Run specific test categories in parallel
pytest -n auto tests/unit/         # Unit tests (~20s)
pytest -n auto tests/integration/  # Integration tests (~25s)
pytest -n auto tests/e2e/          # End-to-end tests (~15s)
pytest -n auto tests/performance/  # Performance tests (~10s)

# Run with coverage
pytest -n auto --cov=maqet --cov-report=html

# Run and stop on first failure
pytest -n auto -x
```

**Test Organization:**

- **Unit Tests** (`tests/unit/`): Fast, isolated, fully mocked
- **Integration Tests** (`tests/integration/`): Real database, mocked processes
- **E2E Tests** (`tests/e2e/`): Complete workflows with real components
- **Performance Tests** (`tests/performance/`): Benchmarks and regression tests

**ProcessTestHarness:**

Reliable subprocess testing with /proc stabilization:

```python
from tests.utils.process_harness import ProcessTestHarness

with ProcessTestHarness(["sleep", "60"]) as harness:
    # Process guaranteed ready, /proc populated
    verify_process(harness.pid, ...)
# Automatic cleanup
```

**Connection Pooling:**

StateManager uses connection pooling for 10-50x faster database queries:

- Pool of 5 reusable connections for reads
- Dedicated connections for writes (avoid lock contention)
- Thread-safe with SQLite WAL mode

**Parallel vs Serial Execution:**

Use **parallel mode** (default):

- Fast test execution (55% faster)
- Simulates concurrent usage patterns
- Recommended for regular development

Use **serial mode** when:

- Debugging test failures
- Analyzing test output carefully
- Running under debugger (pdb)

**Pre-commit Testing:**

For fast pre-commit checks, run E2E tests in parallel:

```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest -n auto tests/e2e/ --maxfail=1 -q
```

E2E tests complete in ~15 seconds with parallel execution.

**Writing Parallel-Safe Tests:**

See [tests/PARALLEL_TESTING.md](tests/PARALLEL_TESTING.md) for:

- Pytest-xdist execution model
- Common pitfalls and solutions
- Best practices and patterns
- Debugging strategies

**Test Requirements:**

Tests require:

- Python 3.12+
- pytest and plugins (installed with `pip install -e ".[dev]"`)
- Optional: QEMU for E2E tests (skipped if not installed)

See [tests/README.md](tests/README.md) for detailed testing documentation and [docs/development/TESTING.md](docs/development/TESTING.md) for contributing guidelines.

### Roadmap

See [Roadmap](docs/development/ROADMAP.md) and [Future Features](docs/development/FUTURE_FEATURES.md) for planned improvements.

## Features

- **Write Once, Use Everywhere** - Single method for CLI, API, and config
- **XDG Compliant** - Follows Linux directory standards
- **Production Ready** - Security hardened, tested, robust error handling
- **Full QMP Support** - Complete QEMU Machine Protocol integration
- **Snapshot Management** - Create, load, list, and delete snapshots
- **Hot-plug Support** - Add/remove devices while VM is running

## Security

Maqet implements defense-in-depth security for VM operations:

### Authentication Secret Protection

- **TOCTOU Protection**: File descriptor-based atomic operations prevent race conditions
- **O_NOFOLLOW**: Prevents symlink attacks on secret files
- **Permission Validation**: Enforces 0600 (user-only) permissions
- **Ownership Verification**: Ensures secrets owned by current user

### Input Validation

- **Command Injection Prevention**: Shell metacharacter detection
- **Path Traversal Prevention**: ".." sequence detection
- **Argument Injection Prevention**: Leading hyphen checks
- **Resource Limits**: Length and size validation

### Security Module

All security-sensitive inputs validated through `maqet.security.validation.InputValidator`:

- VM IDs and names
- Filesystem paths
- Binary paths

### Threat Model

- Attacker cannot read secrets via symlink attacks
- Attacker cannot inject commands via VM IDs
- Attacker cannot escape data directories via path traversal
- Attacker cannot manipulate process arguments

## Contributing

Contributions welcome! See [Development Guide](docs/development/) for contributing guidelines.

## License

GNU General Public License v2.0 - see [LICENSE](LICENSE) file for details.
