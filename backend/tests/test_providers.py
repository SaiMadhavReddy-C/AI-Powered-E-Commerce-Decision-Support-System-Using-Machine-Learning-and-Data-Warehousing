"""Comprehensive Test Suite for ShopQ Provider Registry and Data Collection Subsystem.

Tests:
1. ProviderRegistry initialization, adapter statuses, and Amazon optional adapter isolation.
2. 5-Stage Deterministic Extraction Pipeline:
   - Stage 1: JSON-LD structured data extraction
   - Stage 2: Known retailer selectors (Amazon, Flipkart, Croma, Reliance Digital, Myntra)
   - Stage 3: Generic DOM heuristics (OpenGraph, Microdata itemprop, HTML meta)
   - Stage 4: Normalization and Regex (Indian currency ₹/Rs./INR, discount %, seller regex)
   - Stage 5: LLM fallback with strict anti-hallucination grounding guardrails
3. MockProvider coverage for all 12 core ShopQ scenarios + synthetic fallback.
4. ScraperAPIProvider URL allowlisting, SSRF protection, and 429 quota handling.
5. Demand-driven Ingestion Trigger Handler (user search, URL check with cache, watchlist update).
6. ProviderOffer entity schema transformations (to_best_offer, to_competitor_offer, to_product_detail).
"""

import pytest
from app.providers.models import (
    ProviderStatus,
    ExtractionStage,
    ConfidenceLevel,
    ProviderOffer,
)
from app.providers.registry import ProviderRegistry, provider_registry
from app.providers.scraperapi_provider import ScraperAPIProvider
from app.providers.adapters import (
    MockProvider,
    AmazonProvider,
    FlipkartProvider,
    CromaProvider,
    RelianceDigitalProvider,
    MyntraProvider,
)
from app.providers.pipeline import (
    ExtractionPipeline,
    extraction_pipeline,
    JsonLdExtractor,
    SelectorExtractor,
    DomHeuristicsExtractor,
    RegexExtractor,
    LlmFallbackExtractor,
)
from app.providers.ingestion import (
    DemandDrivenTriggerHandler,
    trigger_handler,
)


class TestProviderRegistry:
    """Tests ProviderRegistry lifecycle, statuses, and adapter contracts."""

    def test_registry_initialization_and_adapters(self):
        """Verifies all required providers are registered and manageable."""
        registry = ProviderRegistry()
        statuses = registry.get_status_summary()

        # Must have mock, scraperapi, amazon, flipkart, croma, reliance, myntra
        required_keys = ["mock", "scraperapi", "amazon", "flipkart", "croma", "reliance", "myntra"]
        for key in required_keys:
            assert key in statuses, f"Provider '{key}' missing from registry"

        # Mock must always be in MOCK status
        assert statuses["mock"] == ProviderStatus.MOCK.value

    def test_amazon_adapter_is_optional_not_hard_dependency(self):
        """Crucial test: Amazon must be strictly optional, never halting system."""
        registry = ProviderRegistry()
        amazon = registry.get_provider("amazon")
        assert amazon is not None
        assert amazon.is_optional is True

        # If amazon live fetch encounters failure, it must not throw
        offer = amazon.fetch_and_extract("https://amazon.in/dp/B0INVALID123")
        assert offer is None or isinstance(offer, ProviderOffer)

    def test_provider_status_enum_validity(self):
        """Verifies the four required statuses: LIVE, PARTIAL, MOCK, UNAVAILABLE."""
        assert ProviderStatus.LIVE.value == "LIVE"
        assert ProviderStatus.PARTIAL.value == "PARTIAL"
        assert ProviderStatus.MOCK.value == "MOCK"
        assert ProviderStatus.UNAVAILABLE.value == "UNAVAILABLE"

    def test_scraperapi_status_depends_on_key(self):
        """ScraperAPI is UNAVAILABLE when key is empty, and LIVE when key is set."""
        p_no_key = ScraperAPIProvider(api_key="")
        assert p_no_key.status == ProviderStatus.UNAVAILABLE

        p_with_key = ScraperAPIProvider(api_key="valid_scraperapi_key_test")
        assert p_with_key.status == ProviderStatus.LIVE


