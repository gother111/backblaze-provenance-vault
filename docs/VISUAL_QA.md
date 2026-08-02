# Visual QA record

Verified on 2026-08-02 against the current local production build served by FastAPI with an
isolated temporary data directory, local storage mode, the local provider, and all B2 and live
provider credential variables explicitly empty. The in-app browser supplied DOM inspection, but
its desktop screenshot cropped at the device scale, so visual proof used the approved Chrome
fallback. No account, credential, B2 object, live provider, deployment, or external submission was
used.

The current NVIDIA NIM provider option is included in this record. `/api/config`
reported NVIDIA unavailable, and the provider control rendered exactly one disabled
`NVIDIA NIM — not configured` option alongside the other unavailable live providers. Local demo
remained selected. This proves the logged-out local selector state only, not NVIDIA account access,
API compatibility, generation, quota, or a public deployment.

## Desktop: 1440 × 1000

- page, header, generator, asset preview, and integrity ledger render without overlap;
- primary **Generate & seal** action is visible in the first viewport;
- title, brief, format, palette, and provider each have one accessible control;
- no horizontal overflow;
- generated asset updates with the submitted title/brief;
- **Verify bytes** returns a passing manifest and byte check;
- **Open manifest** opens a readable modal containing the canonical Genblaze manifest;
- local/demo labels remain visible and do not imply B2 or live-AI proof.
- `document.scrollWidth` equals `document.documentElement.clientWidth` at 1425 CSS px after the
  vertical scrollbar is accounted for;
- browser error/warning log is empty.

## Mobile: 390 × 844

- generator/result layout stacks in reading order;
- `document.scrollWidth` equals `document.clientWidth` (390 px);
- primary action stays inside the viewport width and is reachable by vertical scroll;
- header, title, brief, format, palette, and provider are legible and usable;
- no content is hidden behind fixed navigation.
- the current provider control includes the disabled NVIDIA option with no clipped text;
- the canonical-manifest modal fits the viewport and its inner JSON pane scrolls independently.

## Narrow mobile: 320 × 740

The first pass exposed a real 15 px page-level horizontal overflow. `body { min-width: 320px; }`
competed with the vertical scrollbar at the exact narrow breakpoint. The scoped correction changes
the body minimum to `0`; after rebuilding, document, body, and client widths match and the header,
form controls, provider selector, proof fields, actions, run rows, and footer remain contained.

## Workflow exercised

1. Set title to `Field notebook`.
2. Set brief to `An editorial field notebook beside wild grasses at sunrise, calm natural texture`.
3. Select landscape format and moss palette.
4. Generate and seal.
5. Confirm the new immutable run and Genblaze manifest/hash fields.
6. Verify stored bytes.
7. Open and inspect the canonical manifest.

The exercised run remained local and used `provenance-vault-local` / `procedural-editorial-v1`.
The temporary run is not competition evidence and was never represented as a B2 or NVIDIA result.

## Evidence

- `submission/assets/provenance-vault-nvidia-desktop-qa.jpg`
- `submission/assets/provenance-vault-nvidia-mobile-390-qa.jpg`
- `submission/assets/provenance-vault-nvidia-mobile-manifest-qa.jpg`
- `submission/assets/provenance-vault-nvidia-mobile-320-before.jpg`
- `submission/assets/provenance-vault-nvidia-mobile-320-fixed.jpg`

`make verify` passes after the responsive correction and deployment-dependency guard: Ruff, TypeScript, 22 Python tests, four
frontend tests, and the production build. Chrome exposed no application error or warning. Runtime
request inspection was unavailable; the bounded local server log showed only the local page,
bundled assets, `/api/config`, `/api/runs`, the local asset, the local verification endpoint, and
the local manifest route. This is not proof of a final public deployment's network behavior.

## Remaining live QA

Repeat the full matrix on the final HTTPS deployment with B2 storage and the selected live
provider. The local run cannot establish cloud/provider behavior, anonymous public access,
serverless persistence, B2 permissions, live-provider output, or the judging-period availability
window.
