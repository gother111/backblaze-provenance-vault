from __future__ import annotations

from pathlib import Path

import pytest
from app.config import Settings


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        data_dir=tmp_path / "data with spaces",
        default_provider="local",
        storage_mode="local",
        b2_key_id="",
        b2_app_key="",
        b2_bucket="",
        b2_region="us-west-004",
        b2_public_url_base="",
        gmi_api_key="",
        gmi_image_model="seedream-5.0-lite",
        openai_api_key="",
        openai_image_model="gpt-image-2",
        nvidia_api_key="",
        nvidia_image_model="black-forest-labs/flux.1-schnell",
    )
