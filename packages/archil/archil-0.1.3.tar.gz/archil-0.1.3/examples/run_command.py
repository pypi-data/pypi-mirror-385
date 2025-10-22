"""
Run a command in a container example.

This example shows how to run a one-off command that executes and then exits.
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

    # Run a command (container will execute and then exit)
    print("\nRunning command in container...")
    container = disk.containers.run(
        command="python3 --version && echo 'Command completed successfully!'",
        vcpu_count=1,
        mem_size_mib=256,
        initialization_script="apt-get update && apt-get install -y python3"
    )

    print(f"Container started: {container.container_id}")
    print(f"Status: {container.status}")

    # Wait for command to complete
    print("\nWaiting for command to complete...")
    completed = container.wait_for_completion(timeout=60)

    print(f"\nCommand completed!")
    print(f"  Exit code: {completed.exit_code}")
    print(f"  Status: {completed.status}")

    if completed.exit_code == 0:
        print("✓ Command executed successfully!")
    else:
        print(f"✗ Command failed with exit code {completed.exit_code}")


if __name__ == "__main__":
    main()
