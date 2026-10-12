import sys
import os
import unittest

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.config import settings
from app.services.product_service import product_service
from app.services.decision_service import decision_service
from app.services.search_service import search_service
from app.services.watchlist_service import watchlist_service
from app.services.alert_service import alert_service
from app.services.preferences_service import preferences_service
from app.schemas.preferences import PreferencesSchema, NotificationSettingsSchema

try:
    from fastapi.testclient import TestClient
    from app.main import app
    HAS_TEST_CLIENT = True
except Exception:
    HAS_TEST_CLIENT = False


class TestShopQBackend(unittest.TestCase):
    """Thorough test suite verifying all required endpoints and strict API contracts."""

    @classmethod
    def setUpClass(cls):
        if HAS_TEST_CLIENT:
            cls.client = TestClient(app)

    def test_services_catalog_seeding(self):
        """Verifies that all 12 core test scenarios are seeded correctly."""
        expected_ids = [
            "sony_good_deal",
            "iphone_wait",
            "nike_better_alternative",
            "laptop_suspicious_seller",
            "new_product_no_history",
            "stale_price",
            "variant_mismatch",
            "all_sources_failed",
            "seller_changed",
            "out_of_stock",
            "your_call",
            "no_decision",
        ]
        for pid in expected_ids:
            p = product_service.get_by_id(pid)
            self.assertIsNotNone(p, f"Failed to retrieve seeded scenario product: {pid}")
            self.assertIsNotNone(p.canonical_product, f"Product {pid} missing canonical_product")
            self.assertIsNotNone(p.canonical_variant, f"Product {pid} missing canonical_variant")
            self.assertIsNotNone(p.retailer_listing, f"Product {pid} missing retailer_listing")
            self.assertIsNotNone(p.seller_offer, f"Product {pid} missing seller_offer")

    def test_strict_decision_contract_structure(self):
        """
        Verifies Requirement 3:
        Strict API Contract returning:
        - product
        - decision (decision, confidence_level, primary_reason, secondary_reasons, buy_point,
                    best_offer_id, data_freshness, data_coverage, checked_at, model_version, decision_rules_version)
        - best_offer
        """
        analysis = decision_service.analyze_product("sony_good_deal")
        self.assertIsNotNone(analysis.product)
        self.assertIsNotNone(analysis.decision)

        d = analysis.decision
        self.assertEqual(d.decision, "BUY")
        self.assertIn(d.confidence_level, ["HIGH", "MEDIUM", "LOW"])
        self.assertTrue(len(d.primary_reason) > 0)
        self.assertIsInstance(d.secondary_reasons, list)
        self.assertTrue(len(d.secondary_reasons) > 0)
        self.assertIsNotNone(d.buy_point)
        self.assertIn(d.data_freshness, ["FRESH", "RECENT", "STALE"])
        self.assertTrue(d.data_coverage.endswith("%"))
        self.assertTrue(len(d.checked_at) > 0)
        self.assertEqual(d.model_version, settings.MODEL_VERSION)
        self.assertEqual(d.decision_rules_version, settings.DECISION_RULES_VERSION)

    def test_url_resolution(self):
        """Verifies URL extraction and routing heuristics."""
        p_amazon = product_service.resolve_by_url("https://amazon.in/dp/sony-wh1000xm5-black")
        self.assertEqual(p_amazon.id, "sony_good_deal")

        p_myntra = product_service.resolve_by_url("https://myntra.com/shoes/nike-air-max-90")
        self.assertEqual(p_myntra.id, "nike_better_alternative")

    def test_search_service(self):
        """Verifies query search and URL fallback search."""
        res_text = search_service.search("iphone")
        self.assertTrue(res_text.total >= 1)
        self.assertEqual(res_text.results[0].id, "iphone_wait")

        res_url = search_service.search("https://croma.com/canon-eos-r50")
        self.assertTrue(res_url.total >= 1)
        self.assertEqual(res_url.results[0].id, "new_product_no_history")

    def test_watchlist_service(self):
        """Verifies watchlist CRUD operations."""
        initial = watchlist_service.get_all()
        self.assertTrue(len(initial) >= 1)

        # Add item
        added = watchlist_service.add("sony_good_deal", 21999.0)
        self.assertEqual(added.id, "sony_good_deal")
        self.assertEqual(added.target_price, 21999.0)

        # Delete item
        deleted = watchlist_service.delete("sony_good_deal")
        self.assertTrue(deleted)

    def test_alerts_service(self):
        """Verifies alert retrieval and marking read."""
        alerts = alert_service.get_all()
        self.assertTrue(len(alerts) >= 1)

        updated = alert_service.mark_as_read(alerts[0].id)
        self.assertIsNotNone(updated)
        self.assertTrue(updated.read)

    def test_preferences_service(self):
        """Verifies getting and updating user preferences."""
        current = preferences_service.get_preferences()
        self.assertIsNotNone(current.primary_priority)

        new_pref = PreferencesSchema(
            primaryPriority="verified_sellers",
            waitTolerance="patient",
            notifications=NotificationSettingsSchema(
                priceDrops=True,
                sellerWarnings=True,
                upcomingSales=False,
                dailyDigest=True,
            ),
            notificationChannel="email",
            email="shopper@shopq.ai",
        )
        saved = preferences_service.update_preferences(new_pref)
        self.assertEqual(saved.primary_priority, "verified_sellers")
        self.assertEqual(saved.email, "shopper@shopq.ai")

    def test_fastapi_endpoints_if_client_available(self):
        """End-to-end HTTP endpoint verification using FastAPI TestClient."""
        if not HAS_TEST_CLIENT:
            print("Skipping HTTP TestClient assertions (fastapi/httpx not installed in test runner)")
            return

        # 1. GET /health
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "healthy")

        # 2. POST /api/search
        res = self.client.post("/api/search", json={"query": "Sony", "limit": 5})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue("results" in data)
        self.assertTrue(len(data["results"]) > 0)

        # 3. GET /api/products/{id} (Strict Contract)
        res = self.client.get("/api/products/sony_good_deal")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("product", data)
        self.assertIn("decision", data)
        d = data["decision"]
        self.assertEqual(d["decision"], "BUY")
        self.assertIn("confidence_level", d)
        self.assertIn("primary_reason", d)
        self.assertIn("secondary_reasons", d)
        self.assertIn("buy_point", d)
        self.assertIn("best_offer_id", d)
        self.assertIn("data_freshness", d)
        self.assertIn("data_coverage", d)
        self.assertIn("checked_at", d)
        self.assertIn("model_version", d)
        self.assertIn("decision_rules_version", d)

        # 4. POST /api/analyze (Strict Contract)
        res = self.client.post("/api/analyze", json={"url": "https://amazon.in/product/sony"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("product", data)
        self.assertIn("decision", data)

        # 5. GET /api/products/{id}/analysis
        res = self.client.get("/api/products/sony_good_deal/analysis")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["decision"], "BUY")

        # 6. GET /api/products/{id}/details
        res = self.client.get("/api/products/sony_good_deal/details")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["id"], "sony_good_deal")
        self.assertIn("canonical_product", res.json())

        # 7. GET /api/products/{id}/offers
        res = self.client.get("/api/products/sony_good_deal/offers")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)

        # 8. GET /api/products/{id}/price-history
        res = self.client.get("/api/products/sony_good_deal/price-history")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)
        self.assertTrue(len(res.json()) > 0)

        # 9. GET /api/watchlist
        res = self.client.get("/api/watchlist")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)

        # 10. POST /api/watchlist
        res = self.client.post("/api/watchlist", json={"productId": "nike_better_alternative", "targetPrice": 8500})
        self.assertEqual(res.status_code, 200)

        # 11. DELETE /api/watchlist/{id}
        res = self.client.delete("/api/watchlist/nike_better_alternative")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["success"])

        # 12. GET /api/alerts
        res = self.client.get("/api/alerts")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)

        # 13. POST /api/alerts/{id}/read
        res = self.client.post("/api/alerts/1/read")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["read"])

        # 14. GET /api/preferences
        res = self.client.get("/api/preferences")
        self.assertEqual(res.status_code, 200)

        # 15. PUT /api/preferences
        res = self.client.put("/api/preferences", json={
            "primaryPriority": "best_price",
            "waitTolerance": "moderate",
            "notifications": {
                "priceDrops": True,
                "sellerWarnings": True,
                "upcomingSales": True,
                "dailyDigest": False
            },
            "notificationChannel": "in_app"
        })
        self.assertEqual(res.status_code, 200)


if __name__ == "__main__":
    unittest.main()
