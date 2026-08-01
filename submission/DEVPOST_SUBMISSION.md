# Devpost submission

> **Status: DRAFTED, not submitted.** Resolve every `PENDING` value from one verified live run
> before copying this into Devpost. The project page at
> <https://devpost.com/software/provenance-vault> is a draft handle, not submission proof.

## Project name

Provenance Vault

## Tagline

Generate media. Keep the proof.

## Description

Provenance Vault gives creative teams an inspectable chain of custody for generated campaign
media. The intended live workflow uses Genblaze to orchestrate generation and create a canonical
provenance manifest, then stores the asset and manifest in Backblaze B2 under content-addressed
keys. The app independently reads the stored asset bytes back and compares their SHA-256 digest
with the manifest, keeping manifest integrity and current-object integrity as separate signals.

A creator enters a title and brief, chooses a format, palette, and provider, and selects
**Generate & seal**. The interface presents the resulting media, provider/model, storage key,
asset digest, canonical manifest hash, verification status, manifest viewer, and run library.
The live-provider path is deliberately blocked unless B2 is also configured, preventing a paid
generation from bypassing the required storage and provenance flow.

## Judging alignment

- **Real-world utility:** preserves the prompt, model, parameters, timestamps, and exact output
  digest when creative media moves between tools or teams.
- **Production readiness:** includes explicit failure states, private-object proxying, secret
  redaction, B2-backed serverless persistence, responsive UI checks, automated tests, and both
  Docker and Vercel Services deployment source. These are locally verified; public deployment
  remains pending.
- **B2 storage and data orchestration:** the implemented live path uses Genblaze's B2-compatible
  object-storage sink, content-addressed keys, asset/manifest persistence, and independent B2
  byte read-back. The app index also persists its manifest/record pair through Genblaze S3
  `put/get/list`; unit fakes verify behavior without a cloud call. A real B2 upload/read-back is
  still pending live evidence.
- **Use of Genblaze:** the local rehearsal confirms a real Genblaze `Pipeline`, run/step model,
  canonical manifest, asset digest, and verification flow. The live provider connector and exact
  provider/model must be confirmed by the final run.

## AI provider and model

- Final live provider: `PENDING_FROM_LIVE_RUN`
- Final live model: `PENDING_FROM_LIVE_RUN`
- Development rehearsal only: `provenance-vault-local` / `procedural-editorial-v1`

The local procedural provider is not generative-AI or B2 submission evidence. List only the
provider and model actually returned by the final live Genblaze run, and remove every unused
provider from the final Devpost fields.

## Links

- Working application: `PENDING_PUBLIC_HTTPS_APP_URL`
- Source repository: <https://github.com/gother111/backblaze-provenance-vault>
- Demo video under three minutes: `PENDING_PUBLIC_VIDEO_URL`
- Devpost project draft: <https://devpost.com/software/provenance-vault> (project ID `1369439`)

## Truth boundary

Confirmed locally:

- the React/FastAPI application runs in local rehearsal mode;
- Genblaze creates the run, asset digest, and canonical manifest;
- content-addressed local storage, independent byte re-hashing, and tamper detection work;
- automated lint, backend/frontend tests, type-checking, and frontend build pass;
- B2/live-provider integration and B2-backed run-index code exists and is covered without making
  a cloud call;
- Vercel Services routing and dependency source exists, but no Vercel deployment has been made.

Still required before submission:

- a public HTTPS deployment configured for Backblaze B2;
- one real Genblaze provider run with exact provider/model values;
- matching B2 asset and manifest plus successful byte read-back evidence;
- a public demonstration video under three minutes;
- entrant review, current-rule acceptance, final submission, and confirmation proof.

Complete [LIVE_EVIDENCE_PACKET.md](LIVE_EVIDENCE_PACKET.md) from the same live run, then replace
the pending values and re-check the longer [DEVPOST_DRAFT.md](DEVPOST_DRAFT.md) for any claims or
fields required by the live form.
