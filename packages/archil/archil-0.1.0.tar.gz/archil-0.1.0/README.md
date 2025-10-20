# Archil Python SDK

An ergonomic, **disk-centric** Python SDK for the Archil Control Plane. Inspired by Modal's simplicity and elegance.

## Installation

```bash
pip install archil
```

## Philosophy: Apps Live on Disks

**Archil is disk-centric.** Everything revolves around disks:
- **Apps live ON disks** - not just attached to them
- Your disk contains your data, code, models, and outputs
- The disk is automatically mounted in all your functions at `/mnt/archil`
- You launch applications on disks, not containers with disks attached

## Quick Start - Declarative API (Recommended)

```python
import archil
import os

# Create an app on a disk
# The disk is the fundamental unit - your app lives here
app = archil.App(
    name="my-app",
    disk_id="disk_abc123",
    disk_env="production"
)

# Define a function that runs in a container
# Your disk is automatically mounted at /mnt/archil
@app.function(
    image=archil.Image.python("3.11").pip_install("numpy"),
    vcpu_count=2,
    mem_size_mib=512
)
def process_data():
    import numpy as np
    print("Processing data with numpy...")
    result = np.random.rand(100, 100)

    # Save to your disk
    np.save("/mnt/archil/data/output.npy", result)
    print("Saved to /mnt/archil/data/output.npy")

# Run it remotely
process_data.remote()
```

That's it! The SDK handles:
- Container creation and lifecycle
- Image building and dependency installation
- Resource allocation
- Automatic disk mounting at `/mnt/archil`
- Automatic cleanup

## Features

- 💾 **Disk-Centric**: Apps live on disks - the fundamental unit of Archil
- 🚀 **Declarative API**: Define workloads with simple decorators
- 🎨 **Chainable Image Builder**: Fluent API for building container images
- 🔄 **Async Support**: Built on `httpx` for modern async/await
- 🏷️ **Type-Safe**: Full type hints and Pydantic models
- 📦 **Automatic Mounting**: Your disk is always mounted at `/mnt/archil`
- 🔌 **Port Mapping**: Expose container ports effortlessly
- 🗄️ **Full Disk Management**: Create, manage, and share disks

## API Styles

Archil provides two API styles. Choose what feels best for your use case:

### Declarative API (Modal-inspired, Disk-Centric)

Best for: Defining reusable workloads, ML training, data processing

```python
import archil
import os

# Create app on your training disk
app = archil.App(
    name="ml-training",
    disk_id="disk_abc123",
    disk_env="production"
)

@app.function(
    image=archil.Image.python("3.11").pip_install("torch", "numpy"),
    vcpu_count=8,
    mem_size_mib=16384
)
def train_model():
    import torch
    print("Training with PyTorch...")
    # Your disk is at /mnt/archil
    print("Loading data from /mnt/archil/datasets/")

train_model.remote()  # Runs on your disk
```

### Imperative API

Best for: Dynamic workflows, scripting, one-off tasks

```python
import archil
import asyncio
import os

async def main():
    async with archil.Archil(api_key="your-key") as client:
        # All containers require disk mounts
        mount = archil.ArchilMount(
            disk_id="disk_abc123",
            env="production"
        )

        container = await client.containers.create(
            archil_mount=mount,
            vcpu_count=2,
            mem_size_mib=512
        )
        print(f"Created: {container.container_id}")

asyncio.run(main())
```

## Understanding Disks in Archil

**Disks are the foundation of Archil.** Unlike traditional container platforms where you attach storage to containers, in Archil:

- **You launch apps ON disks** - the disk is the context
- Your app's data, code, and outputs all live on the disk
- The disk is automatically mounted at `/mnt/archil` in every function
- Multiple apps can share the same disk (perfect for data pipelines)
- Disks can be backed by S3, GCS, R2, or any S3-compatible storage

### Creating a Volume

