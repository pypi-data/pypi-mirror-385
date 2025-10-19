"""venvmngr public API.

This package provides helpers to create and manage Python virtual
environments using either the standard library ("venv") or the
"uv" workflow. The public symbols imported here form the convenience
API for external consumers.

Exports:
- `VenvManager`: Standard library venv manager.
- `UVVenvManager`: uv-based environment manager.
- `create_virtual_env`: Convenience constructor on `VenvManager`.
- `acreate_virtual_env`: Async variant of `create_virtual_env`.
- `get_or_create_virtual_env`: Ensure or return an environment.
- `aget_or_create_virtual_env`: Async variant of `get_or_create_virtual_env`.
- `get_virtual_env`: Return a manager for an existing env.
- `locate_system_pythons`: Probe available system Python interpreters.
- `alocate_system_pythons`: Async system Python discovery.
- `get_python_executable`: Resolve a usable Python interpreter path.
"""

from ._venv import VenvManager
from .utils import locate_system_pythons, get_python_executable, alocate_system_pythons
from ._uv import UVVenvManager

create_virtual_env = VenvManager.create_virtual_env
acreate_virtual_env = VenvManager.acreate_virtual_env
get_or_create_virtual_env = VenvManager.get_or_create_virtual_env
aget_or_create_virtual_env = VenvManager.aget_or_create_virtual_env
get_virtual_env = VenvManager.get_virtual_env

__all__ = [
    "VenvManager",
    "create_virtual_env",
    "acreate_virtual_env",
    "get_or_create_virtual_env",
    "aget_or_create_virtual_env",
    "get_virtual_env",
    "locate_system_pythons",
    "alocate_system_pythons",
    "get_python_executable",
    "UVVenvManager",
]
