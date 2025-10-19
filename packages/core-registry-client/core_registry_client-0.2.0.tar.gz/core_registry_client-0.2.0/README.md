# Core Registry Client

Python client SDK for interacting with the Schema Registry Service.

## Installation

```bash
pip install core-registry-client
```

## Quick Start

```python
from core_registry_client import RegistryClient

# Initialize client
client = RegistryClient(base_url="http://localhost:8000")

# Get schema index
index = await client.get_index()

# Fetch specific schema
schema = await client.fetch_schema("v1", "telemetry.FeedbackEvent")

# Negotiate best version
result = await client.negotiate(
    name="telemetry.FeedbackEvent",
    prefer="v2",
    fallback="v1",
)

# Check compatibility
compat = await client.check_compatibility(
    name="telemetry.FeedbackEvent",
    from_track="v1",
    from_version="v1.2.0",
    to_track="v2",
    to_version="v2.0.0",
)
```

## API Reference

### RegistryClient

Main client class for interacting with the registry.

#### Methods

- `get_index()` - Get complete registry index
- `fetch_schema(track, name, version=None)` - Fetch schema by track and name
- `fetch_schema_by_id(schema_id)` - Fetch schema by global ID
- `list_versions(track, name)` - List all versions of a schema
- `check_compatibility(name, from_track, from_version, to_track, to_version)` - Check compatibility
- `negotiate(name, prefer, fallback, supports_tracks=None)` - Negotiate best version
- `upload_schema(...)` - Upload schema (requires admin token)
- `sync_schemas(source, ref=None, path=None)` - Trigger sync (requires admin token)

## Examples

See `examples/` directory for more usage examples.

## License

MIT License

