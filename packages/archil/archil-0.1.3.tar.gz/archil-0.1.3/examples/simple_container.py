"""
Simple container example.

This example shows how to run a container on a disk and wait for completion.
"""

import archil


def main():
    # Initialize client (uses ARCHIL_API_KEY environment variable)
    # Defaults to aws-us-east-1, or specify: region="aws-us-west-2"
    client = archil.Archil()

    print("Getting disk...")
    disks = client.disks.list()
    if not disks:
        print("No disks found. Please create a disk first.")
        return

    disk = disks[0]
    print(f"Using disk: {disk.name} ({disk.disk_id})")

    # Run a container on the disk
    print("\nRunning container...")
    container = disk.containers.run(
        command="echo 'Hello from Archil!' && sleep 2",
        vcpu_count=1,
        mem_size_mib=256
    )

    print(f"Container started!")
    print(f"  ID: {container.container_id}")
    print(f"  Status: {container.status}")

    # Wait for it to complete
    print("\nWaiting for completion...")
    completed = container.wait_for_completion(timeout=30)

    print(f"\nContainer completed!")
    print(f"  Exit code: {completed.exit_code}")
    print(f"  Status: {completed.status}")


if __name__ == "__main__":
    main()
