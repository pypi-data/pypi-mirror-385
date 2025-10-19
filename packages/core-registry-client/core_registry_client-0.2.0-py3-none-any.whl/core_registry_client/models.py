"""Data models for registry client."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

Track = Literal["v1", "v2"]


class SchemaIndexItem(BaseModel):
    """Schema item in index."""

    name: str
    schema_id: str = Field(alias="$schema_id")
    sha256: str
    latest_core_version: str
    deprecated: bool = False


class TrackInfo(BaseModel):
    """Track information."""

    count: int
    schemas: list[SchemaIndexItem]


class RegistryIndex(BaseModel):
    """Registry index response."""

    tracks: dict[Track, TrackInfo]
    generated_at: datetime


class SchemaResponse(BaseModel):
    """Schema response."""

    name: str
    track: Track
    core_version: str
    sha256: str
    schema_id: str = Field(alias="$schema_id")
    content: dict[str, Any]
    deprecated: bool = False
    deprecation_note: str | None = None


class SchemaVersion(BaseModel):
    """Schema version info."""

    core_version: str
    sha256: str
    created_at: datetime
    deprecated: bool = False


class CompatResponse(BaseModel):
    """Compatibility check response."""

    compatible: bool
    breaking_reasons: list[str] = []
    advice: list[str] = []
    x_compat: dict[str, Any] | None = None


class NegotiationResult(BaseModel):
    """Schema negotiation result."""

    name: str
    track: Track
    core_version: str
    sha256: str
    url: str
    deprecated: bool = False

