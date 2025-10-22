"""Environment configuration for Archil."""

from typing import Optional
import re


# Region to environment mapping
REGION_TO_ENV = {
    "aws-us-east-1": "prod.us-east-1.green",
    "aws-us-west-2": "prod.aws.us-west-2.green",
    "aws-eu-west-1": "prod.aws.eu-west-1.green",
    "gcp-us-central1": "prod.gcp.us-central1.blue",
}


class Environment:
    """
    Configuration for Archil environment.

    Can be constructed from:
    - A region string (e.g., "aws-us-east-1")
    - An environment string (e.g., "prod.us-east-1.green")
    - A base_url (e.g., "https://control.green.us-east-1.aws.prod.archil.com")

    Examples:
        >>> # From region
        >>> env = Environment(region="aws-us-east-1")
        >>> env.base_url
        'https://control.green.us-east-1.aws.prod.archil.com'

        >>> # From environment string
        >>> env = Environment(env="prod.us-east-1.green")
        >>> env.base_url
        'https://control.green.us-east-1.aws.prod.archil.com'

        >>> # From custom base_url
        >>> env = Environment(base_url="https://control.red.us-east-1.aws.test.archil.com")
        >>> env.env
        'test.us-east-1.red'
    """

    def __init__(
        self,
        region: Optional[str] = None,
        env: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize environment configuration.

        Args:
            region: Region string (e.g., "aws-us-east-1")
            env: Environment string (e.g., "prod.us-east-1.green")
            base_url: Custom base URL

        Note: Provide only ONE of region, env, or base_url.
        """
        if sum([region is not None, env is not None, base_url is not None]) > 1:
            raise ValueError("Provide only one of: region, env, or base_url")

        if region:
            self._init_from_region(region)
        elif env:
            self._init_from_env(env)
        elif base_url:
            self._init_from_base_url(base_url)
        else:
            # Default to aws-us-east-1
            self._init_from_region("aws-us-east-1")

    def _init_from_region(self, region: str) -> None:
        """Initialize from region string."""
        if region not in REGION_TO_ENV:
            raise ValueError(
                f"Unknown region: {region}. "
                f"Available regions: {', '.join(REGION_TO_ENV.keys())}"
            )

        env_str = REGION_TO_ENV[region]
        self._init_from_env(env_str)

    def _init_from_env(self, env_str: str) -> None:
        """
        Initialize from environment string.

        Formats:
        - stage.region.color (3 parts) -> provider defaults to "aws"
        - stage.provider.region.color (4 parts)
        """
        parts = env_str.split(".")

        if len(parts) == 3:
            # stage.region.color
            self.stage = parts[0]
            self.region = parts[1]
            self.color = parts[2]
            self.provider = "aws"
        elif len(parts) == 4:
            # stage.provider.region.color
            self.stage = parts[0]
            self.provider = parts[1]
            self.region = parts[2]
            self.color = parts[3]
        else:
            raise ValueError(
                f"Invalid environment format: {env_str}. "
                f"Expected 'stage.region.color' or 'stage.provider.region.color'"
            )

        # Construct base_url: control.${color}.${region}.${provider}.${stage}.archil.com
        self.base_url = (
            f"https://control.{self.color}.{self.region}.{self.provider}.{self.stage}.archil.com"
        )

        # Store original env string
        self.env = env_str

    def _init_from_base_url(self, base_url: str) -> None:
        """
        Initialize from base_url.

        Format: https://control.${color}.${region}.${provider}.${stage}.archil.com
        """
        self.base_url = base_url

        # Parse hostname
        match = re.search(r"https?://([^/]+)", base_url)
        if not match:
            raise ValueError(f"Invalid base_url: {base_url}")

        hostname = match.group(1)

        # Pattern: control.{color}.{region}.{provider}.{stage}.archil.com
        pattern = r"control\.([^.]+)\.([^.]+)\.([^.]+)\.([^.]+)\.archil\.com"
        match = re.match(pattern, hostname)

        if not match:
            raise ValueError(
                f"Invalid base_url format: {base_url}. "
                f"Expected: https://control.{{color}}.{{region}}.{{provider}}.{{stage}}.archil.com"
            )

        self.color = match.group(1)
        self.region = match.group(2)
        self.provider = match.group(3)
        self.stage = match.group(4)

        # Construct env string
        if self.provider == "aws":
            # Use 3-part format
            self.env = f"{self.stage}.{self.region}.{self.color}"
        else:
            # Use 4-part format
            self.env = f"{self.stage}.{self.provider}.{self.region}.{self.color}"

    def archil_mount_kwargs(self) -> dict:
        """
        Return the appropriate kwargs for ArchilMount based on stage.

        For production (stage == "prod"), returns region with provider prefix.
        For non-production, returns env string.

        Returns:
            dict: Either {"region": "aws-us-west-2"} or {"env": "test.us-east-1.red"}
        """
        if self.stage == "prod":
            # Construct full region identifier with provider prefix
            return {"region": f"{self.provider}-{self.region}"}
        else:
            return {"env": self.env}

    def __repr__(self) -> str:
        return (
            f"Environment(env='{self.env}', region='{self.region}', "
            f"provider='{self.provider}', base_url='{self.base_url}')"
        )
