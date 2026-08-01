# Demo script: 2 minutes 40 seconds

Record only after the public B2/live-provider acceptance test passes. Keep the browser zoom at 100%, notifications off, credentials hidden, and the DevTools/network pane closed unless it adds necessary evidence.

## 0:00–0:15: problem

**Visual:** Full app, result and proof ledger visible.

**Voice:** “Generated media moves fast, but its prompt, model, parameters, and final bytes are usually separated the moment a file is downloaded. Provenance Vault lets a creative team generate a campaign asset and keep verifiable proof attached to the exact stored object.”

## 0:15–0:35: live configuration proof

**Visual:** Point to `B2 CONNECTED`, then the provider selector. Do not show environment variables or the cloud credential page.

**Voice:** “This public build is connected to a private Backblaze B2 bucket. Live generation is intentionally disabled unless B2 and a Genblaze provider are both configured, so a paid output can never bypass the storage and provenance path.”

## 0:35–1:10: create

**Visual:** Enter a short original prompt, choose landscape and moss, select the verified provider, click **Generate & seal**, wait for the real output.

Suggested prompt: “Editorial field notebook beside wild grasses at sunrise, calm natural texture, no people, no text, original composition.”

**Voice:** “I choose the format and provider, then generate and seal. Genblaze orchestrates the provider step, captures the run metadata, downloads the result, computes its digest, and sends the asset and canonical manifest through its Backblaze-compatible object-storage sink.”

## 1:10–1:35: B2 and Genblaze evidence

**Visual:** New asset, actual provider/model, storage key, asset hash, manifest hash.

**Voice:** “The result is stored under a content-addressed B2 key, so the asset's SHA-256 is part of its identity. This proof ledger exposes the provider, model, B2 key, asset digest, and canonical manifest hash instead of hiding them in logs.”

## 1:35–2:05: independent verification

**Visual:** Click **Verify bytes** and show both checks passing.

**Voice:** “A valid manifest is only half the integrity story. Provenance Vault reads the actual object back from B2 and hashes those bytes again. The manifest check proves the record is canonical; the byte check proves today's stored object still matches it.”

## 2:05–2:25: manifest

**Visual:** Open the manifest. Briefly highlight provider, model, prompt/parameters, timestamp, output SHA-256, and canonical hash. Close it.

**Voice:** “The canonical Genblaze manifest remains inspectable, including provider, model, prompt, parameters, timestamps, output digest, and canonical hash.”

## 2:25–2:40: close

**Visual:** Scroll to the immutable run library, then return to the hero/proof view.

**Voice:** “Provenance Vault turns B2 and Genblaze into a practical chain of custody for creative work: generate media, keep the proof, and verify the bytes whenever they change hands.”

## Recording checklist

- finish at 2:40 or shorter; hard requirement is under three minutes;
- use a genuinely live run, not pre-recorded loading or the local procedural asset;
- show the provider/model and B2-connected state legibly;
- do not reveal credentials, email, account IDs, local paths, unrelated tabs, or private prompts;
- use only original or licensed visuals/audio; silence is safer than unlicensed music;
- export at 1080p with readable UI text;
- upload to a supported public host and test the link in a private browser window;
- place the public URL in Devpost and the final checklist.
