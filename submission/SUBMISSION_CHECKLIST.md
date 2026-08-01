# Submission checklist

Deadline from the official pages: **August 3, 2026 at 5:00 PM EDT**, equivalent to **23:00 CEST in Stockholm**. Submit early enough to recover from upload or form errors.

## A. Personal eligibility

- [ ] I read the current [official rules](https://backblaze-generative-media.devpost.com/rules).
- [ ] I am at least the age of majority where I live.
- [ ] My location, employment/organizer relationship, sanctions status, and other personal facts satisfy the rules.
- [ ] I can legally receive the prize and provide any required tax/eligibility documents.
- [ ] I own/control the entry and have rights to all submitted code, prompts, media, logos, fonts, voice, and music.

## B. Reproducible source

- [x] Entrant-owned GitHub repository exists: <https://github.com/gother111/backblaze-provenance-vault>.
- [x] Repository is public.
- [x] `.env`, credentials, local data, QA scratch files, and research clones are absent from the published commit.
- [x] `README.md` installs and verifies successfully from a clean clone at `f6d1d235f509ffd92e5c502724b1b45878339949`.
- [x] GitHub detects the repository's MIT license; listed third-party packages and integrations match the source.
- [ ] `make verify` passes on the exact final commit.
- [ ] Final commit hash is recorded: `________________`.

## C. Real B2 + Genblaze evidence

- [ ] `PROVENANCE_STORAGE_MODE=b2` on the public deployment.
- [ ] Header says `B2 CONNECTED`.
- [ ] Selected provider is a real Genblaze generative-media connector.
- [ ] Fresh live run succeeds from the public UI.
- [ ] Actual provider/model recorded: `________________` / `________________`.
- [ ] Run ID recorded: `________________`.
- [ ] B2 region recorded (no secret): `________________`.
- [ ] B2 object key recorded: `________________`.
- [ ] Asset SHA-256 recorded: `________________`.
- [ ] Canonical manifest hash recorded: `________________`.
- [ ] Verification UTC timestamp recorded: `________________`.
- [ ] Object and manifest confirmed in B2.
- [ ] **Verify bytes** passes on the public deployment.
- [ ] No credential appears in UI, source, API response, log, screenshot, or video.

## D. Public app

- [ ] HTTPS app URL: `________________`.
- [ ] Anonymous clean-browser access works.
- [ ] `/api/health` returns 200.
- [ ] Persistent volume survives a service restart.
- [ ] Desktop 1440 × 1000 and mobile 390 × 844 pass without horizontal overflow.
- [ ] Generate, manifest, verify, asset, and library flows work.
- [ ] No uncaught browser errors.

## E. Demo video

- [ ] Real live B2/provider run shown.
- [ ] Duration is less than three minutes.
- [ ] Provider/model, B2-connected state, content-addressed key, manifest, and byte verification are legible.
- [ ] No secrets, private data, account identifiers, unrelated tabs, or local-only claims appear.
- [ ] Audio/visual rights are clear.
- [ ] Public anonymous playback works.
- [ ] Video URL: `________________`.

## F. Devpost copy

- [ ] All bracketed markers in `DEVPOST_DRAFT.md` resolved.
- [ ] Project description accurately explains both B2 and Genblaze.
- [ ] Provider/model list matches the actual live run.
- [ ] App, source, and video URLs are correct.
- [ ] Screenshots show the final live deployment.
- [ ] Claims distinguish confirmed facts from future work.
- [ ] No local rehearsal is presented as cloud/AI evidence.

## G. Final submit proof

- [ ] Re-open official overview/rules immediately before submission.
- [ ] Join/sign in and personally accept the current terms.
- [ ] Preview the final submission on desktop and mobile.
- [ ] Submit before Devpost's clock expires.
- [ ] Confirmation page captured and confirmation email retained.
- [ ] Final Devpost URL: `________________`.
- [ ] Submission confirmation time: `________________`.
