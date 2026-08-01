# Exact blockers to a compliant submission

The code and local rehearsal are ready. These remaining steps require the entrant's external accounts, identity, money/credits, or public authorization and were intentionally not performed.

## Hard blockers

1. **Backblaze B2 access**
   - create or select a dedicated private bucket;
   - create a bucket-scoped application key with required read/write/list access;
   - provide bucket, region, key ID, and application key through server-side secrets;
   - complete and record one real upload plus read-back verification.

2. **One live Genblaze media provider**
   - provide a GMI Cloud API key and sufficient generation credit, or an OpenAI API key and credit;
   - confirm the exact available model slug;
   - complete one real Genblaze generation and verify its provider/model/output.

3. **Public deployment**
   - choose/authorize a hosting account;
   - deploy the included Docker service with HTTPS and a persistent volume;
   - add server-side secrets;
   - pass every check in `docs/DEPLOYMENT.md` from a private browser window.

4. **GitHub repository**
   - create the entrant-owned repository and push this project;
   - decide public vs private;
   - if private, grant the organizer account specified on Devpost access;
   - confirm README setup works from a clean clone.

5. **Public demo video**
   - record a real B2/live-provider run using `submission/DEMO_SCRIPT.md`;
   - export under three minutes;
   - upload publicly to a supported host and verify anonymous playback.

6. **Devpost identity and submission**
   - sign in/join the hackathon;
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

## Optional organizer request

The hackathon materials encourage engagement with the Genblaze repository. Starring a repository is an external account action and was not performed. It is not treated here as a substitute for any formal rule requirement.

## Development-only limitation

The image-generation tool used for a UI concept pass failed twice because its upstream service was unreachable. The interface was implemented and browser-verified manually. This is not a runtime or submission blocker.

The Docker 28.3.2 client is installed locally, but its daemon was not running, so the Dockerfile could not be image-built in this environment. The native production frontend/API path was built and served successfully; the final operator should run `docker build -t provenance-vault .` as part of the deployment gate.
