"""
Docker workload example.

This example shows how to run a container with Docker installed,
demonstrating complex initialization scripts and environment variable configuration.

The container:
1. Installs Docker and related tools
2. Installs uv (Python package manager)
3. Clones the sandboxes repository
4. Sets up a Python environment
5. Runs a sandboxes trial

Usage:
    export ARCHIL_API_KEY="your-api-key"
    export ARCHIL_ENVIRONMENT="test.us-east-1.red"
    python docker_workload.py

Note: This example requires the 6.11-full kernel and may take several minutes
to complete due to Docker installation and setup.

If you encounter a 500 error, the initialization script may be too long for
the current API limits. Consider breaking it into smaller steps or using
a pre-built base image with Docker already installed.
"""

import archil
from pathlib import Path


# Docker installation and setup script
INITIALIZATION_SCRIPT = """#!/bin/bash
set -e

# Install Docker
apt-get update
apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# Add Docker repository
ARCH=$(dpkg --print-architecture)
. /etc/os-release
echo "deb [arch=$ARCH signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker packages
apt-get update
apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin git
systemctl enable docker
systemctl start docker

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
. /root/.local/bin/env

# Setup sandboxes
cd /root
git clone https://github.com/laude-institute/sandboxes.git
cd sandboxes
uv venv
. .venv/bin/activate
uv pip install -e .
"""

# Command to run in the container
COMMAND = """#!/bin/bash
mkdir -p /mnt/archil/${ARCHIL_CONTAINER_ID}
cp -r /root/sandbox_config /mnt/archil/${ARCHIL_CONTAINER_ID}/sandbox_config
cd /root/sandboxes
. /root/.local/bin/env
. .venv/bin/activate
sb trials start -t examples/tasks/hello-world
"""


def main():
    # Initialize client using environment variables
    # Expects: ARCHIL_API_KEY and ARCHIL_ENVIRONMENT
    client = archil.Archil()

    print("=" * 70)
    print("Docker Workload Example")
    print("=" * 70)
    print(f"Environment: {client.env}")
    print(f"Region: {client.region}")
    print(f"Base URL: {client.base_url}")
    print()

    # Get a disk
    print("Step 1: Getting disk...")
    disks = client.disks.list()
    if not disks:
        print("No disks found. Please create a disk first.")
        return

    disk = disks[0]
    print(f"✓ Using disk: {disk.name} ({disk.disk_id})")
    print()

    # Launch container with Docker setup
    print("Step 2: Launching container with Docker setup...")
    print("This will install Docker, uv, clone sandboxes, and run a trial.")
    print()

    try:
        container = disk.containers.run(
            command=COMMAND,
            vcpu_count=2,
            mem_size_mib=4096,
            kernel="6.11-full",
            initialization_script=INITIALIZATION_SCRIPT,
            files={
                "/root/sandbox_config": Path("sandboxes")
            }
        )
    except Exception as e:
        print(f"\n✗ Failed to launch container: {e}")
        print()
        print("Note: The initialization script may be too long for current API limits.")
        print("Consider splitting into smaller steps or using a pre-built base image.")
        return

    print(f"✓ Container launched: {container.container_id}")
    print(f"  vCPU: {container.vcpu_count}")
    print(f"  Memory: {container.mem_size_mib} MiB")
    print(f"  Kernel: 6.11-full")
    print()

    # Wait for completion (10 minute timeout for Docker setup)
    print("Step 3: Waiting for container to complete...")
    print("(This may take a few minutes for Docker installation and setup)")
    print()

    try:
        completed = container.wait_for_completion(timeout=600)

        print("=" * 70)
        print("Container completed!")
        print("=" * 70)
        print(f"Exit code: {completed.exit_code}")
        print(f"Status: {completed.status}")

        if completed.exit_code == 0:
            print("\n✓ Docker workload completed successfully!")
        else:
            print(f"\n✗ Failed: {completed.exit_reason}")

    except TimeoutError:
        print("\n✗ Container did not complete within 10 minutes")
        print("You can check the container status later with:")
        print(f"  client.containers.get('{container.container_id}')")


if __name__ == "__main__":
    main()
