"""
Test Environment configuration system.

Validates:
- Region mappings
- Environment string parsing
- Base URL construction
- Custom base_url handling
"""

import archil
from archil.environment import Environment


def test_region_mappings():
    """Test that region strings map to correct environments and URLs."""
    print("Testing region mappings...")

    test_cases = [
        (
            "aws-us-east-1",
            "prod.us-east-1.green",
            "https://control.green.us-east-1.aws.prod.archil.com"
        ),
        (
            "aws-us-west-2",
            "prod.aws.us-west-2.green",
            "https://control.green.us-west-2.aws.prod.archil.com"
        ),
        (
            "aws-eu-west-1",
            "prod.aws.eu-west-1.green",
            "https://control.green.eu-west-1.aws.prod.archil.com"
        ),
        (
            "gcp-us-central1",
            "prod.gcp.us-central1.blue",
            "https://control.blue.us-central1.gcp.prod.archil.com"
        ),
    ]

    for region, expected_env, expected_url in test_cases:
        env = Environment(region=region)
        assert env.env == expected_env, f"Region {region}: expected env {expected_env}, got {env.env}"
        assert env.base_url == expected_url, f"Region {region}: expected URL {expected_url}, got {env.base_url}"
        print(f"  ✓ {region} -> {expected_env}")

    print()


def test_3_part_env_format():
    """Test 3-part environment format (stage.region.color) defaults to aws."""
    print("Testing 3-part environment format...")

    env = Environment(env="prod.us-east-1.green")

    assert env.stage == "prod"
    assert env.region == "us-east-1"
    assert env.color == "green"
    assert env.provider == "aws", "3-part format should default provider to 'aws'"
    assert env.base_url == "https://control.green.us-east-1.aws.prod.archil.com"

    print(f"  ✓ prod.us-east-1.green -> provider='aws' (default)")
    print(f"  ✓ base_url: {env.base_url}")
    print()


def test_4_part_env_format():
    """Test 4-part environment format (stage.provider.region.color)."""
    print("Testing 4-part environment format...")

    env = Environment(env="prod.gcp.us-central1.blue")

    assert env.stage == "prod"
    assert env.provider == "gcp"
    assert env.region == "us-central1"
    assert env.color == "blue"
    assert env.base_url == "https://control.blue.us-central1.gcp.prod.archil.com"

    print(f"  ✓ prod.gcp.us-central1.blue -> provider='gcp' (explicit)")
    print(f"  ✓ base_url: {env.base_url}")
    print()


def test_custom_base_url():
    """Test custom base_url parsing."""
    print("Testing custom base_url...")

    env = Environment(base_url="https://control.red.us-east-1.aws.test.archil.com")

    assert env.stage == "test"
    assert env.region == "us-east-1"
    assert env.provider == "aws"
    assert env.color == "red"
    assert env.env == "test.us-east-1.red", "Should construct 3-part env for aws"
    assert env.base_url == "https://control.red.us-east-1.aws.test.archil.com"

    print(f"  ✓ Parsed base_url correctly")
    print(f"  ✓ Extracted env: {env.env}")
    print()


def test_client_region_initialization():
    """Test client initialization with region parameter."""
    print("Testing client initialization with region...")

    client = archil.Archil(
        api_key="test-key",
        region="aws-us-east-1"
    )

    assert client.base_url == "https://control.green.us-east-1.aws.prod.archil.com"
    assert client.env == "prod.us-east-1.green"
    assert client.region == "us-east-1"

    print(f"  ✓ Client initialized with region='aws-us-east-1'")
    print(f"  ✓ base_url: {client.base_url}")
    print(f"  ✓ env: {client.env}")
    print()


def test_client_environment_string():
    """Test client initialization with environment string."""
    print("Testing client initialization with environment string...")

    client = archil.Archil(
        api_key="test-key",
        environment="test.us-east-1.red"
    )

    assert client.base_url == "https://control.red.us-east-1.aws.test.archil.com"
    assert client.env == "test.us-east-1.red"
    assert client.region == "us-east-1"

    print(f"  ✓ Client initialized with environment='test.us-east-1.red'")
    print(f"  ✓ base_url: {client.base_url}")
    print()


def test_client_custom_base_url():
    """Test client initialization with custom base_url (legacy support)."""
    print("Testing client initialization with custom base_url...")

    client = archil.Archil(
        api_key="test-key",
        base_url="https://control.red.us-east-1.aws.test.archil.com"
    )

    assert client.base_url == "https://control.red.us-east-1.aws.test.archil.com"
    assert client.env == "test.us-east-1.red"
    assert client.region == "us-east-1"

    print(f"  ✓ Client initialized with custom base_url")
    print(f"  ✓ env: {client.env}")
    print()


def test_default_region():
    """Test that client defaults to aws-us-east-1 when nothing specified."""
    print("Testing default region...")

    client = archil.Archil(api_key="test-key")

    assert client.region == "us-east-1"
    assert client.env == "prod.us-east-1.green"
    assert client.base_url == "https://control.green.us-east-1.aws.prod.archil.com"

    print(f"  ✓ Defaults to aws-us-east-1")
    print(f"  ✓ base_url: {client.base_url}")
    print()


def main():
    print("=" * 60)
    print("Environment Configuration Tests")
    print("=" * 60)
    print()

    try:
        test_region_mappings()
        test_3_part_env_format()
        test_4_part_env_format()
        test_custom_base_url()
        test_client_region_initialization()
        test_client_environment_string()
        test_client_custom_base_url()
        test_default_region()

        print("=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)

    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"✗ Test failed: {e}")
        print("=" * 60)
        raise


if __name__ == "__main__":
    main()
