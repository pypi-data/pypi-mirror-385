"""
Archil SDK for Python
======================

A simple Python SDK for the Archil Control Plane.

Basic Usage:
    ```python
    import archil

    # Connect to Archil
    client = archil.Archil(api_key="your-key")

    # Get a disk
    disk = client.disks.list()[0]

    # Run a container on the disk
    container = disk.containers.run(
        command="python train.py",
        vcpu_count=4,
        mem_size_mib=8192
    )

    # Wait for it to complete
    completed = container.wait_for_completion(timeout=600)
    print(f"Exit code: {completed.exit_code}")
    ```
"""

# Core API
from .client import Archil, ArchilAsync
from .containers import Container, ContainerManager, PortMapping, ArchilMount, FileContent, Glob
from .disks import Disk, DiskManager, Mount, AuthorizedUser

# Exceptions
from .exceptions import (
    ArchilError,
    AuthenticationError,
    ContainerError,
    NotFoundError,
    APIError,
)

__version__ = "0.1.3"

__all__ = [
    # Core API
    "Archil",
    "ArchilAsync",
    # Containers
    "Container",
    "ContainerManager",
    "PortMapping",
    "ArchilMount",
    "FileContent",
    "Glob",
    # Disks
    "Disk",
    "DiskManager",
    "Mount",
    "AuthorizedUser",
    # Exceptions
    "ArchilError",
    "AuthenticationError",
    "ContainerError",
    "NotFoundError",
    "APIError",
]
