from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _dependencies(path: Path) -> dict[str, str]:
    project = tomllib.loads(path.read_text())["project"]
    result: dict[str, str] = {}
    for requirement in project["dependencies"]:
        match = re.match(r"[A-Za-z0-9._-]+", requirement)
        assert match is not None, requirement
        result[match.group(0).lower().replace("_", "-")] = requirement
    return result


def test_vercel_backend_declares_every_runtime_provider_at_the_root_version() -> None:
    root = _dependencies(ROOT / "pyproject.toml")
    backend = _dependencies(ROOT / "backend" / "pyproject.toml")

    for package in (
        "fastapi",
        "genblaze",
        "genblaze-gmicloud",
        "genblaze-nvidia",
        "genblaze-openai",
        "httpx",
    ):
        assert backend.get(package) == root.get(package), package
