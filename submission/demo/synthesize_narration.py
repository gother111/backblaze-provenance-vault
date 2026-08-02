#!/usr/bin/env python3
"""Synthesize deterministic, offline Kokoro narration from an explicit model directory.

This helper deliberately has no default model location. Callers must supply a
directory containing the pinned Kokoro weights, config, and voice tensor. The
script forces Hugging Face and Transformers offline mode before importing the
runtime, and records hashes for every source and generated WAV.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any


SAMPLE_RATE = 24_000
MODEL_FILE = "kokoro-v1_0.pth"
CONFIG_FILE = "config.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--voice", default="af_heart")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--model-revision", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    script_path = args.script.resolve()
    model_dir = args.model_dir.resolve()
    output_dir = args.output_dir.resolve()

    config_path = model_dir / CONFIG_FILE
    model_path = model_dir / MODEL_FILE
    voice_path = model_dir / "voices" / f"{args.voice}.pt"
    for path in (script_path, config_path, model_path, voice_path):
        if not path.is_file():
            raise SystemExit(f"Required input is missing: {path}")

    if not 0.5 <= args.speed <= 2.0:
        raise SystemExit("--speed must be between 0.5 and 2.0")

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

    import numpy as np
    import soundfile as sf
    import torch
    from kokoro import KModel, KPipeline

    torch.manual_seed(args.seed)
    torch.set_num_threads(1)

    payload: dict[str, Any] = json.loads(script_path.read_text(encoding="utf-8"))
    scenes = payload.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise SystemExit("Narration script must contain a non-empty scenes array")

    output_dir.mkdir(parents=True, exist_ok=True)
    model = KModel(config=str(config_path), model=str(model_path))
    pipeline = KPipeline(
        lang_code="a",
        repo_id="hexgrad/Kokoro-82M",
        model=model,
        device="cpu",
    )

    rendered: list[dict[str, Any]] = []
    silence = np.zeros(round(SAMPLE_RATE * 0.12), dtype=np.float32)
    for scene in scenes:
        scene_id = str(scene["id"])
        narration = str(scene["narration"]).strip()
        if not narration:
            raise SystemExit(f"Narration is empty for {scene_id}")

        torch.manual_seed(args.seed)
        results = list(
            pipeline(
                narration,
                voice=str(voice_path),
                speed=args.speed,
                split_pattern=r"\n+",
            )
        )
        if not results:
            raise SystemExit(f"Kokoro produced no audio for {scene_id}")

        chunks = [result.audio.detach().cpu().numpy().astype(np.float32) for result in results]
        audio_parts: list[np.ndarray] = []
        for index, chunk in enumerate(chunks):
            if index:
                audio_parts.append(silence)
            audio_parts.append(chunk)
        audio = np.concatenate(audio_parts)

        wav_path = output_dir / f"{scene_id}.wav"
        sf.write(wav_path, audio, SAMPLE_RATE, subtype="PCM_16")
        info = sf.info(wav_path)
        rendered.append(
            {
                "id": scene_id,
                "text": narration,
                "graphemes": [result.graphemes for result in results],
                "phonemes": [result.phonemes for result in results],
                "path": wav_path.name,
                "sample_rate": info.samplerate,
                "frames": info.frames,
                "duration_seconds": round(info.duration, 6),
                "sha256": sha256(wav_path),
            }
        )

    runtime = {
        "python": sys.version.split()[0],
        "python_executable_sha256": sha256(Path(sys.executable)),
        "platform": platform.platform(),
        "kokoro": package_version("kokoro"),
        "torch": package_version("torch"),
        "soundfile": package_version("soundfile"),
        "transformers": package_version("transformers"),
        "misaki": package_version("misaki"),
    }
    runtime["inventory_sha256"] = sha256_text(json.dumps(runtime, sort_keys=True, separators=(",", ":")))

    manifest = {
        "status": "GENERATED_LOCALLY_OFFLINE",
        "script": {"path": script_path.name, "sha256": sha256(script_path)},
        "model": {
            "repository": "hexgrad/Kokoro-82M",
            "revision": args.model_revision,
            "config": {"name": config_path.name, "sha256": sha256(config_path)},
            "weights": {"name": model_path.name, "sha256": sha256(model_path)},
            "voice": {"name": args.voice, "file": voice_path.name, "sha256": sha256(voice_path)},
            "speed": args.speed,
            "seed": args.seed,
            "device": "cpu",
        },
        "runtime": runtime,
        "network": "disabled through HF_HUB_OFFLINE and TRANSFORMERS_OFFLINE",
        "rights_note": (
            "Kokoro-82M weights are identified as Apache-2.0 by the official model card, which "
            "also describes permissive/non-copyrighted training data. Residual caveat: the "
            "official materials reviewed do not provide an explicit output-ownership clause or "
            "voice-by-voice provenance for af_heart. This manifest records that uncertainty and "
            "does not offer a legal conclusion."
        ),
        "cues": rendered,
    }
    manifest_path = output_dir / "narration-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
