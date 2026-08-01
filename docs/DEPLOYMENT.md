# Public deployment gate

The hackathon requires a working, accessible application URL. This repository contains Docker
and Vercel Services deployment source, but no external project, environment, or deployment has
been created or modified.

## Required runtime configuration

- Python 3.11–3.13 runtime (the Docker image uses 3.12)
- `PROVENANCE_STORAGE_MODE=b2`
- `PROVENANCE_DEFAULT_PROVIDER=gmicloud` or `openai`
- private B2 bucket plus a bucket-scoped key with read, write, and list access
- B2 bucket, region, key ID, and application key entered only as server-side secrets
- corresponding AI-provider API key and sufficient credit
- HTTPS public URL

Docker also needs a writable `PROVENANCE_DATA_DIR`; the included image explicitly uses
`/app/data`. A B2-backed serverless deployment does not need a persistent filesystem volume:
the full run record and canonical manifest copy are stored in B2, and unset
`PROVENANCE_DATA_DIR` falls back to OS-temporary provider staging.

## Vercel Services deployment source

The root [vercel.json](../vercel.json) declares two services:

| Service | Entrypoint | Public route prefix |
| --- | --- | --- |
| `frontend` | `frontend` | `/` |
| `backend` | `backend/vercel_app.py` | `/api` |

Before any Vercel build, set **Project Settings → Build & Deployment → Framework Preset** to
**Services**. Without that preset, valid service routes can return 404. Keep the repository root
as the Vercel project root so the single root `vercel.json` can discover both entrypoints.

Vercel removes `/api` before forwarding a backend request. The Vercel entrypoint therefore
declares internal `/health`, `/runs`, and related routes, while public clients and the React app
continue to use `/api/health`, `/api/runs`, and the rest of the existing API. The local/Docker
entrypoint still declares `/api/*` directly. The Vercel entrypoint disables demo seeding, so cold
starts do not create media, consume provider credit, or write B2 objects.

For a Vercel project, enter the required B2 and provider settings in Vercel's server-side
environment settings. Do not prefix them with `VITE_`, and do not set `PROVENANCE_DATA_DIR`
unless it points to an explicitly writable runtime location. No credential value belongs in
`vercel.json`, Git, build output, frontend variables, or deployment logs.

### Serverless persistence truth boundary

When `PROVENANCE_STORAGE_MODE=b2` and all four B2 values are present, the repository factory uses
the installed Genblaze S3 backend's `put`, `get`, and paginated `list` operations. It stores the
canonical manifest first and the full run record last under
`provenance-vault/app-index/v1/`. Record objects are commit markers for listing, so a failed
record upload cannot make a manifest-only partial run visible. The Genblaze sink separately
persists its content-addressed media and canonical manifest objects.

The implementation and failure ordering are covered by unit fakes that make zero network calls.
They do not prove Vercel detection, B2 authentication, bucket permissions, a real upload, cold
start behavior, provider generation, public routing, or anonymous browser access. Those states
remain pending until an authorized deployment completes the acceptance test below.

## Generic Docker deployment

```bash
docker build -t provenance-vault .
docker run --rm \
  -p 8000:8000 \
  --env-file .env \
  -v provenance-data:/app/data \
  provenance-vault
```

Do not commit `.env`. Enter secrets in the host's server-side secret manager.

The app binds to `$PORT` when present, otherwise port 8000, on the Docker/local path.

## Acceptance test

Run these checks against the final HTTPS origin before using it in Devpost:

1. `GET /api/health` returns HTTP 200 and reports `storage_mode: b2` plus `b2.configured: true`.
2. The app loads in a clean/private browser window without login or a local-network dependency.
3. The header says `B2 CONNECTED` and the live provider is selected by default.
4. A fresh generation completes from the public UI.
5. The resulting provider/model are the actual paid provider and model.
6. The storage key includes the exact asset SHA-256.
7. **Open manifest** displays a canonical Genblaze manifest.
8. **Verify bytes** passes after reading the object back from B2.
9. The Genblaze object/manifest and the app-index record/manifest pair are visible in the intended
   B2 bucket without exposing credential values.
10. Refreshing and forcing a fresh service instance does not lose the run index.
11. Browser console has no uncaught errors; desktop and mobile have no horizontal overflow.
12. No key, secret, local file path, private prompt, or account identifier appears in the page source, API responses, logs, or screen recording.

Record the public URL, run ID, asset SHA-256, manifest hash, B2 object key, UTC timestamp, provider, and model in the submission evidence notes. That makes the final claims auditable.

## Rollback

If the live integration fails, do not present local mode or fake-backed tests as a compliant
substitute. Keep the code and local demo, revoke/rotate exposed credentials, remove only the
failed deployment, and report the exact unconfirmed state. The competition entry should be
submitted only after the live gate passes.
