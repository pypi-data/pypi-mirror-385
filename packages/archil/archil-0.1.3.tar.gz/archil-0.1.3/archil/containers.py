"""Container management for Archil."""

from typing import Optional, List, Dict, Any, Union, TYPE_CHECKING
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
import time
import base64
import glob as glob_module
import os

from ._sync import synchronizer
from .exceptions import ContainerError, NotFoundError

# Maximum total file size across all files: 10 MiB
MAX_FILES_SIZE_MIB = 10
MAX_FILES_SIZE_BYTES = MAX_FILES_SIZE_MIB * 1024 * 1024

if TYPE_CHECKING:
    from .client import Archil


class FileContent:
    """
    Marker class for inline file content.

    Example:
        files={"/app/config.txt": FileContent("Hello, World!")}
    """
    def __init__(self, content: str):
        self.content = content


class Glob:
    """
    Marker class for glob patterns.

    Example:
        files={"/configs": Glob("*.yaml")}
    """
    def __init__(self, pattern: str):
        self.pattern = pattern


class PortMapping(BaseModel):
    """Port mapping configuration."""

    container_port: int
    host_port: Optional[int] = None
    protocol: str = "tcp"


class ArchilMount(BaseModel):
    """Archil filesystem mount configuration."""

    disk_id: str
    region: Optional[str] = None
    env: Optional[str] = None
    shared: bool = True


class Container(BaseModel):
    """
    Container instance.

    Attributes:
        container_id: Unique container identifier
        name: Optional container name
        status: Container status (starting, running, stopped, exited, failed)
        filesystem_id: Filesystem/disk ID
        vcpu_count: Number of vCPUs
        mem_size_mib: Memory size in MiB
        kernel: Kernel type
        base_image: Base image name
        port_mappings: Port mappings
        created_at: Creation timestamp
        updated_at: Last update timestamp
        exit_code: Exit code (if exited)
        exit_reason: Exit reason (if failed/exited)
        metadata: Optional metadata dict
    """

    container_id: str
    name: Optional[str] = None
    status: str
    filesystem_id: Optional[str] = None
    vcpu_count: int
    mem_size_mib: int
    kernel: str
    base_image: str
    port_mappings: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime
    exit_code: Optional[int] = None
    exit_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    # Private attribute for client reference (not part of Pydantic model)
    _client: Optional["Archil"] = None

    def _set_client(self, client: "Archil") -> None:
        """Internal method to set client reference."""
        self._client = client

    def wait_for_completion(self, timeout: int = 300, poll_interval: float = 1.0) -> "Container":
        """
        Wait for container to reach a terminal state (exited, stopped, or failed).

        Args:
            timeout: Maximum seconds to wait (default: 300)
            poll_interval: Seconds between status checks (default: 1.0)

        Returns:
            Updated Container instance in terminal state

        Raises:
            TimeoutError: If container doesn't complete within timeout
            RuntimeError: If container not connected to client

        Example:
            ```python
            disk = client.disks.list()[0]
            container = disk.containers.run(command="python train.py")

            # Wait for it to finish
            completed = container.wait_for_completion(timeout=600)
            print(f"Exit code: {completed.exit_code}")
            ```
        """
        if self._client is None:
            raise RuntimeError(
                "This container instance is not connected to a client. "
                "Get containers via disk.containers.run() or client.containers.get() to use wait_for_completion()"
            )

        start_time = time.time()
        terminal_states = {"exited", "stopped", "failed"}

        while time.time() - start_time < timeout:
            # Refresh container status
            updated = self._client.containers.get(self.container_id)

            # Update self with new values
            self.status = updated.status
            self.exit_code = updated.exit_code
            self.exit_reason = updated.exit_reason
            self.updated_at = updated.updated_at

            if self.status in terminal_states:
                return self

            time.sleep(poll_interval)

        raise TimeoutError(
            f"Container {self.container_id} did not complete within {timeout} seconds. "
            f"Last status: {self.status}"
        )