```python
import archil

# From disk ID (most common)
volume = archil.Volume.from_disk_id(
    disk_id="disk_abc123",
    env="production"
)

# From a Disk object
disk = await client.disks.get("disk_abc123")
volume = archil.Volume.from_disk(disk)

# Shared (read-only) mount
volume = archil.Volume.from_disk_id(
    disk_id="disk_abc123",
    env="production",
    shared=True  # Multiple containers can read simultaneously
)
```

### Managing Disks

```python
# Create a new disk
disk = await client.disks.create(
    name="my-dataset",
    provider="s3",
    region="us-west-2",
    mounts=[
        archil.Mount(
            provider="s3",
            bucket="my-bucket",
            region="us-west-2",
            access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
    ]
)

# List disks
disks = await client.disks.list()

# Get disk details
disk = await client.disks.get("disk_abc123")
```

## Declarative API Examples

### Simple Function

```python
import archil
import os

# App lives on a disk
app = archil.App(
    name="hello",
    disk_id="disk_abc123",
    disk_env="production"
)

@app.function()
def say_hello():
    print("Hello from Archil!")
    print("My disk is at /mnt/archil")

say_hello.remote()
```

### With Custom Image

```python
import os

# App lives on your data science disk
app = archil.App(
    name="data-science",
    disk_id="disk_abc123",
    disk_env="production"
)

# Build a custom image
image = (
    archil.Image.python("3.11")
    .pip_install("pandas", "numpy", "scikit-learn")
    .apt_install("git", "curl")
    .run_commands("mkdir -p /workspace")
)

@app.function(
    image=image,
    vcpu_count=4,
    mem_size_mib=8192
)
def analyze_data():
    import pandas as pd
    # Data lives on your disk at /mnt/archil
    df = pd.read_csv("/mnt/archil/input.csv")
    print(f"Loaded {len(df)} rows")

    # Save results back to disk
    df.to_csv("/mnt/archil/output.csv")

analyze_data.remote()
```

### With Additional Volume Mounts

If you need to access additional disks beyond your app's primary disk:

```python
import os

# App lives on your training disk
app = archil.App(
    name="ml-training",
    disk_id="disk_training",  # Primary disk for this app
    disk_env="production"
)

# Define an additional volume for shared datasets
dataset_volume = archil.Volume.from_disk_id(
    disk_id="disk_shared_datasets",
    env="production",
    shared=True  # Read-only shared access
)

@app.function(
    image=archil.Image.python("3.11").pip_install("torch"),
    vcpu_count=8,
    mem_size_mib=16384,
    additional_volumes={"/datasets": dataset_volume}  # Mount additional disk
)
def train():
    import torch
    # App's disk is at /mnt/archil (read-write)
    # Additional shared dataset at /datasets (read-only)
    print("Loading training data from /datasets...")
    print("Saving checkpoints to /mnt/archil/checkpoints/...")

train.remote()
```

### Running Shell Commands

```python
import os

# Batch processing app lives on this disk
app = archil.App(
    name="batch-processing",
    disk_id="disk_abc123",
    disk_env="production"
)

@app.run(
    command="""
    cd /mnt/archil
    wget https://example.com/data.tar.gz
    tar -xzf data.tar.gz
    python process.py
    """,
    image=archil.Image.debian_slim().apt_install("wget", "python3"),
    vcpu_count=2,
    mem_size_mib=2048
)
def batch_job():
    pass

batch_job.remote()
```

### Complete ML Training Example

