"""Mock Provider for ShopQ.

100% reliable out-of-the-box fallback implementation.
Provides deterministic, realistic store offers for all 12 core ShopQ scenarios,
cross-retailer competitor matrices, and synthetic offer resolution for arbitrary queries.
"""

import datetime
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

from app.providers.base import BaseProvider
from app.providers.models import ProviderStatus, ProviderOffer
from app.core.logging import logger


class MockProvider(BaseProvider):
    """
    Fallback data provider delivering realistic e-commerce offers.
    Zero external network calls; 100% reliable uptime.
    """

    ALLOWED_DOMAINS = [
        "amazon.in",
        "flipkart.com",
        "croma.com",
        "reliancedigital.in",
        "myntra.com",
        "shopq.local",
    ]

    def __init__(self):
        super().__init__(
            retailer_id="mock",
            display_name="ShopQ Mock Data Provider",
            allowed_domains=self.ALLOWED_DOMAINS,
            status=ProviderStatus.MOCK,
            is_optional=False,
        )
        self._offers: Dict[str, ProviderOffer] = {}
        self._url_mapping: Dict[str, str] = {}
        self._scenario_mapping: Dict[str, str] = {}
        self._init_scenario_catalog()

    def check_health(self) -> ProviderStatus:
        """Mock provider is always operational."""
        self.status = ProviderStatus.MOCK
        return ProviderStatus.MOCK

    def _init_scenario_catalog(self):
        """Seeds the 12 primary ShopQ scenario offers with exact data contracts."""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        two_mins_ago = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=2)).isoformat()
        fourteen_days_ago = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14)).isoformat()

        scenarios = [
            # 1. sony_good_deal
            ProviderOffer(
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
                seller={
                    "name": "Appario Retail",
                    "rating": 4.8,
                    "reviews": 28500,
                    "reliability": "RELIABLE",
                    "returnPolicy": "10-day replacement",
                    "warranty": "1 year manufacturer",
                },
                seller_name="Appario Retail",
                rating=4.8,
                review_count=28500,
                availability="IN_STOCK",
                shipping="Free Express Delivery",
                shipping_cost=0.0,
                image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80",
                product_url="https://amazon.in/dp/sony-wh1000xm5-black",
                observed_at=two_mins_ago,
                collected_at=now,
                source_type="MOCK",
                source_status="MOCK",
                confidence_score=0.98,
                extraction_stage="MOCK_DATA",
            ),
            # 2. iphone_wait
            ProviderOffer(
                retailer="flipkart",
                retailer_name="Flipkart",
                product_title="Apple iPhone 15 (Blue, 128 GB)",
                brand="Apple",
                model="iPhone 15",
                variant="128GB, Blue",
                category="Smartphones",
                price=65999.0,
                currency="INR",
                original_price=79900.0,
                discount_percentage=17.0,
                seller={
                    "name": "SuperComNet",
                    "rating": 4.6,
                    "reviews": 54000,
                    "reliability": "RELIABLE",
                    "returnPolicy": "7-day replacement",
                    "warranty": "1 year Apple warranty",
                },
                seller_name="SuperComNet",
                rating=4.6,
                review_count=54000,
                availability="IN_STOCK",
                shipping="Free Delivery",
                shipping_cost=0.0,
                image_url="https://placehold.co/300x300/FAF8F5/1A1A1A?text=iPhone",
                product_url="https://flipkart.com/apple-iphone-15-blue-128-gb/p/itm12345",
                observed_at=two_mins_ago,
                collected_at=now,
                source_type="MOCK",
                source_status="MOCK",
                confidence_score=0.96,
                extraction_stage="MOCK_DATA",
            ),
            # 3. nike_better_alternative
            ProviderOffer(
                retailer="amazon",
                retailer_name="Amazon",
                product_title="Nike Air Max 90 Men's Running Shoes",
                brand="Nike",
                model="Air Max 90",
                variant="White/Black, UK 9",
                category="Footwear",
                price=11499.0,
                currency="INR",
                original_price=11999.0,
                discount_percentage=4.0,
                seller={
                    "name": "RetailNet",
                    "rating": 4.2,
                    "reviews": 1400,
                    "reliability": "RELIABLE",
                    "returnPolicy": "10-day return",
                    "warranty": "6 months manufacturer",
                },
                seller_name="RetailNet",
                rating=4.2,
                review_count=1400,
                availability="IN_STOCK",
                shipping="Standard Delivery",
                shipping_cost=0.0,
                image_url="https://placehold.co/300x300/FAF8F5/1A1A1A?text=Nike",
                product_url="https://amazon.in/dp/nike-air-max-90",
                observed_at=two_mins_ago,
                collected_at=now,
                source_type="MOCK",
                source_status="MOCK",
                confidence_score=0.95,
                extraction_stage="MOCK_DATA",
            ),
            # 4. laptop_suspicious_seller
            ProviderOffer(
                retailer="amazon",
                retailer_name="Amazon",
                product_title="HP Pavilion 14 Laptop (13th Gen Intel Core i5, 16GB, 512GB SSD)",
                brand="HP",
                model="Pavilion 14",
                variant="i5 13th Gen, 16GB RAM, 512GB SSD",
                category="Computers",
                price=46999.0,
                currency="INR",
                original_price=64999.0,
                discount_percentage=27.0,
                seller={
                    "name": "QuickDeal Electro Store",
                    "rating": 2.3,
                    "reviews": 34,
                    "reliability": "RISKY",
                    "returnPolicy": "No returns, replacement only",
                    "warranty": "Seller warranty only",
                },
                seller_name="QuickDeal Electro Store",
                rating=2.3,
                review_count=34,
                availability="IN_STOCK",
                shipping="Standard Delivery",
                shipping_cost=0.0,
                image_url="https://placehold.co/300x300/FAF8F5/1A1A1A?text=HP",
                product_url="https://amazon.in/dp/hp-pavilion-14",
                observed_at=two_mins_ago,
                collected_at=now,
                source_type="MOCK",
                source_status="MOCK",
                confidence_score=0.75,
                extraction_stage="MOCK_DATA",
            ),
            # 5. new_product_no_history
            ProviderOffer(
                retailer="croma",
                retailer_name="Croma",
                product_title="Canon EOS R50 Mirrorless Camera (Body Only, Black)",
                brand="Canon",
                model="EOS R50",
                variant="Body Only, Black",
                category="Cameras",
                price=74999.0,
                currency="INR",
                original_price=74999.0,
                discount_percentage=0.0,
                seller={
                    "name": "Croma Official",
                    "rating": 4.8,
                    "reviews": 14,
                    "reliability": "RELIABLE",
                    "returnPolicy": "7-day replacement",
                    "warranty": "2 years manufacturer",
                },
                seller_name="Croma Official",
                rating=4.8,
                review_count=14,
                availability="IN_STOCK",
                shipping="Free Delivery",
                shipping_cost=0.0,
                image_url="https://placehold.co/300x300/FAF8F5/1A1A1A?text=Canon",
                product_url="https://croma.com/canon-eos-r50-mirrorless",
                observed_at=two_mins_ago,
                collected_at=now,
                source_type="MOCK",
                source_status="MOCK",
                confidence_score=0.60,
                extraction_stage="MOCK_DATA",
            ),
            # 6. stale_price
            ProviderOffer(
                retailer="amazon",
                retailer_name="Amazon",
                product_title="Amazon Kindle Paperwhite (16 GB) - 6.8 inch display",
                brand="Amazon",
                model="Kindle Paperwhite",
                variant="16GB, Black, 6.8 inch",
                category="Electronics",
                price=14999.0,
                currency="INR",
                original_price=14999.0,
                discount_percentage=0.0,
                seller={
                    "name": "Cocoblu Retail",
                    "rating": 4.4,
                    "reviews": 8900,
                    "reliability": "RELIABLE",
                    "returnPolicy": "7-day replacement",
                    "warranty": "1 year manufacturer",
                },
                seller_name="Cocoblu Retail",
                rating=4.4,
                review_count=8900,
                availability="IN_STOCK",
                shipping="Free Delivery",
                shipping_cost=0.0,
                image_url="https://placehold.co/300x300/FAF8F5/1A1A1A?text=Kindle",
                product_url="https://amazon.in/dp/kindle-paperwhite-16gb",
                observed_at=fourteen_days_ago,
                collected_at=fourteen_days_ago,
                source_type="MOCK",
                source_status="MOCK",
                confidence_score=0.55,
                uncertain_fields=["price_freshness"],
                extraction_stage="MOCK_DATA",
            ),
            # 7. variant_mismatch
            ProviderOffer(
                retailer="flipkart",
                retailer_name="Flipkart",
                product_title="Apple MacBook Air 13.6-inch M2 (16GB RAM, 512GB SSD, Space Grey)",
                brand="Apple",
                model="MacBook Air M2",
                variant="16GB RAM, 512GB SSD, Space Grey",
                category="Computers",
                price=79990.0,
                currency="INR",
                original_price=119900.0,
                discount_percentage=33.0,
                seller={
                    "name": "IndiTechRetail",
                    "rating": 3.8,
                    "reviews": 820,
                    "reliability": "MODERATE",
                    "returnPolicy": "7-day replacement",
                    "warranty": "1 year Apple warranty",
                },
                seller_name="IndiTechRetail",
                rating=3.8,
                review_count=820,
                availability="IN_STOCK",
                shipping="Free Delivery",
                shipping_cost=0.0,
                image_url="https://placehold.co/300x300/FAF8F5/1A1A1A?text=MacBook",
                product_url="https://flipkart.com/apple-macbook-air-m2/p/itmmacbook",
                observed_at=two_mins_ago,
                collected_at=now,
                source_type="MOCK",
                source_status="MOCK",
                confidence_score=0.70,
                uncertain_fields=["hardware_variant"],
                extraction_stage="MOCK_DATA",
            ),
            # 8. all_sources_failed
            ProviderOffer(
                retailer="flipkart",
                retailer_name="Flipkart",
                product_title="Google Pixel 8 Pro (Obsidian, 128 GB)",
                brand="Google",
                model="Pixel 8 Pro",
                variant="128GB, Obsidian",
                category="Smartphones",
                price=84999.0,
                currency="INR",
                original_price=106999.0,
                discount_percentage=20.0,
                seller={
                    "name": "Unverified Source",
                    "rating": 0.0,
                    "reviews": 0,
                    "reliability": "UNKNOWN",
                    "returnPolicy": "Unknown",
                    "warranty": "Unknown",
                },
                seller_name="Unverified Source",
                rating=0.0,
                review_count=0,
                availability="UNKNOWN",
                shipping="Unknown",
                shipping_cost=0.0,
                image_url="https://placehold.co/300x300/FAF8F5/1A1A1A?text=Pixel",
                product_url="https://flipkart.com/google-pixel-8-pro/p/itmpixel",
                observed_at=two_mins_ago,
                collected_at=now,
                source_type="MOCK",
                source_status="MOCK",
                confidence_score=0.20,
                uncertain_fields=["price", "seller", "availability"],
                extraction_stage="MOCK_DATA",
            ),
            # 9. seller_changed
            ProviderOffer(
                retailer="amazon",
                retailer_name="Amazon",
                product_title="Samsung Galaxy S24 5G (Onyx Black, 256GB)",
                brand="Samsung",
                model="Galaxy S24",
                variant="256GB, Onyx Black",
                category="Smartphones",
                price=59999.0,
                currency="INR",
                original_price=79999.0,
                discount_percentage=25.0,
                seller={
                    "name": "FastGizmos Unlimited",
                    "rating": 3.1,
                    "reviews": 42,
                    "reliability": "MODERATE",
                    "returnPolicy": "7-day replacement",
                    "warranty": "1 year manufacturer",
                },
                seller_name="FastGizmos Unlimited",
                rating=3.1,
                review_count=42,
                availability="IN_STOCK",
                shipping="Standard Merchant Delivery",
                shipping_cost=0.0,
                image_url="https://placehold.co/300x300/FAF8F5/1A1A1A?text=Samsung",
                product_url="https://amazon.in/dp/samsung-galaxy-s24",
                observed_at=two_mins_ago,
                collected_at=now,
                source_type="MOCK",
                source_status="MOCK",
                confidence_score=0.72,
                uncertain_fields=["seller_reputation"],
                extraction_stage="MOCK_DATA",
            ),
            # 10. out_of_stock
            ProviderOffer(
                retailer="amazon",
                retailer_name="Amazon",
                product_title="Sony PlayStation 5 Pro Console (2TB, White)",
                brand="Sony",
                model="PS5 Pro",
                variant="2TB, White",
                category="Gaming",
                price=79990.0,
                currency="INR",
                original_price=69990.0,
                discount_percentage=0.0,
                seller={
                    "name": "ScalperDeals Hub",
                    "rating": 3.5,
                    "reviews": 18,
                    "reliability": "MODERATE",
                    "returnPolicy": "No returns",
                    "warranty": "Seller warranty only",
                },
                seller_name="ScalperDeals Hub",
                rating=3.5,
                review_count=18,
                availability="OUT_OF_STOCK",
                shipping="Merchant Fulfilled",
                shipping_cost=500.0,
                image_url="https://placehold.co/300x300/FAF8F5/1A1A1A?text=PS5+Pro",
                product_url="https://amazon.in/dp/ps5-pro-console",
                observed_at=two_mins_ago,
                collected_at=now,
                source_type="MOCK",
                source_status="MOCK",
                confidence_score=0.90,
                uncertain_fields=["official_availability"],
                extraction_stage="MOCK_DATA",
            ),
            # 11. your_call
            ProviderOffer(
                retailer="amazon",
                retailer_name="Amazon",
                product_title="boAt Airdopes 141 True Wireless Earbuds",
                brand="boAt",
                model="Airdopes 141",
                variant="Bold Black",
                category="Accessories",
                price=999.0,
                currency="INR",
                original_price=4490.0,
                discount_percentage=78.0,
                seller={
                    "name": "Cocoblu Retail",
                    "rating": 4.3,
                    "reviews": 154000,
                    "reliability": "RELIABLE",
                    "returnPolicy": "7-day replacement",
                    "warranty": "1 year manufacturer",
                },
                seller_name="Cocoblu Retail",
                rating=4.3,
                review_count=154000,
                availability="IN_STOCK",
                shipping="Free Delivery",
                shipping_cost=0.0,
                image_url="https://placehold.co/300x300/FAF8F5/1A1A1A?text=boAt",
                product_url="https://amazon.in/dp/boat-airdopes-141",
                observed_at=two_mins_ago,
                collected_at=now,
                source_type="MOCK",
                source_status="MOCK",
                confidence_score=0.95,
                extraction_stage="MOCK_DATA",
            ),
            # 12. no_decision
            ProviderOffer(
                retailer="flipkart",
                retailer_name="Flipkart",
                product_title="Nothing Ear (2) Wireless Earbuds (White)",
                brand="Nothing",
                model="Ear (2)",
                variant="White, Hi-Res Audio",
                category="Headphones",
                price=7499.0,
                currency="INR",
                original_price=9999.0,
                discount_percentage=25.0,
                seller={
                    "name": "SuperComNet",
                    "rating": 4.2,
                    "reviews": 3400,
                    "reliability": "RELIABLE",
                    "returnPolicy": "7-day replacement",
                    "warranty": "1 year manufacturer",
                },
                seller_name="SuperComNet",
                rating=4.2,
                review_count=3400,
                availability="IN_STOCK",
                shipping="Free Delivery",
                shipping_cost=0.0,
                image_url="https://placehold.co/300x300/FAF8F5/1A1A1A?text=Nothing",
                product_url="https://flipkart.com/nothing-ear-2-white/p/itmnothing",
                observed_at=two_mins_ago,
                collected_at=now,
                source_type="MOCK",
                source_status="MOCK",
                confidence_score=0.50,
                uncertain_fields=["price_trend_stability"],
                extraction_stage="MOCK_DATA",
            ),
        ]

        scenario_ids = [
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

        for sid, offer in zip(scenario_ids, scenarios):
            self._offers[sid] = offer
            self._url_mapping[offer.product_url.lower()] = sid
            self._scenario_mapping[sid] = offer.product_url

    def fetch_and_extract(self, url: str) -> Optional[ProviderOffer]:
        """Resolves offer from mock catalog by exact or partial URL matching."""
        if not url:
            return None

        clean_url = url.lower().strip()

        # 1. Exact match
        if clean_url in self._url_mapping:
            sid = self._url_mapping[clean_url]
            return self._offers.get(sid)

        # 2. Token / keyword match against scenarios with matching retailer domain
        parsed = urlparse(clean_url)
        url_domain = (parsed.hostname or "").lower()

        for sid, offer in self._offers.items():
            if sid in clean_url:
                return offer

            # Domain must be compatible if domain is known
            offer_domain = urlparse(offer.product_url).hostname or ""
            if url_domain and offer_domain and url_domain != offer_domain:
                continue

            # Check significant keywords (length >= 4) from title
            significant_terms = [
                term for term in offer.product_title.lower().split()[:4]
                if len(term) >= 4 and not term.isdigit()
            ]
            if any(term in clean_url for term in significant_terms):
                return offer

        # 3. Dynamic generic fallback for uncataloged URLs from allowed retailers
        return self._generate_synthetic_offer(url)

    def search(self, query: str, limit: int = 5) -> List[ProviderOffer]:
        """Searches mock store by keyword, SKU, or URL."""
        if not query:
            return list(self._offers.values())[:limit]

        lower = query.lower().strip()

        # Check if query is a URL
        if lower.startswith("http://") or lower.startswith("https://") or ".com" in lower or ".in" in lower:
            matched = self.fetch_and_extract(query)
            return [matched] if matched else []

        matches: List[ProviderOffer] = []
        tokens = lower.split()

        for sid, offer in self._offers.items():
            haystack = f"{sid} {offer.product_title} {offer.brand or ''} {offer.retailer_name}".lower()
            if any(t in haystack for t in tokens):
                matches.append(offer)

        if not matches:
            # Default to first scenario
            matches = [self._offers["sony_good_deal"]]

        return matches[:limit]

    def get_by_id(self, product_id: str) -> Optional[ProviderOffer]:
        """Direct lookup by scenario identifier."""
        return self._offers.get(product_id)

    def _generate_synthetic_offer(self, url: str) -> ProviderOffer:
        """Generates a realistic, deterministic offer for any unfamiliar retailer URL."""
        parsed = urlparse(url)
        domain = (parsed.hostname or "amazon.in").lower()
        retailer = "amazon"
        retailer_name = "Amazon"

        if "flipkart" in domain:
            retailer, retailer_name = "flipkart", "Flipkart"
        elif "croma" in domain:
            retailer, retailer_name = "croma", "Croma"
        elif "reliance" in domain:
            retailer, retailer_name = "reliance", "Reliance Digital"
        elif "myntra" in domain:
            retailer, retailer_name = "myntra", "Myntra"

        # Generate realistic title from path
        path_segments = [seg for seg in parsed.path.split("/") if seg and seg not in ("dp", "p", "product")]
        title_slug = path_segments[-1] if path_segments else "Consumer Electronics Item"
        title = " ".join(word.capitalize() for word in title_slug.replace("-", " ").replace("_", " ").split())
        if len(title) < 5:
            title = f"{retailer_name} Featured Product"

        price_hash = abs(hash(url)) % 50000 + 999.0
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return ProviderOffer(
            retailer=retailer,
            retailer_name=retailer_name,
            product_title=title,
            brand="Verified Brand",
            category="Electronics",
            price=float(price_hash),
            currency="INR",
            original_price=float(price_hash * 1.15),
            discount_percentage=15.0,
            seller={
                "name": f"{retailer_name} Verified Partner",
                "rating": 4.5,
                "reviews": 1200,
                "reliability": "RELIABLE",
                "returnPolicy": "7-day replacement",
                "warranty": "1 year manufacturer",
            },
            seller_name=f"{retailer_name} Verified Partner",
            rating=4.5,
            review_count=1200,
            availability="IN_STOCK",
            shipping="Free Delivery",
            shipping_cost=0.0,
            image_url="https://placehold.co/300x300/FAF8F5/1A1A1A?text=ShopQ",
            product_url=url,
            observed_at=now_iso,
            collected_at=now_iso,
            source_type="MOCK",
            source_status="MOCK",
            confidence_score=0.85,
            extraction_stage="MOCK_DATA",
        )