def _process_files(files: Optional[Dict[str, Union[FileContent, Glob, Path]]]) -> List[Dict[str, Any]]:
    """
    Process files for upload to container.

    Args:
        files: Dictionary mapping destination paths to file sources
               Sources can be: FileContent (inline), Glob (pattern), or Path (file/folder)

    Returns:
        List of file upload dictionaries with base64-encoded content

    Raises:
        ValueError: If total file size exceeds MAX_FILES_SIZE_MIB or invalid source type
    """
    if not files:
        return []

    result = []
    total_size = 0

    for dest_path, source in files.items():
        if isinstance(source, FileContent):
            # Inline content
            content_bytes = source.content.encode('utf-8')
            total_size += len(content_bytes)
            encoded = base64.b64encode(content_bytes).decode('ascii')

            result.append({
                "path": dest_path,
                "content": encoded,
                "mode": "0644"
            })

        elif isinstance(source, Glob):
            # Glob pattern - find matching files
            matched_files = glob_module.glob(source.pattern, recursive=True)
            if not matched_files:
                raise ValueError(f"Glob pattern '{source.pattern}' matched no files")

            for file_path in matched_files:
                if os.path.isfile(file_path):
                    file_size, encoded = _read_and_encode_file(file_path)
                    total_size += file_size

                    # Preserve relative structure: /dest/path/filename.ext
                    filename = os.path.basename(file_path)
                    full_dest = os.path.join(dest_path, filename)

                    result.append({
                        "path": full_dest,
                        "content": encoded,
                        "mode": "0644"
                    })

        elif isinstance(source, Path):
            if source.is_file():
                # Single file
                file_size, encoded = _read_and_encode_file(str(source))
                total_size += file_size

                result.append({
                    "path": dest_path,
                    "content": encoded,
                    "mode": "0755" if os.access(source, os.X_OK) else "0644"
                })

            elif source.is_dir():
                # Folder - recursively copy all files
                for root, _, filenames in os.walk(source):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        file_size, encoded = _read_and_encode_file(file_path)
                        total_size += file_size

                        # Preserve folder structure
                        rel_path = os.path.relpath(file_path, source)
                        full_dest = os.path.join(dest_path, rel_path)

                        result.append({
                            "path": full_dest,
                            "content": encoded,
                            "mode": "0755" if os.access(file_path, os.X_OK) else "0644"
                        })
            else:
                raise ValueError(f"Path {source} is neither a file nor a directory")

        else:
            raise ValueError(
                f"Invalid file source type: {type(source).__name__}. "
                f"Must be FileContent, Glob, or Path"
            )

    # Validate total size
    if total_size > MAX_FILES_SIZE_BYTES:
        raise ValueError(
            f"Total file size ({total_size / 1024 / 1024:.1f} MiB) "
            f"exceeds limit of {MAX_FILES_SIZE_MIB} MiB. "
            f"For larger files, use an Archil disk or S3."
        )

    return result


def _read_and_encode_file(file_path: str) -> tuple[int, str]:
    """
    Read a file and return its size and base64-encoded content.

    Returns:
        Tuple of (file_size_bytes, base64_encoded_content)
    """
    with open(file_path, 'rb') as f:
        content = f.read()

    file_size = len(content)
    encoded = base64.b64encode(content).decode('ascii')

    return file_size, encoded


