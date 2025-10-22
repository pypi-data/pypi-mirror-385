"""
Example: Creating containers with custom environment variables.

Environment variables are passed to all exec sessions in the container.
Special variables are automatically added:
  - ARCHIL_CONTAINER_ID: The container ID
  - ARCHIL_DISK_ID: The mounted disk ID
  - ARCHIL_REGION: The region/environment name
"""

import archil
from archil import ArchilMount


def main():
    # Initialize the client
    client = archil.Archil(api_key="your-api-key")

    # Example 1: Create a container with environment variables
    print("Example 1: Container with custom environment variables")
    container = client.containers.create(
        archil_mount=ArchilMount(
            disk_id="disk_abc123",
            env="production",
        ),
        vcpu_count=2,
        mem_size_mib=512,
        env={
            "DATABASE_URL": "postgres://user:pass@host:5432/db",
            "API_KEY": "secret-key-value",
            "DEBUG_MODE": "false",
            "LOG_LEVEL": "info"
        }
    )
    print(f"Created container: {container.container_id}")
    print(f"Status: {container.status}")
    print()

    # Example 2: Run a command with environment variables
    print("Example 2: Run a training job with environment variables")
    container = client.containers.run(
        command="python train.py --epochs 10",
        archil_mount=ArchilMount(
            disk_id="disk_abc123",
            env="production",
        ),
        vcpu_count=4,
        mem_size_mib=8192,
        initialization_script="pip install torch torchvision",
        env={
            "WANDB_API_KEY": "your-wandb-key",
            "WANDB_PROJECT": "my-ml-project",
            "MODEL_VERSION": "v2.0",
            "LEARNING_RATE": "0.001"
        }
    )
    print(f"Started training container: {container.container_id}")

    # Wait for completion
    completed = container.wait_for_completion(timeout=600)
    print(f"Training completed with exit code: {completed.exit_code}")
    print()

    # Example 3: Using disk.containers.run() with environment variables
    print("Example 3: Using disk.containers shorthand")
    disks = client.disks.list()
    if disks:
        disk = disks[0]
        container = disk.containers.run(
            command="python analyze_data.py",
            vcpu_count=2,
            mem_size_mib=1024,
            env={
                "INPUT_PATH": "/mnt/archil/data/input",
                "OUTPUT_PATH": "/mnt/archil/data/output",
                "NUM_WORKERS": "4"
            }
        )
        print(f"Created analysis container: {container.container_id}")
        print()

    # Example 4: Environment variables are available in all exec sessions
    print("Example 4: Environment variables persist across exec sessions")
    print("All environment variables (custom + special Archil vars) are available in:")
    print("  - Interactive shell sessions (WebSocket)")
    print("  - Background command execution")
    print("  - Initialization scripts")
    print()
    print("Automatically added variables:")
    print("  - ARCHIL_CONTAINER_ID: Container's unique identifier")
    print("  - ARCHIL_DISK_ID: The mounted disk ID")
    print("  - ARCHIL_REGION: Region or environment name from mount config")


if __name__ == "__main__":
    main()
