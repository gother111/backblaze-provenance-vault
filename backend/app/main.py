from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import ROOT, Settings
from .schemas import CreateRunRequest, RunRecord, VerificationResult
from .service import ConfigurationError, ProvenanceService


def create_app(
    settings: Settings | None = None,
    *,
    seed_demo: bool = True,
    api_prefix: str = "/api",
    serve_frontend: bool = True,
) -> FastAPI:
    resolved_settings = settings or Settings.from_env()
    service = ProvenanceService(resolved_settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.service = service
        if seed_demo:
            service.ensure_demo_run()
        yield

    app = FastAPI(
        title="Provenance Vault API",
        version="0.1.0",
        description="Genblaze media generation with verifiable local or Backblaze B2 storage.",
        lifespan=lifespan,
    )
    router = APIRouter(prefix=api_prefix)

    @router.get("/health")
    def health() -> dict[str, object]:
        return service.health()

    @router.get("/config")
    def config() -> dict[str, object]:
        return resolved_settings.public_capabilities()

    @router.get("/runs", response_model=list[RunRecord])
    def list_runs() -> list[RunRecord]:
        return service.repository.list()

    @router.post("/runs", response_model=RunRecord, status_code=201)
    def create_run(payload: CreateRunRequest) -> RunRecord:
        try:
            return service.create_run(payload)
        except ConfigurationError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    @router.get("/runs/{run_id}", response_model=RunRecord)
    def get_run(run_id: str) -> RunRecord:
        record = service.repository.get(run_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return record

    @router.get("/runs/{run_id}/manifest")
    def get_manifest(run_id: str) -> dict[str, object]:
        try:
            return service.manifest_json(run_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Manifest not found") from exc

    @router.post("/runs/{run_id}/verify", response_model=VerificationResult)
    def verify_run(run_id: str) -> VerificationResult:
        try:
            return service.verify_run(run_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Run not found") from exc

    @router.get("/runs/{run_id}/asset")
    def get_asset(run_id: str) -> Response:
        try:
            payload, media_type = service.asset_bytes(run_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Run not found") from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=410, detail="Asset bytes are missing") from exc
        return Response(
            content=payload,
            media_type=media_type,
            headers={"Cache-Control": "public, max-age=31536000, immutable"},
        )

    app.include_router(router)

    frontend_dist = ROOT / "frontend" / "dist"
    if serve_frontend and frontend_dist.exists():
        assets_dir = frontend_dist / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str) -> FileResponse:
            candidate = (frontend_dist / path).resolve()
            if path and candidate.is_file() and frontend_dist.resolve() in candidate.parents:
                return FileResponse(candidate)
            return FileResponse(frontend_dist / "index.html")

    return app


app = create_app()
