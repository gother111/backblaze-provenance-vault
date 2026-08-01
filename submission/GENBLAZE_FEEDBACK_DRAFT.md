# Genblaze feedback draft: do not post without entrant approval

## Suggested issue title

Clarify manifest integrity versus remote object byte integrity in the B2 quick start

## Suggested body

### Context

While building a creator-facing provenance app, I initially treated `manifest.verify()` as an end-to-end confirmation that the current B2 object still matched the run. After reading the implementation and testing a tampered local object, I found an important distinction: manifest verification validates the canonical manifest and declared asset digest, while verifying today's stored object requires fetching its bytes and hashing them again.

### Why this matters

Both behaviors are reasonable, but provenance-focused users can easily read “verify” as a remote-byte check. In my test, the original manifest remained valid after the stored asset was altered, while an independent SHA-256 comparison correctly failed. Making that boundary explicit would help users build stronger B2 integrity workflows and avoid overclaiming what was verified.

### Suggested documentation change

Add a short “end-to-end stored-byte verification” section beside the B2 `ObjectStorageSink` quick start:

```python
manifest_ok = result.manifest.verify()
key = backend.key_from_url(result.run.steps[-1].assets[0].url)
stored = backend.get(key)
bytes_ok = hashlib.sha256(stored).hexdigest() == asset.sha256
```

The docs could label these as two independent signals:

- **manifest integrity:** canonical record and declared digests are unchanged;
- **object integrity:** bytes currently returned by storage match the declared asset digest.

### Optional API idea

A helper such as `verify_asset_bytes(asset, backend)` could standardize URL-to-key mapping, bounded downloads/streaming, digest comparison, and error reporting across B2-backed apps.

Thanks for making the run/manifest/sink layers composable. The content-addressable B2 path was straightforward once this verification boundary was understood.
