#!/usr/bin/env python3
"""
Generate QR codes for importing RoscomVPN geoasset URLs into v2RayNG.

Two QR codes are produced — one for geoip.dat and one for geosite.dat.
Users can scan these in v2RayNG -> Settings -> Geoasset update to
quickly set the correct geoasset URLs.

By default, the script uses branch-based jsdelivr CDN URLs.
You can also pass `--source releases` to use the GitHub Releases URLs.

Dependencies: Python 3.8+, qrcode[pil]
    pip install qrcode[pil]
"""

import argparse
import os
import sys

try:
    import qrcode
except ImportError:
    print(
        "[!] 'qrcode' package is required.\n"
        "    Install it with:  pip install qrcode[pil]",
        file=sys.stderr,
    )
    sys.exit(1)

# Static branch-based CDN URLs (unversioned, redirects to latest)
CDN_URLS = {
    "geoip.dat": "https://cdn.jsdelivr.net/gh/hydraponique/roscomvpn-geoip/release/geoip.dat",
    "geosite.dat": "https://cdn.jsdelivr.net/gh/hydraponique/roscomvpn-geosite/release/geosite.dat",
}

# Stable URLs that always resolve to the latest release
RELEASES_URLS = {
    "geoip.dat": "https://github.com/hydraponique/roscomvpn-geoip/releases/latest/download/geoip.dat",
    "geosite.dat": "https://github.com/hydraponique/roscomvpn-geosite/releases/latest/download/geosite.dat",
}


def get_urls(source: str) -> dict[str, str]:
    """Return geoasset URLs based on the chosen source."""
    if source == "releases":
        return dict(RELEASES_URLS)
    return dict(CDN_URLS)


def generate_qr(data: str, output_path: str) -> None:
    """Generate a QR code PNG from a string."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate QR codes for v2RayNG geoasset URLs."
    )
    parser.add_argument(
        "--source",
        choices=["cdn", "releases"],
        default="cdn",
        help=(
            "'cdn' — unversioned jsdelivr CDN URLs (default). "
            "'releases' — stable GitHub Releases URLs."
        ),
    )
    parser.add_argument(
        "-d", "--output-dir",
        default=".",
        help="Directory to save QR code images (default: current dir).",
    )
    args = parser.parse_args()

    urls = get_urls(args.source)

    os.makedirs(args.output_dir, exist_ok=True)

    for filename, url in urls.items():
        out_path = os.path.join(args.output_dir, f"{filename}.png")
        generate_qr(url, out_path)
        print(f"[+] {filename}: {os.path.abspath(out_path)}")
        print(f"    URL: {url}")

    print()
    print(
        "Scan these QR codes in v2RayNG -> Settings -> Geoasset update\n"
        "to set the correct geoasset download URLs."
    )


if __name__ == "__main__":
    main()
