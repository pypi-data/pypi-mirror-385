# Integration Tests

This directory contains integration tests for the AnyTask CLI that require a running backend server.

## Prerequisites

1. **Backend Server**: A running AnyTask backend server (default: `http://localhost:8000`)
2. **Authentication**: A valid JWT token for API authentication

## Setup

### 1. Start the Backend Server

Make sure the AnyTask backend server is running. The default URL is `http://localhost:8000`.

If your backend runs on a different URL, set the environment variable:

```bash
export ANYT_TEST_API_URL="http://your-backend-url:port"
```

### 2. Obtain a Test JWT Token

Integration tests require a valid JWT token for authentication. You can obtain one by:

**Option A: Login via CLI**
```bash
anyt auth login
# The token will be saved in ~/.config/anyt/config.json
# Copy the token from there
```

**Option B: Generate from Backend**
```bash
# If you have direct access to the backend, generate a test token
# (specific commands depend on your backend implementation)
```

### 3. Set Environment Variables

```bash
# Required: Set your test JWT token
export ANYT_TEST_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLC..."

# Optional: Set custom API URL (defaults to http://localhost:8000)
export ANYT_TEST_API_URL="http://localhost:8000"
```

## Running Integration Tests

### Run All Integration Tests

```bash
make test-cli-integration
```

Or directly with pytest:

```bash
PYTHONPATH=src uv run pytest tests/cli/integration/ -v
```

### Run Specific Test File

```bash
PYTHONPATH=src uv run pytest tests/cli/integration/test_ai_commands_integration.py -v
```

### Run Specific Test

```bash
PYTHONPATH=src uv run pytest tests/cli/integration/test_ai_commands_integration.py::TestAIDecomposeCommand::test_decompose_basic -v
```

## Test Behavior

### Without ANYT_TEST_TOKEN

If `ANYT_TEST_TOKEN` is not set, all integration tests will be **automatically skipped** with a message:

```
SKIPPED: Integration tests require ANYT_TEST_TOKEN environment variable.
Please set a valid JWT token: export ANYT_TEST_TOKEN='your-jwt-token'
```

### Invalid Token Format

If the token is set but doesn't have the correct JWT format (3 parts separated by dots), tests will be skipped with:

```
SKIPPED: ANYT_TEST_TOKEN must be a valid JWT format (header.payload.signature).
Current token has X segments, expected 3.
```

## Test Configuration

Integration tests use fixtures from `conftest.py`:

- **`integration_auth_token`**: Provides the JWT token from `ANYT_TEST_TOKEN` env var
- **`integration_api_url`**: Provides the API URL (default: http://localhost:8000)
- **`integration_global_config`**: Pre-configured GlobalConfig with test credentials
- **`integration_workspace_config`**: Pre-configured workspace for testing
- **`mock_config_load`**: Automatically mocks config loading with test credentials

## Troubleshooting

### Tests are being skipped

**Problem**: All integration tests show as SKIPPED

**Solution**: Make sure you've set the `ANYT_TEST_TOKEN` environment variable:
```bash
export ANYT_TEST_TOKEN="your-valid-jwt-token"
```

### Authentication errors (401)

**Problem**: Tests fail with "401 Unauthorized" or "Invalid authentication token"

**Solutions**:
1. Verify your JWT token is valid and not expired
2. Make sure the token format is correct (should have 3 parts separated by dots)
3. Check that the backend server is using the same secret key for JWT validation
4. Regenerate a fresh token if the current one is expired

### Connection errors

**Problem**: Tests fail with connection errors

**Solutions**:
1. Make sure the backend server is running
2. Verify the API URL is correct (`echo $ANYT_TEST_API_URL`)
3. Check firewall/network settings

### Backend not found

**Problem**: "Connection refused" or similar errors

**Solution**: Start the backend server before running integration tests

## Example: Complete Setup

```bash
# 1. Start backend (in separate terminal)
cd /path/to/anytask-backend
./start_server.sh  # or your backend startup command

# 2. Get JWT token (one of these methods)
anyt auth login  # then copy token from ~/.config/anyt/config.json
# OR generate test token from backend

# 3. Set environment variables
export ANYT_TEST_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."
export ANYT_TEST_API_URL="http://localhost:8000"

# 4. Run integration tests
make test-cli-integration
```

## CI/CD Integration

For CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Integration Tests
  env:
    ANYT_TEST_TOKEN: ${{ secrets.ANYT_TEST_TOKEN }}
    ANYT_TEST_API_URL: http://localhost:8000
  run: |
    make test-cli-integration
```

## Notes

- Integration tests are automatically marked with `@pytest.mark.integration`
- Tests will be skipped if authentication is not properly configured
- Unit tests (in `tests/cli/unit/`) do NOT require a backend server and use mocked responses
- For development, prefer unit tests when possible; use integration tests to verify end-to-end behavior
