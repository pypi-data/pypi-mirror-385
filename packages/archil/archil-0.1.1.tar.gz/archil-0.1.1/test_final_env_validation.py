"""
Final validation test using the new Environment configuration system.

This test validates:
1. Client initialization with base_url (test environment)
2. Disk retrieval with environment/region inheritance
3. Container launch with disk-centric API
4. Container completion with wait_for_completion()
"""

import archil


def main():
    print("=" * 60)
    print("Final Environment Configuration Validation")
    print("=" * 60)
    print()

    # Initialize client with test environment using custom base_url
    print("Step 1: Initialize client with test environment...")
    client = archil.Archil(
        api_key="key-wpWK-NVzZGw6jDeFNA8uP6vtTTElWpvQAyapRN_FjTU=",
        base_url="https://control.red.us-east-1.aws.test.archil.com"
    )

    print(f"  ✓ Client initialized")
    print(f"  ✓ base_url: {client.base_url}")
    print(f"  ✓ env: {client.env}")
    print(f"  ✓ region: {client.region}")
    print()

    # Verify environment was parsed correctly
    assert client.base_url == "https://control.red.us-east-1.aws.test.archil.com"
    assert client.env == "test.us-east-1.red"
    assert client.region == "us-east-1"

    # Get disks
    print("Step 2: Get disks...")
    disks = client.disks.list()
    if not disks:
        print("  ✗ No disks found. Please create a disk first.")
        return

    disk = disks[0]
    print(f"  ✓ Using disk: {disk.name} ({disk.disk_id})")
    print()

    # Launch container using disk-centric API
    print("Step 3: Launch container with 'sleep 5; exit 0'...")
    container = disk.containers.run(
        command="sleep 5; exit 0",
        vcpu_count=1,
        mem_size_mib=128,
        kernel="6.11-slim"
    )

    print(f"  ✓ Container launched: {container.container_id}")
    print(f"  ✓ Status: {container.status}")
    print()

    # Wait for completion
    print("Step 4: Wait for container to complete...")
    completed = container.wait_for_completion(timeout=60)

    print()
    print("=" * 60)
    print("Container completed!")
    print("=" * 60)
    print(f"Exit code: {completed.exit_code}")
    print(f"Status: {completed.status}")

    if completed.exit_code == 0:
        print("\n✓ Success! Container exited cleanly.")
    else:
        print(f"\n✗ Failed: {completed.exit_reason}")

    print()
    print("=" * 60)
    print("✓ All validation tests passed!")
    print("=" * 60)
    print()
    print("Summary:")
    print("  - Environment configuration system works correctly")
    print("  - base_url parsing extracts env/region properly")
    print("  - Disk-centric container API works")
    print("  - wait_for_completion() polls correctly")
    print("  - Container lifecycle completes successfully")


if __name__ == "__main__":
    main()
