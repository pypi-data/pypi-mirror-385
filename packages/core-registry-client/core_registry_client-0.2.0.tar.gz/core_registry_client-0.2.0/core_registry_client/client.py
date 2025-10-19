"""Registry client implementation."""

from typing import Any

import httpx

from core_registry_client.models import (
    CompatResponse,
    NegotiationResult,
    RegistryIndex,
    SchemaResponse,
    SchemaVersion,
    Track,
)


class RegistryError(Exception):
    """Base exception for registry client errors."""

    pass


class SchemaNotFoundError(RegistryError):
    """Raised when schema is not found."""

    pass


class RegistryClient:
    """Client for interacting with Schema Registry Service."""

    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        """
        Initialize registry client.

        Args:
            base_url: Base URL of registry service
            token: Optional admin token for write operations
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={"Authorization": f"Bearer {token}"} if token else {},
        )

    async def close(self) -> None:
        """Close client connections."""
        await self._client.aclose()

    async def __aenter__(self) -> "RegistryClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def get_index(self) -> RegistryIndex:
        """
        Get complete registry index.

        Returns:
            Registry index with all tracks

        Raises:
            RegistryError: If request fails
        """
        try:
            response = await self._client.get("/index")
            response.raise_for_status()
            return RegistryIndex(**response.json())
        except httpx.HTTPError as e:
            raise RegistryError(f"Failed to get index: {e}")

    async def fetch_schema(
        self,
        track: Track,
        name: str,
        version: str | None = None,
    ) -> SchemaResponse:
        """
        Fetch schema by track and name.

        Args:
            track: Schema track (v1/v2)
            name: Schema name
            version: Optional specific version

        Returns:
            Schema with content

        Raises:
            SchemaNotFoundError: If schema not found
            RegistryError: If request fails
        """
        try:
            params = {"version": version} if version else {}
            response = await self._client.get(
                f"/schemas/{track}/{name}",
                params=params,
            )
            response.raise_for_status()
            return SchemaResponse(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise SchemaNotFoundError(f"Schema not found: {track}/{name}")
            raise RegistryError(f"Failed to fetch schema: {e}")
        except httpx.HTTPError as e:
            raise RegistryError(f"Failed to fetch schema: {e}")

    async def fetch_schema_by_id(self, schema_id: str) -> SchemaResponse:
        """
        Fetch schema by global $schema_id.

        Args:
            schema_id: Global schema identifier

        Returns:
            Schema with content

        Raises:
            SchemaNotFoundError: If schema not found
            RegistryError: If request fails
        """
        try:
            response = await self._client.get(f"/schemas/by-id/{schema_id}")
            response.raise_for_status()
            return SchemaResponse(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise SchemaNotFoundError(f"Schema not found: {schema_id}")
            raise RegistryError(f"Failed to fetch schema: {e}")
        except httpx.HTTPError as e:
            raise RegistryError(f"Failed to fetch schema: {e}")

    async def list_versions(self, track: Track, name: str) -> list[SchemaVersion]:
        """
        List all versions of a schema.

        Args:
            track: Schema track
            name: Schema name

        Returns:
            List of schema versions

        Raises:
            RegistryError: If request fails
        """
        try:
            response = await self._client.get(f"/schemas/{track}/{name}/versions")
            response.raise_for_status()
            return [SchemaVersion(**v) for v in response.json()]
        except httpx.HTTPError as e:
            raise RegistryError(f"Failed to list versions: {e}")

    async def check_compatibility(
        self,
        name: str,
        from_track: Track,
        from_version: str,
        to_track: Track,
        to_version: str,
    ) -> CompatResponse:
        """
        Check compatibility between schema versions.

        Args:
            name: Schema name
            from_track: Source track
            from_version: Source version
            to_track: Target track
            to_version: Target version

        Returns:
            Compatibility assessment

        Raises:
            RegistryError: If request fails
        """
        try:
            response = await self._client.get(
                "/compat/check",
                params={
                    "name": name,
                    "from_track": from_track,
                    "from_version": from_version,
                    "to_track": to_track,
                    "to_version": to_version,
                },
            )
            response.raise_for_status()
            return CompatResponse(**response.json())
        except httpx.HTTPError as e:
            raise RegistryError(f"Failed to check compatibility: {e}")

    async def negotiate(
        self,
        name: str,
        prefer: Track,
        fallback: Track | None = None,
        supports_tracks: list[Track] | None = None,
    ) -> NegotiationResult:
        """
        Negotiate best schema version.

        Args:
            name: Schema name
            prefer: Preferred track
            fallback: Fallback track if preferred not available
            supports_tracks: List of supported tracks (defaults to [prefer, fallback])

        Returns:
            Best available schema version

        Raises:
            SchemaNotFoundError: If no suitable schema found
            RegistryError: If request fails
        """
        if supports_tracks is None:
            supports_tracks = [prefer]
            if fallback:
                supports_tracks.append(fallback)

        # Try preferred track first
        try:
            schema = await self.fetch_schema(prefer, name)
            if not schema.deprecated:
                return NegotiationResult(
                    name=schema.name,
                    track=schema.track,
                    core_version=schema.core_version,
                    sha256=schema.sha256,
                    url=f"{self.base_url}/schemas/{schema.track}/{schema.name}",
                    deprecated=schema.deprecated,
                )
        except SchemaNotFoundError:
            pass

        # Try fallback
        if fallback:
            try:
                schema = await self.fetch_schema(fallback, name)
                return NegotiationResult(
                    name=schema.name,
                    track=schema.track,
                    core_version=schema.core_version,
                    sha256=schema.sha256,
                    url=f"{self.base_url}/schemas/{schema.track}/{schema.name}",
                    deprecated=schema.deprecated,
                )
            except SchemaNotFoundError:
                pass

        raise SchemaNotFoundError(f"No suitable schema found for: {name}")

    async def upload_schema(
        self,
        name: str,
        track: Track,
        core_version: str,
        content: dict[str, Any],
        schema_id_str: str,
        deprecated: bool = False,
        deprecation_note: str | None = None,
        x_compat: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Upload schema (requires admin token).

        Args:
            name: Schema name
            track: Schema track
            core_version: Core version
            content: JSON Schema content
            schema_id_str: Global $schema_id
            deprecated: Deprecation flag
            deprecation_note: Deprecation message
            x_compat: Compatibility metadata

        Returns:
            Upload confirmation

        Raises:
            RegistryError: If upload fails
        """
        if not self.token:
            raise RegistryError("Admin token required for upload")

        try:
            payload = {
                "name": name,
                "track": track,
                "core_version": core_version,
                "content": content,
                "schema_id_str": schema_id_str,
                "deprecated": deprecated,
                "deprecation_note": deprecation_note,
                "x_compat": x_compat or {},
            }
            response = await self._client.post("/admin/schemas", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise RegistryError(f"Failed to upload schema: {e}")

    async def sync_schemas(
        self,
        source: str,
        ref: str | None = None,
        path: str | None = None,
    ) -> dict[str, Any]:
        """
        Trigger schema sync (requires admin token).

        Args:
            source: Source type (github_release | local)
            ref: Git ref for github_release
            path: Local path for local source

        Returns:
            Sync job status

        Raises:
            RegistryError: If sync fails
        """
        if not self.token:
            raise RegistryError("Admin token required for sync")

        try:
            payload = {"source": source, "ref": ref, "path": path}
            response = await self._client.post("/admin/sync", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise RegistryError(f"Failed to sync schemas: {e}")
    
    # Phase 11.1: Enforcement & Drift Intelligence
    
    async def report_drift(
        self,
        local_sha: str,
        registry_sha: str,
        name: str,
        track: str = "v1",
        service_name: str | None = None,
    ) -> None:
        """
        Report schema drift to telemetry (via Pulse events).
        
        Phase 11.1: Drift intelligence reporting.
        
        Args:
            local_sha: SHA256 of local schema
            registry_sha: SHA256 of registry schema
            name: Schema name
            track: Schema track
            service_name: Name of the reporting service
        
        Note:
            This is a fire-and-forget operation. Failures are logged but not raised.
        """
        try:
            payload = {
                "event_type": "telemetry.schema_drift",
                "payload": {
                    "name": name,
                    "track": track,
                    "local_sha256": local_sha,
                    "registry_sha256": registry_sha,
                    "service": service_name or "unknown",
                },
            }
            # In a real implementation, this would publish to Pulse
            # For now, we just log it via the registry
            response = await self._client.post("/admin/telemetry", json=payload)
            # Don't raise on failure - drift reporting is best-effort
            if response.status_code not in (200, 201, 204):
                print(f"Warning: Drift reporting failed with status {response.status_code}")
        except Exception as e:
            # Log but don't fail the caller
            print(f"Warning: Failed to report drift: {e}")
    
    async def enforce(
        self,
        payload: dict[str, Any],
        name: str,
        track: str = "v1",
        version: str | None = None,
        mode: str = "warn",
    ) -> dict[str, Any]:
        """
        Enforce schema validation against the registry.
        
        Phase 11.1: Enforcement modes (warn | strict).
        
        Args:
            payload: JSON payload to validate
            name: Schema name
            track: Schema track
            version: Specific version (None = latest)
            mode: Enforcement mode ("warn" | "strict")
        
        Returns:
            Validation result dict with keys:
                - valid: bool
                - errors: list[str]
                - warnings: list[str]
        
        Raises:
            RegistryError: If mode="strict" and validation fails
        """
        from jsonschema import ValidationError, validate
        
        try:
            # Fetch schema from registry
            schema = await self.get_schema(name, track, version)
            
            # Validate payload
            errors = []
            warnings = []
            
            try:
                validate(instance=payload, schema=schema["content"])
                valid = True
            except ValidationError as e:
                valid = False
                errors.append(str(e.message))
                # Include path if available
                if e.path:
                    path_str = ".".join(str(p) for p in e.path)
                    errors[-1] = f"{path_str}: {errors[-1]}"
            
            result = {
                "valid": valid,
                "errors": errors,
                "warnings": warnings,
                "schema": {
                    "name": name,
                    "track": track,
                    "version": schema.get("core_version"),
                },
            }
            
            # Enforcement logic
            if not valid:
                if mode == "strict":
                    raise RegistryError(
                        f"Schema validation failed in strict mode: {'; '.join(errors)}"
                    )
                elif mode == "warn":
                    warnings.append(f"Schema validation failed (warn mode): {'; '.join(errors)}")
            
            return result
            
        except RegistryError:
            # Re-raise registry errors (including strict mode failures)
            raise
        except Exception as e:
            raise RegistryError(f"Enforcement check failed: {e}")

