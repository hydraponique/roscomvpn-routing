#!/usr/bin/env python3
"""
Generate a Streisand (iOS) routing import link from the current
hydraponique/roscomvpn-routing HAPP config.

The script fetches HAPP/DEFAULT.JSON from GitHub, converts it to the
Xray V2 routing schema, serialises it as a binary plist, and produces
a ready-to-use streisand:// deep-link.

NOTE: This script does NOT update geoip.dat / geosite.dat inside
      Streisand. You must update the geo-databases manually in
      Settings -> Routing -> Assets before applying the rules.

Dependencies: Python 3.8+ (stdlib only, no third-party packages).
"""

import argparse
import base64
import json
import plistlib
import sys
import urllib.request
import uuid

DEFAULT_CONFIG_URL = (
    "https://raw.githubusercontent.com/hydraponique/"
    "roscomvpn-routing/refs/heads/main/HAPP/DEFAULT.JSON"
)


def fetch_config(url: str) -> dict:
    """Download and parse the HAPP DEFAULT.JSON config."""
    print(f"[*] Fetching config from {url} ...")
    try:
        with urllib.request.urlopen(url) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"[!] Failed to fetch config: {exc}", file=sys.stderr)
        sys.exit(1)


def convert_to_v2(config: dict) -> dict:
    """Convert legacy HAPP config to Xray/Streisand V2 routing schema."""
    block_sites = config.get("BlockSites", [])
    proxy_sites = config.get("ProxySites", [])
    direct_sites = config.get("DirectSites", [])
    block_ips = config.get("BlockIp", [])
    proxy_ips = config.get("ProxyIp", [])
    direct_ips = config.get("DirectIp", [])

    v2 = {
        "name": config.get("Name", "RoscomVPN"),
        "uuid": str(uuid.uuid4()).upper(),
        "domainStrategy": "AsIs",
        "domainMatcher": "hybrid",
        "rules": [],
    }

    # Block
    if block_sites or block_ips:
        rule = {"domainMatcher": "hybrid", "outboundTag": "block"}
        if block_sites:
            rule["domain"] = block_sites
        if block_ips:
            rule["ip"] = block_ips
        v2["rules"].append(rule)

    # Proxy
    if proxy_sites or proxy_ips:
        rule = {"domainMatcher": "hybrid", "outboundTag": "proxy"}
        if proxy_sites:
            rule["domain"] = proxy_sites
        if proxy_ips:
            rule["ip"] = proxy_ips
        v2["rules"].append(rule)

    # Direct
    if direct_sites or direct_ips:
        rule = {"domainMatcher": "hybrid", "outboundTag": "direct"}
        if direct_sites:
            rule["domain"] = direct_sites
        if direct_ips:
            rule["ip"] = direct_ips
        v2["rules"].append(rule)

    return v2


def generate_link(v2_config: dict) -> str:
    """Pack V2 config into a streisand:// deep-link.

    Encoding chain:
        dict -> binary plist -> base64 -> "import/route://<b64>"
             -> base64 -> "streisand://<b64>"
    """
    plist_bytes = plistlib.dumps(v2_config, fmt=plistlib.FMT_BINARY)
    inner_b64 = base64.b64encode(plist_bytes).decode("utf-8")
    import_url = f"import/route://{inner_b64}"
    outer_b64 = base64.b64encode(import_url.encode("utf-8")).decode("utf-8")
    return f"streisand://{outer_b64}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Streisand routing import link from HAPP config."
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_CONFIG_URL,
        help="URL of the HAPP DEFAULT.JSON config (default: GitHub main branch).",
    )
    args = parser.parse_args()

    config = fetch_config(args.url)
    v2 = convert_to_v2(config)
    link = generate_link(v2)

    print()
    print("=" * 60)
    print("Streisand V2 Import Link")
    print("=" * 60)
    print(link)
    print("=" * 60)
    print()
    print(
        "[!] Remember to update geoip.dat and geosite.dat in\n"
        "    Streisand -> Settings -> Routing -> Assets\n"
        "    BEFORE applying this routing profile."
    )


if __name__ == "__main__":
    main()
