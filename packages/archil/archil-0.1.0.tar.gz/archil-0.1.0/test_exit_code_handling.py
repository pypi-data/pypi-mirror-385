"""
Test to verify the SDK properly handles and reports non-zero exit codes.

This will help debug if the control plane is correctly reporting failures.
"""

import archil
import os


def test_successful_command():
    """Test a command that exits with code 0."""
    print("=" * 70)
    print("Test 1: Successful Command (exit 0)")
    print("=" * 70)

    os.environ["ARCHIL_API_KEY"] = "key-Qufu9STNK9ZZs0-4XZqySd1ct34M55YXVR1mZmf1piY="
    os.environ["ARCHIL_ENVIRONMENT"] = "test.us-east-1.red"

    client = archil.Archil()

    disks = client.disks.list()
    disk = disks[0]

    print(f"Launching container with 'exit 0'...")
    container = disk.containers.run(
        command="exit 0",
        vcpu_count=1,
        mem_size_mib=128,
        kernel="6.11-slim"
    )

    print(f"Container ID: {container.container_id}")
    print(f"Initial status: {container.status}")
    print()

    print("Waiting for completion...")
    completed = container.wait_for_completion(timeout=30)

    print()
    print("Results:")
    print(f"  Status: {completed.status}")
    print(f"  Exit code: {completed.exit_code}")
    print(f"  Exit reason: {completed.exit_reason}")

    if completed.exit_code == 0:
        print("  ✓ Exit code is correctly 0")
    else:
        print(f"  ✗ ERROR: Expected exit code 0, got {completed.exit_code}")

    print()


def test_failing_command():
    """Test a command that exits with non-zero code."""
    print("=" * 70)
    print("Test 2: Failing Command (exit 1)")
    print("=" * 70)

    os.environ["ARCHIL_API_KEY"] = "key-Qufu9STNK9ZZs0-4XZqySd1ct34M55YXVR1mZmf1piY="
    os.environ["ARCHIL_ENVIRONMENT"] = "test.us-east-1.red"

    client = archil.Archil()

    disks = client.disks.list()
    disk = disks[0]

    print(f"Launching container with 'exit 1'...")
    container = disk.containers.run(
        command="exit 1",
        vcpu_count=1,
        mem_size_mib=128,
        kernel="6.11-slim"
    )

    print(f"Container ID: {container.container_id}")
    print(f"Initial status: {container.status}")
    print()

    print("Waiting for completion...")
    completed = container.wait_for_completion(timeout=30)

    print()
    print("Results:")
    print(f"  Status: {completed.status}")
    print(f"  Exit code: {completed.exit_code}")
    print(f"  Exit reason: {completed.exit_reason}")

    if completed.exit_code == 1:
        print("  ✓ Exit code is correctly 1")
    elif completed.exit_code == 0:
        print("  ✗ ERROR: Exit code is 0, but command failed!")
        print("  This suggests the control plane is not reporting failures correctly.")
    else:
        print(f"  ? Unexpected exit code: {completed.exit_code}")

    print()


def test_command_that_crashes():
    """Test a command that crashes with a higher exit code."""
    print("=" * 70)
    print("Test 3: Command with exit 42")
    print("=" * 70)

    os.environ["ARCHIL_API_KEY"] = "key-Qufu9STNK9ZZs0-4XZqySd1ct34M55YXVR1mZmf1piY="
    os.environ["ARCHIL_ENVIRONMENT"] = "test.us-east-1.red"

    client = archil.Archil()

    disks = client.disks.list()
    disk = disks[0]

    print(f"Launching container with 'exit 42'...")
    container = disk.containers.run(
        command="exit 42",
        vcpu_count=1,
        mem_size_mib=128,
        kernel="6.11-slim"
    )

    print(f"Container ID: {container.container_id}")
    print(f"Initial status: {container.status}")
    print()

    print("Waiting for completion...")
    completed = container.wait_for_completion(timeout=30)

    print()
    print("Results:")
    print(f"  Status: {completed.status}")
    print(f"  Exit code: {completed.exit_code}")
    print(f"  Exit reason: {completed.exit_reason}")

    if completed.exit_code == 42:
        print("  ✓ Exit code is correctly 42")
    elif completed.exit_code == 0:
        print("  ✗ ERROR: Exit code is 0, but command failed!")
        print("  This suggests the control plane is not reporting failures correctly.")
    else:
        print(f"  ? Got exit code {completed.exit_code}, expected 42")

    print()


def test_command_with_error_output():
    """Test a command that outputs to stderr before failing."""
    print("=" * 70)
    print("Test 4: Command with stderr output and exit 5")
    print("=" * 70)

    os.environ["ARCHIL_API_KEY"] = "key-Qufu9STNK9ZZs0-4XZqySd1ct34M55YXVR1mZmf1piY="
    os.environ["ARCHIL_ENVIRONMENT"] = "test.us-east-1.red"

    client = archil.Archil()

    disks = client.disks.list()
    disk = disks[0]

    print(f"Launching container with 'echo ERROR >&2; exit 5'...")
    container = disk.containers.run(
        command="echo ERROR >&2; exit 5",
        vcpu_count=1,
        mem_size_mib=128,
        kernel="6.11-slim"
    )

    print(f"Container ID: {container.container_id}")
    print(f"Initial status: {container.status}")
    print()

    print("Waiting for completion...")
    completed = container.wait_for_completion(timeout=30)

    print()
    print("Results:")
    print(f"  Status: {completed.status}")
    print(f"  Exit code: {completed.exit_code}")
    print(f"  Exit reason: {completed.exit_reason}")

    if completed.exit_code == 5:
        print("  ✓ Exit code is correctly 5")
    elif completed.exit_code == 0:
        print("  ✗ ERROR: Exit code is 0, but command failed!")
    else:
        print(f"  ? Got exit code {completed.exit_code}, expected 5")

    print()


def main():
    print()
    print("#" * 70)
    print("#  Exit Code Handling Tests")
    print("#" * 70)
    print()
    print("This will help verify if the SDK and control plane")
    print("are correctly reporting non-zero exit codes.")
    print()

    try:
        test_successful_command()
        test_failing_command()
        test_command_that_crashes()
        test_command_with_error_output()

        print("=" * 70)
        print("Summary")
        print("=" * 70)
        print()
        print("SDK Behavior:")
        print("  - The SDK directly reports what the API returns")
        print("  - Container.exit_code comes from the API response")
        print("  - Container.status comes from the API response")
        print("  - Container.exit_reason comes from the API response")
        print()
        print("If exit codes are incorrect (showing 0 when they should be non-zero),")
        print("the issue is in the control plane, not the SDK.")
        print()

    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
