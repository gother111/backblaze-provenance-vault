from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    default_provider: str
    storage_mode: str
    b2_key_id: str
    b2_app_key: str
    b2_bucket: str
    b2_region: str
    b2_public_url_base: str
    gmi_api_key: str
    gmi_image_model: str
    openai_api_key: str
    openai_image_model: str
    nvidia_api_key: str
    nvidia_image_model: str

    @classmethod
    def from_env(cls) -> Settings:
        storage_mode = _env("PROVENANCE_STORAGE_MODE", "local")
        data_value = _env("PROVENANCE_DATA_DIR")
        if data_value:
            data_dir = Path(data_value)
            if not data_dir.is_absolute():
                data_dir = ROOT / data_dir
        elif storage_mode == "b2":
            data_dir = Path(tempfile.gettempdir()) / "provenance-vault"
        else:
            data_dir = ROOT / "data"
        return cls(
            data_dir=data_dir.resolve(),
            default_provider=_env("PROVENANCE_DEFAULT_PROVIDER", "local"),
            storage_mode=storage_mode,
            b2_key_id=_env("B2_KEY_ID"),
            b2_app_key=_env("B2_APP_KEY"),
            b2_bucket=_env("B2_BUCKET"),
            b2_region=_env("B2_REGION", "us-west-004"),
            b2_public_url_base=_env("B2_PUBLIC_URL_BASE"),
            gmi_api_key=_env("GMI_API_KEY"),
            gmi_image_model=_env("GMI_IMAGE_MODEL", "seedream-5.0-lite"),
            openai_api_key=_env("OPENAI_API_KEY"),
            openai_image_model=_env("OPENAI_IMAGE_MODEL", "gpt-image-2"),
            nvidia_api_key=_env("NVIDIA_API_KEY"),
            nvidia_image_model=_env(
                "NVIDIA_IMAGE_MODEL", "black-forest-labs/flux.1-schnell"
            ),
        )

    @property
    def b2_ready(self) -> bool:
        return bool(self.b2_key_id and self.b2_app_key and self.b2_bucket and self.b2_region)

    @property
    def gmi_ready(self) -> bool:
        return bool(self.gmi_api_key)

    @property
    def openai_ready(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def nvidia_ready(self) -> bool:
        return bool(self.nvidia_api_key)

    def public_capabilities(self) -> dict[str, object]:
        """Return readiness booleans only. Credential values never leave the server."""
        return {
            "default_provider": self.default_provider,
            "storage_mode": self.storage_mode,
            "providers": {
                "local": True,
                "gmicloud": self.gmi_ready,
                "openai": self.openai_ready,
                "nvidia": self.nvidia_ready,
            },
            "b2": {
                "configured": self.b2_ready,
                "bucket": self.b2_bucket if self.b2_ready else None,
                "region": self.b2_region if self.b2_ready else None,
            },
        }
