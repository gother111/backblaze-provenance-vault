# Devpost draft

> **Evidence rule:** text in `[VERIFY: ...]` brackets is not yet established. Replace it with the exact live result or remove the claim. Do not submit the local rehearsal as proof of B2 or paid-AI generation.

## Project name

Provenance Vault

## Tagline

Generate media. Keep the proof.

## One-line description

Provenance Vault gives creative teams a verifiable chain of custody for generated campaign media by pairing Genblaze manifests with content-addressed Backblaze B2 storage and independent byte verification.

## Inspiration

Generative media is easy to create and surprisingly hard to hand off responsibly. The moment an image moves through downloads, chat, or a shared drive, the final file becomes separated from the model, prompt, parameters, and generation time that produced it. Creative teams need a practical proof trail, not another “AI generated” sticker.

We built Provenance Vault to make provenance part of the creative workflow itself: generate the asset, seal the record, and verify the stored bytes from one calm interface.

## What it does

A creator enters a campaign title and brief, chooses a format, palette, and generation provider, then presses **Generate & seal**. Genblaze runs the provider pipeline and creates a canonical provenance manifest. The asset and manifest are stored in Backblaze B2 under content-addressed keys. Provenance Vault then reads the asset back from B2 and recomputes SHA-256.

The result screen shows:

- the generated media;
- provider and model;
- immutable B2 storage key;
- asset SHA-256;
- canonical manifest hash;
- separate manifest-integrity and stored-byte verification results;
- an inspectable canonical manifest and an immutable run library.

If the stored object changes, byte verification fails even when the original manifest is still internally valid.

## How we built it

- **Genblaze** orchestrates the image provider, run/step metadata, canonical provenance manifest, and object-storage sink.
- **Backblaze B2** is the durable integrity boundary. `S3StorageBackend.for_backblaze` and `ObjectStorageSink` persist assets/manifests with `KeyStrategy.CONTENT_ADDRESSABLE`.
- **FastAPI** validates requests, enforces the “no live generation without B2” gate, maintains the run index, proxies private assets, and independently re-hashes B2 bytes.
- **React + TypeScript** provide the creator workspace, proof ledger, manifest viewer, verifier, and run library.
- **pytest + Vitest + Ruff + TypeScript** cover orchestration, manifests, content addressing, tamper detection, API behavior, secret redaction, formatting, and build correctness.
- A multi-stage **Docker** build packages the frontend and API as one deployable service.

## How we use Backblaze B2

B2 is not a final screenshot dump. It is in the critical path for every live run:

1. Genblaze sends the provider output through its B2-compatible object-storage sink.
2. The sink uses content-addressed keys derived from SHA-256.
3. The canonical provenance manifest is stored alongside the media.
4. Provenance Vault derives the B2 object key from the returned asset URL.
5. It downloads the object from B2 and hashes the actual bytes again during creation.
6. A user can trigger the same B2 read-back at any time with **Verify bytes**.

[VERIFY: insert final B2 bucket region, live run ID, object key, asset SHA-256, manifest hash, and verification timestamp. Never insert credentials.]

## How we use Genblaze

Genblaze is the orchestration and provenance layer, not a thin API wrapper. We use its `Pipeline`, provider connectors, run/step model, asset digests, canonical manifest, B2 `ObjectStorageSink`, strict manifest reads, and content-addressable key strategy. The application adds the creator workflow and makes the difference between manifest integrity and actual stored-byte integrity visible.

## AI providers and models

- [VERIFY: `GMI Cloud` / exact model slug used in the final live run]
- [REMOVE IF UNUSED: `OpenAI` / exact model ID used in the final live run]
- Local procedural provider (`provenance-vault-local`, `procedural-editorial-v1`) is a clearly labelled offline development rehearsal and is not presented as generative-AI submission proof.

## Challenges

The hardest design decision was refusing to treat a valid manifest as proof that the current cloud object is unchanged. Manifest validation proves the record's canonical hash and declarations; it does not automatically re-download the object. We added an independent B2 byte read-back and digest comparison, then wrote a tamper test that demonstrates the two signals diverging.

We also needed a safe local workflow that never spent provider credit or pretended to use cloud storage. The app therefore has two explicit modes and rejects live providers unless B2 is configured.

## Accomplishments we are proud of

- B2 is the durable data/integrity boundary, not a decorative integration.
- Every live generation is blocked unless it can be sealed to B2.
- Content addressing makes the digest part of the object's identity.
- The UI exposes evidence without feeling like an infrastructure console.
- Tampering produces a visible failed byte check instead of a stale green badge.
- The same app can be rehearsed entirely locally without false cloud claims.

## What we learned

Provenance has at least two layers: the integrity of the generation record and the integrity of the media bytes currently in storage. A useful creator tool has to show both. Genblaze made the provider and manifest layer coherent; Backblaze B2 made the resulting evidence durable and independently retrievable.

## What's next

- store the searchable run index itself in B2 or a transactional database;
- add authenticated team workspaces and scoped sharing links;
- extend from still images to video and audio while keeping the same manifest/byte checks;
- support signed export bundles for agencies handing work to clients;
- add retention policies and lifecycle views for campaign archives.

## Built with

Backblaze B2, Genblaze, GMI Cloud [VERIFY], OpenAI [REMOVE IF UNUSED], Python, FastAPI, React, TypeScript, Vite, Pydantic, pytest, Vitest, Ruff, Docker, SHA-256.

## Links

- Live app: `[REQUIRED: public HTTPS URL]`
- Source: `[REQUIRED: GitHub URL]`
- Demo video: `[REQUIRED: public video URL, under 3 minutes]`
