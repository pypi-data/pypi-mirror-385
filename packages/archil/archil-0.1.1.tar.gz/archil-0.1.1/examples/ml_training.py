"""
Machine learning training example.

This example shows how to run a training job on Archil.
"""

import archil


def main():
    # Initialize client (uses ARCHIL_API_KEY environment variable)
    # Defaults to aws-us-east-1, or specify: region="aws-us-west-2"
    client = archil.Archil()

    print("Setting up ML training job...")
    print()

    # Get a disk to store training data and model checkpoints
    print("Step 1: Getting disk...")
    disks = client.disks.list()
    if not disks:
        print("No disks found. Please create a disk first.")
        return

    disk = disks[0]
    print(f"✓ Using disk: {disk.name} ({disk.disk_id})")
    print()

    # Define training script
    training_script = """
python3 << 'EOF'
import time
print("Starting training...")

# Simulate training loop
for epoch in range(5):
    print(f"Epoch {epoch + 1}/5")
    time.sleep(1)

print("Training complete!")
print("Model saved to /mnt/archil/model.pth")
EOF
"""

    # Launch training container
    print("Step 2: Launching training container...")
    container = disk.containers.run(
        command=training_script,
        vcpu_count=4,
        mem_size_mib=8192,
        initialization_script="apt-get update && apt-get install -y python3"
    )

    print(f"✓ Container launched: {container.container_id}")
    print(f"  vCPU: {container.vcpu_count}")
    print(f"  Memory: {container.mem_size_mib} MiB")
    print()

    # Wait for training to complete
    print("Step 3: Waiting for training to complete...")
    completed = container.wait_for_completion(timeout=600)

    print()
    print("=" * 60)
    print("Training job completed!")
    print("=" * 60)
    print(f"Exit code: {completed.exit_code}")
    print(f"Status: {completed.status}")

    if completed.exit_code == 0:
        print("\n✓ Training successful!")
        print(f"Model saved to disk: {disk.disk_id}")
    else:
        print(f"\n✗ Training failed: {completed.exit_reason}")


if __name__ == "__main__":
    main()
