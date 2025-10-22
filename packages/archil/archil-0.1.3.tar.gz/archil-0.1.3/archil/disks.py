"""Disk management for Archil."""

from typing import Optional, List, Dict, Any, Union, TYPE_CHECKING
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel

from .containers import FileContent, Glob
from ._sync import synchronizer
from .exceptions import APIError

if TYPE_CHECKING:
    from .containers import Container, PortMapping
    from .client import Archil


class MountConfig(BaseModel):
    """Mount configuration within a mount response."""

    bucket_name: Optional[str] = None
    bucket_endpoint: Optional[str] = None
    bucket_prefix: Optional[str] = None
    provider: Optional[str] = None
    session_id: Optional[str] = None

    class Config:
        populate_by_name = True
        alias_generator = lambda field: ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(field.split('_')))


class MountResponse(BaseModel):
    """Mount response from API."""

    id: str
    type: str
    path: str
    name: str
    access_mode: Optional[str] = None
    config: Optional[MountConfig] = None
    connection_status: Optional[str] = None
    auth_error: Optional[str] = None

    class Config:
        populate_by_name = True
        alias_generator = lambda field: ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(field.split('_')))


class Mount(BaseModel):
    """Mount configuration for creating a disk."""

    provider: str  # "s3", "gcs", "r2", "s3compatible"
    bucket: str
    region: Optional[str] = None
    endpoint: Optional[str] = None  # For S3-compatible providers
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    prefix: Optional[str] = None


class AuthorizedUser(BaseModel):
    """Authorized user for a disk."""

    type: str  # "token" or "awssts"
    principal: str
    nickname: Optional[str] = None
    token_suffix: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        populate_by_name = True
        alias_generator = lambda field: ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(field.split('_')))


class DiskMetrics(BaseModel):
    """Disk usage metrics."""

    size_bytes: Optional[int] = None
    file_count: Optional[int] = None
    last_updated: Optional[datetime] = None


class MetricsResponse(BaseModel):
    """Metrics response from API."""

    data_transfer: Optional[str] = None
    requests: Optional[str] = None
    avg_response_time: Optional[str] = None

    class Config:
        populate_by_name = True
        alias_generator = lambda field: ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(field.split('_')))


class ConnectedClientResponse(BaseModel):
    """Connected client response."""

    id: Optional[str] = None
    ip_address: Optional[str] = None
    connected_at: Optional[str] = None

    class Config:
        populate_by_name = True
        alias_generator = lambda field: ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(field.split('_')))


class DiskContainerManager:
    """
    Container operations for a specific disk.

    Automatically uses the parent disk's configuration for mounts.
    Access via `disk.containers`.

    Note: This class is NOT decorated with @synchronizer.create_blocking
    because it's accessed via a property and needs to delegate to the
    client's already-wrapped methods.
    """

    def __init__(self, disk: "Disk", client: "Archil"):
        self._disk = disk
        self._client = client

    def run(
        self,
        command: str,
        vcpu_count: int = 1,
        mem_size_mib: int = 128,
        kernel: str = "6.11-slim",
        base_image: str = "ubuntu-22.04",
        initialization_script: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        shared: bool = True,
        files: Optional[Dict[str, Union[FileContent, Glob, Path]]] = None,
    ) -> "Container":
        """
        Run a command in a container using this disk.

        Args:
            command: Command to execute
            vcpu_count: Number of vCPUs (default: 1)
            mem_size_mib: Memory size in MiB (default: 128)
            kernel: Kernel type - "6.11-slim" or "6.11-full" (default: "6.11-slim")
            base_image: Base image (default: "ubuntu-22.04")
            initialization_script: Optional setup script
            env: Optional dictionary of environment variables to pass to all exec sessions
            shared: Whether mount is shared (default: False)

        Returns:
            Container instance

        Example:
            ```python
            # Get a disk
            disks = client.disks.list()
            disk = disks[0]

            # Run a container on this disk with environment variables
            container = disk.containers.run(
                command="python train.py --epochs 10",
                vcpu_count=4,
                mem_size_mib=8192,
                env={
                    "WANDB_API_KEY": "your-key",
                    "MODEL_VERSION": "v2.0"
                }
            )
            ```
        """
        # Import here to avoid circular dependency
        from .containers import ArchilMount

        # Create mount configuration using client's environment
        # The environment determines whether to pass region (for prod) or env (for test)
        mount = ArchilMount(
            disk_id=self._disk.disk_id,
            **self._client.environment.archil_mount_kwargs(),
            shared=shared
        )

        # Use the client's container manager to actually create it
        # Note: self._client.containers is already wrapped by synchronicity,
        # so we just call it directly (no await)
        return self._client.containers.run(
            command=command,
            archil_mount=mount,
            vcpu_count=vcpu_count,
            mem_size_mib=mem_size_mib,
            kernel=kernel,
            base_image=base_image,
            initialization_script=initialization_script,
            env=env,
            files=files,
        )

    def list(self) -> List["Container"]:
        """
        List all containers using this disk.

        Returns:
            List of Container instances

        Example:
            ```python
            disk = client.disks.get("disk_abc123")
            containers = disk.containers.list()
            ```
        """
        # Get all containers and filter by disk ID
        # Note: self._client.containers is already wrapped by synchronicity
        all_containers = self._client.containers.list()
        return [c for c in all_containers if c.filesystem_id == self._disk.disk_id]


