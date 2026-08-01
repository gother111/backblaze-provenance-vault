# Visual QA record

Verified in Codex's built-in in-app browser on 2026-08-01 against the local production build served by FastAPI.

## Desktop: 1440 × 1000

- page, header, generator, asset preview, and integrity ledger render without overlap;
- primary **Generate & seal** action is visible in the first viewport;
- title, brief, format, palette, and provider each have one accessible control;
- no horizontal overflow;
- generated asset updates with the submitted title/brief;
- **Verify bytes** returns a passing manifest and byte check;
- **Open manifest** opens a readable modal containing the canonical Genblaze manifest;
- local/demo labels remain visible and do not imply B2 or paid-AI proof.

## Mobile: 390 × 844

- generator/result layout stacks in reading order;
- `document.scrollWidth` equals `document.clientWidth` (390 px);
- primary action stays inside the viewport width and is reachable by vertical scroll;
- header, title, brief, format, palette, and provider are legible and usable;
- no content is hidden behind fixed navigation.

## Workflow exercised

1. Set title to `Field notebook`.
2. Set brief to `An editorial field notebook beside wild grasses at sunrise, calm natural texture`.
3. Select landscape format and moss palette.
4. Generate and seal.
5. Confirm the new immutable run and Genblaze manifest/hash fields.
6. Verify stored bytes.
7. Open and inspect the canonical manifest.

## Remaining live QA

Repeat the same matrix on the final HTTPS deployment with B2 storage and the selected live provider. The local run cannot establish cloud/provider behavior.
