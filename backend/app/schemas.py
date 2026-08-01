from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class ProviderName(StrEnum):
    LOCAL = "local"
    GMICLOUD = "gmicloud"
    OPENAI = "openai"


class OutputFormat(StrEnum):
    SQUARE = "square"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class Palette(StrEnum):
    CLAY = "clay"
    MOSS = "moss"
    NIGHT = "night"


class CreateRunRequest(BaseModel):
    title: str = Field(default="Untitled campaign", min_length=1, max_length=80)
    brief: str = Field(min_length=12, max_length=1200)
    output_format: OutputFormat = OutputFormat.SQUARE
    palette: Palette = Palette.CLAY
    provider: ProviderName = ProviderName.LOCAL

    @field_validator("title", "brief")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return " ".join(value.split())


class ProvenanceStep(BaseModel):
    index: int
    provider: str
    model: str
    status: str


class RunRecord(BaseModel):
    id: str
    title: str
    brief: str
    output_format: OutputFormat
    palette: Palette
    provider: str
    model: str
    created_at: datetime
    storage_mode: str
    storage_key: str
    manifest_uri: str
    asset_url: str
    asset_sha256: str
    manifest_hash: str
    manifest_verified: bool
    bytes_verified: bool
    media_type: str
    size_bytes: int
    provenance_steps: list[ProvenanceStep]
    is_demo: bool = False


class VerificationResult(BaseModel):
    run_id: str
    manifest_verified: bool
    bytes_verified: bool
    expected_sha256: str
    actual_sha256: str | None
    checked_at: datetime
