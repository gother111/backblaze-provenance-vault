from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from genblaze_core import KeyStrategy, Modality, ObjectStorageSink, Pipeline, parse_manifest
from genblaze_s3 import S3StorageBackend

from .config import Settings
from .local_provider import LocalPosterProvider
from .repository import RunRepository
from .schemas import (
    CreateRunRequest,
    ProvenanceStep,
    ProviderName,
    RunRecord,
    VerificationResult,
)

GMI_ASPECT_RATIOS = {
    "square": "1:1",
    "portrait": "4:5",
    "landscape": "3:2",
}


def openai_size_for(model: str, output_format: str) -> str:
    """Return a size accepted by the selected Genblaze OpenAI model family."""
    if model == "gpt-image-2":
        return {
            "square": "1024x1024",
            "portrait": "1024x1280",
            "landscape": "1344x896",
        }[output_format]
    if model == "dall-e-3":
        return {
            "square": "1024x1024",
            "portrait": "1024x1792",
            "landscape": "1792x1024",
        }[output_format]
    if model == "dall-e-2":
        return "1024x1024"
    return {
        "square": "1024x1024",
        "portrait": "1024x1536",
        "landscape": "1536x1024",
    }[output_format]


class ConfigurationError(RuntimeError):
    pass


class ProvenanceService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.repository = RunRepository(settings.data_dir)

    def ensure_demo_run(self) -> RunRecord:
        existing = self.repository.list()
        if existing:
            return existing[0]
        request = CreateRunRequest(
            title="Morning ritual",
            brief=(
                "A quiet morning ritual for a ceramic studio, soft window light, "
                "tactile clay textures"
            ),
            output_format="square",
            palette="clay",
            provider="local",
        )
        return self.create_run(request, is_demo=True)

    def create_run(self, request: CreateRunRequest, *, is_demo: bool = False) -> RunRecord:
        provider, model, params = self._provider_for(request)
        sink = self._sink_for(request.provider)
        result = (
            Pipeline("provenance-vault", project_id="creator-proof")
            .step(
                provider,
                model=model,
                prompt=request.brief,
                modality=Modality.IMAGE,
                title=request.title,
                output_format=request.output_format.value,
                palette=request.palette.value,
                **params,
            )
            .run(sink=sink, timeout=360, raise_on_failure=True)
        )
        if not result.run.steps or not result.run.steps[-1].assets:
            error = result.run.steps[-1].error if result.run.steps else "No pipeline step returned"
            raise RuntimeError(f"Generation failed: {error}")

        asset = result.run.steps[-1].assets[0]
        if not asset.sha256:
            raise RuntimeError("Genblaze returned an output without a SHA-256 digest")
        manifest = result.manifest
        manifest_json = manifest.to_canonical_json()
        manifest_verified = manifest.verify()

        if self.settings.storage_mode == "b2":
            storage_key = self._b2_key_for(asset.url)
            bytes_verified, _ = self._verify_b2_bytes(storage_key, asset.sha256)
            manifest_uri = manifest.manifest_uri or "b2://manifest-uri-unavailable"
        else:
            storage_key = self._local_key_for(asset.url)
            actual = self._sha256_file(self.settings.data_dir / storage_key)
            bytes_verified = actual == asset.sha256
            manifest_uri = f"local://manifests/{result.run.run_id}.json"

        created_at = result.run.created_at
        record = RunRecord(
            id=result.run.run_id,
            title=request.title,
            brief=request.brief,
            output_format=request.output_format,
            palette=request.palette,
            provider=result.run.steps[-1].provider,
            model=result.run.steps[-1].model,
            created_at=created_at,
            storage_mode=self.settings.storage_mode,
            storage_key=storage_key,
            manifest_uri=manifest_uri,
            asset_url=f"/api/runs/{result.run.run_id}/asset",
            asset_sha256=asset.sha256,
            manifest_hash=manifest.canonical_hash,
            manifest_verified=manifest_verified,
            bytes_verified=bytes_verified,
            media_type=asset.media_type,
            size_bytes=asset.size_bytes or 0,
            provenance_steps=[
                ProvenanceStep(
                    index=index + 1,
                    provider=step.provider,
                    model=step.model,
                    status=getattr(step.status, "value", str(step.status)),
                )
                for index, step in enumerate(result.run.steps)
            ],
            is_demo=is_demo,
        )
        self.repository.save(record, manifest_json)
        return record

    def verify_run(self, run_id: str) -> VerificationResult:
        record = self.repository.get(run_id)
        if record is None:
            raise KeyError(run_id)
        manifest_data = self.repository.manifest(run_id)
        if manifest_data is None:
            raise KeyError(run_id)
        manifest = parse_manifest(dict(manifest_data))
        if record.storage_mode == "b2":
            bytes_verified, actual = self._verify_b2_bytes(
                record.storage_key, record.asset_sha256
            )
        else:
            path = self.settings.data_dir / record.storage_key
            actual = self._sha256_file(path) if path.exists() else None
            bytes_verified = actual == record.asset_sha256
        return VerificationResult(
            run_id=run_id,
            manifest_verified=manifest.verify(),
            bytes_verified=bytes_verified,
            expected_sha256=record.asset_sha256,
            actual_sha256=actual,
            checked_at=datetime.now(UTC),
        )

    def asset_bytes(self, run_id: str) -> tuple[bytes, str]:
        record = self.repository.get(run_id)
        if record is None:
            raise KeyError(run_id)
        if record.storage_mode == "b2":
            backend = self._b2_backend()
            try:
                payload = backend.get(record.storage_key)
            finally:
                backend.close()
            return payload, record.media_type
        path = self.settings.data_dir / record.storage_key
        if not path.exists():
            raise FileNotFoundError(path)
        return path.read_bytes(), record.media_type

    def _provider_for(self, request: CreateRunRequest) -> tuple[Any, str, dict[str, Any]]:
        if request.provider is ProviderName.LOCAL:
            return (
                LocalPosterProvider(self.repository.assets_dir),
                "procedural-editorial-v1",
                {},
            )
        if self.settings.storage_mode != "b2" or not self.settings.b2_ready:
            raise ConfigurationError(
                "Live AI generation is enabled only with configured B2 storage so every "
                "output is downloaded, hashed, and sealed durably."
            )
        if request.provider is ProviderName.GMICLOUD:
            if not self.settings.gmi_ready:
                raise ConfigurationError("GMI_API_KEY is not configured")
            from genblaze_gmicloud import GMICloudImageProvider

            return (
                GMICloudImageProvider(api_key=self.settings.gmi_api_key),
                self.settings.gmi_image_model,
                {"aspect_ratio": GMI_ASPECT_RATIOS[request.output_format.value]},
            )
        if not self.settings.openai_ready:
            raise ConfigurationError("OPENAI_API_KEY is not configured")
        from genblaze_openai import DalleProvider

        return (
            DalleProvider(api_key=self.settings.openai_api_key),
            self.settings.openai_image_model,
            {
                "size": openai_size_for(
                    self.settings.openai_image_model, request.output_format.value
                )
            },
        )

    def _sink_for(self, provider: ProviderName) -> ObjectStorageSink | None:
        if self.settings.storage_mode == "local":
            if provider is not ProviderName.LOCAL:
                raise ConfigurationError("Live providers require PROVENANCE_STORAGE_MODE=b2")
            return None
        if self.settings.storage_mode != "b2":
            raise ConfigurationError("PROVENANCE_STORAGE_MODE must be either local or b2")
        if not self.settings.b2_ready:
            raise ConfigurationError(
                "B2 storage mode requires B2_KEY_ID, B2_APP_KEY, B2_BUCKET, and B2_REGION"
            )
        return ObjectStorageSink(
            self._b2_backend(),
            prefix="provenance-vault",
            key_strategy=KeyStrategy.CONTENT_ADDRESSABLE,
            strict_manifest_reads=True,
        )

    def _b2_backend(self) -> S3StorageBackend:
        kwargs: dict[str, Any] = {
            "region": self.settings.b2_region,
            "key_id": self.settings.b2_key_id,
            "app_key": self.settings.b2_app_key,
            "auto_lifecycle": False,
        }
        if self.settings.b2_public_url_base:
            kwargs["public_url_base"] = self.settings.b2_public_url_base
        return S3StorageBackend.for_backblaze(self.settings.b2_bucket, **kwargs)

    def _b2_key_for(self, url: str) -> str:
        backend = self._b2_backend()
        try:
            key = backend.key_from_url(url)
        finally:
            backend.close()
        if key is None:
            raise RuntimeError(
                "Genblaze returned an asset URL that does not belong to this B2 bucket"
            )
        return key

    def _verify_b2_bytes(self, key: str, expected: str) -> tuple[bool, str | None]:
        backend = self._b2_backend()
        try:
            payload = backend.get(key)
        finally:
            backend.close()
        actual = hashlib.sha256(payload).hexdigest()
        return actual == expected, actual

    def _local_key_for(self, url: str) -> str:
        if not url.startswith("file://"):
            raise RuntimeError("Offline provider returned a non-local asset URL")
        parsed = urlparse(url)
        path = Path(unquote(parsed.path)).resolve()
        try:
            return path.relative_to(self.settings.data_dir).as_posix()
        except ValueError as exc:
            raise RuntimeError("Offline asset escaped the configured data directory") from exc

    @staticmethod
    def _sha256_file(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def health(self) -> dict[str, object]:
        try:
            from genblaze_core import __version__ as genblaze_core_version
        except ImportError:
            genblaze_core_version = "unavailable"
        return {
            "status": "ok",
            "service": "provenance-vault",
            "genblaze_core": genblaze_core_version,
            "capabilities": self.settings.public_capabilities(),
            "runs": len(self.repository.list()),
        }

    def manifest_json(self, run_id: str) -> dict[str, object]:
        manifest = self.repository.manifest(run_id)
        if manifest is None:
            raise KeyError(run_id)
        return manifest
