# kiarina-lib-google-cloud-storage

A Python client library for Google Cloud Storage that separates infrastructure configuration from application logic.

## Design Philosophy

This library follows the principle of **separating infrastructure concerns from application logic**, with special emphasis on **security rule alignment** and **path structure management**.

### The Problem

When using Google Cloud Storage directly, application code becomes tightly coupled with infrastructure details:

```python
# ❌ Infrastructure details leak into application code
from google.cloud import storage
from google.oauth2 import service_account

# Hard-coded credentials and bucket configuration
credentials = service_account.Credentials.from_service_account_file(
    '/path/to/service-account-key.json'
)
client = storage.Client(credentials=credentials)
bucket = client.bucket("prod-us-west1-app-data")  # Hard-coded bucket name
blob = bucket.blob("v2/users/data.json")  # Hard-coded path structure
```

**Problems with this approach:**
- Environment-specific details are scattered throughout the codebase
- Difficult to test (requires mocking or actual GCS access)
- Hard to support multiple environments (dev, staging, production)
- Challenging to implement multi-tenancy
- Credentials management is error-prone
- **Path structures are coupled with application code, making security rule changes difficult**

### The Solution: Blob Name Patterns

This library externalizes all infrastructure configuration, including path structures:

```python
# ✅ Application code only provides variables
from kiarina.lib.google.cloud_storage import get_blob

# Path structure is managed in configuration
blob = get_blob(placeholders={
    "user_id": user_id,
    "agent_id": agent_id,
    "basename": file_name
})
blob.upload_from_string(json.dumps(data))
```

**Benefits:**
- **Environment-agnostic**: Same code works in dev, staging, and production
- **Testable**: Easy to inject test configurations
- **Multi-tenant ready**: Different configurations for different tenants
- **Secure**: Credentials managed through kiarina-lib-google-auth
- **Maintainable**: Infrastructure changes don't require code changes
- **Security-aligned**: Path structures match GCS security rules, managed together

### Why Blob Name Patterns Matter

**The Core Problem**: GCS security rules define path structures, and application code must align with them.

#### Without Blob Name Patterns (Tight Coupling)

```python
# Application code constructs paths
blob_name = f"users/{user_id}/files/{file_name}"
blob = get_blob(blob_name=blob_name)
```

**GCS Security Rules:**
```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /users/{user_id}/files/{basename} {
      allow read, write: if request.auth.uid == user_id;
    }
  }
}
```

**What happens when security requirements change?**

New requirement: Add agent-level isolation for multi-tenancy.

**Updated Security Rules:**
```javascript
match /my-service/{tenant_id}/users/{user_id}/files/{basename} {
  allow read, write: if request.auth.uid == user_id
                     && request.auth.token.tenant_id == tenant_id;
}
```

**Problem**: You must now update **every place** in your application code that constructs these paths:
```python
# Must change all of these
blob_name = f"my-service/{tenant_id}/users/{user_id}/files/{file_name}"  # Changed!
blob_name = f"my-service/{tenant_id}/users/{user_id}/thumbnails/{file_name}"  # Changed!
blob_name = f"my-service/{tenant_id}/users/{user_id}/exports/{file_name}"  # Changed!
# ... and many more
```

#### With Blob Name Patterns (Loose Coupling)

**Configuration (Infrastructure Concern):**
```yaml
# config/production.yaml
google_cloud_storage:
  default:
    bucket_name: "my-app-data"
    blob_name_pattern: "my-service/{tenant_id}/users/{user_id}/files/{basename}"
```

**GCS Security Rules (Infrastructure Concern):**
```javascript
match /my-service/{tenant_id}/users/{user_id}/files/{basename} {
  allow read, write: if request.auth.uid == user_id
                     && request.auth.token.tenant_id == tenant_id;
}
```

**Application Code (Business Logic):**
```python
# Application only provides variables - no path knowledge
blob = get_blob(placeholders={
    "user_id": current_user.id,
    "agent_id": current_agent.id,
    "basename": uploaded_file.name
})
blob.upload_from_string(file_content)
```

**When security rules change**: Only update the configuration file. Application code remains unchanged.

#### Real-World Example: Multi-Environment Security

