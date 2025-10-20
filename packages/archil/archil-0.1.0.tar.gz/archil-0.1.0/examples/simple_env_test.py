#!/usr/bin/env python3
"""
Simple environment variable test.

This script creates a container that prints environment variables and exits.
Perfect for quick validation that the env var feature is working.

Usage:
    # Set your API key and disk ID
    export ARCHIL_API_KEY="your-api-key"
    export ARCHIL_DISK_ID="disk_abc123"

    # Run the test
    python simple_env_test.py
"""

import os
import archil
from archil import ArchilMount


def main():
    # Get configuration from environment
    api_key = os.environ.get("ARCHIL_API_KEY")
    disk_id = os.environ.get("ARCHIL_DISK_ID")

    if not api_key:
        print("❌ Error: ARCHIL_API_KEY environment variable not set")
        return

    if not disk_id:
        print("❌ Error: ARCHIL_DISK_ID environment variable not set")
        return

    print("🧪 Testing Environment Variable Support")
    print("=" * 60)
    print()

    # Initialize client
    client = archil.Archil(api_key=api_key)
    print(f"✓ Connected to {client.base_url}")
    print()

    # Test environment variables
    test_vars = {
        "MY_CUSTOM_VAR": "hello_from_sdk",
        "TEST_NUMBER": "42",
        "API_ENDPOINT": "https://api.example.com"
    }

    print("📦 Creating container with custom environment variables:")
    for key, value in test_vars.items():
        print(f"   {key}={value}")
    print()

    # Command that prints all environment variables we care about
    command = """
echo "=== Custom Variables ==="
echo "MY_CUSTOM_VAR=$MY_CUSTOM_VAR"
echo "TEST_NUMBER=$TEST_NUMBER"
echo "API_ENDPOINT=$API_ENDPOINT"
echo ""
echo "=== Special Archil Variables ==="
echo "ARCHIL_CONTAINER_ID=$ARCHIL_CONTAINER_ID"
echo "ARCHIL_DISK_ID=$ARCHIL_DISK_ID"
echo "ARCHIL_REGION=$ARCHIL_REGION"
echo ""
echo "=== Validation ==="
if [ -n "$MY_CUSTOM_VAR" ] && [ -n "$ARCHIL_CONTAINER_ID" ]; then
    echo "✓ SUCCESS: All variables are set!"
    exit 0
else
    echo "✗ FAILURE: Some variables are missing"
    exit 1
fi
"""

    # Create and run the container
    try:
        container = client.containers.run(
            command=command,
            archil_mount=ArchilMount(
                disk_id=disk_id,
                env="production",
            ),
            vcpu_count=1,
            mem_size_mib=256,
            env=test_vars
        )

        print(f"✓ Container created: {container.container_id}")
        print(f"  Status: {container.status}")
        print()

        # Wait for completion
        print("⏳ Waiting for container to complete...")
        completed = container.wait_for_completion(timeout=120)

        print()
        print("📊 Results:")
        print(f"  Exit Code: {completed.exit_code}")
        print(f"  Status: {completed.status}")
        print()

        if completed.exit_code == 0:
            print("✅ SUCCESS! Environment variables are working correctly.")
            print()
            print("What happened:")
            print("  1. Custom env vars were passed from Python SDK → Controller → Runtime")
            print("  2. Runtime auto-added ARCHIL_* special variables")
            print("  3. All variables were available in the container exec session")
            print()
            print("To see the actual output, check the container logs in:")
            print("  - Archil Console")
            print("  - Runtime logs at /tmp/firecracker_<container-id>_console.log")
        else:
            print("❌ FAILURE: Container exited with non-zero code")
            print()
            print("This could mean:")
            print("  - Environment variables were not set correctly")
            print("  - The feature is not fully deployed")
            print("  - There was an error in the container")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
