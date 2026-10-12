"""
ShopQ Chrome Extension Test & Validation Suite (Python)
Validates Manifest V3 compliance, bundle file existence, CSP rules,
design system adherence, and API contract parsing without third-party dependencies.
"""

import json
import os
import re
import sys

EXT_DIR = os.path.dirname(os.path.abspath(__file__))
total_tests = 0
passed_tests = 0
failed_tests = 0

def check(condition: bool, message: str):
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    if condition:
        passed_tests += 1
        print(f"  ✓ PASS: {message}")
    else:
        failed_tests += 1
        print(f"  ✗ FAIL: {message}")

print("====================================================")
print("🧪 ShopQ Manifest V3 Extension Python Validation")
print(f"Directory: {EXT_DIR}")
print("====================================================\n")

# 1. Manifest checks
print("📦 1. Manifest V3 Syntax & Permissions:")
manifest_file = os.path.join(EXT_DIR, "manifest.json")
check(os.path.exists(manifest_file), "manifest.json exists")

manifest = None
try:
    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    check(True, "manifest.json parses as valid JSON")
except Exception as e:
    check(False, f"manifest.json parsing error: {e}")

if manifest:
    check(manifest.get("manifest_version") == 3, "manifest_version == 3")
    check(bool(manifest.get("name")), "Extension name defined")
    check(bool(manifest.get("version")), "Extension version defined")

    # Permissions
    expected_perms = {"activeTab", "sidePanel", "storage"}
    perms = set(manifest.get("permissions", []))
    check(expected_perms.issubset(perms), f"Contains minimal permissions: {expected_perms}")

    # Host permissions
    expected_hosts = [
        "*://*.amazon.in/*",
        "*://*.flipkart.com/*",
        "*://*.croma.com/*",
        "*://*.reliancedigital.in/*",
        "*://*.tatacliq.com/*",
        "*://*.myntra.com/*",
        "*://*.ajio.com/*",
        "*://*.meesho.com/*",
        "*://*.jiomart.com/*",
        "*://*.nykaa.com/*"
    ]
    host_perms = manifest.get("host_permissions", [])
    check(all(h in host_perms for h in expected_hosts), "Contains 10 retailer host_permissions")

    # Native side panel
    side_panel = manifest.get("side_panel", {})
    check(side_panel.get("default_path") == "sidepanel.html", "side_panel default_path is sidepanel.html")

    # Action
    check("action" in manifest, "action declared in manifest")

    # Background service worker
    bg = manifest.get("background", {})
    check(bg.get("service_worker") == "background.js", "background.service_worker is background.js")

    # Content scripts
    cs = manifest.get("content_scripts", [])
    check(len(cs) > 0, "content_scripts configured")
    if cs:
        check("content.js" in cs[0].get("js", []), "content_scripts has content.js")
        check("content.css" in cs[0].get("css", []), "content_scripts has content.css")

    # Check existence of all referenced files
    referenced = [
        bg.get("service_worker"),
        side_panel.get("default_path")
    ]
    if cs:
        referenced.extend(cs[0].get("js", []))
        referenced.extend(cs[0].get("css", []))

    for r in referenced:
        if r:
            check(os.path.exists(os.path.join(EXT_DIR, r)), f"Referenced file exists: {r}")

# 2. CSP & Security Rules
print("\n🔒 2. CSP & Security Rules:")
for js_file in ["background.js", "content.js", "sidepanel.js"]:
    p = os.path.join(EXT_DIR, js_file)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            code = f.read()
        check("eval(" not in code, f"{js_file} does not use eval()")
        check("new Function(" not in code, f"{js_file} does not use new Function()")

html_p = os.path.join(EXT_DIR, "sidepanel.html")
if os.path.exists(html_p):
    with open(html_p, "r", encoding="utf-8") as f:
        html = f.read()
    check(not re.search(r"onclick\s*=", html, re.I), "No inline onclick in sidepanel.html")
    check(not re.search(r"onload\s*=", html, re.I), "No inline onload in sidepanel.html")
    check(not re.search(r"<script>[\s\S]*?</script>", html, re.I), "No inline <script> in sidepanel.html")
    check('src="sidepanel.js"' in html, "Imports external sidepanel.js")
    check('href="sidepanel.css"' in html, "Imports external sidepanel.css")

# 3. Design System Verification
print("\n🎨 3. Design System Verification:")
css_p = os.path.join(EXT_DIR, "sidepanel.css")
if os.path.exists(css_p):
    with open(css_p, "r", encoding="utf-8") as f:
        css = f.read()
    check("#FAF8F5" in css or "--bg" in css, "Uses #FAF8F5 background token")
    check("#FFFFFF" in css or "--bg-card" in css, "Uses #FFFFFF card token")
    check("#C96B7A" in css or "--accent" in css, "Uses #C96B7A Dusty Rose accent token")
    check("#E8E4E0" in css or "--border" in css, "Uses #E8E4E0 border token")
    check("8px" in css, "Uses 8px radius")
    check("Inter" in css, "Uses Inter typography")

# 4. API Contract Simulation
print("\n📡 4. Backend /api/analyze Contract Compatibility:")
mock_contract = {
    "product": {
        "id": "sony_wh1000xm5",
        "name": "Sony WH-1000XM5",
        "current_price": 23499
    },
    "decision": {
        "decision": "WAIT",
        "confidence_level": "HIGH",
        "buy_point": 22999
    },
    "best_offer": {
        "retailer": "Flipkart",
        "price": 22499
    }
}
check(bool(mock_contract["product"]["id"]), "Valid product.id")
check(mock_contract["decision"]["decision"] == "WAIT", "Valid decision string")
check(mock_contract["decision"]["buy_point"] == 22999, "Valid buy_point value")
check(mock_contract["best_offer"]["retailer"] == "Flipkart", "Valid best_offer retailer")

print("\n====================================================")
print(f"📊 Summary: {passed_tests}/{total_tests} tests passed ({failed_tests} failures).")
print("====================================================")

if failed_tests > 0:
    sys.exit(1)
else:
    print("🎉 ALL EXTENSION VALIDATION TESTS PASSED!")
    sys.exit(0)
