# Local rehearsal judge video

## Current state

The local judge walkthrough is **rendered and validated locally**. It is not uploaded, public,
entered on Devpost, or evidence of a live Backblaze B2/provider run.

| Field | Confirmed value |
| --- | --- |
| Local master | `.submission-private/video/provenance-vault-local-rehearsal-1080p.mp4` |
| Render manifest | `.submission-private/video/provenance-vault-local-rehearsal-1080p.manifest.json` |
| Status | `RENDERED_LOCAL_REHEARSAL_NOT_UPLOADED_NOT_SUBMITTED` |
| Duration | 164.936 seconds (2:44.936) |
| Video | H.264 High, 1920 x 1080, 30 fps, `yuv420p`, 4,947 decoded frames |
| Audio | AAC, 48 kHz mono, no music |
| Subtitles | English text burned into every scene plus 8-cue English `mov_text` track |
| File size | 15,419,477 bytes |
| Master SHA-256 | `8bc7376fb9823383000a03bd4e2bf8990cb9987dbd48f59aaadbf50a31865caa` |
| Render-manifest SHA-256 | `578397b5ec52bbccce376d432145b6004d044dc038ec4809eccdc36feca139f6` |

The master and build derivatives are intentionally under `.submission-private/`, which Git
ignores. The source helpers and narration are under `submission/demo/` and are suitable for
review before any later commit.

## Truth boundary

The first scene, final scene, burned captions, embedded captions, MP4 comment metadata, and
render manifest all say that no live B2 upload or live generative-media provider run is shown.
The video demonstrates only:

- the verified local user experience from the existing rehearsal screenshot;
- real local Genblaze pipeline and canonical-manifest behavior;
- content-addressed local persistence and independent byte re-hashing;
- the tamper-test distinction between manifest integrity and stored-byte integrity;
- locally passing source checks, including network-free B2/provider fakes.

The verification slide also says `LOCAL DIRTY WORKING TREE` and states that its 21 Python and 4
frontend test counts are not attributed to public baseline commit
`e7338e6a1c599799b345b98aeda910594f92757f`.

## Reproducible build

The render helper requires explicit runtime and model paths. It does not guess a model location,
call a TTS API, use a macOS system voice, deploy, upload, or change an external account.

```bash
BACKBLAZE_REPO='/path/to/backblaze-provenance-vault'
AAIFF_RUNTIME='/path/to/astana-a-future-that-waits/production'

cd "$BACKBLAZE_REPO"
uv run --offline submission/demo/render_local_demo.py \
  --script submission/demo/local-rehearsal-narration.json \
  --screenshot submission/assets/provenance-vault-desktop.png \
  --tts-python "$AAIFF_RUNTIME/.venv-tts/bin/python" \
  --model-dir "$AAIFF_RUNTIME/assets/models/kokoro-82m" \
  --model-revision f3ff3571791e39611d31c381e3a41a3af07b4987 \
  --build-dir .submission-private/demo-build \
  --output .submission-private/video/provenance-vault-local-rehearsal-1080p.mp4 \
  --verify-log .submission-private/demo-build/verification-summary.txt
```

`uv run --offline` succeeds in the current environment because Pillow 12.3.0 is cached. A fresh
machine must make the declared Pillow wheel available before using offline mode. FFmpeg 8.1.1
performs the H.264/AAC render. System Arial fonts are rasterized into the slides; no font file is
copied or distributed.

## Source and narration provenance

| Source | SHA-256 |
| --- | --- |
| Narration JSON | `94dcf2031004e109e369b5b74211bb9217a1be58b9f8ef2df0aa6d5ee2fe787b` |
| Existing desktop screenshot | `84fce386ee1cbf6a50bae30374d3db70c647d9a0b4b0ce818fbca4b6c97f5d28` |
| Render helper | `f28b66268fdd2193a4ded57d9a51ff16ada3447977d7b649fda7cd145b013897` |
| Offline TTS helper | `ff911ab3757262ebea45a97c41cb0f2e8b6c01ba17e17c4a99853b5b790a639b` |
| Local verification summary | `d3e79c27a01605e956cd6955e2a4221d97f9f8635db454c4184f97c9ea439e13` |

Narration uses [hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M), pinned at revision
`f3ff3571791e39611d31c381e3a41a3af07b4987`, through local CPU inference with seed 0 and voice
`af_heart` at speed 1.0.

