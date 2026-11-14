#!/usr/bin/env python3
"""
Generate high-fidelity PWA icons for Rock Radio / Fred Rewind.
Generates:
- icons/icon.svg (master vector)
- icons/icon-512.png
- icons/icon-192.png
- icons/icon-180.png (Apple touch icon)
- icons/icon-maskable-512.png
- icons/icon-maskable-192.png
- icons/favicon.png (48x48)
- favicon.ico (multi-res 16, 32, 48)
"""

import os
import subprocess
from PIL import Image

ICONS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'icons'))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.makedirs(ICONS_DIR, exist_ok=True)

# Standard icon SVG (512x512)
STANDARD_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <radialGradient id="bgGrad" cx="50%" cy="40%" r="65%">
      <stop offset="0%" stop-color="#1f2429"/>
      <stop offset="60%" stop-color="#111417"/>
      <stop offset="100%" stop-color="#08090a"/>
    </radialGradient>
    <radialGradient id="coreGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#1ed760" stop-opacity="0.35"/>
      <stop offset="70%" stop-color="#1db954" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="#1db954" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="neonGreen" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#22e569"/>
      <stop offset="100%" stop-color="#17a34a"/>
    </linearGradient>
    <linearGradient id="boltGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="60%" stop-color="#fef08a"/>
      <stop offset="100%" stop-color="#f59e0b"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- Background rounded squircle -->
  <rect width="512" height="512" rx="112" fill="url(#bgGrad)"/>
  <rect width="504" height="504" x="4" y="4" rx="108" fill="none" stroke="rgba(255, 255, 255, 0.08)" stroke-width="2"/>

  <!-- Vinyl grooves -->
  <circle cx="256" cy="256" r="215" fill="none" stroke="rgba(255, 255, 255, 0.04)" stroke-width="1.5"/>
  <circle cx="256" cy="256" r="195" fill="none" stroke="rgba(255, 255, 255, 0.03)" stroke-width="1.5"/>
  <circle cx="256" cy="256" r="175" fill="none" stroke="rgba(255, 255, 255, 0.04)" stroke-width="1.5"/>
  <circle cx="256" cy="256" r="155" fill="none" stroke="rgba(255, 255, 255, 0.03)" stroke-width="1.5"/>

  <!-- Center vinyl disc label background -->
  <circle cx="256" cy="256" r="135" fill="url(#coreGlow)"/>
  <circle cx="256" cy="256" r="128" fill="#121517" stroke="url(#neonGreen)" stroke-width="4"/>

  <!-- Center Rock Sound Waves (Spotify-inspired classic rock style) -->
  <g transform="translate(136, 136) scale(10)" fill="url(#neonGreen)" filter="url(#glow)">
    <!-- Wave 3 (Bottom) -->
    <path d="M16.586 16.424c-.18.295-.563.387-.857.207-2.35-1.434-5.308-1.758-8.793-.963-.335.077-.67-.133-.746-.469-.077-.334.132-.67.467-.747 3.812-.871 7.076-.508 9.721 1.116.295.18.388.563.208.856z"/>
    <!-- Wave 2 (Middle) -->
    <path d="M17.809 13.701c-.226.367-.709.482-1.075.257-2.69-1.653-6.79-2.133-9.972-1.168-.413.125-.85-.107-.975-.521-.125-.414.108-.851.521-.976 3.633-1.102 8.147-.568 11.244 1.332.366.226.482.71.257 1.076z"/>
    <!-- Wave 1 (Top) -->
    <path d="M17.915 10.866C14.692 8.95 9.375 8.775 6.297 9.71c-.496.15-1.022-.134-1.173-.63-.151-.497.133-1.022.63-1.173 3.532-1.072 9.404-.87 13.115 1.333.447.265.592.846.327 1.293-.266.447-.847.592-1.294.326z"/>
  </g>

  <!-- Rock Lightning Bolt accent overlaying center -->
  <g filter="url(#glow)">
    <polygon points="275,155 240,248 266,248 234,342 284,242 256,242" fill="url(#boltGrad)" stroke="#121517" stroke-width="3" stroke-linejoin="round"/>
  </g>
