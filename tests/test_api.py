from __future__ import annotations

from app.config import Settings
from app.main import create_app
from fastapi.testclient import TestClient


def test_api_create_list_manifest_asset_and_verify(settings: Settings) -> None:
    app = create_app(settings, seed_demo=False)
    with TestClient(app) as client:
        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json()["genblaze_core"] != "unavailable"

        created = client.post(
            "/api/runs",
            json={
                "title": "Field notes",
                "brief": "An editorial field notebook beside wild grasses at sunrise",
                "output_format": "landscape",
                "palette": "moss",
                "provider": "local",
            },
        )
        assert created.status_code == 201
        run = created.json()

        listed = client.get("/api/runs")
        assert listed.status_code == 200
        assert listed.json()[0]["id"] == run["id"]

        manifest = client.get(f"/api/runs/{run['id']}/manifest")
        assert manifest.status_code == 200
        assert manifest.json()["canonical_hash"] == run["manifest_hash"]

        asset = client.get(f"/api/runs/{run['id']}/asset")
        assert asset.status_code == 200
        assert asset.headers["content-type"].startswith("image/svg+xml")

        verified = client.post(f"/api/runs/{run['id']}/verify")
        assert verified.status_code == 200
        assert verified.json()["manifest_verified"] is True
        assert verified.json()["bytes_verified"] is True


def test_api_rejects_live_provider_without_server_credentials(settings: Settings) -> None:
    app = create_app(settings, seed_demo=False)
    with TestClient(app) as client:
        response = client.post(
            "/api/runs",
            json={
                "title": "Live test",
                "brief": "A campaign image that needs a real provider and storage",
                "output_format": "square",
                "palette": "clay",
                "provider": "openai",
            },
        )

    assert response.status_code == 409
    assert "B2" in response.json()["detail"]