Different environments often have different security requirements:

**Production** (strict isolation):
```yaml
blob_name_pattern: "v2/production/{tenant_id}/{user_id}/{agent_id}/files/{basename}"
```

**Staging** (relaxed for testing):
```yaml
blob_name_pattern: "v2/staging/{user_id}/files/{basename}"
```

**Development** (flat structure):
```yaml
blob_name_pattern: "dev/{basename}"
```

**Application code** (same for all environments):
```python
blob = get_blob(placeholders={
    "tenant_id": tenant.id,
    "user_id": user.id,
    "agent_id": agent.id,
    "basename": file.name
})
```

Missing placeholders are simply ignored if not present in the pattern.

### Design Principles

1. **Infrastructure defines "where"**: Path structures, bucket names, security rules
2. **Application defines "what"**: Data content, business logic, variables
3. **Configuration is the contract**: Placeholders define the interface between infrastructure and application
4. **Security rules and path patterns are managed together**: Both are infrastructure concerns

## Features

- **Configuration Management**: Use `pydantic-settings-manager` for flexible configuration
- **Type Safety**: Full type hints and Pydantic validation
- **Integration with kiarina-lib-google-auth**: Seamless authentication
- **Multiple Configurations**: Support for multiple named configurations
- **Environment Variable Support**: Configure via environment variables
- **Blob Name Prefix**: Organize blobs with configurable prefixes
- **Native API Access**: Returns native `google-cloud-storage` objects for full API access

## Installation

```bash
pip install kiarina-lib-google-cloud-storage
```

## Quick Start

### Basic Usage

```python
from kiarina.lib.google.cloud_storage import get_blob, settings_manager

# Configure once (typically in your app initialization)
settings_manager.user_config = {
    "default": {
        "bucket_name": "my-app-data",
        "blob_name_pattern": "production/v1/{basename}"
    }
}

# Application code - clean and simple
blob = get_blob(placeholders={"basename": "user_data.json"})
# Actual path: gs://my-app-data/production/v1/user_data.json

# Or use direct blob name (full path)
blob = get_blob(blob_name="production/v1/user_data.json")

# Use native google-cloud-storage API
blob.upload_from_string("Hello, World!")
content = blob.download_as_text()
```

### Configuration via Environment Variables

```bash
# Set once in your deployment environment
export KIARINA_LIB_GOOGLE_CLOUD_STORAGE_BUCKET_NAME="my-app-data"
export KIARINA_LIB_GOOGLE_CLOUD_STORAGE_BLOB_NAME_PREFIX="production/v1"
```

```python
# Application code - no configuration needed
from kiarina.lib.google.cloud_storage import get_blob

blob = get_blob(blob_name="user_data.json")
blob.upload_from_string("Hello, World!")
```

## Real-World Use Cases

### Use Case 1: Multi-Environment Deployment

Deploy the same application code to different environments with different configurations.

```yaml
# config/production.yaml
google_auth:
  default:
    type: "service_account"
    service_account_file: "/secrets/prod-sa-key.json"

google_cloud_storage:
  default:
    bucket_name: "prod-us-west1-app-data"
    blob_name_prefix: "v2/production"

# config/staging.yaml
google_auth:
  default:
    type: "service_account"
    service_account_file: "/secrets/staging-sa-key.json"

google_cloud_storage:
  default:
    bucket_name: "staging-app-data"
    blob_name_prefix: "v2/staging"

# config/development.yaml
google_auth:
  default:
    type: "user_account"
    authorized_user_file: "~/.config/gcloud/application_default_credentials.json"

google_cloud_storage:
  default:
    bucket_name: "dev-local-data"
    blob_name_prefix: "v2/dev"
```

```python
# Application code (same for all environments)
from kiarina.lib.google.cloud_storage import get_blob

def save_user_profile(user_id: str, profile: dict):
    """Save user profile - works in any environment"""
    blob = get_blob(blob_name=f"users/{user_id}/profile.json")
    blob.upload_from_string(json.dumps(profile))

def load_user_profile(user_id: str) -> dict:
    """Load user profile - works in any environment"""
    blob = get_blob(blob_name=f"users/{user_id}/profile.json")
    return json.loads(blob.download_as_text())
```