```python
import archil
import os

# Training app lives on your ML disk
app = archil.App(
    name="resnet-training",
    disk_id="disk_ml_workspace",  # Your models, checkpoints, logs live here
    disk_env="production"
)

# Define training environment
training_image = (
    archil.Image.python("3.11")
    .pip_install("torch", "torchvision", "wandb", "tensorboard")
    .env(
        PYTHONUNBUFFERED="1",
        WANDB_PROJECT="resnet-training"
    )
)

# Mount shared dataset disk
dataset_volume = archil.Volume.from_disk_id(
    disk_id="disk_imagenet",
    env="production",
    shared=True  # Read-only shared datasets
)

@app.function(
    image=training_image,
    vcpu_count=16,
    mem_size_mib=32768,
    kernel_variant="extended",  # For GPU support
    additional_volumes={"/datasets": dataset_volume}
)
def train_resnet():
    import torch
    import torch.nn as nn
    from torchvision import models, datasets, transforms

    print("Loading model...")
    model = models.resnet50(pretrained=False)

    print("Loading data from /datasets...")
    # Training loop here

    print("Training complete!")
    # Save to your app's disk
    torch.save(model.state_dict(), "/mnt/archil/models/resnet50.pth")
    print("Model saved to /mnt/archil/models/resnet50.pth")

if __name__ == "__main__":
    train_resnet.remote()
```

## Image Builder

The `Image` class provides a fluent API for building container images:

```python
image = (
    archil.Image.debian_slim()          # Start with Debian slim
    .apt_install("git", "build-essential")
    .pip_install("torch", "numpy")
    .run_commands(
        "git clone https://github.com/user/repo /app",
        "cd /app && make build"
    )
    .workdir("/app")
    .env(PYTHONUNBUFFERED="1", DEBUG="false")
)
```

### Available Base Images

```python
archil.Image.debian_slim()         # Debian Bookworm Slim
archil.Image.ubuntu("22.04")       # Ubuntu 22.04
archil.Image.python("3.11")        # Python 3.11 slim
```

### Image Methods

- `.apt_install(*packages)` - Install apt packages
- `.pip_install(*packages)` - Install Python packages
- `.run_commands(*commands)` - Run arbitrary shell commands
- `.workdir(path)` - Set working directory
- `.env(**vars)` - Set environment variables
- `.dockerfile(content)` - Build from Dockerfile content

## Volume Management (Declarative API)

```python
# From disk ID (most common)
volume = archil.Volume.from_disk_id(
    disk_id="disk_abc123",
    env="production",
    shared=True  # Mount as read-only
)

# From Disk object
disk = await client.disks.get("disk_abc123")
volume = archil.Volume.from_disk(
    disk=disk,
    shared=False
)

# Use in function as additional volume
@app.function(additional_volumes={"/mnt/data": volume})
def process():
    # App's disk at /mnt/archil
    # Additional volume at /mnt/data
    with open("/mnt/data/input.txt") as f:
        data = f.read()
```

## Imperative API Reference

For cases where you need more control, use the imperative API:

### Container Operations

```python
import archil
import os

async with archil.Archil(api_key="your-key") as client:
    # Create mount (required for all containers)
    mount = archil.ArchilMount(
        disk_id="disk_abc123",
        env="production"
    )

    # Container operations
    container = await client.containers.create(
        archil_mount=mount,  # Required
        vcpu_count=2,
        mem_size_mib=512,
        kernel_variant="base",
        initialization_script="pip install numpy",
        command="python train.py"  # Optional: run and exit
    )

    # List containers
    containers = await client.containers.list()

    # Get container
    container = await client.containers.get("cntr_abc123")

    # Stop container
    await client.containers.stop("cntr_abc123")

    # Delete container
    await client.containers.delete("cntr_abc123")
```

### Disk Operations

```python
import archil
import os

async with archil.Archil(api_key="your-key") as client:
    # Create a disk
    disk = await client.disks.create(
        name="my-dataset",
        provider="s3",
        region="us-west-2",
        mounts=[
            archil.Mount(
                provider="s3",
                bucket="my-bucket",
                region="us-west-2",
                access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
        ]
    )

    # List all disks
    disks = await client.disks.list()

    # Get disk details
    disk = await client.disks.get("disk_abc123")

    # Add authorized user
    await client.disks.add_user(
        disk_id="disk_abc123",
        user_type="token",
        principal="user@example.com",
        nickname="alice",
        token_suffix="ab12"
    )

    # Read directory contents
    contents = await client.disks.read_directory("disk_abc123", inode_id=1)

    # Delete disk
    await client.disks.delete("disk_abc123")
```

