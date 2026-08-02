# Exact blockers to a compliant submission

The public repository, local rehearsal, and Genblaze repository star are recorded. The exact final
source receipt must still be reconciled against `origin/main` before deployment or submission. The
remaining steps require the entrant's external accounts, identity, credentials, terms review,
possible money/credits, or authenticated action and were intentionally not performed.

## Hard blockers

1. **Backblaze B2 access**
   - create or select a dedicated private bucket;
   - create a bucket-scoped application key with required read/write/list access;
   - provide bucket, region, key ID, and application key through server-side secrets;
   - complete and record one real upload plus read-back verification.

2. **One live Genblaze media provider**
   - preferred candidate no-spend route: create/authorize an NVIDIA NIM account, review and accept
     its current terms, verify the current offer/model access in the provider console, and provide
     an authorized API key; the app is prepared for `black-forest-labs/flux.1-schnell`, but free
     access and compatibility are not yet confirmed;
   - alternatives: provide a GMI Cloud API key and sufficient generation credit, or an OpenAI API key and credit;
   - confirm the exact available model slug;
   - complete one real Genblaze generation and verify its provider/model/output.

3. **Public deployment**
   - choose/authorize a hosting account;
   - for Vercel, create/link the project, select the **Services** Framework Preset, and deploy the
     included Vite `/` plus FastAPI `/api` services; or deploy the included Docker service with
     HTTPS and its explicit persistent volume;
   - add server-side secrets;
   - pass every check in `docs/DEPLOYMENT.md` from a private browser window.

4. **Public demo video**
   - a validated 2:44 local-rehearsal master exists, but it explicitly shows no live B2/provider
     run and is not public submission evidence; see `submission/LOCAL_REHEARSAL_VIDEO.md`;
   - record a real B2/live-provider run using `submission/DEMO_SCRIPT.md`;
   - export under three minutes;
   - upload publicly to a supported host and verify anonymous playback.

5. **Devpost identity and submission**
   - the authenticated account can register but was still unregistered at the read-only check on 2026-08-02;
   - join the hackathon only after the entrant supplies the required account email and explicit agreements;
   - personally verify age, residency, sanctions/location, organizer/employment, tax, and prize eligibility;
   - accept official rules and required platform terms;
   - complete all fields, provider/model disclosure, URLs, media, and submit before the deadline;
   - retain the Devpost confirmation page/email as proof.

## Not blockers, but required truth checks

- Replace every `[VERIFY]`, `[REQUIRED]`, and `[REMOVE IF UNUSED]` marker in `DEVPOST_DRAFT.md`.
- Use the exact live provider/model, B2 region, run ID, object key, hashes, and timestamp.
- Confirm every demo prompt and asset is original or licensed and contains no third-party trademark/likeness risk.
- Run `make verify` on the final commit and the live acceptance test after deployment.
- Ensure the final source was created during the eligible submission window or otherwise meets the rules' substantial-new-work condition.

## Completed organizer request

The entrant account starred the Genblaze repository on 2026-08-01. This is recorded as an optional organizer request, not as a substitute for any formal rule requirement.

## Development-only limitation

The image-generation tool used for a UI concept pass failed twice because its upstream service was unreachable. The interface was implemented and browser-verified manually. The current NVIDIA selector delta now passes API, static-render, type, build, desktop Chrome at 1440 × 1000, and responsive Chrome at 390 × 844 and 320 × 740. The narrow pass found and fixed a page-level overflow caused by the body's hard 320 px minimum. This remains local-only evidence and does not establish NVIDIA access, live-provider behavior, B2 behavior, physical-device behavior, or public-deployment behavior.

The Docker 28.3.2 client and server are available locally. On 2026-08-02,
`docker build -t provenance-vault .` completed successfully, and a temporary local-mode container
returned HTTP 200 for `/api/health` and `/`. This is local image/runtime evidence only; it does not
establish B2/provider behavior, HTTPS deployment, public access, or judging-period availability.
