# Environment Variable Feature - Testing & Validation

This document describes how to test and validate the environment variable feature in Archil containers.

## Overview

The environment variable feature allows you to pass custom environment variables to containers when creating them. These variables are available in all exec sessions within the container.

Additionally, three special variables are automatically added:
- `ARCHIL_CONTAINER_ID` - The container's unique identifier
- `ARCHIL_DISK_ID` - The mounted disk ID
- `ARCHIL_REGION` - The region or environment name from the mount configuration

## Quick Test

The fastest way to validate the feature is using the simple test script:

```bash
# Set your credentials
export ARCHIL_API_KEY="your-api-key-here"
export ARCHIL_DISK_ID="disk_abc123"

# Run the test
cd examples
python simple_env_test.py
```

### Expected Output

If everything is working correctly, you should see:

```
🧪 Testing Environment Variable Support
============================================================

✓ Connected to https://api.archil.io

📦 Creating container with custom environment variables:
   MY_CUSTOM_VAR=hello_from_sdk
   TEST_NUMBER=42
   API_ENDPOINT=https://api.example.com

✓ Container created: <container-id>
  Status: starting

⏳ Waiting for container to complete...

📊 Results:
  Exit Code: 0
  Status: exited

✅ SUCCESS! Environment variables are working correctly.
```

## Comprehensive Validation

For more detailed testing, use the full validation script:

```bash
python examples/validate_env_vars.py \
  --disk-id disk_abc123 \
  --api-key your-api-key \
  --region aws-us-east-1
```

This script:
1. Creates a container with multiple test environment variables
2. Runs a validation command that checks each variable
3. Verifies that all custom and special Archil variables are present
4. Reports success or failure with detailed diagnostics

## Manual Testing

You can also test manually by creating containers programmatically:

```python
import archil
from archil import ArchilMount

client = archil.Archil(api_key="your-key")

# Create a container with env vars
container = client.containers.run(
    command="env | grep -E '(MY_VAR|ARCHIL_)'",
    archil_mount=ArchilMount(
        disk_id="disk_abc123",
        env="production",
    ),
    env={
        "MY_VAR_1": "value1",
        "MY_VAR_2": "value2"
    }
)

# Wait and check results
completed = container.wait_for_completion(timeout=120)
print(f"Exit code: {completed.exit_code}")
```

## Verifying in the Container

To verify environment variables are actually available in the container, you can:

### Option 1: Via Container Command
Run a command that prints the variables:

```python
container = client.containers.run(
    command="echo MY_VAR=$MY_VAR && echo ARCHIL_CONTAINER_ID=$ARCHIL_CONTAINER_ID",
    archil_mount=ArchilMount(disk_id="disk_id"),
    env={"MY_VAR": "test"}
)
```

### Option 2: Via WebSocket Connection
Connect to the container interactively and run:

```bash
env | grep -E '(MY_|ARCHIL_)'
```

### Option 3: Check Runtime Logs
On the runtime host, check the console logs:

```bash
cat /tmp/firecracker_<container-id>_console.log
```

## Troubleshooting

### Container exits with non-zero code

**Possible causes:**
1. Environment variables not being passed from SDK to Controller
2. Controller not passing env vars to Runtime
3. Runtime not applying env vars to exec sessions

**Debug steps:**
1. Check SDK is sending env vars: Add debug logging to `archil/containers.py`
2. Check Controller receives env vars: Check Controller logs
3. Check Runtime receives env vars: Check Runtime logs at `/tmp/firecracker_<id>_console.log`
4. Verify all components are updated with the latest code

### Variables are undefined in container

**Possible causes:**
1. Env vars not included in exec request payload
2. Agent not applying env vars to process environment

**Debug steps:**
1. Check WebSocket exec request includes "env" field
2. Check agent logs for environment variable application
3. Verify the agent is handling the env field correctly

### Special Archil variables missing

**Possible causes:**
1. `get_exec_env()` not being called
2. Mount info not stored in ContainerInfo
3. Container ID not being passed

**Debug steps:**
1. Check `ContainerInfo` has `archil_mount_info` field populated
2. Verify `get_exec_env()` is called before exec request
3. Check logs for "Starting exec session with N environment variables"

## Architecture Flow

Here's how environment variables flow through the system:

```
Python SDK (env dict)
    ↓
Controller API (/api/containers)
    ↓
Controller stores in DynamoDB
    ↓
Controller sends InternalStartRequest to Runtime
    ↓
Runtime stores in ContainerInfo
    ↓
WebSocket connection → get_exec_env()
    ↓
Runtime adds special Archil vars
    ↓
VsockRequest with complete env map
    ↓
Agent applies to exec session
    ↓
All variables available in container
```

## Success Criteria

The feature is working correctly when:

1. ✅ Custom env vars can be passed via Python SDK
2. ✅ Variables are stored in Controller's DynamoDB
3. ✅ Variables are passed to Runtime in start request
4. ✅ Variables are available in WebSocket exec sessions
5. ✅ Special Archil variables are automatically added
6. ✅ All variables persist for the container's lifetime

## Related Files

### Python SDK
- `archil/containers.py` - Container creation with env support
- `archil/disks.py` - Disk-scoped container creation
- `examples/container_with_env_vars.py` - Usage examples
- `examples/simple_env_test.py` - Quick validation script
- `examples/validate_env_vars.py` - Comprehensive validation

### Controller (Go)
- `src/containers/models.go` - Data models with env field
- `src/containers/manager.go` - Container creation logic
- `src/containers/runtime_client.go` - Runtime communication

### Runtime (Rust)
- `server/src/internal_api.rs` - API endpoint handling
- `server/src/containers.rs` - Container management and env handling
- `server/src/server.rs` - WebSocket handler with env injection
