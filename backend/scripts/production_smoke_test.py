"""ShopQ Production Integration Smoke Test.

Executes a focused end-to-end integration check across:
1. Health check & configuration
2. Search & discovery (/api/search)
3. Live analysis & decision engine (/api/analyze)
4. 4-Level Schema product endpoints (/api/products/{id})
5. Time-series price history & observations (/api/products/{id}/price-history)
6. Watchlist management (/api/watchlist)
7. Notification alerts (/api/alerts)
8. User preferences (/api/preferences)
9. Chrome Extension sidepanel API compatibility
"""

import sys
import json
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend root to path
backend_root = str(Path(__file__).resolve().parent.parent)
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app.main import app

def run_smoke_test():
    client = TestClient(app)

    print("=" * 80)
    print("SHOPQ REAL PRODUCTION INTEGRATION SMOKE TEST")
    print("=" * 80)

    # 1. Health check
    res_health = client.get("/health")
    assert res_health.status_code == 200
    print("✓ 1. Health Check (/health): 200 OK")
    print(f"     Payload: {res_health.json()}")

    # 2. Search API
    res_search = client.post("/api/search", json={"query": "sony", "limit": 10})
    assert res_search.status_code == 200
    search_data = res_search.json()
    assert len(search_data["results"]) > 0
    print(f"✓ 2. Search API (POST /api/search?q=sony): {len(search_data['results'])} result(s) returned")

    # 3. Product Analysis API (/api/analyze)
    analyze_payload = {"url": "https://www.amazon.in/dp/B09XS7JWHH", "force_refresh": True}
    res_analyze = client.post("/api/analyze", json=analyze_payload)
    assert res_analyze.status_code == 200
    an_data = res_analyze.json()
    print("ANALYZE RESPONSE KEYS:", list(an_data.keys()))
    best_off = an_data.get("bestOffer") or an_data.get("best_offer") or an_data["product"].get("bestOffer") or an_data["product"].get("best_offer")
    print("✓ 3. Product Analysis API (POST /api/analyze): 200 OK")
    print(f"     Product: {an_data['product']['name']}")
    print(f"     Decision: {an_data['decision']['decision']} (Confidence: {an_data['decision']['confidence_level']})")
    if best_off:
        print(f"     Best Offer: {best_off.get('retailer', 'Store')} - ₹{best_off.get('price', 0):,.2f}")

    # 4. Product Details API (/api/products/{id} & /api/products/{id}/details)
    res_prod = client.get("/api/products/sony_good_deal")
    assert res_prod.status_code == 200
    p_resp = res_prod.json()
    assert "product" in p_resp
    assert "decision" in p_resp

    res_details = client.get("/api/products/sony_good_deal/details")
    assert res_details.status_code == 200
    p_data = res_details.json()
    cp = p_data.get("canonical_product") or p_data.get("canonicalProduct")
    cv = p_data.get("canonical_variant") or p_data.get("canonicalVariant")
    rl = p_data.get("retailer_listing") or p_data.get("retailerListing")
    so = p_data.get("seller_offer") or p_data.get("sellerOffer")

    assert cp is not None
    assert cv is not None
    assert rl is not None
    assert so is not None
    assert cp["id"] == "cp_sony_good_deal"
    print("✓ 4. 4-Level Schema Details (GET /api/products/sony_good_deal/details): 200 OK")
    print(f"     Canonical Product: {cp['name']}")
    print(f"     Retailer Listing: {rl.get('retailer') or rl.get('retailerName')}")

    # 5. Price History API (/api/products/{id}/price-history)
    res_hist = client.get("/api/products/sony_good_deal/price-history")
    assert res_hist.status_code == 200
    hist_data = res_hist.json()
    assert isinstance(hist_data, list) and len(hist_data) > 0
    print(f"✓ 5. Price History API (GET /api/products/sony_good_deal/price-history): {len(hist_data)} observation points")

    # 6. Watchlist API (/api/watchlist)
    res_wl_add = client.post("/api/watchlist", json={"product_id": "sony_good_deal", "target_price": 23000.0})
    assert res_wl_add.status_code == 200
    res_wl_get = client.get("/api/watchlist")
    assert res_wl_get.status_code == 200
    wl_items = res_wl_get.json()
    assert isinstance(wl_items, list)
    print(f"✓ 6. Watchlist API (/api/watchlist): Add & List verified ({len(wl_items)} item(s) in watchlist)")

    # 7. Alerts API (/api/alerts)
    res_alerts = client.get("/api/alerts")
    assert res_alerts.status_code == 200
    alert_list = res_alerts.json()
    assert isinstance(alert_list, list)
    print(f"✓ 7. Alerts API (/api/alerts): {len(alert_list)} alert(s) present")

    # 8. Preferences API
    res_pref = client.get("/api/preferences")
    assert res_pref.status_code == 200
    print("✓ 8. Preferences API (/api/preferences): Settings loaded cleanly")

    # 9. Chrome Extension SidePanel compatibility check
    ext_payload = {"url": "https://www.flipkart.com/sony-wh-1000xm5-bluetooth-headset/p/itm7e6ec3fa0e676"}
    res_ext = client.post("/api/analyze", json=ext_payload)
    assert res_ext.status_code == 200
    ext_data = res_ext.json()
    assert ext_data["decision"]["decision"] in ("BUY", "WAIT", "CAUTION", "YOUR_CALL", "NO_DECISION")
    print("✓ 9. Extension SidePanel Contract: Compatible response generated")

    print("\n" + "=" * 80)
    print("🎉 ALL PRODUCTION SMOKE TESTS PASSED CLEANLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_smoke_test()
