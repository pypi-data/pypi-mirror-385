"""
Demonstration of environment variable support for region/environment configuration.
"""

import os
import archil


def demo_with_region_env_var():
    """Demo: Using ARCHIL_REGION environment variable"""
    print("=" * 70)
    print("Demo 1: ARCHIL_REGION Environment Variable")
    print("=" * 70)
    print()

    os.environ["ARCHIL_API_KEY"] = "demo-key"
    os.environ["ARCHIL_REGION"] = "aws-us-west-2"

    client = archil.Archil()

    print("Configuration:")
    print("  export ARCHIL_REGION='aws-us-west-2'")
    print()
    print("Client initialized:")
    print(f"  client.region:   {client.region}")
    print(f"  client.env:      {client.env}")
    print(f"  client.base_url: {client.base_url}")
    print()

    # Cleanup
    del os.environ["ARCHIL_REGION"]


def demo_with_environment_env_var():
    """Demo: Using ARCHIL_ENVIRONMENT environment variable"""
    print("=" * 70)
    print("Demo 2: ARCHIL_ENVIRONMENT Environment Variable")
    print("=" * 70)
    print()

    os.environ["ARCHIL_API_KEY"] = "demo-key"
    os.environ["ARCHIL_ENVIRONMENT"] = "test.us-east-1.red"

    client = archil.Archil()

    print("Configuration:")
    print("  export ARCHIL_ENVIRONMENT='test.us-east-1.red'")
    print()
    print("Client initialized:")
    print(f"  client.region:   {client.region}")
    print(f"  client.env:      {client.env}")
    print(f"  client.base_url: {client.base_url}")
    print()

    # Cleanup
    del os.environ["ARCHIL_ENVIRONMENT"]


def demo_priority_explicit_over_env():
    """Demo: Explicit parameters override environment variables"""
    print("=" * 70)
    print("Demo 3: Explicit Parameters Override Environment Variables")
    print("=" * 70)
    print()

    os.environ["ARCHIL_API_KEY"] = "demo-key"
    os.environ["ARCHIL_REGION"] = "aws-us-west-2"

    print("Configuration:")
    print("  export ARCHIL_REGION='aws-us-west-2'")
    print("  client = archil.Archil(region='aws-eu-west-1')")
    print()

    client = archil.Archil(region="aws-eu-west-1")

    print("Client initialized:")
    print(f"  client.region:   {client.region}")
    print(f"  client.env:      {client.env}")
    print(f"  client.base_url: {client.base_url}")
    print()
    print("✓ Explicit parameter wins!")
    print()

    # Cleanup
    del os.environ["ARCHIL_REGION"]


def demo_priority_environment_over_region():
    """Demo: ARCHIL_ENVIRONMENT takes priority over ARCHIL_REGION"""
    print("=" * 70)
    print("Demo 4: ARCHIL_ENVIRONMENT Takes Priority Over ARCHIL_REGION")
    print("=" * 70)
    print()

    os.environ["ARCHIL_API_KEY"] = "demo-key"
    os.environ["ARCHIL_REGION"] = "aws-us-west-2"
    os.environ["ARCHIL_ENVIRONMENT"] = "test.us-east-1.red"

    print("Configuration:")
    print("  export ARCHIL_REGION='aws-us-west-2'")
    print("  export ARCHIL_ENVIRONMENT='test.us-east-1.red'")
    print()

    client = archil.Archil()

    print("Client initialized:")
    print(f"  client.region:   {client.region}")
    print(f"  client.env:      {client.env}")
    print(f"  client.base_url: {client.base_url}")
    print()
    print("✓ ARCHIL_ENVIRONMENT wins!")
    print()

    # Cleanup
    del os.environ["ARCHIL_REGION"]
    del os.environ["ARCHIL_ENVIRONMENT"]


def demo_default_behavior():
    """Demo: Default behavior when no env vars set"""
    print("=" * 70)
    print("Demo 5: Default Behavior (No Environment Variables)")
    print("=" * 70)
    print()

    os.environ["ARCHIL_API_KEY"] = "demo-key"
    # Make sure no region/environment vars are set
    os.environ.pop("ARCHIL_REGION", None)
    os.environ.pop("ARCHIL_ENVIRONMENT", None)

    print("Configuration:")
    print("  (no ARCHIL_REGION or ARCHIL_ENVIRONMENT set)")
    print()

    client = archil.Archil()

    print("Client initialized:")
    print(f"  client.region:   {client.region}")
    print(f"  client.env:      {client.env}")
    print(f"  client.base_url: {client.base_url}")
    print()
    print("✓ Defaults to aws-us-east-1!")
    print()

    # Cleanup
    del os.environ["ARCHIL_API_KEY"]


def main():
    print()
    print("#" * 70)
    print("#  Environment Variable Configuration - Demonstrations")
    print("#" * 70)
    print()

    demo_with_region_env_var()
    demo_with_environment_env_var()
    demo_priority_explicit_over_env()
    demo_priority_environment_over_region()
    demo_default_behavior()

    print("=" * 70)
    print("Summary - Priority Order (Highest to Lowest):")
    print("=" * 70)
    print("  1. Explicit parameters (region=, environment=, base_url=)")
    print("  2. ARCHIL_ENVIRONMENT environment variable")
    print("  3. ARCHIL_REGION environment variable")
    print("  4. Default (aws-us-east-1)")
    print()
    print("Benefits:")
    print("  ✓ No code changes needed to switch environments")
    print("  ✓ Perfect for CI/CD pipelines")
    print("  ✓ Follows 12-Factor App principles")
    print("  ✓ Easy per-developer or per-environment configuration")
    print()


if __name__ == "__main__":
    main()
