# Visual direction

## Concept

The interface treats provenance like an archival proof sheet rather than a generic cloud dashboard. The visual hierarchy pairs an editorial creation surface with a compact evidence ledger.

- **Mood:** tactile paper, studio archive, restrained technical trust
- **Primary ink:** forest `#173229`
- **Paper:** warm off-white `#f1ede3`
- **Action/seal:** vermilion `#b74f37`
- **Supporting palette:** moss, clay, charcoal
- **Typography:** high-contrast serif headings with neutral sans-serif utility text
- **Geometry:** ruled divisions, open planes, almost no floating rounded cards
- **Motion:** limited to busy/verification feedback and smooth in-page navigation

## Desktop composition

- fixed-height utility header with wordmark, three in-page actions, and storage status;
- narrow left generator rail;
- large media proof area on the right;
- metadata immediately under the asset;
- integrity inspector as a ledger, not a badge detached from evidence;
- immutable run library below the main work surface.

At 1440 × 1000, the primary generation action remains visible without scrolling. At shorter heights, spacing compresses while the information hierarchy stays intact.

## Mobile composition

At 390 px wide, the header compacts, generator and result columns stack, controls remain at least touch-sized, and the document has no horizontal overflow. The generation action is reachable after a short vertical scroll; provenance evidence follows the asset in reading order.

## Truthful state language

- local: `LOCAL DEMO`, `OFFLINE REHEARSAL`, “without claiming a cloud upload”;
- live: `B2 CONNECTED`, actual provider/model, B2 storage key;
- verification: separate manifest and byte results;
- errors: inline, plain-language, and never silently converted into success.

## Design-process limitation

The required image-generation concept pass was attempted twice through the configured image-generation tool. Both attempts failed because its upstream service was unreachable. No API-key CLI fallback was used because that requires separate user approval. The shipped visual direction was therefore composed directly from the product requirements and verified in the browser. This affects only concept-generation evidence, not the app runtime.
