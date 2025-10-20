# Environment Configuration System - Implementation Summary

## Overview

Implemented a flexible environment configuration system for the Archil SDK that supports multiple initialization methods:

1. **Environment Variables** (simplest for dev/CI): `ARCHIL_REGION`, `ARCHIL_ENVIRONMENT`
2. **Region-based parameters**: `region="aws-us-east-1"`
3. **Environment string**: `environment="test.us-east-1.red"`
4. **Custom base_url**: `base_url="https://control.red.us-east-1.aws.test.archil.com"`

**Priority**: Explicit parameters > `ARCHIL_ENVIRONMENT` > `ARCHIL_REGION` > default (aws-us-east-1)

## Changes Made

### 1. New File: `archil/environment.py`

Created `Environment` class that handles:

- **Region mappings** to predefined environments:
  - `aws-us-east-1` → `prod.us-east-1.green`
  - `aws-us-west-2` → `prod.aws.us-west-2.green`
  - `aws-eu-west-1` → `prod.aws.eu-west-1.green`
  - `gcp-us-central1` → `prod.gcp.us-central1.blue`

- **Environment string parsing**:
  - 3-part format: `stage.region.color` (defaults provider to "aws")
  - 4-part format: `stage.provider.region.color`

- **Base URL construction**: `control.${color}.${region}.${provider}.${stage}.archil.com`

- **URL parsing**: Extracts environment components from existing URLs

### 2. Updated: `archil/client.py`

Modified `_ArchilAsync.__init__()` to:

- Accept `region`, `environment`, or `base_url` parameters (mutually exclusive)
- Read `ARCHIL_REGION` and `ARCHIL_ENVIRONMENT` environment variables if no parameters provided
- Create `Environment` object internally
- Default to `aws-us-east-1` when none specified

Priority order:
1. Explicit parameters (`region=`, `environment=`, `base_url=`)
2. `ARCHIL_ENVIRONMENT` environment variable
3. `ARCHIL_REGION` environment variable
4. Default to `aws-us-east-1`

Added properties:

```python
@property
def base_url(self) -> str:
    """Get the base URL."""
    return self.environment.base_url

@property
def env(self) -> str:
    """Get the environment string."""
    return self.environment.env

@property
def region(self) -> str:
    """Get the region."""
    return self.environment.region
```

### 3. Updated: Examples

- `examples/simple_container.py`
- `examples/run_command.py`
- `examples/ml_training.py`
- `examples/README.md`

All examples now show that the client defaults to `aws-us-east-1` and can optionally specify a different region.

## Usage Examples

### 1. Environment Variables (Simplest for Dev/CI)

```bash
export ARCHIL_API_KEY="your-api-key"
export ARCHIL_REGION="aws-us-west-2"
```

```python
import archil

# No parameters needed - reads from environment
client = archil.Archil()

# Result:
# - base_url: https://control.green.us-west-2.aws.prod.archil.com
# - env: prod.aws.us-west-2.green
# - region: us-west-2
```

Or use `ARCHIL_ENVIRONMENT` for more control:

```bash
export ARCHIL_ENVIRONMENT="test.us-east-1.red"
```

```python
client = archil.Archil()
# - base_url: https://control.red.us-east-1.aws.test.archil.com
# - env: test.us-east-1.red
```

### 2. Simple Region-Based (Recommended for Scripts)

```python
import archil

# Use predefined region mapping
client = archil.Archil(region="aws-us-east-1")

# Result:
# - base_url: https://control.green.us-east-1.aws.prod.archil.com
# - env: prod.us-east-1.green
# - region: us-east-1
```

### 3. Environment String (Advanced)

```python
import archil

# 3-part format (defaults to AWS)
client = archil.Archil(environment="test.us-east-1.red")

# 4-part format (explicit provider)
client = archil.Archil(environment="prod.gcp.us-central1.blue")

# Result:
# - base_url: https://control.red.us-east-1.aws.test.archil.com
# - env: test.us-east-1.red
# - region: us-east-1
```

### 4. Custom Base URL (For Test/Custom Environments)

```python
import archil

# Direct URL specification
client = archil.Archil(
    base_url="https://control.red.us-east-1.aws.test.archil.com"
)

# The client automatically extracts:
# - env: test.us-east-1.red
# - region: us-east-1
# - provider: aws
# - stage: test
# - color: red
```

### 5. Default Behavior

```python
import archil

# No parameters and no environment variables - defaults to aws-us-east-1
client = archil.Archil()

# Result:
# - base_url: https://control.green.us-east-1.aws.prod.archil.com
# - env: prod.us-east-1.green
# - region: us-east-1
```

**Note**: Default only applies when no parameters AND no `ARCHIL_REGION`/`ARCHIL_ENVIRONMENT` variables are set.

## Validation

Created comprehensive tests to verify:

✓ Region mappings work correctly
✓ 3-part environment format defaults provider to "aws"
✓ 4-part environment format uses explicit provider
✓ Custom base_url parsing extracts components correctly
✓ Client initialization works with all methods (parameters, env vars, defaults)
✓ Environment variable support (`ARCHIL_REGION`, `ARCHIL_ENVIRONMENT`)
✓ Priority order: explicit parameters > `ARCHIL_ENVIRONMENT` > `ARCHIL_REGION` > default
✓ Default region (aws-us-east-1) is used when nothing specified
✓ End-to-end container launch works with test environment

## Test Results

All tests pass:

```bash
$ python test_environment_config.py
Testing region mappings...
  ✓ aws-us-east-1 -> prod.us-east-1.green
  ✓ aws-us-west-2 -> prod.aws.us-west-2.green
  ✓ aws-eu-west-1 -> prod.aws.eu-west-1.green
  ✓ gcp-us-central1 -> prod.gcp.us-central1.blue

Testing 3-part environment format...
  ✓ prod.us-east-1.green -> provider='aws' (default)

Testing 4-part environment format...
  ✓ prod.gcp.us-central1.blue -> provider='gcp' (explicit)

Testing custom base_url...
  ✓ Parsed base_url correctly

✓ All tests passed!
```

End-to-end validation with real API:

```bash
$ python test_final_env_validation.py
Step 1: Initialize client with test environment...
  ✓ Client initialized
  ✓ base_url: https://control.red.us-east-1.aws.test.archil.com
  ✓ env: test.us-east-1.red
  ✓ region: us-east-1

Step 2: Get disks...
  ✓ Using disk: archil-data-workspace (dsk-000000000000413d)

Step 3: Launch container with 'sleep 5; exit 0'...
  ✓ Container launched: ae1e991b-2cef-486d-8245-2fe460cf61fe

Step 4: Wait for container to complete...
  ✓ Success! Container exited cleanly.

✓ All validation tests passed!
```

## Benefits

1. **Environment Variable Support**: Configure once with `ARCHIL_REGION`, use everywhere (great for dev/CI)
2. **Simpler API**: Users can just specify `region="aws-us-east-1"` instead of full URLs
3. **Flexibility**: Still supports custom environments and test deployments
4. **Automatic Parsing**: Base URL automatically extracts environment/region
5. **Type Safety**: Environment class validates inputs and provides clear error messages
6. **Clear Defaults**: Defaults to production aws-us-east-1 for convenience
7. **Priority System**: Explicit parameters always override environment variables

## Backward Compatibility

✓ Existing code using `base_url` continues to work
✓ No breaking changes to the API
✓ Only additions and improvements
