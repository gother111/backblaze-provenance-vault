# Live submission evidence packet

Use this packet only after a real provider run succeeds on the public HTTPS deployment with
Backblaze B2 storage enabled. It converts one live run into the exact facts needed by the
Devpost description, demo, screenshots, and final checklist.

This tracked file is a blank template. Copy it to `.submission-private/live-evidence.md` before
filling it. The private folder is ignored by Git. Never record credentials, authorization
headers, provider account IDs, or secret-manager screenshots.

Current state on 2026-08-02: **template ready; no live B2/provider run or public deployment has
been evidenced.**

## 1. Freeze the final source before deployment

Run these checks from the exact checkout intended for deployment:

```bash
git status --short --branch
uv lock --check
make verify
uv pip compile backend/pyproject.toml --no-header --no-annotate
git rev-parse HEAD
```

Do not fill the final-source row from an uncommitted or dirty tree. After an intentional final
commit is made and published, confirm that the public repository shows the same full SHA. If NVIDIA is the
selected provider, confirm the exact model is available to the authorized account before setting
the deployment default. Do not record a credential, account ID, private console URL, or quota
screen. Package versions, selector screenshots, and mocked responses are not compatibility proof.

## 2. Freeze one evidence run

Use a fresh run created from the public UI. Do not use the seeded local rehearsal.

1. Open the public app in a private browser window and confirm it needs no login.
2. Confirm the header says `B2 CONNECTED` and select the intended live provider.
3. Use an original prompt that is safe to show publicly.
4. Click **Generate & seal** once and wait for the result.
5. Click **Verify bytes** after the result loads.
6. Keep that run selected while collecting every field below.
7. Confirm the matching asset and manifest in the B2 console without recording the console.

Do not switch to a second run halfway through. The run ID, provider/model, object key, asset
digest, manifest hash, and verification timestamp must all describe the same run.

## 3. Evidence manifest

Fill `Observed value` only from the public UI, API response, Git, video host, or B2 console.
Leave a row `PENDING` if its proof surface has not been checked.

| Claim | Required observed value | Authoritative proof surface | Observed value | Evidence handle |
| --- | --- | --- | --- | --- |
| Final source | Full 40-character commit SHA | `git rev-parse HEAD` and public GitHub commit | PENDING | PENDING |
| Lock consistency | `uv lock --check` passes | Exact final checkout | PENDING | PENDING |
| Final source checks | `make verify` passes | Exact final checkout | PENDING | PENDING |
| Public app | HTTPS origin | Clean private browser | PENDING | PENDING |
| Anonymous access | Loads with no login or local dependency | Clean private browser | PENDING | PENDING |
| API health | HTTP 200 and `status: ok` | `GET /api/health` | PENDING | PENDING |
| Storage mode | `b2` | Run JSON and app header | PENDING | PENDING |
| B2 readiness | `configured: true` | Health JSON | PENDING | PENDING |
| B2 region | Exact non-secret region | Health JSON | PENDING | PENDING |
| Live provider | `nvidia`, `gmicloud`, or `openai`, matching the UI | Run JSON | PENDING | PENDING |
| Live model | Exact model slug returned by Genblaze | Run JSON | PENDING | PENDING |
| Run identity | Exact run ID; `is_demo: false` | Run JSON | PENDING | PENDING |
| B2 asset key | Exact content-addressed `storage_key` | Run JSON and B2 console | PENDING | PENDING |
| Asset digest | 64-character `asset_sha256` | Run JSON | PENDING | PENDING |
| Content addressing | Asset digest occurs in the storage key | Compare the two rows above | PENDING | PENDING |
| Manifest digest | Exact `manifest_hash` | Run JSON and manifest JSON | PENDING | PENDING |
| Manifest integrity | `manifest_verified: true` | Verification JSON | PENDING | PENDING |
| Stored-byte integrity | `bytes_verified: true` | Verification JSON | PENDING | PENDING |
| Byte digest match | `actual_sha256` equals `expected_sha256` | Verification JSON | PENDING | PENDING |
| Verification time | Exact UTC `checked_at` | Verification JSON | PENDING | PENDING |
| B2 persistence | Matching asset and manifest exist | B2 console | PENDING | PENDING |
| Restart persistence | Run remains after service restart | Public app and run API | PENDING | PENDING |
| Desktop acceptance | Final live flow works at 1440 x 1000 | Private browser | PENDING | PENDING |
| Mobile acceptance | Final live flow works at 390 x 844 | Private browser | PENDING | PENDING |
| Browser health | No uncaught console errors | Browser console after the full flow | PENDING | PENDING |
| Demo | Public URL and duration under 3:00 | YouTube, Vimeo, or Youku in private browser | PENDING | PENDING |
| Availability window | Free, unrestricted app access through Aug 11, 2026 at 5:00 PM EDT | Hosting settings and private browser | PENDING | PENDING |
| Devpost receipt | Final project URL and confirmation time | Devpost confirmation page/email | PENDING | PENDING |