**Result:**
- Production: `gs://prod-us-west1-app-data/v2/production/users/{user_id}/profile.json`
- Staging: `gs://staging-app-data/v2/staging/users/{user_id}/profile.json`
- Development: `gs://dev-local-data/v2/dev/users/{user_id}/profile.json`

### Use Case 2: Multi-Tenant Application

Support multiple tenants with isolated storage, without changing application code.

```python
from kiarina.lib.google.cloud_storage import settings_manager, get_blob

# Configure tenant-specific storage and authentication
from kiarina.lib.google.auth import settings_manager as auth_settings_manager

# Authentication configuration (separate from storage)
auth_settings_manager.user_config = {
    "tenant_acme": {
        "type": "service_account",
        "service_account_file": "/secrets/acme-sa-key.json"
    },
    "tenant_globex": {
        "type": "service_account",
        "service_account_file": "/secrets/globex-sa-key.json"
    }
}

# Storage configuration (separate from authentication)
settings_manager.user_config = {
    "tenant_acme": {
        "bucket_name": "acme-corp-data",
        "blob_name_prefix": "app-data"
    },
    "tenant_globex": {
        "bucket_name": "globex-data",
        "blob_name_prefix": "app-data"
    }
}

# Application code - tenant-agnostic
def save_document(tenant_id: str, doc_id: str, content: bytes):
    """Save document for any tenant"""
    config_key = f"tenant_{tenant_id}"
    blob = get_blob(
        blob_name=f"documents/{doc_id}.pdf",
        config_key=config_key,
        auth_config_key=config_key
    )
    blob.upload_from_string(content)

def list_documents(tenant_id: str) -> list[str]:
    """List documents for any tenant"""
    from kiarina.lib.google.cloud_storage import get_bucket

    config_key = f"tenant_{tenant_id}"
    bucket = get_bucket(config_key=config_key, auth_config_key=config_key)

    # Get prefix from settings
    settings = settings_manager.get_settings(config_key)
    prefix = f"{settings.blob_name_prefix}/documents/" if settings.blob_name_prefix else "documents/"

    blobs = bucket.list_blobs(prefix=prefix)
    return [blob.name for blob in blobs]
```

**Result:**
- Tenant ACME: `gs://acme-corp-data/app-data/documents/{doc_id}.pdf`
- Tenant Globex: `gs://globex-data/app-data/documents/{doc_id}.pdf`

### Use Case 3: Testing

Write tests without touching real Google Cloud Storage.

```python
# tests/conftest.py
import pytest
from kiarina.lib.google.cloud_storage import settings_manager

@pytest.fixture
def mock_storage_config():
    """Configure test storage"""
    settings_manager.user_config = {
        "test": {
            "bucket_name": "test-bucket",
            "blob_name_prefix": f"test-run-{datetime.now().isoformat()}"
        }
    }
    yield
    # Cleanup test data if needed

# tests/test_user_service.py
def test_save_user_profile(mock_storage_config):
    """Test user profile saving"""
    from myapp.services import save_user_profile

    # Application code uses test configuration automatically
    save_user_profile("user123", {"name": "Alice"})

    # Verify using the same configuration
    from kiarina.lib.google.cloud_storage import get_blob
    blob = get_blob(blob_name="users/user123/profile.json")
    assert blob.exists()
```

### Use Case 4: Debugging and Troubleshooting

Understand where your data is actually stored.

```python
from kiarina.lib.google.cloud_storage import settings_manager

def debug_storage_config(config_key: str | None = None):
    """Show actual storage paths for debugging"""
    settings = settings_manager.get_settings(config_key)

    print(f"Configuration: {config_key or 'default'}")
    print(f"  Bucket: {settings.bucket_name}")
    print(f"  Prefix: {settings.blob_name_prefix or '(none)'}")
    print(f"  Auth: {settings.google_auth_config_key}")

    # Example paths
    example_blob = "users/123/profile.json"
    if settings.blob_name_prefix:
        full_path = f"{settings.blob_name_prefix}/{example_blob}"
    else:
        full_path = example_blob

    print(f"  Example: gs://{settings.bucket_name}/{full_path}")

# Usage
debug_storage_config("production")
# Output:
# Configuration: production
#   Bucket: prod-us-west1-app-data
#   Prefix: v2/production
#   Auth: production
#   Example: gs://prod-us-west1-app-data/v2/production/users/123/profile.json
```

