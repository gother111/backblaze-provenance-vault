# Backblaze Generative Media Hackathon research

Competition pages were checked on **2026-08-01**. Official Genblaze release and package sources
were reconciled on **2026-08-02**. The official rules and Devpost clock remain authoritative.

## Deadline and prizes

- Submission deadline: **August 3, 2026 at 5:00 PM EDT**.
- Stockholm equivalent: **August 3, 2026 at 23:00 CEST**.
- Prize pool: **$10,000 USD**: first place $7,000, second place $2,000, third place $1,000.

Sources: [overview](https://backblaze-generative-media.devpost.com/) and [official rules](https://backblaze-generative-media.devpost.com/rules).

## Core build requirement

The entry must be a generative-media application that uses both:

1. **Backblaze B2** for storage/data orchestration; and
2. **Genblaze** for the generative-media pipeline.

This app's intended live proof is one NVIDIA NIM, GMI Cloud, or OpenAI image run orchestrated by
Genblaze, persisted by Genblaze's content-addressed B2 sink, then read back from B2 and
independently re-hashed. NVIDIA NIM is the prepared candidate no-spend route through the official
`genblaze-nvidia==0.3.3` connector, but current offer/model access is unverified and still requires
an authorized account, current terms acceptance, an API key, and one verified live response.

## Submission deliverables

The official pages require:

- a working, accessible application URL;
- a public or private GitHub repository with complete setup instructions;
- if private, repository access for the organizer account specified by Devpost (`b2genblaze` at the time checked);
- a description of what was built and how B2 and Genblaze are used;
- a list of AI providers and models used;
- a public demo video no longer than three minutes, hosted on a supported public video platform;
- all required Devpost fields and acceptance of the official rules.

Use [submission/SUBMISSION_CHECKLIST.md](../submission/SUBMISSION_CHECKLIST.md) as the final gate.

## Judging

The overview lists four equally weighted criteria:

- real-world utility;
- production readiness;
- use of Backblaze B2 storage/data orchestration;
- use of Genblaze.

Provenance Vault maps directly to those criteria:

| Criterion | Entry evidence |
| --- | --- |
| Real-world utility | Creator-facing chain of custody for generated campaign media |
| Production readiness | explicit failure states, private B2 proxy, persistent deployment path, tests, responsive UI, credential redaction |
| B2 use | content-addressed asset/manifest persistence plus B2 read-back and SHA-256 verification |
| Genblaze use | provider pipeline, run state, asset metadata, canonical manifest, B2 sink, storage-key strategy |

## Eligibility and ownership

The competition is online and broadly global. A Swedish resident is not inherently excluded, but the entrant must personally confirm all eligibility conditions, including age of majority, jurisdiction, employment/organizer conflicts, sanctions/excluded-location clauses, and ability to receive the prize. The app cannot verify those facts.

The rules state that projects should be new for the hackathon, or an existing project must add substantial new B2 and Genblaze functionality during the submission period. They also require original work and authorization for third-party integrations/assets. Technical assistance is allowed subject to the rules, but the entrant must own/control the entry and its creative decisions.

The entrant retains project IP, while granting the organizer the limited judging and promotional rights described in the official rules. Winners may need tax and eligibility documentation.

## Genblaze resources

The [resources page](https://backblaze-generative-media.devpost.com/resources) describes Genblaze as a unified pipeline that emits a SHA-256 provenance manifest including provider, model, prompt, parameters, timestamps, and outputs. The [updates page](https://backblaze-generative-media.devpost.com/updates) announced the `v0.7.0` release wave shortly before the deadline. The repository pins the corresponding currently published package versions in `uv.lock`.

### Genblaze v0.7 release-wave reconciliation

| Official fact checked on 2026-08-02 | Local source state | Claim boundary |
| --- | --- | --- |
| The [`v0.7.0` release notes](https://github.com/backblaze-labs/genblaze/releases/tag/v0.7.0) say the wave tag is not the umbrella PyPI version. They list `genblaze==0.4.5`, `genblaze-core==0.3.8`, and `genblaze-nvidia==0.3.3`. | The root and backend projects pin the umbrella and NVIDIA versions; `uv.lock` resolves core `0.3.8`; `uv lock --check` passes. | Confirms release/package alignment, not provider compatibility. |
| The [`genblaze-nvidia` 0.3.3 package](https://pypi.org/project/genblaze-nvidia/0.3.3/) is published from the official `v0.7.0` tag with PyPI attestations. Its documented image connector is `NvidiaImageProvider`, its credential variable is `NVIDIA_API_KEY`, and its image families include `black-forest-labs/flux*`. | The app uses that provider class, variable, and the candidate model `black-forest-labs/flux.1-schnell`; the lockfile hashes match the published 0.3.3 artifacts. | Confirms intended API shape and artifact identity only. |
| The [official multi-provider sample](https://github.com/backblaze-labs/genblaze-gen-media-multi-provider-sample) names `flux.1-schnell` as its NVIDIA image default and describes a free/no-card route, but tells users to confirm offers in the provider console because they change. | NVIDIA is available as a disabled selector until `NVIDIA_API_KEY` is configured; a network-free fake covers one inline response. | Does not confirm current account eligibility, free access, quota, exact model availability, a real response, or a successful B2 run. |

The submission may name NVIDIA and an exact model only if the same final public run returns those
values. Configuration defaults, package documentation, selector screenshots, and mocked responses
must not be used as live compatibility evidence.

## Actions intentionally not taken

No Devpost registration or rule acceptance, cloud/provider account creation or access, credential
use, purchase, public deployment, video upload, or final submission was performed during this
hardening pass. The existing public repository, draft project handle, and previously recorded
Genblaze star are separate historical states, not evidence of submission.
