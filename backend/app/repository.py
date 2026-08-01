from __future__ import annotations

import json
from pathlib import Path

from .schemas import RunRecord


class RunRepository:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.records_dir = data_dir / "records"
        self.manifests_dir = data_dir / "manifests"
        self.assets_dir = data_dir / "objects" / "assets"
        for directory in (self.records_dir, self.manifests_dir, self.assets_dir):
            directory.mkdir(parents=True, exist_ok=True)

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
