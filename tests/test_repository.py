from __future__ import annotations

import tempfile
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from app.config import ROOT, Settings
from app.repository import B2RunRepository, RunRepository, create_run_repository
from app.schemas import RunRecord
from genblaze_core.exceptions import StorageError
from genblaze_core.storage.errors import StorageErrorCode
from genblaze_core.storage.types import FileEntry, ListPage


class FakeB2Backend:
    def __init__(self, *, page_size: int = 1000) -> None:
        self.objects: dict[str, bytes] = {}
        self.calls: list[tuple[str, str]] = []
        self.fail_put_keys: set[str] = set()
        self.page_size = page_size

    def put(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str | None = None,
    ) -> str:
        assert content_type == "application/json"
        self.calls.append(("put", key))
        if key in self.fail_put_keys:
            raise StorageError("injected put failure", operation="put")
        self.objects[key] = bytes(data)
        return key

    def get(self, key: str) -> bytes:
        self.calls.append(("get", key))
        try:
            return self.objects[key]
        except KeyError as exc:
            raise StorageError(
                "missing fake object",
                error_code=StorageErrorCode.NOT_FOUND,
                status_code=404,
                operation="get",
            ) from exc

    def list(
        self,
        prefix: str = "",
        *,
        max_keys: int = 1000,
        continuation_token: str | None = None,
    ) -> ListPage:
        self.calls.append(("list", prefix))
        keys = sorted(key for key in self.objects if key.startswith(prefix))
        offset = int(continuation_token or "0")
        page_size = min(max_keys, self.page_size)
        selected = keys[offset : offset + page_size]
        entries = tuple(
            FileEntry(
                key=key,
                size=len(self.objects[key]),
                last_modified=datetime(2026, 8, 1, tzinfo=UTC),
                etag="fake-etag",
            )
            for key in selected
        )
        next_offset = offset + len(selected)
        next_token = str(next_offset) if next_offset < len(keys) else None
        return ListPage(entries=entries, next_token=next_token)

    def key_from_url(self, url: str) -> str | None:
        return url.removeprefix("b2://") if url.startswith("b2://") else None

    def close(self) -> None:
        self.calls.append(("close", ""))


def run_record(run_id: str, *, minutes: int = 0) -> RunRecord:
    return RunRecord(
        id=run_id,
        title=f"Run {run_id}",
        brief="A sufficiently detailed test campaign brief",
        output_format="square",
        palette="clay",
        provider="test-provider",
        model="test-model",
        created_at=datetime(2026, 8, 1, 12, 0, tzinfo=UTC) + timedelta(minutes=minutes),
        storage_mode="b2",
        storage_key=f"assets/{run_id}.png",
        manifest_uri=f"b2://manifests/{run_id}.json",
        asset_url=f"/api/runs/{run_id}/asset",
        asset_sha256="a" * 64,
        manifest_hash="b" * 64,
        manifest_verified=True,
        bytes_verified=True,
        media_type="image/png",
        size_bytes=123,
        provenance_steps=[
            {
                "index": 1,
                "provider": "test-provider",
                "model": "test-model",
                "status": "completed",
            }
        ],
    )


def configured_b2(settings: Settings) -> Settings:
    return replace(
        settings,
        storage_mode="b2",
        b2_key_id="fake-key-id",
        b2_app_key="fake-app-key",
        b2_bucket="fake-bucket",
    )


def test_b2_repository_writes_manifest_before_record_and_round_trips(tmp_path: Path) -> None:
    backend = FakeB2Backend(page_size=1)
    repository = B2RunRepository(lambda: backend, tmp_path)
    older = run_record("older")
    newer = run_record("newer", minutes=1)

    repository.save(older, '{"canonical_hash":"older"}')
    repository.save(newer, '{"canonical_hash":"newer"}')

    assert backend.calls[:2] == [
        ("put", f"{repository.manifests_prefix}older.json"),
        ("put", f"{repository.records_prefix}older.json"),
    ]
    assert repository.get("newer") == newer
    assert repository.manifest("newer") == {"canonical_hash": "newer"}
    assert [record.id for record in repository.list()] == ["newer", "older"]
    assert sum(operation == "list" for operation, _ in backend.calls) == 2


def test_failed_record_write_leaves_no_listed_incomplete_pair(tmp_path: Path) -> None:
    backend = FakeB2Backend()
    repository = B2RunRepository(lambda: backend, tmp_path)
    record = run_record("incomplete")
    record_key = f"{repository.records_prefix}{record.id}.json"
    manifest_key = f"{repository.manifests_prefix}{record.id}.json"
    backend.fail_put_keys.add(record_key)

    with pytest.raises(StorageError, match="injected put failure"):
        repository.save(record, '{"canonical_hash":"incomplete"}')

    assert manifest_key in backend.objects
    assert record_key not in backend.objects
    assert repository.list() == []


def test_b2_repository_returns_none_for_missing_objects(tmp_path: Path) -> None:
    backend = FakeB2Backend()
    repository = B2RunRepository(lambda: backend, tmp_path)

    assert repository.get("missing") is None
    assert repository.manifest("missing") is None


def test_repository_factory_uses_b2_only_when_mode_and_credentials_are_ready(
    settings: Settings,
) -> None:
    backend = FakeB2Backend()

    assert isinstance(create_run_repository(settings, lambda: backend), RunRepository)
    assert isinstance(
        create_run_repository(configured_b2(settings), lambda: backend),
        B2RunRepository,
    )
    assert isinstance(
        create_run_repository(replace(settings, storage_mode="b2"), lambda: backend),
        RunRepository,
    )


def test_b2_mode_without_explicit_data_dir_uses_os_temp(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROVENANCE_STORAGE_MODE", "b2")
    monkeypatch.delenv("PROVENANCE_DATA_DIR", raising=False)

    settings = Settings.from_env()

    assert settings.data_dir == (Path(tempfile.gettempdir()) / "provenance-vault").resolve()


def test_explicit_data_dir_still_overrides_b2_temp_default(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    explicit = tmp_path / "persistent data"
    monkeypatch.setenv("PROVENANCE_STORAGE_MODE", "b2")
    monkeypatch.setenv("PROVENANCE_DATA_DIR", str(explicit))

    assert Settings.from_env().data_dir == explicit.resolve()


def test_local_mode_keeps_repository_data_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROVENANCE_STORAGE_MODE", "local")
    monkeypatch.delenv("PROVENANCE_DATA_DIR", raising=False)

    assert Settings.from_env().data_dir == (ROOT / "data").resolve()
