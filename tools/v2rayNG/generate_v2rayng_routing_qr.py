#!/usr/bin/env python3
"""
Generate a v2RayNG custom routing rules QR code from the current
hydraponique/roscomvpn-routing HAPP config.

The script fetches HAPP/DEFAULT.JSON from GitHub, converts it to the
v2RayNG custom routing-rules JSON format, generates a QR code image,
and also prints the JSON to stdout for clipboard import.

Dependencies: Python 3.8+, qrcode[pil]
    pip install qrcode[pil]
"""

import argparse
import json
import os
import sys
import urllib.request

try:
    import qrcode
except ImportError:
    print(
        "[!] 'qrcode' package is required.\n"
        "    Install it with:  pip install qrcode[pil]",
        file=sys.stderr,
    )
    sys.exit(1)

DEFAULT_CONFIG_URL = (
    "https://raw.githubusercontent.com/hydraponique/"
    "roscomvpn-routing/refs/heads/main/HAPP/DEFAULT.JSON"
)

# How HAPP outbound names map to v2RayNG outbound tags
OUTBOUND_MAP = {
    "Block": "block",
    "Proxy": "proxy",
    "Direct": "direct",
}

# Friendly remarks for each rule group
REMARKS_MAP = {
    "Block": "BLOCK (Ads & Tracking)",
    "Proxy": "PROXY (VPN Required)",
    "Direct": "DIRECT (Russia & LAN)",
}


def fetch_config(url: str) -> dict:
    """Download and parse the HAPP DEFAULT.JSON config."""
    print(f"[*] Fetching config from {url} ...")
    try:
        with urllib.request.urlopen(url) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"[!] Failed to fetch config: {exc}", file=sys.stderr)
        sys.exit(1)


def convert_to_v2rayng_rules(config: dict) -> list[dict]:
    """Convert HAPP config to v2RayNG custom routing rules JSON."""
    rules = []
    idx = 1
    for group in ("Block", "Proxy", "Direct"):
        sites = config.get(f"{group}Sites", [])
        ips = config.get(f"{group}Ip", [])
        if not sites and not ips:
            continue
        rule: dict = {
            "remarks": f"{idx}. {REMARKS_MAP[group]}",
            "outboundTag": OUTBOUND_MAP[group],
            "enabled": True,
        }
        if sites:
            rule["domain"] = sites
        if ips:
            rule["ip"] = ips
        rules.append(rule)
        idx += 1
    return rules


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
        description="Generate a v2RayNG routing rules QR code from HAPP config."
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_CONFIG_URL,
        help="URL of the HAPP DEFAULT.JSON config.",
    )
    parser.add_argument(
        "-o", "--output",
        default="v2rayng_routing_qr.png",
        help="Output QR code image path (default: v2rayng_routing_qr.png).",
    )
    args = parser.parse_args()

    config = fetch_config(args.url)
    rules = convert_to_v2rayng_rules(config)

    # Compact JSON for QR (minimize size)
    json_compact = json.dumps(rules, separators=(",", ":"), ensure_ascii=False)

    # Pretty JSON for display / clipboard
    json_pretty = json.dumps(rules, indent=2, ensure_ascii=False)

    generate_qr(json_compact, args.output)

    print(f"\n[+] QR code saved to: {os.path.abspath(args.output)}")
    print(f"[+] Data length: {len(json_compact)} chars")
    print()
    print("JSON rules (copy to clipboard for manual import):")
    print("-" * 50)
    print(json_pretty)
    print("-" * 50)
    print()
    print(
        "[!] Remember to set Domain Strategy to 'IPIfNonMatch' in\n"
        "    v2RayNG Settings before importing these rules."
    )


if __name__ == "__main__":
    main()
