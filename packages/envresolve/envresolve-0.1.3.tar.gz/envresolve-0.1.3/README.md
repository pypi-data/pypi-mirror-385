# envresolve

Resolve environment variables from secret stores like Azure Key Vault.

## Features

- **Variable expansion**: Expand `${VAR}` and `$VAR` syntax in strings
- **Secret resolution**: Fetch secrets from Azure Key Vault (more providers coming)
- **Circular reference detection**: Prevents infinite loops in variable chains
- **Type-safe**: Full mypy type checking support

## Quick Start

### Variable Expansion

Expand variables without connecting to external services:

```python
from envresolve import expand_variables

env = {"VAULT": "corp-kv", "SECRET": "db-password"}
result = expand_variables("akv://${VAULT}/${SECRET}", env)
print(result)  # akv://corp-kv/db-password
```

### Load from .env File

Load environment variables from a `.env` file with automatic secret resolution:

```python
import envresolve

# .env file content:
# VAULT_NAME=my-vault
# DATABASE_URL=akv://${VAULT_NAME}/db-url
# API_KEY=akv://${VAULT_NAME}/api-key

# Requires: pip install envresolve[azure]
# Requires: Azure authentication (az login, Managed Identity, etc.)
envresolve.register_azure_kv_provider()

# Load .env and resolve all secret URIs
# By default, exports to os.environ
resolved_vars = envresolve.load_env(".env")

# Or load without exporting
resolved_vars = envresolve.load_env(".env", export=False)
```

### Direct Secret Resolution

Fetch individual secrets from Azure Key Vault:

```python
import envresolve

# Requires: pip install envresolve[azure]
# Requires: Azure authentication (az login, Managed Identity, etc.)
try:
    envresolve.register_azure_kv_provider()
    secret_value = envresolve.resolve_secret("akv://corp-vault/db-password")
    print(secret_value)
except envresolve.ProviderRegistrationError as e:
    print(f"Azure SDK not available: {e}")
except envresolve.SecretResolutionError as e:
    print(f"Failed to fetch secret: {e}")
```

### Resolve Existing Environment Variables

Resolve secret URIs already set in `os.environ` (useful for containerized applications):

```python
import os
import envresolve

# Environment variables set by container orchestrator or parent process
os.environ["API_KEY"] = "akv://prod-vault/api-key"
os.environ["DB_PASSWORD"] = "akv://prod-vault/db-password"

# Requires: pip install envresolve[azure]
envresolve.register_azure_kv_provider()

# Resolve all environment variables containing secret URIs
resolved = envresolve.resolve_os_environ()

# Resolve only specific keys
resolved = envresolve.resolve_os_environ(keys=["API_KEY"])

# Resolve variables with prefix and strip the prefix
# DEV_API_KEY -> API_KEY, DEV_DB_URL -> DB_URL
os.environ["DEV_API_KEY"] = "akv://dev-vault/api-key"
os.environ["DEV_DB_URL"] = "akv://dev-vault/db-url"
resolved = envresolve.resolve_os_environ(prefix="DEV_")
```

## Installation

```bash
# Basic installation (variable expansion only)
pip install envresolve

# With Azure Key Vault support
pip install envresolve[azure]
```

## Documentation

Full documentation: https://osoekawaitlab.github.io/envresolve/

## Development

### Setup

This project uses `uv` for dependency management and `nox` for task automation:

```bash
# Install uv (if not already installed)
pip install uv

# Clone the repository
git clone https://github.com/osoekawaitlab/envresolve.git
cd envresolve

# Install dependencies (including dev dependencies)
uv pip install -e ".[azure]" --group=dev
```

### Running Tests

```bash
# Quick test during development
nox -s tests_unit      # Unit tests only (fast)
nox -s tests_e2e       # E2E tests with mocked Azure SDK

# Full test suite
nox -s tests           # All tests with coverage report (HTML in htmlcov/)

# Test across Python versions
nox -s tests_all_versions  # Test on Python 3.10-3.14

# Test without Azure SDK
nox -s tests_without_azure  # For environments without Azure dependencies
```

### Code Quality

```bash
# Run all quality checks
nox -s quality         # Type checking (mypy) + linting (ruff)

# Individual checks
nox -s mypy            # Type checking only
nox -s lint            # Linting only
nox -s format_code     # Auto-format code

# Run everything
nox -s check_all       # Tests + quality checks
```

### Live Azure Tests

Optional integration tests against real Azure Key Vault:

```bash
# One-time setup
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your Azure credentials
terraform init
terraform apply

# Before running tests
az login
source scripts/setup_live_tests.sh

# Run live tests
nox -s tests_live
```

See [Live Azure Tests documentation](https://osoekawaitlab.github.io/envresolve/developer-guide/live-tests/) for detailed setup instructions.

### Build Documentation

```bash
# Build documentation
nox -s docs_build

# Serve documentation locally (with live reload)
nox -s docs_serve      # Open http://localhost:8000
```

### Contributing

See [Contributing Guide](https://osoekawaitlab.github.io/envresolve/contributing/) for guidelines on:

- Code style and conventions
- Test-driven development workflow
- Creating issues and pull requests
- Architecture Decision Records (ADRs)
