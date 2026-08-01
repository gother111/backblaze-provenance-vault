# Provenance Vault

**Generate media. Keep the proof.** Provenance Vault is a small production-shaped app for creators who need to prove where a campaign asset came from. A generation request runs through [Genblaze](https://github.com/backblaze-labs/genblaze), the output is written to Backblaze B2 under a content-addressed key, and the app can fetch the stored bytes again to verify their SHA-256 digest against the canonical provenance manifest.

![Provenance Vault desktop interface](submission/assets/provenance-vault-desktop.png)

This repository is an entry candidate for the [Backblaze Generative Media Hackathon](https://backblaze-generative-media.devpost.com/). It is deliberately honest about readiness: the local mode is fully exercised, while live B2 and paid AI-provider calls require the account credentials listed in [submission/BLOCKERS.md](submission/BLOCKERS.md).

Public source: <https://github.com/gother111/backblaze-provenance-vault>

## Why it is useful

Creative teams routinely move generated media from a model into chat, downloads, shared drives, and publishing tools. That breaks the connection between the final file and the prompt, model, parameters, and generation time. Provenance Vault keeps that chain inspectable:

1. A creator enters a title, brief, format, palette, and provider.
2. Genblaze runs the provider step and constructs its canonical manifest.
3. In live mode, Genblaze's `ObjectStorageSink` writes the asset and manifest to Backblaze B2 with `KeyStrategy.CONTENT_ADDRESSABLE`.
4. The API reads the stored asset back and independently computes SHA-256.
5. The interface shows the provider/model, storage key, asset hash, manifest hash, and verification result.

The result is not a vague “AI generated” badge. It is a reproducible evidence trail tied to the exact stored bytes.

## Two explicit modes

| Mode | What runs | What it proves |
| --- | --- | --- |
| Local rehearsal | Real Genblaze `Pipeline`, deterministic local SVG provider, content-addressed local object, canonical manifest, byte re-hash | UI, orchestration, persistence, manifest validation, tamper detection. It does **not** claim AI generation or a B2 upload. |
| Live entry | Genblaze GMI Cloud or OpenAI provider, Genblaze B2 object-storage sink, B2 read-back, manifest and byte verification | The actual competition integration after credentials and one successful end-to-end run are supplied. |

The UI labels local output `OFFLINE REHEARSAL` and shows `LOCAL DEMO` in the header. Live claims should only be used after completing the evidence gate in [submission/SUBMISSION_CHECKLIST.md](submission/SUBMISSION_CHECKLIST.md).

## Architecture

```mermaid
flowchart LR
    A["Creator brief"] --> B["FastAPI service"]
    B --> C["Genblaze Pipeline"]
    C --> D{"Provider"}
    D -->|rehearsal| E["Deterministic SVG provider"]
    D -->|live| F["GMI Cloud or OpenAI"]
    E --> G{"Storage mode"}
    F --> G
    G -->|rehearsal| H["Local content-addressed object"]
    G -->|live| I["Genblaze ObjectStorageSink"]
    I --> J["Private Backblaze B2 bucket"]
    H --> K["Canonical Genblaze manifest"]
    J --> K
    K --> L["Independent byte re-hash"]
    L --> M["React provenance inspector"]
```

The important implementation detail is that `Manifest.verify()` and byte verification are separate checks. The former verifies the canonical manifest and declared digests. The app also downloads the actual stored object and hashes it again, so an altered or missing object fails visibly.

More detail is in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Local quick start

Requirements: Python 3.11–3.13, [uv](https://docs.astral.sh/uv/), Node.js, and npm.

```bash
cp .env.example .env
make install
```

In terminal 1:

```bash
set -a
source .env
set +a
make api
```

In terminal 2:

```bash
make web
```

Open `http://127.0.0.1:5173`. The API is at `http://127.0.0.1:8000`; its health endpoint is `/api/health`.

To run the built single-service app:

```bash
make build
.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

## Configure the live competition path

Create a private B2 bucket and a bucket-scoped application key that can read and write files. Keep all values server-side:

```dotenv
PROVENANCE_STORAGE_MODE=b2
PROVENANCE_DEFAULT_PROVIDER=gmicloud
PROVENANCE_DATA_DIR=data

B2_KEY_ID=...
B2_APP_KEY=...
B2_BUCKET=...
B2_REGION=us-west-004

GMI_API_KEY=...
GMI_IMAGE_MODEL=seedream-5.0-lite
```

OpenAI is also supported through the official Genblaze connector:

```dotenv
OPENAI_API_KEY=...
OPENAI_IMAGE_MODEL=gpt-image-2
PROVENANCE_DEFAULT_PROVIDER=openai
```

Restart the API after changing environment variables. A live provider is intentionally rejected unless B2 is also configured. This prevents a successful paid generation from bypassing the competition's storage requirement.

Run one new asset, press **Verify bytes**, then confirm all of the following before recording the demo:

- the header says `B2 CONNECTED`;
- the selected provider is GMI Cloud or OpenAI;
- the run's storage mode is `b2`;
- the storage key is content-addressed and contains the asset SHA-256;
- manifest verification and byte verification both pass;
- the object and manifest exist in the intended B2 bucket.

## API surface

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Service, Genblaze version, capability booleans, run count |
| `GET` | `/api/config` | Non-secret readiness state for the UI |
| `GET` | `/api/runs` | Immutable local run index |
| `POST` | `/api/runs` | Generate, seal, persist, and verify one asset |
| `GET` | `/api/runs/{id}/asset` | Stream the local or B2 object through the API |
| `GET` | `/api/runs/{id}/manifest` | Return the canonical Genblaze manifest |
| `POST` | `/api/runs/{id}/verify` | Re-read bytes and compare SHA-256 |

Interactive API documentation is available at `/docs` while the service is running.

## Verification

```bash
make verify
```

This runs Python linting, backend tests, TypeScript checking, frontend tests, and the production frontend build. The backend suite covers actual local Genblaze orchestration, canonical manifests, content-addressed keys, a directory containing spaces, API behavior, secret redaction, provider-size contracts, and byte-tampering detection.

## Deployment

The included [Dockerfile](Dockerfile) builds the React client and serves it from the FastAPI process. A deployment must provide a persistent volume for `PROVENANCE_DATA_DIR`; B2 contains the durable media and manifests, while this prototype's searchable run index is a small local JSON store.

Example:

```bash
docker build -t provenance-vault .
docker run --rm -p 8000:8000 --env-file .env -v provenance-data:/app/data provenance-vault
```

Do not bake `.env` into the image or expose provider/B2 credentials to the browser. See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for the public-deployment acceptance checks.

## Repository map

- `backend/app/`: FastAPI API, Genblaze pipeline, B2 sink, repository, and verifier
- `frontend/src/`: React interface and provenance inspector
- `tests/`: backend integration and API tests
- `docs/`: architecture, rules research, design system, deployment, and QA evidence
- `submission/`: concise and extended Devpost copy, live-evidence packet, demo script, readiness checklist, blockers, and Genblaze feedback draft

## Current evidence status

| Claim | Status on 2026-08-01 |
| --- | --- |
| App works locally | Confirmed |
| Real Genblaze pipeline and manifest run locally | Confirmed |
| Content-addressed storage and byte tamper detection | Confirmed locally |
| Responsive desktop/mobile UI | Confirmed in Codex's in-app browser |
| B2 integration code exists | Confirmed by inspection/tests that do not call B2 |
| Successful real B2 upload/read-back | **Not yet confirmed: credentials required** |
| Successful paid AI-provider generation | **Not yet confirmed: provider credential/credit required** |
| Public GitHub repository | Confirmed: <https://github.com/gother111/backblaze-provenance-vault> |
| Public app, public demo video, Devpost submission | **Not yet created** |

Do not collapse these states. A compliant final entry needs the last three rows completed before the deadline.

## Official references

- [Hackathon overview and submission requirements](https://backblaze-generative-media.devpost.com/)
- [Official rules](https://backblaze-generative-media.devpost.com/rules)
- [Hackathon resources](https://backblaze-generative-media.devpost.com/resources)
- [Hackathon updates](https://backblaze-generative-media.devpost.com/updates)
- [Genblaze repository](https://github.com/backblaze-labs/genblaze)
- [Backblaze B2 APIs](https://www.backblaze.com/docs/cloud-storage-apis)
- [Backblaze S3-compatible API](https://www.backblaze.com/docs/cloud-storage-call-the-s3-compatible-api)

## License

[MIT](LICENSE). The entrant must still verify rights for every prompt, generated output, logo, font, sample asset, voice, and music used in the final public demo.
