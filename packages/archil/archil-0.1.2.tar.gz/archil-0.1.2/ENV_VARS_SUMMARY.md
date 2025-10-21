# Environment Variable Support - Summary

## Added Features

Added support for `ARCHIL_REGION` and `ARCHIL_ENVIRONMENT` environment variables, complementing the existing `ARCHIL_API_KEY` support.

## Priority Order

When initializing the client, configuration is resolved in this order:

1. **Explicit parameters** (highest priority)
   - `region="aws-us-east-1"`
   - `environment="test.us-east-1.red"`
   - `base_url="https://..."`

2. **ARCHIL_ENVIRONMENT** environment variable
   - `export ARCHIL_ENVIRONMENT="test.us-east-1.red"`

3. **ARCHIL_REGION** environment variable
   - `export ARCHIL_REGION="aws-us-west-2"`

4. **Default** (lowest priority)
   - Defaults to `aws-us-east-1` if nothing else is specified

## Usage Examples

### Simple Region Configuration

```bash
export ARCHIL_API_KEY="your-api-key"
export ARCHIL_REGION="aws-us-west-2"
```

```python
import archil

# No parameters needed!
client = archil.Archil()

# Result:
# - base_url: https://control.green.us-west-2.aws.prod.archil.com
# - env: prod.aws.us-west-2.green
# - region: us-west-2
```

### Custom Environment Configuration

```bash
export ARCHIL_API_KEY="your-api-key"
export ARCHIL_ENVIRONMENT="test.us-east-1.red"
```

```python
import archil

# Automatically uses test environment
client = archil.Archil()

# Result:
# - base_url: https://control.red.us-east-1.aws.test.archil.com
# - env: test.us-east-1.red
# - region: us-east-1
```

### Override with Explicit Parameters

```bash
export ARCHIL_REGION="aws-us-west-2"  # This will be ignored
```

```python
import archil

# Explicit parameter takes precedence
client = archil.Archil(region="aws-eu-west-1")

# Result: uses aws-eu-west-1, not the env var
```

## Benefits

### 1. Development & Testing

Set environment variables once in your shell:

```bash
# Development setup
export ARCHIL_API_KEY="dev-key"
export ARCHIL_ENVIRONMENT="test.us-east-1.red"

# Now all scripts use test environment by default
python script1.py
python script2.py
python script3.py
```

### 2. CI/CD Integration

Configure via environment in your CI/CD pipeline:

```yaml
# GitHub Actions
env:
  ARCHIL_API_KEY: ${{ secrets.ARCHIL_API_KEY }}
  ARCHIL_REGION: aws-us-west-2

steps:
  - name: Run tests
    run: python tests.py  # Automatically uses correct region
```

### 3. Docker/Container Deployments

```dockerfile
ENV ARCHIL_API_KEY=${ARCHIL_API_KEY}
ENV ARCHIL_REGION=aws-eu-west-1

CMD ["python", "app.py"]
```

### 4. 12-Factor App Compliance

Follows [12-Factor App](https://12factor.net/) configuration principles by storing config in environment variables.

## Implementation Details

### Code Changes

**archil/client.py**:
```python
# Check environment variables if no parameters provided
env_var = os.getenv("ARCHIL_ENVIRONMENT")
region_var = os.getenv("ARCHIL_REGION")

if env_var:
    self.environment = Environment(env=env_var)
elif region_var:
    self.environment = Environment(region=region_var)
else:
    # Default to aws-us-east-1
    self.environment = Environment(region="aws-us-east-1")
```

### Test Coverage

Created comprehensive tests in `test_env_vars.py`:

✓ ARCHIL_REGION environment variable is respected
✓ ARCHIL_ENVIRONMENT environment variable is respected
✓ Explicit parameters override environment variables
✓ ARCHIL_ENVIRONMENT takes priority over ARCHIL_REGION
✓ Defaults to aws-us-east-1 when no env vars set

All tests pass successfully!

## Available Regions

When using `ARCHIL_REGION`, these predefined mappings are available:

- `aws-us-east-1` → `prod.us-east-1.green`
- `aws-us-west-2` → `prod.aws.us-west-2.green`
- `aws-eu-west-1` → `prod.aws.eu-west-1.green`
- `gcp-us-central1` → `prod.gcp.us-central1.blue`

For custom environments, use `ARCHIL_ENVIRONMENT` with the full environment string.

## Documentation Updates

- `examples/README.md`: Added Prerequisites section showing env var usage
- `examples/README.md`: Updated Region & Environment Configuration section
- `examples/docker_workload.py`: New example demonstrating `ARCHIL_ENVIRONMENT`
- `ENVIRONMENT_CONFIG_SUMMARY.md`: Updated with env var priority order
- All example files: Added comments about region configuration

## Backward Compatibility

✓ Fully backward compatible
✓ Existing code works without changes
✓ Environment variables are optional
✓ Defaults remain unchanged (aws-us-east-1)
