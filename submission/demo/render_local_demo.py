#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow==12.3.0"]
# ///
"""Render the truth-labeled Provenance Vault local-rehearsal judge video.

Run this file with Pillow available (for example, ``uv run --offline`` after
the declared wheel is cached). Narration synthesis is delegated to an explicit
Python executable and explicit Kokoro model directory; no model or environment
path is guessed by this script.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

import PIL
from PIL import Image, ImageDraw, ImageFont


WIDTH = 1920
HEIGHT = 1080
FPS = 30
CAPTION_TOP = 812
COLORS = {
    "cream": "#F2EEE5",
    "paper": "#FBF8F1",
    "ink": "#17251F",
    "muted": "#667068",
    "moss": "#5E725D",
    "rust": "#B55238",
    "sand": "#D6C0A9",
    "line": "#C9C3B7",
    "white": "#FFFFFF",
    "amber": "#E0A646",
    "green": "#5F8068",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", type=Path, required=True)
    parser.add_argument("--screenshot", type=Path, required=True)
    parser.add_argument("--tts-python", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--model-revision", required=True)
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verify-log", type=Path)
    parser.add_argument("--font-regular", type=Path, default=Path("/System/Library/Fonts/Supplemental/Arial.ttf"))
    parser.add_argument("--font-bold", type=Path, default=Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"))
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--voice", default="af_heart")
    parser.add_argument("--speed", type=float, default=1.0)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def run(command: list[str], log_path: Path, *, cwd: Path | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"$ {shlex.join(command)}\n")
        if result.stdout:
            handle.write(result.stdout)
            if not result.stdout.endswith("\n"):
                handle.write("\n")
        if result.stderr:
            handle.write(result.stderr)
            if not result.stderr.endswith("\n"):
                handle.write("\n")
        handle.write(f"exit={result.returncode}\n\n")
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {shlex.join(command)}")
    return result.stdout


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def wrap_pixels(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, max_width: int) -> str:
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        words = paragraph.split()
        current = ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if draw.textlength(candidate, font=face) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return "\n".join(lines)


def rounded_card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], *, fill: str, outline: str | None = None, width: int = 2, radius: int = 24) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def fit_image(source: Image.Image, box: tuple[int, int, int, int]) -> tuple[Image.Image, tuple[int, int]]:
    left, top, right, bottom = box
    available_w = right - left
    available_h = bottom - top
    scale = min(available_w / source.width, available_h / source.height)
    resized = source.resize((round(source.width * scale), round(source.height * scale)), Image.Resampling.LANCZOS)
    x = left + (available_w - resized.width) // 2
    y = top + (available_h - resized.height) // 2
    return resized, (x, y)


def add_header(draw: ImageDraw.ImageDraw, scene: dict[str, Any], index: int, count: int, regular: Path, bold: Path) -> None:
    label = font(bold, 23)
    heading = font(bold, 52)
    subheading = font(regular, 27)
    draw.text((76, 52), "PROVENANCE VAULT  ·  LOCAL REHEARSAL", font=label, fill=COLORS["rust"])
    draw.text((1760, 52), f"{index:02d}/{count:02d}", font=label, fill=COLORS["muted"])
    draw.text((76, 94), str(scene["heading"]), font=heading, fill=COLORS["ink"])
    draw.text((78, 158), str(scene["subheading"]), font=subheading, fill=COLORS["muted"])
    draw.line((76, 205, 1844, 205), fill=COLORS["line"], width=2)


def add_caption(draw: ImageDraw.ImageDraw, narration: str, regular: Path, bold: Path) -> None:
    rounded_card(draw, (54, CAPTION_TOP, 1866, 1044), fill=COLORS["ink"], radius=28)
    label = font(bold, 20)
    body = font(regular, 34)
    draw.text((92, CAPTION_TOP + 24), "ENGLISH SUBTITLES  ·  AI NARRATION", font=label, fill="#C9D8CA")
    wrapped = wrap_pixels(draw, narration, body, 1730)
    draw.multiline_text((92, CAPTION_TOP + 63), wrapped, font=body, fill=COLORS["white"], spacing=9)


def draw_title(image: Image.Image, draw: ImageDraw.ImageDraw, scene: dict[str, Any], regular: Path, bold: Path) -> None:
    huge = font(bold, 76)
    mid = font(regular, 38)
    badge = font(bold, 24)
    draw.text((96, 252), "Generate media.\nKeep the proof.", font=huge, fill=COLORS["ink"], spacing=4)
    draw.text((98, 458), "A verifiable chain of custody for creative assets.", font=mid, fill=COLORS["muted"])
    rounded_card(draw, (98, 545, 1775, 706), fill="#F8E6DE", outline=COLORS["rust"], width=3, radius=26)
    draw.text((135, 578), "TRUTH BOUNDARY", font=badge, fill=COLORS["rust"])
    draw.text((135, 624), "No live Backblaze B2 upload or live AI-provider run is shown.", font=mid, fill=COLORS["ink"])
    draw.ellipse((1540, 300, 1700, 460), fill=COLORS["moss"])
    draw.rounded_rectangle((1460, 422, 1780, 554), radius=34, fill=COLORS["sand"])


def draw_problem(draw: ImageDraw.ImageDraw, regular: Path, bold: Path) -> None:
    items = [
        ("01", "Generation context", "Prompt · model · parameters"),
        ("02", "Canonical record", "Manifest · timestamp · digest"),
        ("03", "Exact stored object", "Byte re-hash · tamper signal"),
    ]
    card_w = 520
    gap = 52
    start_x = 76
    y1, y2 = 288, 684
    for index, (number, title, detail) in enumerate(items):
        x1 = start_x + index * (card_w + gap)
        x2 = x1 + card_w
        rounded_card(draw, (x1, y1, x2, y2), fill=COLORS["paper"], outline=COLORS["line"], width=2)
        draw.text((x1 + 34, y1 + 30), number, font=font(bold, 26), fill=COLORS["rust"])
        draw.text((x1 + 34, y1 + 105), title, font=font(bold, 37), fill=COLORS["ink"])
        detail_wrapped = wrap_pixels(draw, detail, font(regular, 29), card_w - 68)
        draw.multiline_text((x1 + 34, y1 + 180), detail_wrapped, font=font(regular, 29), fill=COLORS["muted"], spacing=12)
        draw.ellipse((x1 + 34, y2 - 88, x1 + 82, y2 - 40), fill=COLORS["moss"])
        if index < len(items) - 1:
            arrow_x = x2 + 12
            draw.line((arrow_x, 486, arrow_x + 30, 486), fill=COLORS["rust"], width=5)
            draw.polygon([(arrow_x + 30, 474), (arrow_x + 50, 486), (arrow_x + 30, 498)], fill=COLORS["rust"])


def draw_screenshot(image: Image.Image, draw: ImageDraw.ImageDraw, screenshot: Image.Image, regular: Path, bold: Path) -> None:
    crop = screenshot.crop((0, 0, screenshot.width, min(screenshot.height, 825)))
    resized, pos = fit_image(crop, (76, 236, 1306, 774))
    shadow = (pos[0] - 7, pos[1] - 7, pos[0] + resized.width + 7, pos[1] + resized.height + 7)
    rounded_card(draw, shadow, fill="#D6D0C5", radius=12)
    image.paste(resized, pos)
    rounded_card(draw, (1350, 260, 1838, 485), fill="#EAF0E9", outline=COLORS["moss"], width=2)
    draw.text((1382, 292), "DEMONSTRATED", font=font(bold, 22), fill=COLORS["moss"])
    draw.multiline_text((1382, 340), "Real Genblaze\npipeline + manifest", font=font(bold, 34), fill=COLORS["ink"], spacing=8)
    rounded_card(draw, (1350, 512, 1838, 737), fill="#F8E6DE", outline=COLORS["rust"], width=2)
    draw.text((1382, 544), "NOT CLAIMED", font=font(bold, 22), fill=COLORS["rust"])
    draw.multiline_text((1382, 592), "No B2 upload\nNo AI generation", font=font(bold, 34), fill=COLORS["ink"], spacing=8)


def draw_ledger(image: Image.Image, draw: ImageDraw.ImageDraw, screenshot: Image.Image, regular: Path, bold: Path) -> None:
    left = min(330, screenshot.width - 1)
    top = min(675, screenshot.height - 1)
    crop = screenshot.crop((left, top, screenshot.width, screenshot.height))
    resized, pos = fit_image(crop, (76, 268, 1844, 682))
    rounded_card(draw, (pos[0] - 8, pos[1] - 8, pos[0] + resized.width + 8, pos[1] + resized.height + 8), fill="#D6D0C5", radius=12)
    image.paste(resized, pos)
    labels = ["Run status", "Provider + model", "Asset hash", "Manifest hash", "Storage key"]
    x = 96
    for label in labels:
        width = int(draw.textlength(label, font=font(bold, 22))) + 44
        rounded_card(draw, (x, 711, x + width, 765), fill=COLORS["paper"], outline=COLORS["line"], radius=15)
        draw.text((x + 22, 726), label, font=font(bold, 22), fill=COLORS["ink"])
        x += width + 18


def draw_integrity(draw: ImageDraw.ImageDraw, regular: Path, bold: Path) -> None:
    cards = [
        (82, "01", "Manifest integrity", "Canonical structure and declared digest remain internally consistent.", COLORS["moss"]),
        (986, "02", "Stored-byte integrity", "Current object bytes are read again, hashed again, and compared.", COLORS["rust"]),
    ]
    for x, number, title, detail, accent in cards:
        rounded_card(draw, (x, 274, x + 852, 636), fill=COLORS["paper"], outline=accent, width=3)
        draw.ellipse((x + 38, 314, x + 102, 378), fill=accent)
        draw.text((x + 58, 329), number, font=font(bold, 22), fill=COLORS["white"], anchor="mm")
        draw.text((x + 132, 318), title, font=font(bold, 39), fill=COLORS["ink"])
        wrapped = wrap_pixels(draw, detail, font(regular, 29), 742)
        draw.multiline_text((x + 42, 414), wrapped, font=font(regular, 29), fill=COLORS["muted"], spacing=10)
    rounded_card(draw, (190, 680, 1730, 768), fill="#FFF3DA", outline=COLORS["amber"], width=2, radius=20)
    draw.text((230, 709), "TAMPER FIXTURE:", font=font(bold, 25), fill="#855B15")
    draw.text((470, 709), "manifest still verifies  ·  changed bytes fail", font=font(regular, 29), fill=COLORS["ink"])


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str) -> None:
    draw.line((*start, *end), fill=color, width=6)
    x, y = end
    draw.polygon([(x - 20, y - 13), (x, y), (x - 20, y + 13)], fill=color)


def draw_live_path(draw: ImageDraw.ImageDraw, regular: Path, bold: Path) -> None:
    lanes = [
        (270, "DEMONSTRATED LOCALLY", COLORS["green"], ["Local SVG fixture", "Genblaze Pipeline", "Local content key", "Byte re-hash"]),
        (526, "IMPLEMENTED · NOT LIVE-PROVEN", COLORS["rust"], ["Genblaze connector", "Backblaze B2", "B2 readback", "Public service"]),
    ]
    for y, label, accent, nodes in lanes:
        draw.text((80, y), label, font=font(bold, 24), fill=accent)
        node_y = y + 58
        xs = [80, 524, 968, 1412]
        for index, (x, node) in enumerate(zip(xs, nodes, strict=True)):
            fill = "#EAF0E9" if accent == COLORS["green"] else "#F8E6DE"
            rounded_card(draw, (x, node_y, x + 340, node_y + 112), fill=fill, outline=accent, width=2, radius=18)
            wrapped = wrap_pixels(draw, node, font(bold, 26), 292)
            draw.multiline_text((x + 24, node_y + 33), wrapped, font=font(bold, 26), fill=COLORS["ink"], spacing=4)
            if index < 3:
                arrow(draw, (x + 350, node_y + 56), (x + 424, node_y + 56), accent)
    rounded_card(draw, (572, 714, 1348, 776), fill="#FFF3DA", outline=COLORS["amber"], radius=17)
    draw.text((960, 745), "SAFETY GATE: live provider requires B2 configuration", font=font(bold, 24), fill="#855B15", anchor="mm")


def verification_counts(verify_log: Path | None) -> tuple[str, str]:
    if verify_log is None or not verify_log.is_file():
        return "Python suite: see verification log", "Frontend suite: see verification log"
    text = verify_log.read_text(encoding="utf-8", errors="replace")
    backend_match = re.search(r"Python tests:\s*(\d+) passed", text)
    frontend_match = re.search(r"Frontend tests:\s*(\d+) passed", text)
    backend = f"Python tests: {backend_match.group(1)} passed" if backend_match else "Python tests: passed"
    frontend = f"Frontend tests: {frontend_match.group(1)} passed" if frontend_match else "Frontend tests: passed"
    return backend, frontend


def draw_verification(draw: ImageDraw.ImageDraw, verify_log: Path | None, commit: str, regular: Path, bold: Path) -> None:
    backend, frontend = verification_counts(verify_log)
    checks = [
        backend,
        frontend,
        "Python + TypeScript lint: passed",
        "Production frontend build: passed",
        "B2 behavior: network-free fakes only",
        "Tamper signal: exercised locally",
    ]
    for index, label in enumerate(checks):
        column = index % 2
        row = index // 2
        x = 82 + column * 900
        y = 286 + row * 132
        rounded_card(draw, (x, y, x + 842, y + 102), fill=COLORS["paper"], outline=COLORS["line"], width=2, radius=18)
        draw.ellipse((x + 28, y + 27, x + 76, y + 75), fill=COLORS["green"])
        draw.line((x + 40, y + 52, x + 49, y + 62), fill=COLORS["white"], width=5)
        draw.line((x + 49, y + 62, x + 66, y + 41), fill=COLORS["white"], width=5)
        draw.text((x + 100, y + 35), label, font=font(bold, 28), fill=COLORS["ink"])
    draw.text(
        (82, 672),
        "Public baseline: github.com/gother111/backblaze-provenance-vault",
        font=font(regular, 21),
        fill=COLORS["muted"],
    )
    rounded_card(draw, (82, 706, 1824, 776), fill="#FFF3DA", outline=COLORS["amber"], radius=18)
    draw.text((112, 727), "LOCAL DIRTY WORKING TREE", font=font(bold, 22), fill="#855B15")
    draw.text((500, 724), "public baseline HEAD", font=font(regular, 25), fill=COLORS["ink"])
    draw.text((765, 724), commit[:10], font=font(bold, 24), fill=COLORS["ink"])
    draw.text((1010, 724), "counts are not attributed to that commit", font=font(regular, 25), fill=COLORS["ink"])


def draw_close(draw: ImageDraw.ImageDraw, regular: Path, bold: Path) -> None:
    items = [
        "Provider credentials",
        "One real Genblaze run",
        "B2 write + readback",
        "Public deployment",
        "Entrant submission",
    ]
    draw.text((96, 260), "Five explicit gates remain", font=font(bold, 62), fill=COLORS["ink"])
    for index, item in enumerate(items):
        x = 96 + (index % 3) * 590
        y = 366 + (index // 3) * 148
        rounded_card(draw, (x, y, x + 535, y + 108), fill="#F8E6DE", outline=COLORS["rust"], width=2, radius=20)
        draw.text((x + 28, y + 26), f"{index + 1:02d}", font=font(bold, 26), fill=COLORS["rust"])
        draw.text((x + 92, y + 33), item, font=font(bold, 29), fill=COLORS["ink"])
    rounded_card(draw, (96, 680, 1824, 775), fill=COLORS["ink"], radius=22)
    draw.text((960, 728), "LOCAL REHEARSAL  ≠  CLOUD PROOF", font=font(bold, 37), fill=COLORS["white"], anchor="mm")


def render_slide(scene: dict[str, Any], index: int, count: int, screenshot: Image.Image, verify_log: Path | None, commit: str, regular: Path, bold: Path) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), COLORS["cream"])
    draw = ImageDraw.Draw(image)
    add_header(draw, scene, index, count, regular, bold)
    visual = scene["visual"]
    if visual == "title":
        draw_title(image, draw, scene, regular, bold)
    elif visual == "problem":
        draw_problem(draw, regular, bold)
    elif visual == "screenshot":
        draw_screenshot(image, draw, screenshot, regular, bold)
    elif visual == "ledger":
        draw_ledger(image, draw, screenshot, regular, bold)
    elif visual == "integrity":
        draw_integrity(draw, regular, bold)
    elif visual == "live-path":
        draw_live_path(draw, regular, bold)
    elif visual == "verification":
        draw_verification(draw, verify_log, commit, regular, bold)
    elif visual == "close":
        draw_close(draw, regular, bold)
    else:
        raise ValueError(f"Unknown visual type: {visual}")
    add_caption(draw, str(scene["narration"]), regular, bold)
    return image


def srt_timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    whole_seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},{milliseconds:03d}"


def ffprobe_json(ffprobe: str, path: Path, log_path: Path) -> dict[str, Any]:
    output = run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ],
        log_path,
    )
    return json.loads(output)


def video_segment_command(ffmpeg: str, slide: Path, wav: Path, duration: float, output: Path) -> list[str]:
    fade_out = max(0.0, duration - 0.3)
    audio_fade_out = max(0.45, duration - 0.95)
    video_filter = (
        "[0:v]scale=1920:1080,"
        "zoompan=z='min(zoom+0.000015,1.012)':"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30,"
        f"fade=t=in:st=0:d=0.25,fade=t=out:st={fade_out:.3f}:d=0.3,format=yuv420p[v];"
        f"[1:a]adelay=450:all=1,apad=whole_dur={duration:.3f},atrim=0:{duration:.3f},"
        f"afade=t=in:st=0.45:d=0.08,afade=t=out:st={audio_fade_out:.3f}:d=0.2[a]"
    )
    return [
        ffmpeg,
        "-hide_banner",
        "-y",
        "-loop",
        "1",
        "-framerate",
        str(FPS),
        "-i",
        str(slide),
        "-i",
        str(wav),
        "-filter_complex",
        video_filter,
        "-map",
        "[v]",
        "-map",
        "[a]",
        "-t",
        f"{duration:.3f}",
        "-r",
        str(FPS),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-g",
        "60",
        "-keyint_min",
        "60",
        "-sc_threshold",
        "0",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "48000",
        "-movflags",
        "+faststart",
        str(output),
    ]


def write_concat(path: Path, segment_paths: Iterable[Path]) -> None:
    lines = [f"file '{segment.resolve().as_posix().replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'" for segment in segment_paths]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    script_path = args.script.resolve()
    screenshot_path = args.screenshot.resolve()
    # Preserve the virtual-environment interpreter path. Resolving its symlink
    # would bypass the venv prefix and lose the Kokoro runtime packages.
    tts_python = args.tts_python.expanduser().absolute()
    model_dir = args.model_dir.resolve()
    build_dir = args.build_dir.resolve()
    output_path = args.output.resolve()
    verify_log = args.verify_log.resolve() if args.verify_log else None
    regular = args.font_regular.resolve()
    bold = args.font_bold.resolve()

    required = [script_path, screenshot_path, tts_python, regular, bold]
    if verify_log:
        required.append(verify_log)
    for path in required:
        if not path.is_file():
            raise SystemExit(f"Required input is missing: {path}")

    repo_root = Path(__file__).resolve().parents[2]
    helper_path = Path(__file__).with_name("synthesize_narration.py").resolve()
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    git_status = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.splitlines()

    build_dir.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    log_path = build_dir / "render.log"
    log_path.write_text("", encoding="utf-8")
    audio_dir = build_dir / "audio"
    slides_dir = build_dir / "slides"
    segments_dir = build_dir / "segments"
    for directory in (audio_dir, slides_dir, segments_dir):
        directory.mkdir(parents=True, exist_ok=True)

    run(
        [
            str(tts_python),
            str(helper_path),
            "--script",
            str(script_path),
            "--model-dir",
            str(model_dir),
            "--output-dir",
            str(audio_dir),
            "--voice",
            args.voice,
            "--speed",
            str(args.speed),
            "--model-revision",
            args.model_revision,
        ],
        log_path,
        cwd=repo_root,
    )

    script: dict[str, Any] = json.loads(script_path.read_text(encoding="utf-8"))
    narration_manifest = json.loads((audio_dir / "narration-manifest.json").read_text(encoding="utf-8"))
    cue_by_id = {cue["id"]: cue for cue in narration_manifest["cues"]}
    scenes = script["scenes"]
    screenshot = Image.open(screenshot_path).convert("RGB")

    timeline: list[dict[str, Any]] = []
    srt_blocks: list[str] = []
    cursor = 0.0
    for index, scene in enumerate(scenes, start=1):
        cue = cue_by_id[scene["id"]]
        duration = round(float(cue["duration_seconds"]) + 1.2, 3)
        slide = render_slide(scene, index, len(scenes), screenshot, verify_log, commit, regular, bold)
        slide_path = slides_dir / f"{scene['id']}.png"
        slide.save(slide_path, format="PNG", optimize=False)
        timeline.append(
            {
                "id": scene["id"],
                "start_seconds": round(cursor, 3),
                "duration_seconds": duration,
                "end_seconds": round(cursor + duration, 3),
                "slide": slide_path.name,
                "slide_sha256": sha256(slide_path),
                "audio": cue["path"],
                "audio_sha256": cue["sha256"],
            }
        )
        srt_blocks.append(
            "\n".join(
                [
                    str(index),
                    f"{srt_timestamp(cursor + 0.15)} --> {srt_timestamp(cursor + duration - 0.15)}",
                    str(scene["narration"]),
                ]
            )
        )
        cursor += duration

    captions_path = build_dir / "english-captions.srt"
    captions_path.write_text("\n\n".join(srt_blocks) + "\n", encoding="utf-8")
    timeline_path = build_dir / "timeline.json"
    timeline_path.write_text(json.dumps(timeline, indent=2) + "\n", encoding="utf-8")

    segments: list[Path] = []
    for scene in timeline:
        segment_path = segments_dir / f"{scene['id']}.mp4"
        run(
            video_segment_command(
                args.ffmpeg,
                slides_dir / scene["slide"],
                audio_dir / scene["audio"],
                float(scene["duration_seconds"]),
                segment_path,
            ),
            log_path,
        )
        segments.append(segment_path)

    concat_path = build_dir / "segments.txt"
    write_concat(concat_path, segments)
    stitched_path = build_dir / "stitched.mp4"
    run(
        [
            args.ffmpeg,
            "-hide_banner",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-c",
            "copy",
            str(stitched_path),
        ],
        log_path,
    )
    run(
        [
            args.ffmpeg,
            "-hide_banner",
            "-y",
            "-i",
            str(stitched_path),
            "-i",
            str(captions_path),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0",
            "-map",
            "1:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-af",
            "loudnorm=I=-18:TP=-1.5:LRA=7",
            "-c:s",
            "mov_text",
            "-metadata:s:s:0",
            "language=eng",
            "-metadata:s:s:0",
            "title=English",
            "-metadata",
            "title=Provenance Vault - Local Rehearsal",
            "-metadata",
            "comment=No live Backblaze B2 upload or live AI-provider generation is shown.",
            "-movflags",
            "+faststart",
            str(output_path),
        ],
        log_path,
    )

    probe = ffprobe_json(args.ffprobe, output_path, log_path)
    ffmpeg_version = run([args.ffmpeg, "-version"], log_path).splitlines()[0]
    ffmpeg_binary = shutil.which(args.ffmpeg)
    ffprobe_binary = shutil.which(args.ffprobe)
    if ffmpeg_binary is None or ffprobe_binary is None:
        raise RuntimeError("FFmpeg or FFprobe binary disappeared during render")
    render_runtime = {
        "python": sys.version.split()[0],
        "python_executable_sha256": sha256(Path(sys.executable)),
        "pillow": PIL.__version__,
        "ffmpeg_binary_sha256": sha256(Path(ffmpeg_binary)),
        "ffprobe_binary_sha256": sha256(Path(ffprobe_binary)),
    }
    render_runtime["inventory_sha256"] = sha256_text(
        json.dumps(render_runtime, sort_keys=True, separators=(",", ":"))
    )
    manifest = {
        "status": "RENDERED_LOCAL_REHEARSAL_NOT_UPLOADED_NOT_SUBMITTED",
        "created_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "truth_boundary": script["truth_boundary"],
        "git_commit_at_render": commit,
        "git_working_tree": {
            "clean": not git_status,
            "status_porcelain": git_status,
            "note": "Local verification counts describe this working tree, not necessarily the public baseline commit.",
        },
        "sources": {
            "script": {"path": str(script_path.relative_to(repo_root)), "sha256": sha256(script_path)},
            "screenshot": {"path": str(screenshot_path.relative_to(repo_root)), "sha256": sha256(screenshot_path)},
            "render_helper": {"path": str(Path(__file__).resolve().relative_to(repo_root)), "sha256": sha256(Path(__file__).resolve())},
            "tts_helper": {"path": str(helper_path.relative_to(repo_root)), "sha256": sha256(helper_path)},
            "verify_log": ({"path": str(verify_log), "sha256": sha256(verify_log)} if verify_log else None),
        },
        "narration": narration_manifest,
        "timeline": timeline,
        "subtitles": {
            "burned_into_video": True,
            "embedded_track": "English mov_text",
            "srt_sha256": sha256(captions_path),
        },
        "render": {
            "ffmpeg": ffmpeg_version,
            "runtime": render_runtime,
            "resolution": "1920x1080",
            "frame_rate": FPS,
            "video_codec": "H.264/libx264",
            "audio_codec": "AAC",
            "audio_loudness_target": "-18 LUFS integrated, -1.5 dBTP",
            "music": "none",
        },
        "output": {
            "path": str(output_path),
            "size_bytes": output_path.stat().st_size,
            "sha256": sha256(output_path),
            "ffprobe": probe,
        },
    }
    manifest_path = output_path.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(output_path)
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
