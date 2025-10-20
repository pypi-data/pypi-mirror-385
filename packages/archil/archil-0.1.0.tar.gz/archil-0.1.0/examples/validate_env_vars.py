#!/usr/bin/env python3
"""
Validation script for environment variable support.

This script creates a container with custom environment variables and validates
that they are correctly passed to the container by running a command that prints
all environment variables.

Usage:
    python validate_env_vars.py --disk-id <disk_id> [--api-key <key>] [--region <region>]

Requirements:
    - Valid Archil API key (via --api-key or ARCHIL_API_KEY env var)
    - Existing disk ID to mount
    - Access to the Archil control plane
"""

import argparse
import os
import sys
import time
from typing import Dict, Set

import archil
from archil import ArchilMount


# Test environment variables to set
TEST_ENV_VARS = {
    "TEST_VAR_1": "hello_world",
    "TEST_VAR_2": "12345",
    "DATABASE_URL": "postgres://test:test@localhost:5432/testdb",
    "API_KEY": "test-api-key-value",
    "DEBUG_MODE": "true"
}

# Special Archil variables that should be auto-added
EXPECTED_ARCHIL_VARS = {
    "ARCHIL_CONTAINER_ID",
    "ARCHIL_DISK_ID",
    "ARCHIL_REGION"
}


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate environment variable support in Archil containers"
    )
    parser.add_argument(
        "--disk-id",
        required=True,
        help="Disk ID to mount in the container"
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("ARCHIL_API_KEY"),
        help="Archil API key (default: ARCHIL_API_KEY env var)"
    )
    parser.add_argument(
        "--region",
        default="aws-us-east-1",
        help="Region for the mount (default: aws-us-east-1)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds to wait for container completion (default: 300)"
    )
    return parser.parse_args()


def create_validation_command() -> str:
    """
    Create a shell command that prints all environment variables we care about.

    Returns a command that:
    1. Prints all custom test variables
    2. Prints all special Archil variables
    3. Exits with code 0 if all expected vars exist, 1 otherwise
    """
    # Build a command that checks for each expected variable
    var_checks = []

    # Check custom variables
    for var_name in TEST_ENV_VARS.keys():
        var_checks.append(f'echo "{var_name}=${{var_name}}"')

    # Check special Archil variables
    for var_name in EXPECTED_ARCHIL_VARS:
        var_checks.append(f'echo "{var_name}=${{var_name}}"')

    # Create the full command
    command = " && ".join(var_checks)

    # Add validation - check that all vars are non-empty
    validation_checks = []
    for var_name in list(TEST_ENV_VARS.keys()) + list(EXPECTED_ARCHIL_VARS):
        validation_checks.append(f'[ -n "${{{var_name}}}" ]')

    validation_command = " && ".join(validation_checks)

    # Combine: print vars, then validate
    full_command = f"set -e && {command} && echo '---VALIDATION---' && {validation_command} && echo 'SUCCESS: All variables present!'"

    return full_command


def parse_container_output(container) -> Dict[str, str]:
    """
    Parse environment variables from container output.

    Note: This is a simplified version. In a real scenario, you'd need to
    connect to the container and read its output, or check logs.
    """
    # This is a placeholder - in reality you'd need to:
    # 1. Connect to the container via WebSocket
    # 2. Read the command output
    # 3. Parse the environment variable lines

    print("Note: To fully validate, you would need to:")
    print("  1. Connect to the container via WebSocket")
    print("  2. Read the command output")
    print("  3. Verify all variables are present")
    return {}


def main():
    args = parse_args()

    if not args.api_key:
        print("Error: API key required (via --api-key or ARCHIL_API_KEY env var)")
        sys.exit(1)

    print("=" * 70)
    print("Environment Variable Validation")
    print("=" * 70)
    print()

    # Initialize client
    print("Initializing Archil client...")
    client = archil.Archil(api_key=args.api_key)
    print(f"  Region: {client.region}")
    print(f"  Base URL: {client.base_url}")
    print()

    # Print test configuration
    print("Test Configuration:")
    print(f"  Disk ID: {args.disk_id}")
    print(f"  Region: {args.region}")
    print(f"  Timeout: {args.timeout}s")
    print()

    print("Custom Environment Variables to Test:")
    for key, value in TEST_ENV_VARS.items():
        print(f"  {key}={value}")
    print()

    print("Expected Auto-Added Archil Variables:")
    for var in EXPECTED_ARCHIL_VARS:
        print(f"  {var}")
    print()

    # Create the validation command
    validation_cmd = create_validation_command()
    print("Validation Command:")
    print(f"  {validation_cmd[:100]}...")
    print()

    # Create container with environment variables
    print("Creating container with environment variables...")
    try:
        container = client.containers.run(
            command=validation_cmd,
            archil_mount=ArchilMount(
                disk_id=args.disk_id,
                region=args.region,
            ),
            vcpu_count=1,
            mem_size_mib=256,
            env=TEST_ENV_VARS
        )
        print(f"✓ Container created: {container.container_id}")
        print(f"  Status: {container.status}")
        print()
    except Exception as e:
        print(f"✗ Failed to create container: {e}")
        sys.exit(1)

    # Wait for container to complete
    print(f"Waiting for container to complete (timeout: {args.timeout}s)...")
    try:
        completed = container.wait_for_completion(timeout=args.timeout)
        print(f"✓ Container completed")
        print(f"  Exit Code: {completed.exit_code}")
        print(f"  Status: {completed.status}")
        print()
    except TimeoutError as e:
        print(f"✗ Container did not complete within timeout: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error waiting for container: {e}")
        sys.exit(1)

    # Validate results
    print("Validation Results:")
    print("-" * 70)

    if completed.exit_code == 0:
        print("✓ Container exited successfully (exit code 0)")
        print()
        print("This indicates that:")
        print("  1. All custom environment variables were present in the container")
        print("  2. All special Archil variables were auto-added")
        print("  3. Variables were accessible in the exec session")
        print()
        print("SUCCESS! Environment variable support is working correctly.")
        print()
        print("To see the actual values, you can:")
        print("  1. Check the container logs in the Archil console")
        print("  2. Connect to the container via WebSocket and run 'env'")
        print("  3. Use the Archil CLI to view container output")
    else:
        print(f"✗ Container exited with non-zero exit code: {completed.exit_code}")
        print()
        print("This may indicate:")
        print("  - One or more environment variables were not set correctly")
        print("  - The validation command failed")
        print("  - There was an error in the container")
        print()
        print("FAILURE: Environment variable support may not be working correctly.")
        print()
        print("Troubleshooting steps:")
        print("  1. Check container logs in the Archil console")
        print("  2. Verify the runtime and controller are updated")
        print("  3. Check that env vars are being passed through the API")

    print("=" * 70)
    sys.exit(0 if completed.exit_code == 0 else 1)


if __name__ == "__main__":
    main()
