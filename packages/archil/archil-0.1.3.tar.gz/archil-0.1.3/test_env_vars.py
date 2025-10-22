"""
Test environment variable support for ARCHIL_REGION and ARCHIL_ENVIRONMENT.
"""

import os
import archil


def test_archil_region_env_var():
    """Test that ARCHIL_REGION environment variable is respected."""
    print("Test 1: ARCHIL_REGION environment variable...")

    # Set environment variable
    os.environ["ARCHIL_REGION"] = "aws-us-west-2"
    os.environ["ARCHIL_API_KEY"] = "test-key"

    try:
        client = archil.Archil()

        assert client.region == "us-west-2", f"Expected us-west-2, got {client.region}"
        assert client.env == "prod.aws.us-west-2.green", f"Expected prod.aws.us-west-2.green, got {client.env}"
        assert client.base_url == "https://control.green.us-west-2.aws.prod.archil.com"

        print(f"  ✓ ARCHIL_REGION='aws-us-west-2'")
        print(f"  ✓ region: {client.region}")
        print(f"  ✓ env: {client.env}")
        print(f"  ✓ base_url: {client.base_url}")

    finally:
        # Clean up
        del os.environ["ARCHIL_REGION"]
        del os.environ["ARCHIL_API_KEY"]

    print()


def test_archil_environment_env_var():
    """Test that ARCHIL_ENVIRONMENT environment variable is respected."""
    print("Test 2: ARCHIL_ENVIRONMENT environment variable...")

    # Set environment variable
    os.environ["ARCHIL_ENVIRONMENT"] = "test.us-east-1.red"
    os.environ["ARCHIL_API_KEY"] = "test-key"

    try:
        client = archil.Archil()

        assert client.region == "us-east-1"
        assert client.env == "test.us-east-1.red"
        assert client.base_url == "https://control.red.us-east-1.aws.test.archil.com"

        print(f"  ✓ ARCHIL_ENVIRONMENT='test.us-east-1.red'")
        print(f"  ✓ region: {client.region}")
        print(f"  ✓ env: {client.env}")
        print(f"  ✓ base_url: {client.base_url}")

    finally:
        # Clean up
        del os.environ["ARCHIL_ENVIRONMENT"]
        del os.environ["ARCHIL_API_KEY"]

    print()


def test_priority_explicit_param_over_env_var():
    """Test that explicit parameters override environment variables."""
    print("Test 3: Explicit parameter overrides environment variable...")

    # Set environment variables
    os.environ["ARCHIL_REGION"] = "aws-us-west-2"
    os.environ["ARCHIL_ENVIRONMENT"] = "test.us-east-1.red"
    os.environ["ARCHIL_API_KEY"] = "test-key"

    try:
        # Explicit region should override env vars
        client = archil.Archil(region="aws-eu-west-1")

        assert client.region == "eu-west-1"
        assert client.env == "prod.aws.eu-west-1.green"
        assert client.base_url == "https://control.green.eu-west-1.aws.prod.archil.com"

        print(f"  ✓ Explicit region='aws-eu-west-1' overrides ARCHIL_REGION")
        print(f"  ✓ region: {client.region}")
        print(f"  ✓ env: {client.env}")

    finally:
        # Clean up
        del os.environ["ARCHIL_REGION"]
        del os.environ["ARCHIL_ENVIRONMENT"]
        del os.environ["ARCHIL_API_KEY"]

    print()


def test_priority_environment_over_region():
    """Test that ARCHIL_ENVIRONMENT takes priority over ARCHIL_REGION."""
    print("Test 4: ARCHIL_ENVIRONMENT takes priority over ARCHIL_REGION...")

    # Set both environment variables
    os.environ["ARCHIL_REGION"] = "aws-us-west-2"
    os.environ["ARCHIL_ENVIRONMENT"] = "test.us-east-1.red"
    os.environ["ARCHIL_API_KEY"] = "test-key"

    try:
        client = archil.Archil()

        # ARCHIL_ENVIRONMENT should win
        assert client.region == "us-east-1"
        assert client.env == "test.us-east-1.red"
        assert client.base_url == "https://control.red.us-east-1.aws.test.archil.com"

        print(f"  ✓ ARCHIL_ENVIRONMENT='test.us-east-1.red' takes priority")
        print(f"  ✓ region: {client.region}")
        print(f"  ✓ env: {client.env}")

    finally:
        # Clean up
        del os.environ["ARCHIL_REGION"]
        del os.environ["ARCHIL_ENVIRONMENT"]
        del os.environ["ARCHIL_API_KEY"]

    print()


def test_default_when_no_env_vars():
    """Test that it defaults to aws-us-east-1 when no env vars set."""
    print("Test 5: Default to aws-us-east-1 when no env vars...")

    os.environ["ARCHIL_API_KEY"] = "test-key"

    # Make sure no region/environment vars are set
    os.environ.pop("ARCHIL_REGION", None)
    os.environ.pop("ARCHIL_ENVIRONMENT", None)

    try:
        client = archil.Archil()

        assert client.region == "us-east-1"
        assert client.env == "prod.us-east-1.green"
        assert client.base_url == "https://control.green.us-east-1.aws.prod.archil.com"

        print(f"  ✓ Defaults to aws-us-east-1")
        print(f"  ✓ region: {client.region}")
        print(f"  ✓ env: {client.env}")

    finally:
        # Clean up
        del os.environ["ARCHIL_API_KEY"]

    print()


def main():
    print("=" * 70)
    print("Environment Variable Support Tests")
    print("=" * 70)
    print()

    try:
        test_archil_region_env_var()
        test_archil_environment_env_var()
        test_priority_explicit_param_over_env_var()
        test_priority_environment_over_region()
        test_default_when_no_env_vars()

        print("=" * 70)
        print("✓ All tests passed!")
        print("=" * 70)
        print()
        print("Priority order (highest to lowest):")
        print("  1. Explicit parameters (region=, environment=, base_url=)")
        print("  2. ARCHIL_ENVIRONMENT environment variable")
        print("  3. ARCHIL_REGION environment variable")
        print("  4. Default (aws-us-east-1)")

    except AssertionError as e:
        print()
        print("=" * 70)
        print(f"✗ Test failed: {e}")
        print("=" * 70)
        raise


if __name__ == "__main__":
    main()