## Configuration

This library uses [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) for flexible configuration management.

### GoogleCloudStorageSettings

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `bucket_name` | `str \| None` | Yes* | Google Cloud Storage bucket name |
| `blob_name_pattern` | `str \| None` | No | Blob name pattern with placeholders (e.g., "users/{user_id}/files/{basename}") |

*Required when using `get_bucket()` or `get_blob()`

**Note:** Authentication is configured separately through `auth_config_key` parameters in the API functions, which reference configurations in [kiarina-lib-google-auth](../kiarina-lib-google-auth/).

### Configuration Methods

#### 1. Programmatic Configuration

```python
from kiarina.lib.google.cloud_storage import settings_manager

settings_manager.user_config = {
    "default": {
        "bucket_name": "my-bucket",
        "blob_name_prefix": "app-data"
    }
}
```

#### 2. Environment Variables

All settings can be configured via environment variables with the `KIARINA_LIB_GOOGLE_CLOUD_STORAGE_` prefix:

```bash
export KIARINA_LIB_GOOGLE_CLOUD_STORAGE_BUCKET_NAME="my-bucket"
export KIARINA_LIB_GOOGLE_CLOUD_STORAGE_BLOB_NAME_PREFIX="app-data"
```

**Note:** Authentication is configured separately via `KIARINA_LIB_GOOGLE_AUTH_*` environment variables. See [kiarina-lib-google-auth](../kiarina-lib-google-auth/) for details.

#### 3. Configuration Files (with YAML)

```python
import yaml
from kiarina.lib.google.cloud_storage import settings_manager

# Load from YAML file
with open("config.yaml") as f:
    config = yaml.safe_load(f)

settings_manager.user_config = config["google_cloud_storage"]
```

### Integration with kiarina-lib-google-auth

This library integrates seamlessly with [kiarina-lib-google-auth](../kiarina-lib-google-auth/) for authentication.

**Key Design:** Authentication and storage configurations are **completely separate**, allowing flexible combinations.

```python
from kiarina.lib.google.auth import settings_manager as auth_settings_manager
from kiarina.lib.google.cloud_storage import settings_manager as storage_settings_manager

# Configure authentication (separate)
auth_settings_manager.user_config = {
    "default": {
        "type": "service_account",
        "service_account_file": "~/service-account-key.json"
    },
    "user_auth": {
        "type": "user_account",
        "authorized_user_file": "~/.config/gcloud/application_default_credentials.json"
    }
}

# Configure storage (separate)
storage_settings_manager.user_config = {
    "default": {
        "bucket_name": "my-bucket"
    },
    "backup": {
        "bucket_name": "my-backup-bucket"
    }
}

# Use with default authentication
from kiarina.lib.google.cloud_storage import get_bucket
bucket = get_bucket()  # Uses default auth + default storage

# Mix and match configurations
bucket = get_bucket(config_key="backup", auth_config_key="user_auth")
# Uses user_auth authentication + backup storage configuration
```

**Benefits of Separation:**
- **Flexibility**: Use same auth with multiple buckets, or multiple auths with same bucket
- **Clarity**: Clear distinction between "who" (auth) and "where" (storage)
- **Reusability**: Share authentication across different storage configurations

## API Reference

### get_storage_client()

Get a Google Cloud Storage client with credentials from kiarina-lib-google-auth.

```python
def get_storage_client(
    auth_config_key: str | None = None,
    **kwargs: Any
) -> storage.Client
```

**Parameters:**
- `auth_config_key`: Configuration key for kiarina-lib-google-auth (default: None uses active key)
- `**kwargs`: Additional arguments passed to `storage.Client()`

**Returns:**
- `storage.Client`: Authenticated Google Cloud Storage client

**Example:**
```python
client = get_storage_client()
client = get_storage_client(auth_config_key="production")
client = get_storage_client(project="my-project")  # Override project
```

### get_bucket()

Get a Google Cloud Storage bucket.

