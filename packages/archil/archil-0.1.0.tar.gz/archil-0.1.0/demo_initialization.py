"""
Demonstration of the three ways to initialize the Archil client.
"""

import archil


def demo_region_based():
    """Method 1: Region-based (Simplest - Recommended)"""
    print("=" * 70)
    print("Method 1: Region-Based Initialization (Simplest)")
    print("=" * 70)

    client = archil.Archil(
        api_key="demo-key",
        region="aws-us-east-1"
    )

    print(f"\nInput:  region='aws-us-east-1'")
    print(f"\nOutput:")
    print(f"  base_url: {client.base_url}")
    print(f"  env:      {client.env}")
    print(f"  region:   {client.region}")
    print()


def demo_environment_string():
    """Method 2: Environment string (Advanced)"""
    print("=" * 70)
    print("Method 2: Environment String (Advanced)")
    print("=" * 70)

    # 3-part format
    print("\n3-part format (defaults to AWS):")
    client1 = archil.Archil(
        api_key="demo-key",
        environment="test.us-east-1.red"
    )
    print(f"  Input:    environment='test.us-east-1.red'")
    print(f"  base_url: {client1.base_url}")
    print(f"  env:      {client1.env}")
    print(f"  region:   {client1.region}")

    # 4-part format
    print("\n4-part format (explicit provider):")
    client2 = archil.Archil(
        api_key="demo-key",
        environment="prod.gcp.us-central1.blue"
    )
    print(f"  Input:    environment='prod.gcp.us-central1.blue'")
    print(f"  base_url: {client2.base_url}")
    print(f"  env:      {client2.env}")
    print(f"  region:   {client2.region}")
    print()


def demo_base_url():
    """Method 3: Custom base_url (For custom deployments)"""
    print("=" * 70)
    print("Method 3: Custom Base URL (Custom/Test Environments)")
    print("=" * 70)

    client = archil.Archil(
        api_key="demo-key",
        base_url="https://control.red.us-east-1.aws.test.archil.com"
    )

    print(f"\nInput:  base_url='https://control.red.us-east-1.aws.test.archil.com'")
    print(f"\nExtracted:")
    print(f"  env:      {client.env}")
    print(f"  region:   {client.region}")
    print(f"  base_url: {client.base_url}")
    print()


def demo_default():
    """Default behavior (no region/environment specified)"""
    print("=" * 70)
    print("Method 4: Default (No Region/Environment Specified)")
    print("=" * 70)

    client = archil.Archil(api_key="demo-key")

    print(f"\nInput:  (none)")
    print(f"\nDefaults to aws-us-east-1:")
    print(f"  base_url: {client.base_url}")
    print(f"  env:      {client.env}")
    print(f"  region:   {client.region}")
    print()


def demo_available_regions():
    """Show all available predefined regions"""
    print("=" * 70)
    print("Available Predefined Regions")
    print("=" * 70)
    print()

    from archil.environment import REGION_TO_ENV

    for region, env in REGION_TO_ENV.items():
        client = archil.Archil(api_key="demo-key", region=region)
        print(f"  {region:<20} → {env:<30} → {client.base_url}")

    print()


def main():
    print()
    print("#" * 70)
    print("#  Archil Client Initialization Methods")
    print("#" * 70)
    print()

    demo_region_based()
    demo_environment_string()
    demo_base_url()
    demo_default()
    demo_available_regions()

    print("=" * 70)
    print("Recommendation: Use region='aws-us-east-1' for simplest setup")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