## Authentication

### Environment Variable (Recommended)
```bash
export ARCHIL_API_KEY=your-api-key
```

```python
# Uses ARCHIL_API_KEY for authentication
app = archil.App(
    name="my-app",
    disk_id="disk_abc123",
    disk_env="production"
)
```

### Direct API Key
```python
app = archil.App(
    name="my-app",
    disk_id="disk_abc123",
    disk_env="production",
    api_key="your-api-key"
)
```

## Error Handling

```python
from archil import ContainerError, NotFoundError, APIError

try:
    container = await client.containers.get("invalid_id")
except NotFoundError:
    print("Container not found")
except ContainerError as e:
    print(f"Container operation failed: {e}")
except APIError as e:
    print(f"API error {e.status_code}: {e}")
```

## Advanced Features

### Port Mapping

```python
# App must be created on a disk first
app = archil.App(
    name="web-app",
    disk_id="disk_abc123",
    disk_env="production"
)

@app.function(
    ports=[8080, 8443],
    image=archil.Image.python("3.11").pip_install("flask")
)
def web_server():
    from flask import Flask
    app = Flask(__name__)

    @app.route("/")
    def hello():
        return "Hello from Archil!"

    app.run(host="0.0.0.0", port=8080)
```

### Kernel Variants

```python
# App on disk
app = archil.App(
    name="gpu-training",
    disk_id="disk_abc123",
    disk_env="production"
)

@app.function(
    kernel_variant="extended",  # For additional drivers (GPU, etc.)
    vcpu_count=8,
    mem_size_mib=16384
)
def gpu_training():
    import torch
    print(f"CUDA available: {torch.cuda.is_available()}")
```

### Metadata

```python
mount = archil.ArchilMount(
    disk_id="disk_abc123",
    env="production"
)

container = await client.containers.create(
    archil_mount=mount,
    vcpu_count=2,
    mem_size_mib=512,
    metadata={
        "experiment_id": "exp_123",
        "model_version": "v2.0",
        "user": "alice"
    }
)
```

## Development

### Setup

```bash
git clone https://github.com/archil/archil-sdk-python
cd archil-sdk-python
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
pytest --cov=archil  # With coverage
```

### Code Quality

```bash
black archil/           # Format code
ruff check archil/      # Lint
mypy archil/            # Type check
```

## Examples

See the `examples/` directory for more:

- `declarative_simple.py` - Simple hello world
- `declarative_ml_training.py` - ML training workflow
- `declarative_data_processing.py` - Data processing pipeline
- `run_command.py` - Running shell commands
- `simple_container.py` - Basic container creation

## Comparison with Modal

Archil's API is heavily inspired by Modal. Here's how they compare:

```python
# Modal
import modal
stub = modal.Stub("my-app")
@stub.function(image=modal.Image.debian_slim())
def my_func():
    pass

# Archil (disk-centric declarative style)
import archil
app = archil.App(name="my-app", disk_id="disk_abc123", disk_env="production")
@app.function(image=archil.Image.debian_slim())
def my_func():
    # Disk automatically mounted at /mnt/archil
    pass
```

Key differences:
- **Archil** is built for Archil's control plane and container infrastructure
- **Modal** is a hosted platform with additional features like scheduled runs, webhooks, etc.
- **Archil** gives you more control over the underlying infrastructure

## License

MIT

## Support

- Documentation: https://docs.archil.cloud
- Issues: https://github.com/archil/archil-sdk-python/issues
- Email: support@archil.cloud

## Publishing to PyPI

See [PUBLISHING.md](PUBLISHING.md) for detailed instructions on publishing this package to PyPI.