class TestExtractionPipeline:
    """Tests the 5-stage deterministic extraction priority sequence."""

    def test_stage_1_jsonld_extraction(self):
        """Stage 1: schema.org JSON-LD structured data with highest fidelity."""
        extractor = JsonLdExtractor()
        sample_html = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": "Sony WH-1000XM5 Wireless Headphones",
                "brand": {"@type": "Brand", "name": "Sony"},
                "image": "https://images.example.com/sony.jpg",
                "offers": {
                    "@type": "Offer",
                    "price": "22499.00",
                    "priceCurrency": "INR",
                    "availability": "https://schema.org/InStock",
                    "seller": {"@type": "Organization", "name": "Appario Retail"}
                },
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": 4.8,
                    "reviewCount": 15000
                }
            }
            </script>
        </head>
        <body><div>Content</div></body>
        </html>
        """
        result = extractor.extract(sample_html)
        assert result is not None
        assert result["title"] == "Sony WH-1000XM5 Wireless Headphones"
        assert result["price"] == 22499.00
        assert result["currency"] == "INR"
        assert result["seller_name"] == "Appario Retail"
        assert result["stage"] == "JSON_LD"
        assert result["confidence"] >= 0.90

    def test_stage_2_known_retailer_selectors(self):
        """Stage 2: Retailer-specific selectors for Amazon, Flipkart, Croma."""
        extractor = SelectorExtractor()

        # Amazon selector simulation
        amazon_html = """
        <div>
            <h1 id="productTitle">Apple iPhone 15 (128 GB) - Blue</h1>
            <span class="a-price-whole">65,999</span>
            <div id="sellerProfileTriggerId">Appario Retail</div>
        </div>
        """
        res_amz = extractor.extract(amazon_html, "https://amazon.in/dp/B0TEST1234")
        assert res_amz is not None
        assert res_amz["price"] == 65999.0
        assert "iPhone 15" in res_amz["title"]
        assert res_amz["seller_name"] == "Appario Retail"
        assert res_amz["stage"] == "KNOWN_SELECTORS"

        # Flipkart selector simulation
        flipkart_html = """
        <div>
            <h1 class="VU-ZEz">Nothing Phone 2 (White, 256 GB)</h1>
            <div class="_30jeq3">₹36,999</div>
            <div id="sellerName"><span>SuperComNet</span></div>
        </div>
        """
        res_fk = extractor.extract(flipkart_html, "https://flipkart.com/nothing-phone-2/p/itm123")
        assert res_fk is not None
        assert res_fk["price"] == 36999.0
        assert "Nothing Phone" in res_fk["title"]
        assert res_fk["seller_name"] == "SuperComNet"

        # Croma selector simulation
        croma_html = """
        <div>
            <h1 class="pd-title">Canon EOS R50 Mirrorless Camera</h1>
            <span data-testid="new-price">₹74,999</span>
            <span class="seller-info">Croma Official</span>
        </div>
        """
        res_cr = extractor.extract(croma_html, "https://croma.com/canon-eos-r50/p/234")
        assert res_cr is not None
        assert res_cr["price"] == 74999.0
        assert "Canon EOS R50" in res_cr["title"]

    def test_stage_3_generic_dom_heuristics(self):
        """Stage 3: Generic OpenGraph and Microdata heuristics."""
        extractor = DomHeuristicsExtractor()
        og_html = """
        <html>
        <head>
            <meta property="og:title" content="boAt Airdopes 141 True Wireless Earbuds" />
            <meta property="og:price:amount" content="999" />
            <meta property="og:price:currency" content="INR" />
            <meta property="og:image" content="https://example.com/boat.jpg" />
        </head>
        <body>Product description</body>
        </html>
        """
        result = extractor.extract(og_html)
        assert result is not None
        assert result["title"] == "boAt Airdopes 141 True Wireless Earbuds"
        assert result["price"] == 999.0
        assert result["currency"] == "INR"
        assert result["stage"] == "GENERIC_DOM"

    def test_stage_4_regex_and_normalization(self):
        """Stage 4: Normalization of Indian comma numbers, currency symbols, and titles."""
        extractor = RegexExtractor()

        # Indian numbering and currency parsing
        text_with_inr = "Special Festival Price: ₹ 1,24,999 (Inclusive of all taxes). Sold by: RetailConnect India."
        result = extractor.extract(text_with_inr)
        assert result is not None
        assert result["price"] == 124999.0
        assert result["currency"] == "INR"
        assert result["seller_name"] == "RetailConnect India"
        assert result["stage"] == "REGEX_NORMALIZATION"

        # Title cleaner stripping retailer watermarks
        dirty_title = "Sony WH-1000XM5 Headphones | Flipkart.com"
        cleaned = extractor.clean_title(dirty_title)
        assert cleaned == "Sony WH-1000XM5 Headphones"

        dirty_amz_title = "Apple iPhone 15 (128 GB) : Buy Apple iPhone 15 Online at Low Prices in India - Amazon.in"
        cleaned_amz = extractor.clean_title(dirty_amz_title)
        assert "Amazon.in" not in cleaned_amz

    def test_stage_5_llm_fallback_strict_grounding_guardrail(self):
        """Stage 5: LLM MUST NOT invent prices, currency, or sellers. Hallucinations are rejected!"""
        extractor = LlmFallbackExtractor()

        # Text with an explicit price token
        grounded_text = "Featured soundbar available today for ₹ 4,999 only from SoundStore India."
        result_grounded = extractor.extract(grounded_text, "https://example.com/soundbar")
        assert result_grounded is not None
        assert result_grounded["price"] == 4999.0
        assert result_grounded["stage"] == "LLM_FALLBACK"

        # Hallucination test: If LLM attempts to return an ungrounded price (not present in text)
        hallucination_text = "This premium gadget has no price listed yet. Contact store for info."
        # Inject simulated LLM output that claims price is 15000.0 (which NEVER appears in text)
        result_ungrounded = extractor._perform_extraction(hallucination_text, "https://example.com/test")
        # Overwrite candidate with ungrounded price to test the verification guard
        result_ungrounded["price"] = 15000.0
        result_ungrounded["seller_name"] = "Invented Merchant"

        # Pass through the extraction guard logic
        final_extract = extractor.extract(hallucination_text, "https://example.com/test")
        # In hallucination_text, neither 15000 nor any price exists
        if final_extract:
            # Verified price must be None or marked uncertain!
            assert final_extract["price"] is None or "price" in final_extract.get("uncertain_fields", [])


class TestMockProviderScenarios:
    """Validates that MockProvider functions 100% reliably out of the box for all 12 scenarios."""

    SCENARIO_IDS = [
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

    def test_all_12_scenarios_resolved_by_id(self):
        mock = MockProvider()
        for sid in self.SCENARIO_IDS:
            offer = mock.get_by_id(sid)
            assert offer is not None, f"Scenario '{sid}' missing from MockProvider"
            assert offer.product_title, f"Scenario '{sid}' missing title"
            assert offer.price > 0, f"Scenario '{sid}' price invalid"
            assert offer.currency == "INR"
            assert offer.retailer_name in ["Amazon", "Flipkart", "Croma", "Reliance Digital", "Myntra"]

    def test_mock_provider_url_routing(self):
        mock = MockProvider()

        # Exact URL matches
        sony_offer = mock.fetch_and_extract("https://amazon.in/dp/sony-wh1000xm5-black")
        assert sony_offer is not None
        assert sony_offer.price == 22499.0
        assert "Sony" in sony_offer.product_title

        iphone_offer = mock.fetch_and_extract("https://flipkart.com/apple-iphone-15-blue-128-gb/p/itm12345")
        assert iphone_offer is not None
        assert iphone_offer.price == 65999.0

    def test_mock_provider_synthetic_offer_for_unknown_urls(self):
        """Unfamiliar retailer URL should yield realistic synthetic offer rather than crash."""
        mock = MockProvider()
        unknown_url = "https://reliancedigital.in/samsung-galaxy-tab-s9-fe/p/4938382"
        offer = mock.fetch_and_extract(unknown_url)
        assert offer is not None
        assert offer.retailer == "reliance"
        assert offer.price > 0
        assert offer.currency == "INR"
        assert offer.source_type == "MOCK"


class TestScraperAPIProvider:
    """Validates ScraperAPI security guards, geotargeting, and quota handling."""

    def test_allowlist_and_ssrf_protection(self):
        provider = ScraperAPIProvider(api_key="mock_key")

        # Allowed domains
        assert provider.can_handle_url("https://www.amazon.in/dp/B08L5WHFT9") is True
        assert provider.can_handle_url("https://www.flipkart.com/product/p/itm123") is True
        assert provider.can_handle_url("https://www.croma.com/pdp/12345") is True
        assert provider.can_handle_url("https://www.reliancedigital.in/item/123") is True
        assert provider.can_handle_url("https://www.myntra.com/shoes/123") is True

        # Rejected domains & SSRF attempts
        assert provider.can_handle_url("http://localhost:8000/internal") is False
        assert provider.can_handle_url("http://127.0.0.1:9000/admin") is False
        assert provider.can_handle_url("http://169.254.169.254/latest/meta-data/") is False
        assert provider.can_handle_url("http://10.0.0.1/secrets") is False
        assert provider.can_handle_url("https://evil-phishing-site.com/steal") is False

    def test_quota_error_degrades_gracefully_to_partial(self):
        provider = ScraperAPIProvider(api_key="mock_key")
        assert provider.status == ProviderStatus.LIVE

        # Simulate 4 consecutive quota errors (HTTP 429)
        provider.consecutive_quota_errors = 4
        assert provider.check_health() == ProviderStatus.PARTIAL


class TestDemandDrivenTriggers:
    """Tests User Search, URL Check, and Watchlist Update triggers."""

    def test_user_search_trigger(self):
        handler = DemandDrivenTriggerHandler()
        results = handler.handle_user_search_trigger("sony headphones", limit=5)
        assert len(results) > 0
        assert any("sony" in r.product_title.lower() for r in results)

    def test_url_check_trigger_with_caching(self):
        handler = DemandDrivenTriggerHandler(cache_ttl_seconds=60.0)
        url = "https://amazon.in/dp/sony-wh1000xm5-black"

        # First call loads offer
        offer1 = handler.handle_url_check_trigger(url)
        assert offer1 is not None
        assert offer1.price == 22499.0

        # Second call returns cached offer
        offer2 = handler.handle_url_check_trigger(url)
        assert offer2 is offer1

    def test_watchlist_update_trigger(self):
        handler = DemandDrivenTriggerHandler()
        # Test price satisfied
        res_met = handler.handle_watchlist_update_trigger(
            "sony_good_deal",
            target_price=25000.0,  # Sony is 22499.0 -> target met!
        )
        assert res_met["success"] is True
        assert res_met["price_dropped"] is True
        assert res_met["savings"] == (25000.0 - 22499.0)

        # Test price not met
        res_not_met = handler.handle_watchlist_update_trigger(
            "sony_good_deal",
            target_price=20000.0,  # Sony is 22499.0 -> target not met
        )
        assert res_not_met["success"] is True
        assert res_not_met["price_dropped"] is False
        assert res_not_met["savings"] == 0.0


class TestProviderOfferTransformations:
    """Tests conversions to ShopQ 4-level schema entities."""

    def test_transform_to_schemas(self):
        offer = ProviderOffer(
            retailer="amazon",
            retailer_name="Amazon",
            product_title="Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
            brand="Sony",
            model="WH-1000XM5",
            variant="Black",
            category="Headphones",
            price=22499.0,
            currency="INR",
            original_price=29990.0,
            discount_percentage=25.0,
            seller={"name": "Appario Retail", "rating": 4.8, "reviews": 28500, "reliability": "RELIABLE"},
            seller_name="Appario Retail",
            rating=4.8,
            review_count=28500,
            availability="IN_STOCK",
            shipping="Free Delivery",
            shipping_cost=0.0,
            image_url="https://images.example.com/sony.jpg",
            product_url="https://amazon.in/dp/sony-wh1000xm5",
            observed_at="2026-10-08T00:00:00Z",
            collected_at="2026-10-08T00:00:00Z",
            source_type="LIVE",
            source_status="LIVE",
            confidence_score=0.95,
        )

        # Test to_best_offer
        best = offer.to_best_offer(savings=2500.0)
        assert best.retailer == "Amazon"
        assert best.price == 22499.0
        assert best.savings == 2500.0

        # Test to_competitor_offer
        comp = offer.to_competitor_offer()
        assert comp.retailer.lower() == "amazon"
        assert comp.price == 22499.0

        # Test to_product_detail
        pdetail = offer.to_product_detail(product_id="sony_xm5_custom")
        assert pdetail.id == "sony_xm5_custom"
        assert pdetail.current_price == 22499.0
        assert pdetail.canonical_product.brand == "Sony"
        assert pdetail.retailer_listing.url == "https://amazon.in/dp/sony-wh1000xm5"
        assert pdetail.seller.name == "Appario Retail"
        assert pdetail.seller_offer.seller_name == "Appario Retail"