```python
def get_bucket(
    config_key: str | None = None,
    *,
    auth_config_key: str | None = None,
    **kwargs: Any
) -> storage.Bucket
```

**Parameters:**
- `config_key`: Configuration key for storage settings (default: None uses active key)
- `auth_config_key`: Configuration key for authentication (default: None uses active key)
- `**kwargs`: Additional arguments passed to `get_storage_client()`

**Returns:**
- `storage.Bucket`: Google Cloud Storage bucket

**Raises:**
- `ValueError`: If `bucket_name` is not set in settings

**Example:**
```python
bucket = get_bucket()
bucket = get_bucket(config_key="production")
bucket = get_bucket(config_key="production", auth_config_key="prod_auth")

# Use native google-cloud-storage API
for blob in bucket.list_blobs(prefix="users/"):
    print(blob.name)
```

### get_blob()

Get a Google Cloud Storage blob.

```python
def get_blob(
    blob_name: str | None = None,
    *,
    placeholders: dict[str, Any] | None = None,
    config_key: str | None = None,
    auth_config_key: str | None = None,
    **kwargs: Any
) -> storage.Blob
```

**Parameters:**
- `blob_name`: Full blob name (path). If provided, this takes precedence.
- `placeholders`: Placeholders for blob_name_pattern formatting.
- `config_key`: Configuration key for storage settings (default: None uses active key)
- `auth_config_key`: Configuration key for authentication (default: None uses active key)
- `**kwargs`: Additional arguments passed to `get_bucket()`

**Returns:**
- `storage.Blob`: Google Cloud Storage blob

**Raises:**
- `ValueError`: If blob_name cannot be determined or pattern formatting fails

**Priority:**
1. Explicit `blob_name` parameter (full path)
2. `blob_name_pattern` with `placeholders`
3. `blob_name_pattern` without placeholders (fixed name)

**Example:**
```python
# Direct blob name (full path)
blob = get_blob(blob_name="production/v1/data.json")

# Using pattern with placeholders
# If blob_name_pattern="users/{user_id}/files/{basename}"
blob = get_blob(placeholders={"user_id": "123", "basename": "profile.json"})
# Actual: gs://bucket/users/123/files/profile.json

# Using fixed pattern from settings
# If blob_name_pattern="data/fixed.json"
blob = get_blob()
# Actual: gs://bucket/data/fixed.json

# Complex pattern
# If blob_name_pattern="my-service/{tenant_id}/users/{user_id}/files/{basename}"
blob = get_blob(placeholders={
    "tenant_id": "tenant123",
    "user_id": "user123",
    "agent_id": "agent456",
    "basename": "document.pdf"
})
# Actual: gs://bucket/my-service/tenant123/users/user123/files/document.pdf

# With custom configurations
blob = get_blob(
    placeholders={"basename": "data.json"},
    config_key="production",
    auth_config_key="prod_auth"
)

# Use native google-cloud-storage API
blob.upload_from_string("content")
content = blob.download_as_text()
blob.delete()
```

### settings_manager

Global settings manager instance for Google Cloud Storage configuration.

```python
settings_manager: SettingsManager[GoogleCloudStorageSettings]
```

**Properties:**
- `settings`: Get the current active settings
- `user_config`: Get/set user configuration
- `active_key`: Get/set active configuration key

**Methods:**
- `get_settings(key: str)`: Get settings by specific key
- `clear()`: Clear cached settings

## Common Operations

### Upload and Download

```python
from kiarina.lib.google.cloud_storage import get_blob

# Upload from string
blob = get_blob(blob_name="data.json")
blob.upload_from_string(json.dumps({"key": "value"}))

# Upload from file
blob = get_blob(blob_name="document.pdf")
blob.upload_from_filename("/path/to/document.pdf")

# Download as string
blob = get_blob(blob_name="data.json")
content = blob.download_as_text()
data = json.loads(content)

# Download to file
blob = get_blob(blob_name="document.pdf")
blob.download_to_filename("/path/to/downloaded.pdf")
```

### List Blobs

