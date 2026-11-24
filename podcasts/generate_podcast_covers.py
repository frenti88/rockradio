#!/usr/bin/env python3
"""Generates 7 crisp flat-color minimalist SVG podcast covers with high-contrast icons."""
from pathlib import Path

OUT_DIR = Path("/home/antigravity/frenti88/rockradio/podcasts")

COVERS = [
    (
        "cover_ep01_diseno.svg",
        "#1E3A8A",  # Cobalt Blue
        "#FFFFFF",
        "#FDE047",
        "APARTE",
        # Bezier pen nib + golden spark
        """
        <g transform="translate(400, 385)" fill="none" stroke="{fg}" stroke-width="18" stroke-linecap="round" stroke-linejoin="round">
          <path d="M 0 -130 L 85 15 L 48 115 L -48 115 L -85 15 Z"/>
          <line x1="0" y1="-130" x2="0" y2="-10"/>
          <circle cx="0" cy="5" r="22" fill="{accent}" stroke="{fg}" stroke-width="14"/>
          <path d="M -115 -70 Q 0 -150 115 -70" stroke="{accent}" stroke-width="10" stroke-dasharray="12 16"/>
          <circle cx="-115" cy="-70" r="10" fill="{accent}" stroke="none"/>
          <circle cx="115" cy="-70" r="10" fill="{accent}" stroke="none"/>
        </g>
        """,
    ),
    (
        "cover_ep02_nuevo_medio.svg",
        "#C2410C",  # Warm Terracotta
        "#FFF7ED",
        "#FDBA74",
        "APARTE",
        # Paint tube + brush stroke (Monet / new medium)
        """
        <g transform="translate(400, 385)" fill="none" stroke="{fg}" stroke-width="18" stroke-linecap="round" stroke-linejoin="round">
          <rect x="-55" y="-120" width="110" height="190" rx="18"/>
          <line x1="-55" y1="-70" x2="55" y2="-70"/>
          <path d="M -28 70 L -20 115 L 20 115 L 28 70"/>
          <rect x="-65" y="-145" width="130" height="25" rx="8" fill="{accent}" stroke="{fg}" stroke-width="14"/>
          <path d="M -22 -15 Q 0 -45 22 -15 Q 0 15 -22 -15 Z" fill="{accent}" stroke="none"/>
          <path d="M -105 145 Q 0 115 105 145" stroke="{accent}" stroke-width="16"/>
        </g>
        """,
    ),
    (
        "cover_ep03_tendencias_2027.svg",
        "#065F46",  # Deep Emerald
        "#ECFDF5",
        "#6EE7B7",
        "APARTE",
        # Adaptive modular UI grid + AI spark
        """
        <g transform="translate(400, 385)" fill="none" stroke="{fg}" stroke-width="18" stroke-linecap="round" stroke-linejoin="round">
          <rect x="-130" y="-120" width="115" height="115" rx="22"/>
          <rect x="15" y="-120" width="115" height="65" rx="20" fill="{accent}" stroke="none"/>
          <rect x="15" y="-25" width="115" height="145" rx="22"/>
          <rect x="-130" y="25" width="115" height="95" rx="22"/>
          <path d="M -72 -88 L -72 -38 M -97 -63 L -47 -63" stroke="{accent}" stroke-width="16"/>
        </g>
        """,
    ),
    (
        "cover_ep04_resumen_semanal.svg",
        "#4C1D95",  # Deep Indigo Purple
        "#F5F3FF",
        "#C4B5FD",
        "APARTE",
        # Morning radio broadcast mic + sound waves
        """
        <g transform="translate(400, 385)" fill="none" stroke="{fg}" stroke-width="18" stroke-linecap="round" stroke-linejoin="round">
          <rect x="-48" y="-130" width="96" height="155" rx="48" fill="{accent}" stroke="{fg}"/>
          <path d="M -88 -10 A 88 88 0 0 0 88 -10"/>
          <line x1="0" y1="78" x2="0" y2="132"/>
          <line x1="-56" y1="132" x2="56" y2="132"/>
          <path d="M -135 -60 A 140 140 0 0 0 -135 20" stroke="{accent}" stroke-width="14"/>
          <path d="M 135 -60 A 140 140 0 0 1 135 20" stroke="{accent}" stroke-width="14"/>
        </g>
        """,
    ),
    (
        "cover_mas_alla_01.svg",
        "#0F766E",  # Rich Teal
        "#F0FDFA",
        "#5EEAD4",
        "MÁS ALLÁ DE LA INTERFAZ",
        # Contextual interface: adaptive eye + connected nodes
        """
        <g transform="translate(400, 385)" fill="none" stroke="{fg}" stroke-width="18" stroke-linecap="round" stroke-linejoin="round">
          <path d="M -145 0 Q 0 -115 145 0 Q 0 115 -145 0 Z"/>
          <circle cx="0" cy="0" r="46" fill="{accent}" stroke="{fg}"/>
          <circle cx="0" cy="0" r="16" fill="#0F766E" stroke="none"/>
          <circle cx="-110" cy="-95" r="14" fill="{accent}" stroke="none"/>
          <circle cx="110" cy="-95" r="14" fill="{accent}" stroke="none"/>
          <circle cx="0" cy="115" r="14" fill="{accent}" stroke="none"/>
        </g>
        """,
    ),
    (
        "cover_ep05_no_hacer_nada.svg",
        "#B45309",  # Warm Amber
        "#FEF3C7",
        "#FDE68A",
        "APARTE",
        # Calm coffee cup with gentle rising steam
        """
        <g transform="translate(400, 395)" fill="none" stroke="{fg}" stroke-width="18" stroke-linecap="round" stroke-linejoin="round">
          <path d="M -100 -35 L 80 -35 L 65 85 A 45 45 0 0 1 20 125 L -40 125 A 45 45 0 0 1 -85 85 Z"/>
          <path d="M 80 -10 L 115 -10 A 35 35 0 0 1 115 60 L 72 60"/>
          <line x1="-115" y1="150" x2="95" y2="150" stroke="{accent}" stroke-width="16"/>
          <path d="M -45 -75 Q -60 -110 -40 -140" stroke="{accent}" stroke-width="14"/>
          <path d="M -5 -75 Q -20 -115 0 -150" stroke="{accent}" stroke-width="14"/>
          <path d="M 35 -75 Q 20 -110 40 -140" stroke="{accent}" stroke-width="14"/>
        </g>
        """,
    ),
    (
        "cover_ep06_maquina_horror.svg",
        "#7F1D1D",  # Dark Crimson
        "#FEF2F2",
        "#FCA5A5",
        "APARTE",
        # Cybernetic / biomechanical eye + circuit lines
        """
        <g transform="translate(400, 385)" fill="none" stroke="{fg}" stroke-width="18" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="0,-135 120,-65 120,65 0,135 -120,65 -120,-65"/>
          <circle cx="0" cy="0" r="56" stroke="{accent}" stroke-width="16"/>
          <circle cx="0" cy="0" r="24" fill="{accent}" stroke="none"/>
          <line x1="0" y1="-135" x2="0" y2="-56"/>
          <line x1="0" y1="56" x2="0" y2="135"/>
          <line x1="-120" y1="0" x2="-56" y2="0"/>
          <line x1="56" y1="0" x2="120" y2="0"/>
        </g>
        """,
    ),
]


def main():
    for fname, bg, fg, accent, label, icon_svg in COVERS:
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800">
  <rect width="800" height="800" fill="{bg}"/>
  {icon_svg.format(fg=fg, accent=accent)}
  <text x="400" y="690" text-anchor="middle" font-family="system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif" font-size="34" font-weight="700" letter-spacing="8" fill="{fg}" opacity="0.92">{label}</text>
</svg>
"""
        out = OUT_DIR / fname
        out.write_text(svg, encoding="utf-8")
        print(f"Created {out.name}")


if __name__ == "__main__":
    main()
