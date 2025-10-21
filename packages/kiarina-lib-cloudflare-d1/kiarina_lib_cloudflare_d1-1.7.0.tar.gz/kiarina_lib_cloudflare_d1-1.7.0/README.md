# kiarina-lib-cloudflare-d1

A Python client library for [Cloudflare D1](https://developers.cloudflare.com/d1/) that separates infrastructure configuration from application logic.

## Design Philosophy: Infrastructure-Application Separation

This library follows the principle of **complete separation between infrastructure configuration and application logic**.

### The Problem

Most applications tightly couple infrastructure details with business logic:

```python
# ❌ Bad: Infrastructure details leak into application code
import httpx

def get_user(user_id: int):
    response = httpx.post(
        f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/d1/database/{DATABASE_ID}/query",
        headers={"Authorization": f"Bearer {API_TOKEN}"},
        json={"sql": "SELECT * FROM users WHERE id = ?", "params": [user_id]}
    )
    return response.json()
```

**Problems with this approach:**
- ❌ Can't test without real Cloudflare credentials
- ❌ Can't switch environments (dev/staging/prod) without code changes
- ❌ Security risks (credentials visible in code)
- ❌ Hard to support multi-tenancy (multiple Cloudflare accounts)
- ❌ Infrastructure details scattered throughout the codebase

### The Solution

This library externalizes all infrastructure configuration:

```python
# ✅ Good: Pure business logic, infrastructure injected externally
from kiarina.lib.cloudflare.d1 import create_d1_client

def get_user(user_id: int):
    client = create_d1_client()  # Configuration injected from environment
    result = client.query("SELECT * FROM users WHERE id = ?", [user_id])
    return result.first.rows
```

**Benefits:**
- ✅ Same code works in dev, staging, and production
- ✅ Easy to test (inject test configuration)
- ✅ Credentials managed externally (environment variables, secrets manager)
- ✅ Multi-tenancy support built-in
- ✅ Infrastructure changes don't require code changes

## When to Use This Library

### ✅ Use this library if:

- You deploy the same code to multiple environments (dev/staging/prod)
- You need to support multiple Cloudflare accounts (multi-tenancy)
- You want to test without real D1 databases
- You manage credentials externally (environment variables, secrets manager)
- You value clean separation between infrastructure and application logic

### ❌ Don't use this library if:

- You only have one environment and don't plan to change it
- You're building Cloudflare Workers (use native D1 bindings instead)
- You prefer to manage all configuration in code
- You need ORM-like features (this is a thin wrapper by design)

## Features

- **Configuration Management**: Use `pydantic-settings-manager` for flexible configuration
- **Sync & Async**: Support for both synchronous and asynchronous operations
- **Type Safety**: Full type hints and Pydantic validation
- **Integration with kiarina-lib-cloudflare-auth**: Seamless authentication
- **Multiple Configurations**: Support for multiple named configurations
- **Environment Variable Support**: Configure via environment variables
- **Thin Wrapper**: Simple, maintainable, and easy to understand

## Installation

```bash
pip install kiarina-lib-cloudflare-d1
```

## Quick Start

### Basic Usage (Sync)

```python
from kiarina.lib.cloudflare.d1 import create_d1_client

# Get a D1 client with default settings
client = create_d1_client()

# Execute a query
result = client.query("SELECT * FROM users WHERE id = ?", [1])

# Access results
for row in result.first.rows:
    print(row)
```

### Async Usage

```python
from kiarina.lib.cloudflare.d1.asyncio import create_d1_client

async def main():
    # Get an async D1 client
    client = create_d1_client()

    # Execute a query
    result = await client.query("SELECT * FROM users WHERE id = ?", [1])

    # Access results
    for row in result.first.rows:
        print(row)
```

## Real-World Use Cases

### Use Case 1: Multi-Environment Deployment

Deploy the same application code to different environments with different configurations.

```yaml
# config/production.yaml
cloudflare_d1:
  default:
    database_id: "prod-database-id"

cloudflare_auth:
  default:
    account_id: "prod-account-id"
    api_token: "${CLOUDFLARE_PROD_API_TOKEN}"  # From secrets manager

# config/staging.yaml
cloudflare_d1:
  default:
    database_id: "staging-database-id"

cloudflare_auth:
  default:
    account_id: "staging-account-id"
    api_token: "${CLOUDFLARE_STAGING_API_TOKEN}"
```

```python
# Application code (same for all environments)
from kiarina.lib.cloudflare.d1 import create_d1_client

def get_user_profile(user_id: int):
    """Get user profile - works in any environment"""
    client = create_d1_client()
    result = client.query("SELECT * FROM users WHERE id = ?", [user_id])
    return result.first.rows[0] if result.first.rows else None
```

**Result:**
- Production: Uses `prod-database-id` and production credentials
- Staging: Uses `staging-database-id` and staging credentials
- Development: Uses local test database
- **No code changes required**

### Use Case 2: Multi-Tenant Application

Support multiple tenants with isolated databases, without changing application code.

```python
from kiarina.lib.cloudflare.d1 import settings_manager, create_d1_client
from kiarina.lib.cloudflare.auth import settings_manager as auth_settings_manager

# Configure tenant-specific databases
settings_manager.user_config = {
    "tenant_acme": {
        "database_id": "acme-corp-database-id"
    },
    "tenant_globex": {
        "database_id": "globex-database-id"
    }
}

auth_settings_manager.user_config = {
    "tenant_acme": {
        "account_id": "acme-account-id",
        "api_token": "acme-api-token"
    },
    "tenant_globex": {
        "account_id": "globex-account-id",
        "api_token": "globex-api-token"
    }
}

# Application code - tenant-agnostic
def get_tenant_users(tenant_id: str):
    """Get users for any tenant"""
    config_key = f"tenant_{tenant_id}"
    client = create_d1_client(
        config_key=config_key,
        auth_config_key=config_key
    )
    result = client.query("SELECT * FROM users")
    return result.first.rows

# Use with different tenants
acme_users = get_tenant_users("acme")
globex_users = get_tenant_users("globex")
```

### Use Case 3: Testing

Write tests without touching real Cloudflare D1 databases.

```python
# tests/conftest.py
import pytest
from kiarina.lib.cloudflare.d1 import settings_manager
from kiarina.lib.cloudflare.auth import settings_manager as auth_settings_manager

@pytest.fixture
def mock_d1_config():
    """Configure test D1 database"""
    settings_manager.user_config = {
        "test": {
            "database_id": "test-database-id"
        }
    }
    auth_settings_manager.user_config = {
        "test": {
            "account_id": "test-account-id",
            "api_token": "test-api-token"
        }
    }
    
    # Set active key to test
    settings_manager.active_key = "test"
    auth_settings_manager.active_key = "test"
    
    yield
    
    # Cleanup
    settings_manager.clear()
    auth_settings_manager.clear()

# tests/test_user_service.py
def test_get_user_profile(mock_d1_config):
    """Test user profile retrieval"""
    from myapp.services import get_user_profile
    
    # Application code uses test configuration automatically
    profile = get_user_profile(user_id=1)
    
    assert profile is not None
    assert "name" in profile
```

## Configuration

This library uses [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) for flexible configuration management and integrates with [kiarina-lib-cloudflare-auth](../kiarina-lib-cloudflare-auth/) for authentication.

### Environment Variables

Configure the D1 connection and authentication using environment variables:

```bash
# D1 database ID
export KIARINA_LIB_CLOUDFLARE_D1_DATABASE_ID="your-database-id"

# Cloudflare authentication (from kiarina-lib-cloudflare-auth)
export KIARINA_LIB_CLOUDFLARE_AUTH_ACCOUNT_ID="your-account-id"
export KIARINA_LIB_CLOUDFLARE_AUTH_API_TOKEN="your-api-token"
```

### Programmatic Configuration

```python
from kiarina.lib.cloudflare.d1 import settings_manager
from kiarina.lib.cloudflare.auth import settings_manager as auth_settings_manager

# Configure D1 settings
settings_manager.user_config = {
    "development": {
        "database_id": "dev-database-id"
    },
    "production": {
        "database_id": "prod-database-id"
    }
}

# Configure authentication
auth_settings_manager.user_config = {
    "development": {
        "account_id": "dev-account-id",
        "api_token": "dev-api-token"
    },
    "production": {
        "account_id": "prod-account-id",
        "api_token": "prod-api-token"
    }
}

# Switch to production configuration
settings_manager.active_key = "production"
auth_settings_manager.active_key = "production"

client = create_d1_client()
```

### Runtime Overrides

```python
from kiarina.lib.cloudflare.d1 import create_d1_client

# Use specific configuration keys
client = create_d1_client(
    config_key="production",
    auth_config_key="production"
)
```

## Integration with Other kiarina Libraries

This library is part of the kiarina ecosystem, designed for consistent infrastructure management:

```python
# Unified configuration approach across different services
from kiarina.lib.cloudflare.d1 import create_d1_client
from kiarina.lib.redis import get_redis
from kiarina.lib.google.cloud_storage import get_blob

# All configured externally, same pattern
d1_client = create_d1_client()
redis_client = get_redis()
storage_blob = get_blob(blob_name="data.json")

# Application code is clean and infrastructure-agnostic
result = d1_client.query("SELECT * FROM users WHERE id = ?", [1])
redis_client.set("user:1", json.dumps(result.first.rows[0]))
storage_blob.upload_from_string(json.dumps(result.first.rows[0]))
```

## API Reference

### D1Client

The main client class for interacting with Cloudflare D1.

```python
class D1Client:
    def query(self, sql: str, params: list[Any] | None = None) -> Result
```

**Sync Example:**
```python
from kiarina.lib.cloudflare.d1 import create_d1_client

client = create_d1_client()
result = client.query("SELECT * FROM users WHERE age > ?", [18])
```

**Async Example:**
```python
from kiarina.lib.cloudflare.d1.asyncio import create_d1_client

client = create_d1_client()
result = await client.query("SELECT * FROM users WHERE age > ?", [18])
```

### create_d1_client()

Create a D1 client with configuration.

```python
def create_d1_client(
    config_key: str | None = None,
    *,
    auth_config_key: str | None = None,
) -> D1Client
```

**Parameters:**
- `config_key` (str | None): Configuration key for D1 settings (default: None uses active key)
- `auth_config_key` (str | None): Configuration key for authentication settings (default: None uses active key)

**Returns:**
- `D1Client`: Configured D1 client instance

**Example:**
```python
# Use default configuration
client = create_d1_client()

# Use specific configurations
client = create_d1_client(
    config_key="production",
    auth_config_key="production"
)
```

### Result

Query result container with access to result data.

```python
class Result:
    success: bool
    result: list[QueryResult]
    
    @property
    def first(self) -> QueryResult
```

**Properties:**
- `success` (bool): Whether the query was successful
- `result` (list[QueryResult]): List of query results
- `first` (QueryResult): First query result (raises ValueError if no results)

**Example:**
```python
result = client.query("SELECT * FROM users")

# Check success
if result.success:
    # Access first result
    first_result = result.first
    
    # Iterate over rows
    for row in first_result.rows:
        print(row)
```

### QueryResult

Individual query result with metadata and rows.

```python
class QueryResult:
    success: bool
    meta: dict[str, Any]
    results: list[dict[str, Any]]
    
    @property
    def rows(self) -> list[dict[str, Any]]
```

**Properties:**
- `success` (bool): Whether this specific query was successful
- `meta` (dict[str, Any]): Query metadata (e.g., affected rows, execution time)
- `results` (list[dict[str, Any]]): Query result rows
- `rows` (list[dict[str, Any]]): Alias for `results`

**Example:**
```python
result = client.query("SELECT id, name, email FROM users")
query_result = result.first

# Access metadata
print(f"Rows returned: {query_result.meta.get('rows_read', 0)}")

# Access rows
for row in query_result.rows:
    print(f"User: {row['name']} ({row['email']})")
```

## Usage Examples

### Basic CRUD Operations

```python
from kiarina.lib.cloudflare.d1 import create_d1_client

client = create_d1_client()

# Create
result = client.query(
    "INSERT INTO users (name, email) VALUES (?, ?)",
    ["Alice", "alice@example.com"]
)
print(f"Inserted: {result.success}")

# Read
result = client.query("SELECT * FROM users WHERE name = ?", ["Alice"])
for row in result.first.rows:
    print(f"Found user: {row}")

# Update
result = client.query(
    "UPDATE users SET email = ? WHERE name = ?",
    ["alice.new@example.com", "Alice"]
)
print(f"Updated: {result.success}")

# Delete
result = client.query("DELETE FROM users WHERE name = ?", ["Alice"])
print(f"Deleted: {result.success}")
```

### Batch Operations

```python
# Insert multiple rows
users = [
    ("Alice", "alice@example.com"),
    ("Bob", "bob@example.com"),
    ("Charlie", "charlie@example.com")
]

for name, email in users:
    client.query(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        [name, email]
    )

# Query all
result = client.query("SELECT * FROM users")
print(f"Total users: {len(result.first.rows)}")
```

### Async Batch Operations

```python
from kiarina.lib.cloudflare.d1.asyncio import create_d1_client
import asyncio

async def insert_users():
    client = create_d1_client()
    
    users = [
        ("Alice", "alice@example.com"),
        ("Bob", "bob@example.com"),
        ("Charlie", "charlie@example.com")
    ]
    
    # Execute queries concurrently
    tasks = [
        client.query(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            [name, email]
        )
        for name, email in users
    ]
    
    results = await asyncio.gather(*tasks)
    print(f"Inserted {sum(r.success for r in results)} users")

asyncio.run(insert_users())
```

### Error Handling

```python
from kiarina.lib.cloudflare.d1 import create_d1_client
import httpx

client = create_d1_client()

try:
    result = client.query("SELECT * FROM users")
    
    if not result.success:
        print("Query failed")
    else:
        for row in result.first.rows:
            print(row)
            
except httpx.HTTPStatusError as e:
    print(f"HTTP error: {e.response.status_code}")
except ValueError as e:
    print(f"No results: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Working with Metadata

```python
result = client.query("SELECT * FROM users")
query_result = result.first

# Access query metadata
meta = query_result.meta
print(f"Duration: {meta.get('duration', 0)}ms")
print(f"Rows read: {meta.get('rows_read', 0)}")
print(f"Rows written: {meta.get('rows_written', 0)}")
```

## Configuration Reference

### D1Settings

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `database_id` | `str` | Yes | Cloudflare D1 database ID |

### Environment Variables

All settings can be configured via environment variables with the `KIARINA_LIB_CLOUDFLARE_D1_` prefix:

```bash
# D1 database ID
export KIARINA_LIB_CLOUDFLARE_D1_DATABASE_ID="your-database-id"
```

### Integration with kiarina-lib-cloudflare-auth

This library requires authentication configuration from [kiarina-lib-cloudflare-auth](../kiarina-lib-cloudflare-auth/):

```bash
# Cloudflare account ID
export KIARINA_LIB_CLOUDFLARE_AUTH_ACCOUNT_ID="your-account-id"

# Cloudflare API token
export KIARINA_LIB_CLOUDFLARE_AUTH_API_TOKEN="your-api-token"
```

See the [kiarina-lib-cloudflare-auth documentation](../kiarina-lib-cloudflare-auth/README.md) for more authentication options.

## Why a Thin Wrapper?

This library is intentionally a thin wrapper around the Cloudflare D1 API. This is a **feature, not a limitation**.

### Benefits of Being Thin

1. **Easy to Understand**: The code is simple and straightforward
2. **Easy to Maintain**: Fewer abstractions mean fewer bugs
3. **Easy to Extend**: You can easily add your own abstractions on top
4. **API Compatibility**: Changes to Cloudflare D1 API are easy to adopt
5. **Predictable Behavior**: What you see is what you get

### What This Library Does

- ✅ Separates infrastructure configuration from application code
- ✅ Provides type-safe configuration management
- ✅ Offers consistent API across sync and async
- ✅ Integrates with kiarina authentication libraries

### What This Library Doesn't Do

- ❌ ORM features (use SQLAlchemy or similar if needed)
- ❌ Query builders (use raw SQL or a query builder library)
- ❌ Schema migrations (use a migration tool)
- ❌ Connection pooling (not needed for HTTP-based API)

**Philosophy**: Do one thing well - separate infrastructure from application logic.

## Development

### Prerequisites

- Python 3.12+
- Cloudflare account with D1 database

### Setup

```bash
# Clone the repository
git clone https://github.com/kiarina/kiarina-python.git
cd kiarina-python

# Setup development environment
mise run setup
```

### Running Tests

Tests require actual Cloudflare D1 credentials. Set the following environment variables:

```bash
# Cloudflare authentication
export KIARINA_LIB_CLOUDFLARE_AUTH_TEST_ACCOUNT_ID="your-account-id"
export KIARINA_LIB_CLOUDFLARE_AUTH_TEST_API_TOKEN="your-api-token"

# D1 database ID
export KIARINA_LIB_CLOUDFLARE_D1_TEST_DATABASE_ID="your-test-database-id"
```

Run tests:

```bash
# Run format, lint, type checks and tests
mise run package kiarina-lib-cloudflare-d1

# Coverage report
mise run package:test kiarina-lib-cloudflare-d1 --coverage
```

Tests will be skipped (xfail) if these environment variables are not set.

## Dependencies

- [httpx](https://www.python-httpx.org/) - HTTP client for API requests
- [kiarina-lib-cloudflare-auth](../kiarina-lib-cloudflare-auth/) - Cloudflare authentication library
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Settings management
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) - Advanced settings management

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Contributing

This is a personal project, but contributions are welcome! Please feel free to submit issues or pull requests.

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python) - The main monorepo containing this package
- [kiarina-lib-cloudflare-auth](../kiarina-lib-cloudflare-auth/) - Cloudflare authentication library
- [Cloudflare D1](https://developers.cloudflare.com/d1/) - Cloudflare's serverless SQL database
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) - Configuration management library used by this package
