from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from genblaze_core.exceptions import StorageError
from genblaze_core.storage.errors import StorageErrorCode
from genblaze_core.storage.types import ListPage

from .config import Settings
from .schemas import RunRecord


class RepositoryBackend(Protocol):
    def put(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str | None = None,
    ) -> str: ...

    def get(self, key: str) -> bytes: ...

    def key_from_url(self, url: str) -> str | None: ...

    def list(
        self,
        prefix: str = "",
        *,
        max_keys: int = 1000,
        continuation_token: str | None = None,
    ) -> ListPage: ...

    def close(self) -> None: ...


BackendFactory = Callable[[], RepositoryBackend]


class RunRepositoryProtocol(Protocol):
    assets_dir: Path

    def save(self, record: RunRecord, manifest_json: str) -> None: ...

    def get(self, run_id: str) -> RunRecord | None: ...

    def list(self) -> list[RunRecord]: ...

    def manifest(self, run_id: str) -> dict[str, object] | None: ...


class RunRepository:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.records_dir = data_dir / "records"
        self.manifests_dir = data_dir / "manifests"
        self.assets_dir = data_dir / "objects" / "assets"

    def save(self, record: RunRecord, manifest_json: str) -> None:
        self._atomic_write(
            self.records_dir / f"{record.id}.json",
            record.model_dump_json(indent=2),
        )
        self._atomic_write(self.manifests_dir / f"{record.id}.json", manifest_json)

    def get(self, run_id: str) -> RunRecord | None:
        path = self.records_dir / f"{run_id}.json"
        if not path.exists():
            return None
        return RunRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def list(self) -> list[RunRecord]:
        records = [
            RunRecord.model_validate_json(path.read_text(encoding="utf-8"))
            for path in self.records_dir.glob("*.json")
        ]
        return sorted(records, key=lambda item: item.created_at, reverse=True)

    def manifest(self, run_id: str) -> dict[str, object] | None:
        path = self.manifests_dir / f"{run_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _atomic_write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(f"{path.suffix}.tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(path)


class B2RunRepository:
    """Persist the searchable run index in the configured B2 bucket.

    The record object is the commit marker for a pair. Saving the canonical
    manifest first means a failed record write can leave an unreferenced
    manifest, but never a listed record whose manifest was not written.
    """

    prefix = "provenance-vault/app-index/v1"

    def __init__(self, backend_factory: BackendFactory, staging_dir: Path) -> None:
        self.backend_factory = backend_factory
        self.assets_dir = staging_dir / "objects" / "assets"
        self.records_prefix = f"{self.prefix}/records/"
        self.manifests_prefix = f"{self.prefix}/manifests/"

    def save(self, record: RunRecord, manifest_json: str) -> None:
        backend = self.backend_factory()
        try:
            backend.put(
                self._manifest_key(record.id),
                manifest_json.encode("utf-8"),
                content_type="application/json",
            )
            backend.put(
                self._record_key(record.id),
                record.model_dump_json(indent=2).encode("utf-8"),
                content_type="application/json",
            )
        finally:
            backend.close()

    def get(self, run_id: str) -> RunRecord | None:
        backend = self.backend_factory()
        try:
            payload = self._get_optional(backend, self._record_key(run_id))
        finally:
            backend.close()
        if payload is None:
            return None
        return RunRecord.model_validate_json(payload)

    def list(self) -> list[RunRecord]:
        backend = self.backend_factory()
        records: list[RunRecord] = []
        continuation_token: str | None = None
        try:
            while True:
                page = backend.list(
                    prefix=self.records_prefix,
                    continuation_token=continuation_token,
                )
                for entry in page.entries:
                    if not entry.key.endswith(".json"):
                        continue
                    payload = self._get_optional(backend, entry.key)
                    if payload is not None:
                        records.append(RunRecord.model_validate_json(payload))
                continuation_token = page.next_token
                if continuation_token is None:
                    break
        finally:
            backend.close()
        return sorted(records, key=lambda item: item.created_at, reverse=True)

    def manifest(self, run_id: str) -> dict[str, object] | None:
        backend = self.backend_factory()
        try:
            payload = self._get_optional(backend, self._manifest_key(run_id))
        finally:
            backend.close()
        if payload is None:
            return None
        manifest = json.loads(payload)
        if not isinstance(manifest, dict):
            raise ValueError(f"Manifest {run_id!r} is not a JSON object")
        return manifest

    def _record_key(self, run_id: str) -> str:
        return f"{self.records_prefix}{run_id}.json"

    def _manifest_key(self, run_id: str) -> str:
        return f"{self.manifests_prefix}{run_id}.json"

    @staticmethod
    def _get_optional(backend: RepositoryBackend, key: str) -> bytes | None:
        try:
            return backend.get(key)
        except StorageError as exc:
            if exc.error_code is StorageErrorCode.NOT_FOUND or exc.status_code == 404:
                return None
            raise


def create_run_repository(
    settings: Settings,
    backend_factory: BackendFactory | None = None,
) -> RunRepositoryProtocol:
    if settings.storage_mode == "b2" and settings.b2_ready:
        if backend_factory is None:
            raise ValueError("A B2 backend factory is required for B2 repository mode")
        return B2RunRepository(backend_factory, settings.data_dir)
    return RunRepository(settings.data_dir)
