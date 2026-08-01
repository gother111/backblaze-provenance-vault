# Backblaze Generative Media Hackathon research

Checked against the official pages on **2026-08-01**. The official rules and Devpost clock remain authoritative.

## Deadline and prizes

- Submission deadline: **August 3, 2026 at 5:00 PM EDT**.
- Stockholm equivalent: **August 3, 2026 at 23:00 CEST**.
- Prize pool: **$10,000 USD**: first place $7,000, second place $2,000, third place $1,000.

Sources: [overview](https://backblaze-generative-media.devpost.com/) and [official rules](https://backblaze-generative-media.devpost.com/rules).

## Core build requirement

The entry must be a generative-media application that uses both:

1. **Backblaze B2** for storage/data orchestration; and
2. **Genblaze** for the generative-media pipeline.

This app's intended live proof is one GMI Cloud or OpenAI image run orchestrated by Genblaze, persisted by Genblaze's content-addressed B2 sink, then read back from B2 and independently re-hashed.

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

## Actions intentionally not taken

No Devpost registration, rule acceptance, GitHub repository creation/star, cloud account creation, provider purchase, public deployment, video upload, or final submission was performed. Those are external identity/account actions reserved for the entrant.
