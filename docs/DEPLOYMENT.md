# Public deployment gate

The hackathon requires a working, accessible application URL. This repository contains a Docker deployment artifact but has not created or modified any external deployment.

## Required runtime configuration

- Python 3.11–3.13 runtime (the Docker image uses 3.12)
- writable persistent volume mounted at `PROVENANCE_DATA_DIR`
- `PROVENANCE_STORAGE_MODE=b2`
- `PROVENANCE_DEFAULT_PROVIDER=gmicloud` or `openai`
- B2 bucket, region, key ID, and application key
- corresponding AI-provider API key and sufficient credit
- HTTPS public URL

The app binds to `$PORT` when present, otherwise port 8000.

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
9. The object and manifest are visible in the intended B2 bucket.
10. Refreshing and restarting the service does not lose the run index.
11. Browser console has no uncaught errors; desktop and mobile have no horizontal overflow.
12. No key, secret, local file path, private prompt, or account identifier appears in the page source, API responses, logs, or screen recording.

Record the public URL, run ID, asset SHA-256, manifest hash, B2 object key, UTC timestamp, provider, and model in the submission evidence notes. That makes the final claims auditable.

## Rollback

If the live integration fails, do not present local mode as a compliant substitute. Keep the code and local demo, revoke/rotate exposed credentials, remove only the failed deployment, and report the exact unconfirmed state. The competition entry should be submitted only after the live gate passes.
