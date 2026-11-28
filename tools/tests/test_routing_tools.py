import sys
import os
import importlib.util

def import_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Resolve paths
TOOLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

streisand = import_module_from_path('streisand_link', os.path.join(TOOLS_DIR, 'streisand', 'generate_streisand_link.py'))
v2rayng = import_module_from_path('v2rayng_qr', os.path.join(TOOLS_DIR, 'v2rayNG', 'generate_v2rayng_routing_qr.py'))
geoasset = import_module_from_path('geoasset_qr', os.path.join(TOOLS_DIR, 'v2rayNG', 'generate_geoasset_qr.py'))
singbox = import_module_from_path('singbox_rules', os.path.join(TOOLS_DIR, 'sing-box', 'generate_singbox_rules.py'))


# Mock HAPP/DEFAULT.JSON for all tests
mock_config = {
    "Name": "TestVPN",
    "BlockSites": ["geosite:win-spy", "domain:tracker.com"],
    "BlockIp": [],
    "ProxySites": ["geosite:youtube", "keyword:proxy"],
    "ProxyIp": [],
    "DirectSites": ["geosite:category-ru"],
    "DirectIp": ["geoip:direct"],
    "Geoipurl": "https://custom.cdn/geoip.dat",
    "Geositeurl": "https://custom.cdn/geosite.dat"
}

def test_streisand_conversion():
    v2 = streisand.convert_to_v2(mock_config)
    assert v2["name"] == "TestVPN"
    assert v2["domainStrategy"] == "AsIs"
    assert v2["domainMatcher"] == "hybrid"
    assert "uuid" in v2
    assert len(v2["rules"]) == 3
    
    block_rule = next(r for r in v2["rules"] if r["outboundTag"] == "block")
    assert "geosite:win-spy" in block_rule["domain"]

    proxy_rule = next(r for r in v2["rules"] if r["outboundTag"] == "proxy")
    assert "geosite:youtube" in proxy_rule["domain"]
    assert "ip" not in proxy_rule

def test_v2rayng_conversion():
    rules = v2rayng.convert_to_v2rayng_rules(mock_config)
    assert len(rules) == 3
    
    block_rule = rules[0]
    assert block_rule["outboundTag"] == "block"
    assert "1. BLOCK" in block_rule["remarks"]
    assert "geosite:win-spy" in block_rule["domain"]
    assert block_rule["enabled"] is True

    proxy_rule = rules[1]
    assert proxy_rule["outboundTag"] == "proxy"
    assert "2. PROXY" in proxy_rule["remarks"]
    assert "keyword:proxy" in proxy_rule["domain"]

def test_singbox_conversion():
    rules = singbox.build_rules(mock_config)
    
    # DNS Hijack (1) + Block (1) + Proxy (1) + Direct (1)
    assert len(rules) == 4
    
    assert rules[0]["action"] == "hijack-dns"
    assert rules[0]["protocol"] == "dns"
    
    block_rule = next(r for r in rules if r.get("action") == "reject")
    assert "outbound" not in block_rule
    assert "domain_suffix" in block_rule and "tracker.com" in block_rule["domain_suffix"]
    
    proxy_rule = next(r for r in rules if r.get("outbound") == "proxy")
    assert proxy_rule["action"] == "route"
    assert "domain_keyword" in proxy_rule and "proxy" in proxy_rule["domain_keyword"]
    
    direct_rule = next(r for r in rules if r.get("outbound") == "direct")
    assert direct_rule["action"] == "route"

def test_geoasset_urls_releases():
    # Calling the method used by script when --source releases
    urls = geoasset.RELEASES_URLS
    assert "github.com" in urls["geoip.dat"]
    assert "latest/download" in urls["geoip.dat"]
    assert "github.com" in urls["geosite.dat"]

if __name__ == "__main__":
    # Ensure pytest or similar runner is used
    print("Run `pytest tools/tests/test_routing_tools.py` to execute these tests.")