@synchronizer.create_blocking
class ContainerManager:
    """
    Manager for container operations.

    Access via `client.containers`.
    """

    def __init__(self, client: "Archil"):  # type: ignore
        self._client = client

    async def create(
        self,
        archil_mount: ArchilMount,
        vcpu_count: int = 1,
        mem_size_mib: int = 128,
        kernel: str = "6.11-slim",
        base_image: str = "ubuntu-22.04",
        initialization_script: Optional[str] = None,
        command: Optional[str] = None,
        port_mappings: Optional[List[PortMapping]] = None,
        env: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Union[FileContent, Glob, Path]]] = None,
    ) -> Container:
        """
        Create a new container with required disk mount.

        Args:
            archil_mount: Required Archil filesystem mount
            vcpu_count: Number of vCPUs (default: 1)
            mem_size_mib: Memory size in MiB (default: 128)
            kernel: Kernel type - "6.11-slim" or "6.11-full" (default: "6.11-slim")
            base_image: Base image (default: "ubuntu-22.04")
            initialization_script: Optional script to run during container setup
            command: Optional command to execute and exit immediately
            port_mappings: Optional list of port mappings
            env: Optional dictionary of environment variables to pass to all exec sessions.
                 Special variables are automatically added: ARCHIL_CONTAINER_ID, ARCHIL_REGION, ARCHIL_DISK_ID
            metadata: Optional metadata dictionary
            files: Optional dictionary mapping destination paths to file sources.
                   Sources can be: FileContent (inline), Glob (pattern), or Path (file/folder).
                   Maximum total size: 10 MiB across all files.

        Returns:
            Container instance

        Example:
            ```python
            from pathlib import Path
            from archil import FileContent, Glob

            # Create a container with required disk mount
            container = await client.containers.create(
                archil_mount=ArchilMount(
                    disk_id="disk_abc123",
                    env="production",
                ),
                vcpu_count=2,
                mem_size_mib=512
            )

            # Create a container with a command (runs and exits)
            container = await client.containers.create(
                archil_mount=ArchilMount(
                    disk_id="disk_abc123",
                    env="production",
                ),
                command="python train.py",
                vcpu_count=4,
                mem_size_mib=2048
            )

            # Create a container with files
            container = await client.containers.create(
                archil_mount=ArchilMount(
                    disk_id="disk_abc123",
                    env="production",
                ),
                files={
                    "/app/config.json": Path("config.json"),      # Single file
                    "/app/script.py": Path("script.py"),          # Single file
                    "/app": Path("./app_folder"),                 # Copy entire folder
                    "/configs": Glob("*.yaml"),                   # Glob pattern
                    "/inline.txt": FileContent("Hello, World!"),  # Inline content
                }
            )

            # Create a container with initialization, port mappings, and environment variables
            container = await client.containers.create(
                archil_mount=ArchilMount(
                    disk_id="disk_abc123",
                    env="production",
                ),
                initialization_script="pip install torch",
                port_mappings=[
                    PortMapping(container_port=8080, protocol="tcp")
                ],
                env={
                    "DATABASE_URL": "postgres://...",
                    "API_KEY": "secret-key",
                    "DEBUG_MODE": "true"
                }
            )
            ```
        """
        payload: Dict[str, Any] = {
            "vcpu_count": vcpu_count,
            "mem_size_mib": mem_size_mib,
            "kernel": kernel,
            "base_image": base_image,
        }

        if initialization_script:
            payload["initialization_script"] = initialization_script

        if command:
            payload["command"] = command

        # archil_mount is now required
        payload["archil_mount"] = archil_mount.dict()

        if port_mappings:
            payload["port_mappings"] = [pm.dict() for pm in port_mappings]

        if env:
            payload["env"] = env

        if metadata:
            payload["metadata"] = metadata

        # Process and include files if provided
        if files:
            processed_files = _process_files(files)
            if processed_files:
                payload["files"] = processed_files

        try:
            data = await self._client.request("POST", "/api/containers", json=payload)
            container = Container(**data)
            container._set_client(self._client)
            return container
        except Exception as e:
            raise ContainerError(f"Failed to create container: {str(e)}")

    async def get(self, container_id: str) -> Container:
        """
        Get container by ID.

        Args:
            container_id: Container ID

        Returns:
            Container instance

        Raises:
            NotFoundError: If container not found

        Example:
            ```python
            container = await client.containers.get("cntr_abc123")
            print(f"Status: {container.status}")
            print(f"IP: {container.container_ip}")
            ```
        """
        try:
            data = await self._client.request("GET", f"/api/containers/{container_id}")
            container = Container(**data)
            container._set_client(self._client)
            return container
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise NotFoundError(f"Container {container_id} not found")
            raise ContainerError(f"Failed to get container: {str(e)}")

    async def list(self) -> List[Container]:
        """
        List all containers for the authenticated user.

        Returns:
            List of Container instances

        Example:
            ```python
            containers = await client.containers.list()
            for container in containers:
                print(f"{container.container_id}: {container.status}")
            ```
        """
        try:
            data = await self._client.request("GET", "/api/containers")
            if isinstance(data, list):
                containers = [Container(**item) for item in data]
                # Set client reference on each container
                for container in containers:
                    container._set_client(self._client)
                return containers
            return []
        except Exception as e:
            raise ContainerError(f"Failed to list containers: {str(e)}")

    async def stop(self, container_id: str) -> Dict[str, str]:
        """
        Stop a running container.

        Args:
            container_id: Container ID

        Returns:
            Status message

        Example:
            ```python
            result = await client.containers.stop("cntr_abc123")
            print(result["message"])
            ```
        """
        try:
            data = await self._client.request("POST", f"/api/containers/{container_id}/stop")
            return data
        except Exception as e:
            raise ContainerError(f"Failed to stop container: {str(e)}")

    async def delete(self, container_id: str) -> Dict[str, str]:
        """
        Delete a container (stops it first if running).

        Args:
            container_id: Container ID

        Returns:
            Status message

        Example:
            ```python
            result = await client.containers.delete("cntr_abc123")
            print(result["message"])
            ```
        """
        try:
            data = await self._client.request("DELETE", f"/api/containers/{container_id}")
            return data
        except Exception as e:
            raise ContainerError(f"Failed to delete container: {str(e)}")

    async def connect(self, container_id: str) -> Dict[str, Any]:
        """
        Generate connection token for connecting to a container via WebSocket.

        Args:
            container_id: Container ID

        Returns:
            Dictionary with websocket_url, token, and expires_at

        Example:
            ```python
            conn_info = await client.containers.connect("cntr_abc123")
            print(f"WebSocket URL: {conn_info['websocket_url']}")
            ```
        """
        try:
            data = await self._client.request("POST", f"/api/containers/{container_id}/connect")
            return data
        except Exception as e:
            raise ContainerError(f"Failed to generate connection token: {str(e)}")

    async def run(
        self,
        command: str,
        archil_mount: ArchilMount,
        vcpu_count: int = 1,
        mem_size_mib: int = 128,
        kernel: str = "6.11-slim",
        base_image: str = "ubuntu-22.04",
        initialization_script: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Union[FileContent, Glob, Path]]] = None,
    ) -> Container:
        """
        Convenience method to run a command in a container and exit.

        This is equivalent to `create()` with the `command` parameter set,
        but provides a more intuitive interface for one-off command execution.

        Args:
            command: Command to execute
            archil_mount: Required Archil filesystem mount
            vcpu_count: Number of vCPUs (default: 1)
            mem_size_mib: Memory size in MiB (default: 128)
            kernel: Kernel type - "6.11-slim" or "6.11-full" (default: "6.11-slim")
            base_image: Base image (default: "ubuntu-22.04")
            initialization_script: Optional setup script
            env: Optional dictionary of environment variables to pass to all exec sessions
            files: Optional dictionary mapping destination paths to file sources.
                   Sources can be: FileContent (inline), Glob (pattern), or Path (file/folder).
                   Maximum total size: 10 MiB across all files.

        Returns:
            Container instance

        Example:
            ```python
            from pathlib import Path
            from archil import FileContent, Glob

            # Run a training job with environment variables and files
            container = await client.containers.run(
                command="python train.py --epochs 10",
                archil_mount=ArchilMount(
                    disk_id="disk_data",
                    env="production",
                ),
                vcpu_count=4,
                mem_size_mib=8192,
                initialization_script="pip install torch torchvision",
                env={
                    "WANDB_API_KEY": "your-key",
                    "MODEL_VERSION": "v2.0"
                },
                files={
                    "/app/config.yaml": Path("config.yaml"),
                    "/app/secrets.txt": FileContent("secret-key-123"),
                }
            )
            ```
        """
        return await self.create(
            archil_mount=archil_mount,
            command=command,
            vcpu_count=vcpu_count,
            mem_size_mib=mem_size_mib,
            kernel=kernel,
            base_image=base_image,
            initialization_script=initialization_script,
            env=env,
            files=files,
        )
