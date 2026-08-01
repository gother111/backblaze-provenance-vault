from __future__ import annotations

# SVG path and element strings intentionally remain one element per source line.
# ruff: noqa: E501
import hashlib
import html
from pathlib import Path

from genblaze_core import Asset, SyncProvider
from genblaze_core.models.step import Step
from genblaze_core.runnable.config import RunnableConfig

PALETTES = {
    "clay": {
        "background": "#eee9df",
        "ground": "#d8c2ad",
        "object": "#b94d33",
        "object_dark": "#733727",
        "ink": "#15221d",
        "light": "#faf7ef",
    },
    "moss": {
        "background": "#e8eadf",
        "ground": "#bec8ae",
        "object": "#52694e",
        "object_dark": "#2f4335",
        "ink": "#17211b",
        "light": "#faf8ed",
    },
    "night": {
        "background": "#19201e",
        "ground": "#303b36",
        "object": "#d96a4b",
        "object_dark": "#913f2d",
        "ink": "#f3efe4",
        "light": "#f1d8ad",
    },
}

FORMATS = {
    "square": (1080, 1080),
    "portrait": (1080, 1350),
    "landscape": (1350, 900),
}


class LocalPosterProvider(SyncProvider):
    """Zero-key Genblaze provider for an honest offline product rehearsal.

    It emits deterministic SVG bytes so the full pipeline, canonical manifest,
    content-addressed layout, and byte verification can be exercised without
    pretending an external AI provider or B2 request occurred.
    """

    name = "provenance-vault-local"

    def __init__(self, object_root: Path) -> None:
        super().__init__()
        self.object_root = object_root

    def generate(self, step: Step, config: RunnableConfig | None = None) -> Step:
        del config
        output_format = str(step.params.get("output_format", "square"))
        palette_name = str(step.params.get("palette", "clay"))
        title = str(step.params.get("title", "Untitled campaign"))
        width, height = FORMATS.get(output_format, FORMATS["square"])
        palette = PALETTES.get(palette_name, PALETTES["clay"])
        svg = render_editorial_svg(
            title=title,
            brief=step.prompt,
            width=width,
            height=height,
            palette=palette,
        )
        payload = svg.encode("utf-8")
        digest = hashlib.sha256(payload).hexdigest()
        destination = self.object_root / digest[:2] / digest[2:4] / f"{digest}.svg"
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            destination.write_bytes(payload)

        step.assets.append(
            Asset(
                url=destination.resolve().as_uri(),
                media_type="image/svg+xml",
                sha256=digest,
                size_bytes=len(payload),
                width=width,
                height=height,
                metadata={
                    "mode": "offline-rehearsal",
                    "generator": "deterministic-svg",
                    "palette": palette_name,
                    "format": output_format,
                },
            )
        )
        return step


def render_editorial_svg(
    *, title: str, brief: str, width: int, height: int, palette: dict[str, str]
) -> str:
    """Render a deterministic editorial still-life poster as valid SVG."""
    safe_title = html.escape(title[:70])
    safe_brief = html.escape(brief[:170])
    seed = int(hashlib.sha256(f"{title}|{brief}".encode()).hexdigest()[:8], 16)
    rotation = (seed % 9) - 4
    sun_x = int(width * (0.70 + (seed % 7) / 100))
    sun_y = int(height * (0.19 + (seed % 5) / 100))
    cup_x = int(width * 0.64)
    cup_y = int(height * 0.52)
    cup_w = int(width * 0.22)
    cup_h = int(height * 0.24)
    line_y = int(height * 0.84)
    title_size = max(42, int(width * 0.055))
    body_size = max(20, int(width * 0.019))
    grain = " ".join(
        f'<circle cx="{(seed * (i + 13)) % width}" cy="{(seed * (i + 29)) % height}" '
        f'r="{1 + i % 2}" fill="{palette["ink"]}" opacity="0.035"/>'
        for i in range(42)
    )
    handle_x = cup_x + cup_w - 8
    handle_y = cup_y + int(cup_h * 0.34)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{safe_title}</title>
  <desc id="desc">Offline generated campaign study. {safe_brief}</desc>
  <rect width="{width}" height="{height}" fill="{palette['background']}"/>
  <path d="M0 {int(height * .63)} L{width} {int(height * .48)} V{height} H0Z" fill="{palette['ground']}"/>
  <circle cx="{sun_x}" cy="{sun_y}" r="{int(width * .12)}" fill="{palette['light']}" opacity=".92"/>
  <path d="M{int(width * .51)} 0 L{int(width * .73)} 0 L{int(width * .94)} {height} L{int(width * .72)} {height}Z" fill="{palette['light']}" opacity=".30"/>
  <g transform="rotate({rotation} {cup_x + cup_w // 2} {cup_y + cup_h // 2})">
    <ellipse cx="{cup_x + cup_w // 2}" cy="{cup_y + cup_h}" rx="{int(cup_w * .62)}" ry="{int(cup_h * .13)}" fill="{palette['object_dark']}" opacity=".24"/>
    <rect x="{cup_x}" y="{cup_y}" width="{cup_w}" height="{cup_h}" rx="{int(cup_w * .09)}" fill="{palette['object']}"/>
    <ellipse cx="{cup_x + cup_w // 2}" cy="{cup_y}" rx="{cup_w // 2}" ry="{int(cup_h * .10)}" fill="{palette['light']}"/>
    <ellipse cx="{cup_x + cup_w // 2}" cy="{cup_y}" rx="{int(cup_w * .40)}" ry="{int(cup_h * .065)}" fill="{palette['object_dark']}"/>
    <path d="M{handle_x} {handle_y} C{handle_x + int(cup_w * .38)} {handle_y - 12}, {handle_x + int(cup_w * .40)} {handle_y + int(cup_h * .58)}, {handle_x} {handle_y + int(cup_h * .55)}" fill="none" stroke="{palette['object']}" stroke-width="{int(cup_w * .10)}" stroke-linecap="round"/>
  </g>
  <g fill="{palette['ink']}">
    <text x="{int(width * .075)}" y="{int(height * .14)}" font-family="Georgia, serif" font-size="{title_size}" font-weight="600">{safe_title}</text>
    <foreignObject x="{int(width * .078)}" y="{int(height * .18)}" width="{int(width * .39)}" height="{int(height * .24)}">
      <div xmlns="http://www.w3.org/1999/xhtml" style="font-family:Arial,sans-serif;font-size:{body_size}px;line-height:1.45;color:{palette['ink']};">{safe_brief}</div>
    </foreignObject>
    <line x1="{int(width * .075)}" y1="{line_y}" x2="{int(width * .925)}" y2="{line_y}" stroke="{palette['ink']}" stroke-width="2" opacity=".55"/>
    <text x="{int(width * .075)}" y="{line_y + int(height * .055)}" font-family="Arial, sans-serif" font-size="{max(16, int(width * .014))}" letter-spacing="4">PROVENANCE VAULT / OFFLINE REHEARSAL</text>
  </g>
  {grain}
</svg>"""
