# Archil SDK Examples

This directory contains examples showing how to use the Archil Python SDK.

## Prerequisites

```bash
# Install the SDK
pip install -e ..

# Set your API key
export ARCHIL_API_KEY="your-api-key-here"

# Optional: Set your region (defaults to aws-us-east-1)
export ARCHIL_REGION="aws-us-west-2"

# Or set a specific environment
export ARCHIL_ENVIRONMENT="test.us-east-1.red"
```

## Examples

### 1. Simple Container (`simple_container.py`)

Basic example showing how to run a container and wait for completion.

```bash
python simple_container.py
```

**What it demonstrates:**
- Getting a disk
- Running a container with `disk.containers.run()`
- Using `wait_for_completion()` to wait for the container to finish

---

### 2. Run Command (`run_command.py`)

Example of running a one-off command in a container.

```bash
python run_command.py
```

**What it demonstrates:**
- Running a command that executes and exits
- Using initialization scripts to set up the environment
- Checking exit codes for success/failure

---

### 3. ML Training (`ml_training.py`)

Example of running a machine learning training job.

```bash
python ml_training.py
```

**What it demonstrates:**
- Running longer-running workloads
- Using more resources (4 vCPUs, 8GB RAM)
- Training with data persistence on disks

---

### 4. Docker Workload (`docker_workload.py`)

Example of running a complex workload with Docker installation.

```bash
export ARCHIL_ENVIRONMENT="test.us-east-1.red"
python docker_workload.py
```

**What it demonstrates:**
- Using environment variables for configuration (`ARCHIL_ENVIRONMENT`)
- Complex initialization scripts (Docker installation)
- Running containerized workloads within Archil containers
- Using the 6.11-full kernel for systemd support

**Note:** This example demonstrates advanced usage. The initialization script installs Docker, uv, and sets up a Python environment. If you encounter API errors, the script may need to be shortened or split into multiple steps.

---

## Key Concepts

### Synchronous API

All examples use the synchronous API - no `asyncio` needed!

```python
import archil

client = archil.Archil()  # Simple!
disks = client.disks.list()  # No await!
```

### Region & Environment Configuration

The client supports multiple ways to specify your environment:

**1. Environment Variables (Simplest for Dev/CI)**

```bash
export ARCHIL_REGION="aws-us-west-2"
# Now all scripts use this region by default
python example.py
```

**2. Explicit Parameters**

```python
# Region
client = archil.Archil(region="aws-us-east-1")

# Environment string
client = archil.Archil(environment="test.us-east-1.red")

# Custom base_url
client = archil.Archil(base_url="https://control.red.us-east-1.aws.test.archil.com")
```

**Priority**: Explicit parameters > `ARCHIL_ENVIRONMENT` > `ARCHIL_REGION` > default (aws-us-east-1)

Available regions: `aws-us-east-1`, `aws-us-west-2`, `aws-eu-west-1`, `gcp-us-central1`

### Disk-Centric Containers

Containers are a property of disks:

```python
disk = client.disks.list()[0]
container = disk.containers.run(command="...")
```

This makes the relationship clear and automatically configures the mount.

### Environment Variables

The client automatically reads configuration from environment variables:

```bash
export ARCHIL_API_KEY="key-xxx"           # Required (or pass api_key=)
export ARCHIL_REGION="aws-us-west-2"      # Optional (defaults to aws-us-east-1)
# OR
export ARCHIL_ENVIRONMENT="test.us-east-1.red"  # Optional (overrides ARCHIL_REGION)

python example.py  # No need to pass parameters!
```

### Wait for Completion

Built-in method to wait for containers to finish:

```python
container = disk.containers.run(command="...")
completed = container.wait_for_completion(timeout=600)
print(f"Exit code: {completed.exit_code}")
```

No manual polling required!

---

## Common Patterns

### Error Handling

```python
try:
    container = disk.containers.run(command="...")
    completed = container.wait_for_completion(timeout=300)

    if completed.exit_code == 0:
        print("Success!")
    else:
        print(f"Failed: {completed.exit_reason}")

except TimeoutError:
    print("Container took too long")
except archil.ContainerError as e:
    print(f"Container error: {e}")
```

### Resource Configuration

```python
container = disk.containers.run(
    command="...",
    vcpu_count=8,           # CPUs
    mem_size_mib=16384,     # 16GB RAM
    kernel="6.11-full",     # Kernel type
    base_image="ubuntu-22.04"
)
```

### Initialization Scripts

```python
container = disk.containers.run(
    command="python train.py",
    initialization_script="""
        apt-get update
        apt-get install -y python3-pip
        pip install torch torchvision
    """
)
```

---

## Need Help?

- SDK Documentation: https://docs.archil.com
- Report Issues: https://github.com/archil/archil-sdk-python/issues