| Kokoro asset | SHA-256 |
| --- | --- |
| `config.json` | `5abb01e2403b072bf03d04fde160443e209d7a0dad49a423be15196b9b43c17f` |
| `kokoro-v1_0.pth` | `496dba118d1a58f5f3db2efc88dbdc216e0483fc89fe6e47ee1f2c53f18ad1e4` |
| `af_heart.pt` | `0ab5709b8ffab19bfd849cd11d98f75b60af7733253ad0d67b12382a102cb4ff` |

Recorded TTS runtime: Python 3.12.13, Kokoro 0.9.4, Torch 2.13.0, SoundFile 0.13.1,
Transformers 5.14.1, and Misaki 0.9.4. The TTS Python executable SHA-256 is
`eb9d74b9c7cfdfb2c9b91614edb2c3607360ba46c5aa7fc4557b3a4a23e97cff`; the canonical
runtime-inventory SHA-256 is
`87ac5115e7ecfa90e19c58b5aeefc01feb39092ae8d1fc7c1d4ee4a15cd14683`.
`HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` are set before runtime import. A repeated CPU
synthesis test sentence produced byte-identical WAVs.

Recorded render runtime: Python 3.12.7, Pillow 12.3.0, FFmpeg binary SHA-256
`00d01197255300c02122c783dd0126a9e7f47d6c6a19faafae2e6610efd071d3`, FFprobe binary
SHA-256 `daba6e06838d10260602536a676069cef6d756345e1c6d66268ceb7f2d5e7c39`, and canonical
runtime-inventory SHA-256
`20d0279af8287ee93fbf1bf3e6e04f5897de65b3c5e4f4d9525fb859788ab4fe`.

The official model card identifies the weights as Apache-2.0 and describes the training data as
permissive or non-copyrighted. Residual caveat: the reviewed official materials do not state an
explicit output-ownership clause or voice-by-voice provenance for `af_heart`. The render manifest
records that uncertainty and does not make a legal conclusion.

Codex drafted the narration and created the deterministic slide, subtitle, TTS, and FFmpeg
tooling. That assistance should remain disclosed anywhere the final entry asks for AI tools or
media provenance.

## Validation and review evidence

- recorded render-time `make verify`: passed on the dirty local working tree with 21 Python tests
  and 4 frontend tests;
- fresh final-hardening `make verify` on 2026-08-02: passed with 22 Python tests and 4 frontend
  tests; the already-rendered verification slide still truthfully shows its earlier 21-test receipt;
- full video and audio decode to the null sink: passed with no FFmpeg decode error;
- EBU R128: `-18.2 LUFS` integrated, `3.6 LU` range, `-1.5 dBFS` true peak;
- volume scan: `-18.7 dB` mean, `-1.5 dB` maximum;
- subtitle extraction: 8 English cues found;
- contact sheet: `.submission-private/demo-build/review/contact-sheet.png`, SHA-256
  `a15fdede51df783edbd5cfe22f0ddc525d3bf3c52967a3354290569d057d3fc2`;
- manual review: all eight scene designs are visible; headings and burned captions stay inside
  frame; local and pending lanes remain visually distinct; no secret, email, account ID, local
  model path, or credential is visible in the video.

## Asset state ledger

| Asset | State |
| --- | --- |
| Existing rehearsal screenshot | `SOURCE_CAPTURED`, `VALIDATED` |
| Narration script and disclosure copy | `BRIEFED`, `VALIDATED` |
| Eight Kokoro cue WAVs | `GENERATED`, `VALIDATED`, local only |
| Eight 1920 x 1080 slides | `DERIVED`, `VALIDATED`, local only |
| Captioned MP4 master | `BUILT_OR_RENDERED`, `VALIDATED`, local only |
| Public video URL | `BLOCKED`, not uploaded |
| Competition demo evidence | `BLOCKED`, requires one real B2/provider run |
| Devpost submission | `BLOCKED`, not submitted |

## Remaining blockers

This master is useful for judge review and as a deterministic fallback edit, but it cannot replace
the live demo required by the current submission plan. The remaining gates are the same ones shown
in the film: authorized provider credentials, one real Genblaze generation, B2 write and readback,
public deployment, a public anonymous video host, entrant review and rule acceptance, and a final
Devpost receipt.
