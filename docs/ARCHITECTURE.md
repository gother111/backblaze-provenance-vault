# Architecture and integrity model

## Design goal

Provenance Vault should answer one narrow question well: **does this exact media object still match the generation record attached to it?** It is a creator-facing workflow, not a blockchain, copyright oracle, or detector that guesses whether arbitrary media is AI generated.

## Request path

1. `POST /api/runs` validates the title, brief, output format, palette, and provider with Pydantic.
2. `ProvenanceService` creates a Genblaze `Pipeline` and one image-generation step.
3. The selected provider returns an asset:
   - local rehearsal: `LocalPosterProvider`, a deterministic `SyncProvider` that emits SVG bytes;
   - live: Genblaze `GMICloudImageProvider` or `DalleProvider`.
4. Storage is selected independently:
   - local rehearsal: provider writes to `data/objects/assets/<prefix>/<sha>.svg`;
   - live: `ObjectStorageSink(S3StorageBackend.for_backblaze(...))` writes with `KeyStrategy.CONTENT_ADDRESSABLE` and strict manifest reads.
5. Genblaze creates the canonical manifest and its canonical hash.
6. The service derives the stored object key, reads the final bytes, and independently calculates SHA-256.
7. A small atomic JSON repository stores the UI run index and a local copy of the canonical manifest.
8. The React client renders the media, provenance steps, B2/local storage key, hashes, and verification actions.

## Why both checks matter

`manifest.verify()` checks the canonical manifest structure/hash and its declared asset digest. That establishes that the manifest has not silently changed. It does not by itself prove that the current bytes in object storage still match the declared digest.

`verify_run()` therefore performs a second check:

```text
stored bytes -> SHA-256 -> compare with manifest asset SHA-256
```

The tests demonstrate the distinction by appending bytes to a stored SVG. Manifest verification continues to pass, while byte verification fails.

## Backblaze B2 usage

The live path uses B2 through Genblaze's S3 connector rather than treating B2 as a decorative export target:

- `S3StorageBackend.for_backblaze` configures the Backblaze endpoint and credentials.
- `ObjectStorageSink` orchestrates asset and manifest persistence.
- content-addressed keys make the asset digest part of its durable identity.
- strict manifest reads catch unavailable or inconsistent manifest storage.
- the app reads the B2 object back during creation and on every manual verification.
- the asset endpoint streams the B2 object through the backend, so a private bucket can remain private.

This is meaningful data orchestration: B2 is the integrity boundary for the creator's final asset, not only a place to host a screenshot.

## Genblaze usage

Genblaze owns the provider step, run state, asset metadata, canonical manifest, sink, storage strategy, and provider-specific connector behavior. The application adds the creator workflow, explicit local/live safety gate, B2 read-back, run index, tamper signal, and UI.

Pinned packages:

- `genblaze==0.4.5` (umbrella package)
- `genblaze-core==0.3.8` (resolved by the lockfile)
- `genblaze-s3==0.3.6` (resolved by the lockfile)
- `genblaze-gmicloud==0.3.5`
- `genblaze-openai==0.3.4`

The upstream repository was at release tag `v0.7.0` during implementation; Genblaze's package versions are independently versioned.

## Failure policy

- A live provider is refused unless B2 is fully configured.
- Missing provider credentials produce a configuration error before generation.
- A pipeline without a returned asset is treated as a failed request.
- An asset without a SHA-256 digest is rejected.
- A B2 URL that cannot be mapped back to the configured bucket is rejected.
- Missing local bytes return HTTP 410; unknown runs/manifests return HTTP 404.
- Provider/runtime failures return HTTP 502 with a useful message, without serializing credentials.
- The public configuration endpoint exposes readiness booleans and, only when configured, bucket/region names. It never returns keys.

## Persistence boundary

B2 is durable for live assets and canonical manifests. The run-library index is intentionally a small filesystem repository for hackathon scope. A public deployment must mount a persistent volume at `PROVENANCE_DATA_DIR`; otherwise the UI's index can reset on redeploy even though B2 objects remain safe.

The next production step would be a B2-backed run-index snapshot or a transactional database. That is not necessary to demonstrate the core integrity workflow and would add risk before the deadline.

## Security notes

- Keep B2 and provider keys server-side and out of frontend build variables.
- Use a private, dedicated bucket and a bucket-scoped application key with only required read/write/list capabilities.
- Rotate any credential that appears in logs, recordings, screenshots, commits, or Devpost fields.
- Do not put confidential client prompts into a public demo.
- Treat generated output as untrusted content; the current image endpoint returns only provider media bytes and a recorded media type.
- Add authentication, quotas, request size limits, moderation policy, and per-user isolation before real multi-tenant use.
