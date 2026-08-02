from __future__ import annotations

import base64
from pathlib import Path

import httpx
from genblaze_core.models.step import Step
from genblaze_nvidia import NvidiaImageProvider


def test_nvidia_provider_decodes_inline_image(tmp_path: Path) -> None:
    image = b"\x89PNG\r\n\x1a\nnetwork-free-test-image"

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/genai/black-forest-labs/flux.1-schnell"
        assert b'"aspect_ratio":"3:2"' in request.content
        return httpx.Response(
            200,
            json={
                "artifacts": [
                    {
                        "base64": base64.b64encode(image).decode(),
                        "mime_type": "image/png",
                    }
                ]
            },
        )

    with httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://nim.invalid/v1"
    ) as client:
        provider = NvidiaImageProvider(
            api_key="",
            output_dir=tmp_path,
            http_client=client,
        )
        step = Step(
            provider="nvidia-nim-image",
            model="black-forest-labs/flux.1-schnell",
            prompt="An original field notebook beside wild grasses",
            params={"aspect_ratio": "3:2"},
        )

        result = provider.generate(step)

    assert len(result.assets) == 1
    asset = result.assets[0]
    assert Path(asset.url.removeprefix("file://")).read_bytes() == image
    assert result.provider_payload == {"nvidia": {"status": "succeeded"}}
