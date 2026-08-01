from __future__ import annotations

import json

import pytest
from app.config import Settings
from app.schemas import CreateRunRequest
from app.service import ConfigurationError, ProvenanceService, openai_size_for


def sample_request(**overrides: object) -> CreateRunRequest:
    values: dict[str, object] = {
        "title": "Morning ritual",
        "brief": "A tactile ceramic studio campaign in quiet morning light",
        "output_format": "square",
        "palette": "clay",
        "provider": "local",
    }
    values.update(overrides)
    return CreateRunRequest(**values)


def test_local_run_creates_verified_genblaze_manifest_and_content_addressed_asset(
    settings: Settings,
) -> None:
    service = ProvenanceService(settings)

    record = service.create_run(sample_request())
    verification = service.verify_run(record.id)
    manifest = service.manifest_json(record.id)
    payload, media_type = service.asset_bytes(record.id)

    assert record.manifest_verified is True
    assert record.bytes_verified is True
    assert verification.manifest_verified is True
    assert verification.bytes_verified is True
    assert record.asset_sha256 in record.storage_key
    assert media_type == "image/svg+xml"
    assert payload.startswith(b"<svg")
    assert manifest["canonical_hash"] == record.manifest_hash
    assert manifest["run"]["steps"][0]["provider"] == "provenance-vault-local"


def test_byte_verification_detects_tampering(settings: Settings) -> None:
    service = ProvenanceService(settings)
    record = service.create_run(sample_request())
    asset_path = settings.data_dir / record.storage_key
    asset_path.write_bytes(asset_path.read_bytes() + b"tampered")

    verification = service.verify_run(record.id)

    assert verification.manifest_verified is True
    assert verification.bytes_verified is False
    assert verification.actual_sha256 != verification.expected_sha256


def test_live_provider_requires_b2_storage(settings: Settings) -> None:
    service = ProvenanceService(settings)

    with pytest.raises(ConfigurationError, match="B2 storage"):
        service.create_run(sample_request(provider="gmicloud"))


def test_public_capabilities_do_not_expose_secrets(settings: Settings) -> None:
    secret_settings = Settings(
        **{
            **settings.__dict__,
            "b2_key_id": "secret-id",
            "b2_app_key": "secret-app-key",
            "b2_bucket": "demo-bucket",
            "gmi_api_key": "secret-gmi",
            "openai_api_key": "secret-openai",
        }
    )

    serialized = json.dumps(secret_settings.public_capabilities())

    assert "secret-id" not in serialized
    assert "secret-app-key" not in serialized
    assert "secret-gmi" not in serialized
    assert "secret-openai" not in serialized
    assert "demo-bucket" in serialized


@pytest.mark.parametrize(
    ("model", "output_format", "expected"),
    [
        ("gpt-image-2", "landscape", "1344x896"),
        ("gpt-image-1", "portrait", "1024x1536"),
        ("dall-e-3", "landscape", "1792x1024"),
        ("dall-e-2", "portrait", "1024x1024"),
    ],
)
def test_openai_size_mapping_matches_model_contract(
    model: str, output_format: str, expected: str
) -> None:
    assert openai_size_for(model, output_format) == expected