```python
from kiarina.lib.google.cloud_storage import get_bucket, settings_manager

bucket = get_bucket()

# Get prefix from settings
settings = settings_manager.settings
prefix = f"{settings.blob_name_prefix}/users/" if settings.blob_name_prefix else "users/"

# List blobs
for blob in bucket.list_blobs(prefix=prefix):
    print(f"{blob.name}: {blob.size} bytes")
```

### Check Existence

```python
from kiarina.lib.google.cloud_storage import get_blob

blob = get_blob(blob_name="data.json")
if blob.exists():
    print("Blob exists")
    print(f"Size: {blob.size} bytes")
    print(f"Updated: {blob.updated}")
else:
    print("Blob does not exist")
```

### Delete Blob

```python
from kiarina.lib.google.cloud_storage import get_blob

blob = get_blob(blob_name="old_data.json")
if blob.exists():
    blob.delete()
    print("Blob deleted")
```

### Copy Blob

```python
from kiarina.lib.google.cloud_storage import get_bucket

bucket = get_bucket()
source_blob = bucket.blob("source.json")
destination_blob = bucket.blob("backup/source.json")

bucket.copy_blob(source_blob, bucket, destination_blob.name)
print("Blob copied")
```

## Error Handling

```python
from google.cloud import storage
from google.api_core import exceptions
from kiarina.lib.google.cloud_storage import get_blob

try:
    blob = get_blob(blob_name="data.json")
    content = blob.download_as_text()
except exceptions.NotFound:
    print("Blob not found")
except exceptions.Forbidden:
    print("Permission denied")
except exceptions.GoogleAPIError as e:
    print(f"Google API error: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Best Practices

### 1. Configure Once, Use Everywhere

```python
# app/config.py
from kiarina.lib.google.cloud_storage import settings_manager
import yaml

def init_storage_config():
    """Initialize storage configuration at app startup"""
    with open("config/storage.yaml") as f:
        config = yaml.safe_load(f)
    settings_manager.user_config = config

# app/main.py
from app.config import init_storage_config

def main():
    init_storage_config()
    # Now all modules can use get_blob() without configuration
```

### 2. Use Logical Names

```python
# ✅ Good - logical, environment-agnostic names
blob = get_blob(blob_name="users/123/profile.json")
blob = get_blob(blob_name="reports/2024/january.pdf")

# ❌ Bad - environment-specific details in code
blob = get_blob(blob_name="prod-v2-users-123-profile.json")
```

### 3. Organize with Prefixes

```python
# Configure hierarchical structure
settings_manager.user_config = {
    "default": {
        "bucket_name": "my-app-data",
        "blob_name_prefix": "production/v2"  # Version and environment
    }
}

# Application uses clean paths
blob = get_blob(blob_name="users/123/profile.json")
# Actual: gs://my-app-data/production/v2/users/123/profile.json
```

### 4. Validate Configuration

```python
def validate_storage_config(config_key: str | None = None) -> bool:
    """Validate storage configuration at startup"""
    try:
        from kiarina.lib.google.cloud_storage import get_bucket
        bucket = get_bucket(config_key)
        bucket.exists()
        print(f"✓ Storage configuration valid: {bucket.name}")
        return True
    except Exception as e:
        print(f"✗ Storage configuration invalid: {e}")
        return False

# At app startup
if not validate_storage_config():
    raise RuntimeError("Invalid storage configuration")
```

## Development

### Prerequisites

- Python 3.12+

### Setup

```bash
# Clone the repository
git clone https://github.com/kiarina/kiarina-python.git
cd kiarina-python

# Setup development environment
mise run setup
```

### Running Tests

```bash
# Run format, lint, type checks and tests
mise run package kiarina-lib-google-cloud-storage

# Coverage report
mise run package:test kiarina-lib-google-cloud-storage --coverage
```

## Dependencies

- [google-cloud-storage](https://github.com/googleapis/python-storage) - Google Cloud Storage client library
- [kiarina-lib-google-auth](../kiarina-lib-google-auth/) - Google Cloud authentication library
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Settings management
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) - Advanced settings management

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Contributing

This is a personal project, but contributions are welcome! Please feel free to submit issues or pull requests.

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python) - The main monorepo containing this package
- [kiarina-lib-google-auth](../kiarina-lib-google-auth/) - Google Cloud authentication library
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) - Configuration management library used by this package
