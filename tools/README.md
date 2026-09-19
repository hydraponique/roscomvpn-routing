# 🛠️ Community Routing Tools

Python scripts to generate routing configurations for various VPN clients from the [HAPP/DEFAULT.JSON](../HAPP/DEFAULT.JSON) config.

All scripts fetch the latest config from GitHub automatically — no manual updates needed.

## 📁 Structure

```
tools/
├── streisand/
│   └── generate_streisand_link.py    # iOS (Streisand) import link
├── v2rayNG/
│   ├── generate_v2rayng_routing_qr.py  # Android routing rules QR
│   └── generate_geoasset_qr.py         # Geoasset URL QR codes
├── sing-box/
│   └── generate_singbox_rules.py       # sing-box rules JSON
└── README.md
```

## 📋 Requirements

- Python 3.8+
- `qrcode[pil]` (only for QR code scripts)

```bash
pip install qrcode[pil]
```

## 🚀 Usage

### Streisand (iOS)

Generates a `streisand://` deep-link for importing routing rules:

```bash
python tools/streisand/generate_streisand_link.py
```

> **⚠️ Important:** You must update `geoip.dat` and `geosite.dat` manually in Streisand (Settings → Routing → Assets) before applying the routing profile.

### v2RayNG (Android)

**Routing rules QR code:**

```bash
python tools/v2rayNG/generate_v2rayng_routing_qr.py
```

Generates `v2rayng_routing_qr.png` and prints the JSON to stdout for clipboard import.

> **⚠️ Important:** Set **Domain Strategy** to `IPIfNonMatch` in v2RayNG Settings before importing rules.

**Geoasset URL QR codes:**

```bash
# Unversioned jsdelivr CDN URLs (default, recommended)
python tools/v2rayNG/generate_geoasset_qr.py

# GitHub Releases URLs
python tools/v2rayNG/generate_geoasset_qr.py --source releases
```

Generates `geoip.dat.png` and `geosite.dat.png`. Scan in v2RayNG → Settings → Geoasset update.

### sing-box (Throne / NekoRay v4.0+)

```bash
# Print to stdout
python tools/sing-box/generate_singbox_rules.py

# Save to file
python tools/sing-box/generate_singbox_rules.py -o singbox_rules.json
```

Import in Throne / NekoRay: Preferences → Routing Setting → Advanced → Import JSON.

## 🔧 Advanced

All scripts accept `--url` to point at a custom config URL:

```bash
python tools/streisand/generate_streisand_link.py --url https://example.com/custom.json
```

Run any script with `--help` for full usage details.