`Evidence handle` should be a URL, screenshot filename, video timecode, or a short note such as
`B2 console checked 2026-08-02T18:42:00Z`. Do not paste secrets or full private console pages.

## 4. Read-only API cross-check

After copying the exact public origin and run ID from the browser, run these commands. They do
not create a generation. The verification request re-reads the already stored object from B2.

```bash
ENTRY_ORIGIN='https://replace-with-final-origin.example'
EVIDENCE_RUN_ID='replace-with-live-run-id'

curl --fail --silent --show-error "$ENTRY_ORIGIN/api/health" \
  | python3 -m json.tool

curl --fail --silent --show-error "$ENTRY_ORIGIN/api/config" \
  | python3 -m json.tool

curl --fail --silent --show-error "$ENTRY_ORIGIN/api/runs/$EVIDENCE_RUN_ID" \
  | python3 -m json.tool

curl --fail --silent --show-error \
  "$ENTRY_ORIGIN/api/runs/$EVIDENCE_RUN_ID/manifest" \
  | python3 -m json.tool

curl --fail --silent --show-error --request POST \
  "$ENTRY_ORIGIN/api/runs/$EVIDENCE_RUN_ID/verify" \
  | python3 -m json.tool

curl --fail --silent --show-error --output /dev/null \
  --write-out 'asset_http=%{http_code}\n' \
  "$ENTRY_ORIGIN/api/runs/$EVIDENCE_RUN_ID/asset"
```

Review output before saving or sharing it. The health response includes the configured bucket
name, and the manifest contains the public demo prompt and provider metadata. It should never
contain keys, tokens, or authorization headers.

## 5. Screenshot and video evidence

Capture only the final live deployment. Suggested evidence handles:

| Filename | Required visible proof |
| --- | --- |
| `01-live-result.png` | `B2 CONNECTED`, generated asset, provider, and exact model |
| `02-proof-ledger.png` | B2 storage key, asset SHA-256, manifest hash, and both green checks |
| `03-manifest.png` | Canonical manifest fields for the same run, with no secret or account data |
| `04-mobile.png` | Final live run at 390 x 844 with no horizontal overflow |

In the demo, the same proof should appear at the timecodes in `DEMO_SCRIPT.md`. Do not show a
credential console, environment variables, browser autofill, notifications, or a local-mode run.

## 6. Copy-ready live evidence paragraph

Replace every `PENDING` token below only after the evidence manifest is complete. The provider
name and model must be copied from the run JSON, not from configuration defaults.

> On `PENDING UTC timestamp`, Provenance Vault completed live run `PENDING run ID` through
> Genblaze using `PENDING provider` and model `PENDING model`. Genblaze stored the output in
> Backblaze B2 region `PENDING region` under content-addressed key `PENDING object key`. The
> asset SHA-256 was `PENDING asset hash` and the canonical manifest hash was `PENDING manifest
> hash`. A fresh B2 read-back returned the same SHA-256, so both manifest integrity and stored-byte
> integrity passed for that run.

Paste the completed paragraph into the live-evidence marker in `DEVPOST_DRAFT.md`. Remove any
unused provider from both **AI providers and models** and **Built with**.

## 7. Final reconciliation

Before submitting, compare all four surfaces:

- Devpost description values match the evidence manifest exactly.
- Demo video shows the same provider/model and one internally consistent live run.
- Public app still loads anonymously and the recorded run still verifies.
- Public GitHub HEAD matches the final source SHA and `make verify` passes on that commit.

Then re-open the [official overview](https://backblaze-generative-media.devpost.com/) and
[official rules](https://backblaze-generative-media.devpost.com/rules). The entrant must
personally confirm eligibility, accept the current rules, submit, and retain the confirmation
page/email. A saved Devpost draft is not submission proof.
