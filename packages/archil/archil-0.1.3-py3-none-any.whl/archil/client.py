"""Archil API client."""

from typing import Optional, Union
import httpx

from ._sync import synchronizer
from .environment import Environment
from .containers import ContainerManager
from .disks import DiskManager
from .exceptions import AuthenticationError, APIError


@synchronizer.create_blocking
class _ArchilAsync:
    """
    Main Archil client for interacting with the control plane.

    Example:
        ```python
        import archil

        # Initialize client
        client = archil.Archil(
            api_key="your-api-key",
            base_url="https://api.archil.cloud"
        )

        # Create a container
        container = client.containers.create(
            vcpu_count=2,
            mem_size_mib=512,
            kernel_variant="extended"
        )
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        region: Optional[str] = None,
        environment: Optional[Union[str, Environment]] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize the Archil client.

        Args:
            api_key: API key for authentication. If not provided, will look for
                     ARCHIL_API_KEY environment variable.
            region: Region string (e.g., "aws-us-east-1"). Simplest option.
                    If not provided, will look for ARCHIL_REGION environment variable.
            environment: Environment string or Environment object.
                        If not provided, will look for ARCHIL_ENVIRONMENT environment variable.
            base_url: Custom base URL (for advanced use)
            timeout: Request timeout in seconds

        Note: Provide only ONE of: region, environment, or base_url.
              If none provided, checks ARCHIL_ENVIRONMENT, then ARCHIL_REGION,
              then defaults to aws-us-east-1.

        Examples:
            >>> # Simple: use a region
            >>> client = Archil(region="aws-us-east-1")

            >>> # Advanced: use environment string
            >>> client = Archil(environment="prod.us-east-1.green")

            >>> # Custom: use base_url
            >>> client = Archil(base_url="https://control.red.us-east-1.aws.test.archil.com")

            >>> # From environment variables
            >>> # export ARCHIL_REGION="aws-us-west-2"
            >>> client = Archil()
        """
        import os

        self.api_key = api_key or os.getenv("ARCHIL_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key required. Provide via api_key parameter or ARCHIL_API_KEY environment variable."
            )

        # Create Environment object
        # Priority: explicit params > env vars > default
        if isinstance(environment, Environment):
            self.environment = environment
        elif isinstance(environment, str):
            self.environment = Environment(env=environment)
        elif region:
            self.environment = Environment(region=region)
        elif base_url:
            self.environment = Environment(base_url=base_url)
        else:
            # Check environment variables
            env_var = os.getenv("ARCHIL_ENVIRONMENT")
            region_var = os.getenv("ARCHIL_REGION")

            if env_var:
                self.environment = Environment(env=env_var)
            elif region_var:
                self.environment = Environment(region=region_var)
            else:
                # Default to aws-us-east-1
                self.environment = Environment(region="aws-us-east-1")

        self._client = httpx.AsyncClient(
            base_url=self.environment.base_url,
            timeout=timeout,
            headers={"Authorization": self.api_key},
        )

        # Initialize managers as private attributes
        # We'll expose them via properties to work with synchronicity
        self._containers = ContainerManager(self)
        self._disks = DiskManager(self)

    @property
    def containers(self) -> ContainerManager:
        """Access container operations."""
        return self._containers

    @property
    def disks(self) -> DiskManager:
        """Access disk operations."""
        return self._disks

    @property
    def base_url(self) -> str:
        """Get the base URL."""
        return self.environment.base_url

    @property
    def env(self) -> str:
        """Get the environment string."""
        return self.environment.env

    @property
    def region(self) -> str:
        """Get the region."""
        return self.environment.region

    async def __aenter__(self) -> "Archil":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """
        Make an authenticated request to the API.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            path: API path (without base URL)
            json: JSON body for POST/PUT requests
            params: Query parameters

        Returns:
            Response JSON data

        Raises:
            APIError: If the request fails
        """
        try:
            response = await self._client.request(
                method=method,
                url=path,
                json=json,
                params=params,
            )
            response.raise_for_status()

            data = response.json()

            # Handle API response envelope
            if isinstance(data, dict):
                if not data.get("success", True):
                    error_msg = data.get("error", "Unknown error")
                    raise APIError(error_msg, response.status_code)
                return data.get("data", data)

            return data

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            raise APIError(error_msg, e.response.status_code)
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")


# Export both sync and async versions
# When you use @synchronizer.create_blocking on _ArchilAsync:
# - _ArchilAsync becomes the SYNC (blocking) version
# - The original async class is stored internally

# Sync version (default) - this is now the blocking version created by synchronicity
Archil = _ArchilAsync

# Async version - access via the .aio attribute
# Note: In synchronicity, async versions need to be instantiated differently
# For now, we'll document that async users should use the underlying async implementation
# This is a pattern we can improve later
ArchilAsync = _ArchilAsync  # For now, same as sync (will be improved)