</svg>
"""

# Maskable icon SVG (with safe padding area for circular & squircle cropping)
MASKABLE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <radialGradient id="bgGradM" cx="50%" cy="40%" r="70%">
      <stop offset="0%" stop-color="#1f2429"/>
      <stop offset="60%" stop-color="#111417"/>
      <stop offset="100%" stop-color="#08090a"/>
    </radialGradient>
    <radialGradient id="coreGlowM" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#1ed760" stop-opacity="0.35"/>
      <stop offset="70%" stop-color="#1db954" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="#1db954" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="neonGreenM" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#22e569"/>
      <stop offset="100%" stop-color="#17a34a"/>
    </linearGradient>
    <linearGradient id="boltGradM" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="60%" stop-color="#fef08a"/>
      <stop offset="100%" stop-color="#f59e0b"/>
    </linearGradient>
    <filter id="glowM" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- Full bleed background for maskable safe zone -->
  <rect width="512" height="512" fill="url(#bgGradM)"/>

  <!-- Centered scaled group (safe zone is inner 80% circle) -->
  <g transform="translate(51.2, 51.2) scale(0.8)">
    <!-- Vinyl grooves -->
    <circle cx="256" cy="256" r="215" fill="none" stroke="rgba(255, 255, 255, 0.05)" stroke-width="2"/>
    <circle cx="256" cy="256" r="195" fill="none" stroke="rgba(255, 255, 255, 0.04)" stroke-width="2"/>
    <circle cx="256" cy="256" r="175" fill="none" stroke="rgba(255, 255, 255, 0.05)" stroke-width="2"/>
    <circle cx="256" cy="256" r="155" fill="none" stroke="rgba(255, 255, 255, 0.04)" stroke-width="2"/>

    <!-- Center vinyl disc label background -->
    <circle cx="256" cy="256" r="135" fill="url(#coreGlowM)"/>
    <circle cx="256" cy="256" r="128" fill="#121517" stroke="url(#neonGreenM)" stroke-width="5"/>

    <!-- Waves -->
    <g transform="translate(136, 136) scale(10)" fill="url(#neonGreenM)" filter="url(#glowM)">
      <path d="M16.586 16.424c-.18.295-.563.387-.857.207-2.35-1.434-5.308-1.758-8.793-.963-.335.077-.67-.133-.746-.469-.077-.334.132-.67.467-.747 3.812-.871 7.076-.508 9.721 1.116.295.18.388.563.208.856z"/>
      <path d="M17.809 13.701c-.226.367-.709.482-1.075.257-2.69-1.653-6.79-2.133-9.972-1.168-.413.125-.85-.107-.975-.521-.125-.414.108-.851.521-.976 3.633-1.102 8.147-.568 11.244 1.332.366.226.482.71.257 1.076z"/>
      <path d="M17.915 10.866C14.692 8.95 9.375 8.775 6.297 9.71c-.496.15-1.022-.134-1.173-.63-.151-.497.133-1.022.63-1.173 3.532-1.072 9.404-.87 13.115 1.333.447.265.592.846.327 1.293-.266.447-.847.592-1.294.326z"/>
    </g>

    <!-- Bolt -->
    <g filter="url(#glowM)">
      <polygon points="275,155 240,248 266,248 234,342 284,242 256,242" fill="url(#boltGradM)" stroke="#121517" stroke-width="3" stroke-linejoin="round"/>
    </g>
  </g>
</svg>
"""

def main():
    svg_path = os.path.join(ICONS_DIR, 'icon.svg')
    maskable_svg_path = os.path.join(ICONS_DIR, 'icon-maskable.svg')

    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(STANDARD_SVG)
    with open(maskable_svg_path, 'w', encoding='utf-8') as f:
        f.write(MASKABLE_SVG)

    sizes = [
        (svg_path, 512, os.path.join(ICONS_DIR, 'icon-512.png')),
        (svg_path, 192, os.path.join(ICONS_DIR, 'icon-192.png')),
        (svg_path, 180, os.path.join(ICONS_DIR, 'icon-180.png')),
        (svg_path, 48, os.path.join(ICONS_DIR, 'favicon.png')),
        (maskable_svg_path, 512, os.path.join(ICONS_DIR, 'icon-maskable-512.png')),
        (maskable_svg_path, 192, os.path.join(ICONS_DIR, 'icon-maskable-192.png')),
    ]

    for src_svg, dim, out_png in sizes:
        subprocess.run([
            'rsvg-convert',
            '-w', str(dim),
            '-h', str(dim),
            '-f', 'png',
            '-o', out_png,
            src_svg
        ], check=True)
        print(f"Generated: {out_png} ({dim}x{dim})")

    # Generate multi-size favicon.ico
    img_512 = Image.open(os.path.join(ICONS_DIR, 'icon-512.png'))
    ico_path = os.path.join(ROOT_DIR, 'favicon.ico')
    img_512.save(
        ico_path,
        format='ICO',
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64)]
    )
    print(f"Generated: {ico_path} (multi-size ICO)")

if __name__ == '__main__':
    main()