class Disk(BaseModel):
    """
    Archil disk instance.

    Attributes:
        id: Unique disk identifier string (e.g. "dsk-000000000000413d")
        name: Disk name
        organization: Owner organization ID
        status: Disk status
        provider: Primary storage provider
        region: Primary region
        created_at: Creation timestamp (camelCase: createdAt)
        last_accessed: Last access timestamp (camelCase: lastAccessed)
        data_size: Data size in bytes (camelCase: dataSize)
        monthly_usage: Monthly usage cost (camelCase: monthlyUsage)
        mounts: List of storage backend mounts
        metrics: Usage metrics
        connected_clients: List of connected clients (camelCase: connectedClients)
        authorized_users: List of users with access (camelCase: authorizedUsers)
    """

    id: str  # Disk ID string like "dsk-000000000000413d"
    name: str
    organization: str
    status: str
    provider: str
    region: str
    created_at: str
    last_accessed: str
    data_size: Optional[int] = None
    monthly_usage: Optional[str] = None
    mounts: List[MountResponse]
    metrics: MetricsResponse
    connected_clients: Optional[List[ConnectedClientResponse]] = None
    authorized_users: Optional[List[AuthorizedUser]] = None

    class Config:
        populate_by_name = True
        alias_generator = lambda field: ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(field.split('_')))

    # Private attribute for client reference (not part of Pydantic model)
    _client: Optional["Archil"] = None

    def _set_client(self, client: "Archil") -> None:
        """Internal method to set client reference."""
        self._client = client

    @property
    def disk_id(self) -> str:
        """Get disk ID."""
        return self.id

    @property
    def containers(self) -> "DiskContainerManager":
        """
        Access container operations for this disk.

        Returns:
            DiskContainerManager instance

        Example:
            ```python
            disk = client.disks.list()[0]
            container = disk.containers.run(
                command="python train.py"
            )
            ```
        """
        if self._client is None:
            raise RuntimeError(
                "This disk instance is not connected to a client. "
                "Get disks via client.disks.list() or client.disks.get() to use disk.containers"
            )
        return DiskContainerManager(self, self._client)


