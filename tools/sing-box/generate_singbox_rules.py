#!/usr/bin/env python3
"""
Generate sing-box route rules JSON from the current
hydraponique/roscomvpn-routing HAPP config.

The output is compatible with sing-box-based clients:
  - Throne
  - NekoRay v4.0+
  - Any sing-box client that supports JSON rule import

The script converts geosite/geoip entries to rule_set URLs pointing
to the .srs files hosted on the jsdelivr CDN by hydraponique.

Dependencies: Python 3.8+ (stdlib only, no third-party packages).
"""

import argparse
import json
import sys
import urllib.request

DEFAULT_CONFIG_URL = (
    "https://raw.githubusercontent.com/hydraponique/"
    "roscomvpn-routing/refs/heads/main/HAPP/DEFAULT.JSON"
)

# CDN base URLs for .srs rule-set files
GEOSITE_SRS_BASE = (
    "https://cdn.jsdelivr.net/gh/hydraponique/roscomvpn-geosite/release/sing-box"
)
GEOIP_SRS_BASE = (
    "https://cdn.jsdelivr.net/gh/hydraponique/roscomvpn-geoip/release/sing-box"
)

# Name mapping: DEFAULT.JSON uses some names that differ from the .srs filenames
GEOSITE_NAME_MAP = {
    "epicgames": "epic-games",
}

# Categories for which hydraponique publishes .srs files
KNOWN_GEOSITE_SRS = {
    "whitelist", "category-ru", "category-geoblock-ru",
    "apple", "google-play", "google-deepmind",
    "microsoft", "github", "telegram", "youtube",
    "twitch", "twitch-ads", "pinterest",
    "steam", "epicgames", "epic-games",
    "riot", "escapefromtarkov", "faceit", "origin",
    "category-ads", "win-spy", "private", "torrent",
}

KNOWN_GEOIP_SRS = {"direct", "whitelist", "private"}


def fetch_config(url: str) -> dict:
    """Download and parse the HAPP DEFAULT.JSON config."""
    print(f"[*] Fetching config from {url} ...")
    try:
        with urllib.request.urlopen(url) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"[!] Failed to fetch config: {exc}", file=sys.stderr)
        sys.exit(1)


def _geosite_to_srs(name: str) -> str | None:
    """Convert a geosite category name to its .srs CDN URL."""
    mapped = GEOSITE_NAME_MAP.get(name, name)
    if mapped in KNOWN_GEOSITE_SRS:
        return f"{GEOSITE_SRS_BASE}/{mapped}.srs"
    return None


def _geoip_to_srs(name: str) -> str | None:
    """Convert a geoip category name to its .srs CDN URL."""
    if name in KNOWN_GEOIP_SRS:
        return f"{GEOIP_SRS_BASE}/{name}.srs"
    return None


def _parse_entries(site_entries: list[str], ip_entries: list[str]) -> dict:
    """Parse HAPP list entries into sing-box rule fields."""
    rule_sets: list[str] = []
    domain_suffix: list[str] = []
    domain_keyword: list[str] = []
    domain: list[str] = []

    for entry in site_entries:
        if entry.startswith("geosite:"):
            url = _geosite_to_srs(entry[len("geosite:"):])
            if url:
                rule_sets.append(url)
            else:
                print(f"[!] Warning: no .srs found for {entry}, skipping.")
        elif entry.startswith("domain:"):
            domain_suffix.append(entry[len("domain:"):])
        elif entry.startswith("keyword:"):
            domain_keyword.append(entry[len("keyword:"):])
        else:
            domain.append(entry)

    for entry in ip_entries:
        if entry.startswith("geoip:"):
            url = _geoip_to_srs(entry[len("geoip:"):])
            if url:
                rule_sets.append(url)
            else:
                print(f"[!] Warning: no .srs found for {entry}, skipping.")

    fields: dict = {}
    if rule_sets:
        fields["rule_set"] = rule_sets
    if domain:
        fields["domain"] = domain
    if domain_suffix:
        fields["domain_suffix"] = domain_suffix
    if domain_keyword:
        fields["domain_keyword"] = domain_keyword
    return fields


def build_rules(config: dict) -> list[dict]:
    """Build the full sing-box route rules array from HAPP config."""
    rules: list[dict] = []

    # 1. DNS hijack (always first)
    rules.append({"action": "hijack-dns", "protocol": "dns"})

    groups = [
        ("Block", "block"),
        ("Proxy", "proxy"),
        ("Direct", "direct"),
    ]

    for group, action_type in groups:
        sites = config.get(f"{group}Sites", [])
        ips = config.get(f"{group}Ip", [])
        if not sites and not ips:
            continue

        fields = _parse_entries(sites, ips)
        if not fields:
            continue

        if action_type == "block":
            rule: dict = {"action": "reject"}
        else:
            rule = {"action": "route", "outbound": action_type}

        rule.update(fields)
        rules.append(rule)

    return rules


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate sing-box route rules JSON from HAPP config."
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_CONFIG_URL,
        help="URL of the HAPP DEFAULT.JSON config.",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output JSON file path. If omitted, prints to stdout.",
    )
    args = parser.parse_args()

    config = fetch_config(args.url)
    rules = build_rules(config)
    json_str = json.dumps(rules, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str + "\n")
        print(f"\n[+] Rules saved to: {args.output}")
    else:
        print()
        print(json_str)

    print(f"\n[+] {len(rules)} rules generated.")
    print(
        "\nImport in Throne / NekoRay v4.0+:\n"
        "  Preferences -> Routing Setting -> Advanced -> Import JSON"
    )


if __name__ == "__main__":
    main()
