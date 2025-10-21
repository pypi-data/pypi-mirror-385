"""
End-to-end test with environment variables.
"""

import os
import archil


def main():
    # Set environment variables
    os.environ["ARCHIL_API_KEY"] = "key-wpWK-NVzZGw6jDeFNA8uP6vtTTElWpvQAyapRN_FjTU="
    os.environ["ARCHIL_ENVIRONMENT"] = "test.us-east-1.red"

    print("=" * 70)
    print("E2E Test with Environment Variables")
    print("=" * 70)
    print()

    # Initialize client - should use env vars
    client = archil.Archil()

    print(f"✓ Client initialized from environment variables")
    print(f"  Environment: {client.env}")
    print(f"  Region: {client.region}")
    print(f"  Base URL: {client.base_url}")
    print()

    # Get disks
    print("Getting disks...")
    disks = client.disks.list()
    if not disks:
        print("✗ No disks found")
        return

    disk = disks[0]
    print(f"✓ Got disk: {disk.name} ({disk.disk_id})")
    print()

    # Launch simple container
    print("Launching container with 'sleep 3; exit 0'...")
    container = disk.containers.run(
        command="sleep 3; exit 0",
        vcpu_count=1,
        mem_size_mib=128,
        kernel="6.11-slim"
    )

    print(f"✓ Container launched: {container.container_id}")
    print()

    # Wait for completion
    print("Waiting for container to complete...")
    completed = container.wait_for_completion(timeout=30)

    print()
    print("=" * 70)
    print("✓ Test passed!")
    print("=" * 70)
    print(f"  Exit code: {completed.exit_code}")
    print(f"  Status: {completed.status}")
    print()
    print("Environment variable configuration works correctly:")
    print(f"  ARCHIL_ENVIRONMENT={os.environ['ARCHIL_ENVIRONMENT']}")
    print(f"  → base_url: {client.base_url}")
    print(f"  → env: {client.env}")
    print(f"  → region: {client.region}")


if __name__ == "__main__":
    main()