@synchronizer.create_blocking
class DiskManager:
    """
    Manager for disk operations.

    Access via `client.disks`.
    """

    def __init__(self, client: "Archil"):  # type: ignore
        self._client = client

    async def create(
        self,
        name: str,
        provider: str,
        region: str,
        tier: str = "standard",
        mounts: Optional[List[Mount]] = None,
        authorized_users: Optional[List[AuthorizedUser]] = None,
    ) -> Disk:
        """
        Create a new disk.

        Args:
            name: Disk name (alphanumeric, hyphens, underscores only)
            provider: Storage provider ("s3", "gcs", "r2", "s3compatible")
            region: Region for the disk
            tier: Storage tier (default: "standard")
            mounts: List of storage backend mounts (1-10 required)
            authorized_users: List of authorized users

        Returns:
            Disk instance

        Example:
            ```python
            # Create a disk with S3 backend
            disk = await client.disks.create(
                name="my-dataset",
                provider="s3",
                region="us-west-2",
                mounts=[
                    archil.Mount(
                        provider="s3",
                        bucket="my-bucket",
                        region="us-west-2",
                        access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                        secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
                    )
                ]
            )
            ```
        """
        if not mounts:
            raise ValueError("At least one mount is required")

        if len(mounts) > 10:
            raise ValueError("Maximum 10 mounts allowed")

        payload: Dict[str, Any] = {
            "name": name,
            "provider": provider,
            "region": region,
            "tier": tier,
            "mounts": [m.dict(exclude_none=True) for m in mounts],
        }

        if authorized_users:
            payload["authorizedUsers"] = [u.dict(exclude_none=True) for u in authorized_users]

        try:
            data = await self._client.request("POST", "/api/disks", json=payload)
            # The API returns diskId, so we need to fetch the full disk object
            disk_id = data.get("diskId") or data.get("disk_id")
            return await self.get(disk_id)
        except Exception as e:
            raise APIError(f"Failed to create disk: {str(e)}")

    async def get(self, disk_id: str) -> Disk:
        """
        Get disk by ID.

        Args:
            disk_id: Disk ID

        Returns:
            Disk instance

        Example:
            ```python
            disk = await client.disks.get("disk_abc123")
            print(f"Disk: {disk.name}")
            print(f"Mounts: {len(disk.mounts)}")
            ```
        """
        try:
            data = await self._client.request("GET", f"/api/disks/{disk_id}")
            disk = Disk(**data)
            disk._set_client(self._client)
            return disk
        except Exception as e:
            raise APIError(f"Failed to get disk: {str(e)}")

    async def list(self) -> List[Disk]:
        """
        List all disks for the authenticated user.

        Returns:
            List of Disk instances

        Example:
            ```python
            disks = await client.disks.list()
            for disk in disks:
                print(f"{disk.name}: {disk.disk_id}")
            ```
        """
        try:
            data = await self._client.request("GET", "/api/disks")
            if isinstance(data, list):
                disks = [Disk(**item) for item in data]
                # Set client reference on each disk
                for disk in disks:
                    disk._set_client(self._client)
                return disks
            return []
        except Exception as e:
            raise APIError(f"Failed to list disks: {str(e)}")

    async def delete(self, disk_id: str) -> Dict[str, str]:
        """
        Delete a disk.

        Args:
            disk_id: Disk ID

        Returns:
            Status message

        Example:
            ```python
            result = await client.disks.delete("disk_abc123")
            print(result["message"])
            ```
        """
        try:
            data = await self._client.request("DELETE", f"/api/disks/{disk_id}")
            return data
        except Exception as e:
            raise APIError(f"Failed to delete disk: {str(e)}")

    async def check_name(self, name: str) -> Dict[str, Any]:
        """
        Check if a disk name is available.

        Args:
            name: Disk name to check

        Returns:
            Dictionary with availability status

        Example:
            ```python
            result = await client.disks.check_name("my-dataset")
            if result["available"]:
                print("Name is available!")
            ```
        """
        try:
            data = await self._client.request(
                "GET", "/api/disks/check-name", params={"name": name}
            )
            return data
        except Exception as e:
            raise APIError(f"Failed to check name: {str(e)}")

    async def add_user(
        self,
        disk_id: str,
        user_type: str,
        principal: str,
        nickname: Optional[str] = None,
        token_suffix: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Add an authorized user to a disk.

        Args:
            disk_id: Disk ID
            user_type: User type ("token" or "awssts")
            principal: User principal/identifier
            nickname: Optional nickname (required for token type)
            token_suffix: Optional token suffix (required for token type, exactly 4 chars)

        Returns:
            Status message

        Example:
            ```python
            # Add token-based user
            result = await client.disks.add_user(
                disk_id="disk_abc123",
                user_type="token",
                principal="user@example.com",
                nickname="alice",
                token_suffix="ab12"
            )
            ```
        """
        payload: Dict[str, Any] = {
            "userType": user_type,
            "principal": principal,
        }

        if nickname:
            payload["nickname"] = nickname
        if token_suffix:
            if len(token_suffix) != 4:
                raise ValueError("token_suffix must be exactly 4 characters")
            payload["tokenSuffix"] = token_suffix

        try:
            data = await self._client.request(
                "POST", f"/api/disks/{disk_id}/users", json=payload
            )
            return data
        except Exception as e:
            raise APIError(f"Failed to add user: {str(e)}")

    async def remove_user(
        self, disk_id: str, user_type: str, user_id: str
    ) -> Dict[str, str]:
        """
        Remove an authorized user from a disk.

        Args:
            disk_id: Disk ID
            user_type: User type ("token" or "awssts")
            user_id: User ID to remove

        Returns:
            Status message

        Example:
            ```python
            result = await client.disks.remove_user(
                disk_id="disk_abc123",
                user_type="token",
                user_id="user_xyz"
            )
            ```
        """
        try:
            data = await self._client.request(
                "DELETE", f"/api/disks/{disk_id}/users/{user_type}/{user_id}"
            )
            return data
        except Exception as e:
            raise APIError(f"Failed to remove user: {str(e)}")

    async def read_directory(
        self, disk_id: str, inode_id: int = 1
    ) -> Dict[str, Any]:
        """
        Read directory contents on a disk.

        Args:
            disk_id: Disk ID
            inode_id: Inode ID of directory to read (default: 1 for root)

        Returns:
            Directory listing

        Example:
            ```python
            contents = await client.disks.read_directory("disk_abc123")
            for item in contents.get("items", []):
                print(item["name"])
            ```
        """
        try:
            data = await self._client.request(
                "POST", f"/api/disks/{disk_id}/readdir/{inode_id}"
            )
            return data
        except Exception as e:
            raise APIError(f"Failed to read directory: {str(e)}")

    async def check_mount_credentials(
        self, mount: Mount
    ) -> Dict[str, Any]:
        """
        Verify mount/bucket credentials before creating a disk.

        Args:
            mount: Mount configuration to verify

        Returns:
            Verification result with authorization status and bucket listing

        Example:
            ```python
            mount = archil.Mount(
                provider="s3",
                bucket="my-bucket",
                region="us-west-2",
                access_key_id=key_id,
                secret_access_key=secret
            )

            result = await client.disks.check_mount_credentials(mount)
            if result["authorized"]:
                print("Credentials are valid!")
            ```
        """
        try:
            data = await self._client.request(
                "POST", "/api/mounts/check", json=mount.dict(exclude_none=True)
            )
            return data
        except Exception as e:
            raise APIError(f"Failed to check credentials: {str(e)}")
