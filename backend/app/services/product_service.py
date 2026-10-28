import re
import datetime
from typing import List, Optional, Dict, Any
from app.schemas.product import (
    ProductDetailSchema,
    PriceHistoryPointSchema,
    CanonicalProductSchema,
    CanonicalVariantSchema,
    RetailerListingSchema,
    SellerOfferSchema,
)
from app.schemas.offer import BestOfferSchema, CompetitorOfferSchema, SellerSchema
from app.core.logging import logger
from app.providers.ingestion.trigger_handler import trigger_handler

def generate_price_history(
    start_price: float,
    end_price: float,
    days: int = 90,
    noise: float = 500.0,
    shipping_cost: float = 0.0,
    availability_status: str = "IN_STOCK",
) -> List[PriceHistoryPointSchema]:
    """Generates synthetic historical price observations over a given time window."""
    history: List[PriceHistoryPointSchema] = []
    now = datetime.datetime.now(datetime.timezone.utc)

    for i in range(days - 1, -1, -1):
        dt = now - datetime.timedelta(days=i)
        observed_at = dt.isoformat()
        collected_at = (dt + datetime.timedelta(minutes=2)).isoformat()

        progress = (1.0 - (i / (days - 1))) if days > 1 else 1.0
        price = start_price + (end_price - start_price) * progress

        if days > 1 and noise > 0:
            pseudo_rand = (((i * 9301 + 49297) % 233280) / 233280.0) - 0.5
            price += pseudo_rand * noise

        rounded_price = max(1.0, float(round(price)))

        history.append(
            PriceHistoryPointSchema(
                date=observed_at,
                observed_at=observed_at,
                collected_at=collected_at,
                price=rounded_price,
                shippingCost=shipping_cost,
                availabilityStatus=availability_status,
            )
        )

    if history:
        history[-1].price = float(end_price)

    return history


def create_product(
    id: str,
    name: str,
    brand: str,
    category: str,
    variant: str,
    image: str,
    current_price: float,
    retailer: str,
    retailer_url: str,
    seller: Dict[str, Any],
    recommendation: str,
    confidence: str,
    explanation: str,
    reasons: List[str],
    buy_point: Optional[float] = None,
    trend: str = "STABLE",
    historical_low: Optional[float] = None,
    historical_high: Optional[float] = None,
    last_checked: Optional[str] = None,
    price_history: Optional[List[PriceHistoryPointSchema]] = None,
    competitors: Optional[List[CompetitorOfferSchema]] = None,
    best_offer: Optional[BestOfferSchema] = None,
    shipping_cost: float = 0.0,
    availability_status: str = "IN_STOCK",
    data_status: str = "SAMPLE",
) -> ProductDetailSchema:
    """Builds a normalized ProductDetailSchema with complete 4-level identity schema."""
    seller_norm = SellerSchema(
        name=seller.get("name", "Verified Merchant"),
        rating=float(seller.get("rating", 4.5)),
        reviews=int(seller.get("reviews", seller.get("reviewCount", 1000))),
        reviewCount=int(seller.get("reviewCount", seller.get("reviews", 1000))),
        reliability=seller.get("reliability", "RELIABLE"),
        returnPolicy=seller.get("returnPolicy", seller.get("return_policy", "7-day replacement")),
        warranty=seller.get("warranty", "1 year manufacturer"),
    )

    clean_var = re.sub(r"[^a-z0-9]", "_", (variant or "std").lower())
    clean_seller = re.sub(r"[^a-z0-9]", "_", seller_norm.name.lower())

    cp = CanonicalProductSchema(
        id=f"cp_{id}",
        name=name,
        title=name,
        brand=brand,
        category=category,
        model=variant or name,
        description=explanation,
    )

    cv = CanonicalVariantSchema(
        id=f"cv_{id}_{clean_var}",
        productId=cp.id,
        variant=variant or "Standard",
        color=variant or "Standard",
        sku=f"SKU-{id.upper()}",
        image=image or "https://placehold.co/300x300/FAF8F5/1A1A1A?text=ShopQ",
    )

    rl = RetailerListingSchema(
        id=f"rl_{retailer}_{id}",
        variantId=cv.id,
        retailer=retailer,
        retailerName=retailer.capitalize() if retailer else "Store",
        url=retailer_url or f"https://{retailer}.com/product/{id}",
        listingSku=f"LST-{id.upper()}",
        availabilityStatus=availability_status,
    )

    so = SellerOfferSchema(
        id=f"so_{clean_seller}_{id}",
        listingId=rl.id,
        sellerId=f"seller_{clean_seller}",
        sellerName=seller_norm.name,
        price=current_price,
        currency="INR",
        shippingCost=shipping_cost,
        availabilityStatus=availability_status,
        rating=seller_norm.rating,
        reviews=seller_norm.reviews,
        reviewCount=seller_norm.review_count,
        reliability=seller_norm.reliability,
        returnPolicy=seller_norm.return_policy,
        warranty=seller_norm.warranty,
    )

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    return ProductDetailSchema(
        id=id,
        name=name,
        brand=brand,
        category=category,
        variant=variant,
        image=cv.image,
        currentPrice=current_price,
        retailer=retailer,
        retailerUrl=rl.url,
        seller=seller_norm,
        recommendation=recommendation,
        confidence=confidence,
        explanation=explanation,
        reasons=reasons,
        buyPoint=buy_point,
        trend=trend,
        historicalLow=historical_low if historical_low is not None else current_price,
        historicalHigh=historical_high if historical_high is not None else current_price,
        lastChecked=last_checked or now_iso,
        dataStatus=data_status,
        priceHistory=price_history or [],
        competitors=competitors or [],
        bestOffer=best_offer,
        canonical_product=cp,
        canonical_variant=cv,
        retailer_listing=rl,
        seller_offer=so,
    )


class ProductService:
    """Service handling catalog management, identity extraction, and product lookups."""

    def __init__(self):
        self._products: Dict[str, ProductDetailSchema] = {}
        self._aliases: Dict[str, str] = {
            "sony_wh1000xm5": "sony_good_deal",
            "iphone_15": "iphone_wait",
            "hp_laptop": "laptop_suspicious_seller",
            "new_camera": "new_product_no_history",
            "boat_earbuds": "your_call",
            "dont_rush": "oneplus_12",
            "wait_sale": "samsung_s24",
        }
        self._init_seed_data()

    def _init_seed_data(self):
        """Seeds the 12 core test scenarios + supplementary fixture products."""
        # 1. sony_good_deal (BUY)
        p1 = create_product(
            id="sony_good_deal",
            name="Sony WH-1000XM5",
            brand="Sony",
            category="Headphones",
            variant="Black",
            image="https://placehold.co/300x300/FAF8F5/1A1A1A?text=Sony",
            current_price=22499.0,
            retailer="amazon",
            retailer_url="https://amazon.in/product/sony",
            seller={
                "name": "Appario Retail",
                "rating": 4.8,
                "reviews": 28500,
                "reliability": "RELIABLE",
                "returnPolicy": "10-day replacement",
                "warranty": "1 year manufacturer",
            },
            recommendation="BUY",
            confidence="HIGH",
            explanation="This is the lowest price recorded in 90 days. Backed by a verified top-tier seller with direct manufacturer warranty.",
            reasons=[
                "Price dropped ₹3,500 today to ₹22,499 (lowest in 90 days)",
                "Top-rated authorized seller (Appario Retail, 4.8★)",
                "10-day replacement policy and 1-year manufacturer warranty",
                "Competitors are priced ₹2,500+ higher",
            ],
            buy_point=23999.0,
            trend="FALLING",
            historical_low=22499.0,
            historical_high=29990.0,
            price_history=generate_price_history(27999.0, 22499.0, 90, 600.0),
            competitors=[
                CompetitorOfferSchema(
                    retailer="flipkart",
                    seller="RetailNet",
                    price=24999.0,
                    isReliable=True,
                    available=True,
                    inStock=True,
                    url="https://flipkart.com/product/sony",
                ),
                CompetitorOfferSchema(
                    retailer="croma",
                    seller="Croma",
                    price=26990.0,
                    isReliable=True,
                    available=True,
                    inStock=True,
                    url="https://croma.com/product/sony",
                ),
            ],
        )
        self._products[p1.id] = p1

        # 2. iphone_wait (WAIT)
        p2 = create_product(
            id="iphone_wait",
            name="Apple iPhone 15",
            brand="Apple",
            category="Electronics",
            variant="128GB, Blue",
            image="https://placehold.co/300x300/FAF8F5/1A1A1A?text=iPhone",
            current_price=65999.0,
            retailer="flipkart",
            retailer_url="https://flipkart.com/product/iphone",
            seller={
                "name": "SuperComNet",
                "rating": 4.6,
                "reviews": 54000,
                "reliability": "RELIABLE",
                "returnPolicy": "7-day replacement",
                "warranty": "1 year Apple warranty",
            },
            recommendation="WAIT",
            confidence="HIGH",
            explanation="Prices recently surged to ₹65,999 near the 90-day peak. A festival sale is expected within 10 days where it often drops below ₹55,000.",
            reasons=[
                "Price jumped 18% over the past week near its 90-day high",
                "Major festival sale scheduled within 10 days",
                "Historical data shows regular drops to ₹54,999 during sales",
                "Target buy price is ₹54,999",
            ],
            buy_point=54999.0,
            trend="RISING",
            historical_low=52999.0,
            historical_high=66999.0,
            price_history=generate_price_history(54999.0, 65999.0, 90, 800.0),
            competitors=[
                CompetitorOfferSchema(
                    retailer="amazon",
                    seller="Appario Retail",
                    price=66490.0,
                    isReliable=True,
                    available=True,
                    inStock=True,
                    url="https://amazon.in/product/iphone",
                ),
                CompetitorOfferSchema(
                    retailer="reliance",
                    seller="Reliance Digital",
                    price=65900.0,
                    isReliable=True,
                    available=True,
                    inStock=True,
                    url="https://reliancedigital.in/product/iphone",
                ),
            ],
        )
        self._products[p2.id] = p2

        # 3. nike_better_alternative (CHECK_ALT)
        p3 = create_product(
            id="nike_better_alternative",
            name="Nike Air Max 90",
            brand="Nike",
            category="Fashion",
            variant="White/Black, UK 9",
            image="https://placehold.co/300x300/FAF8F5/1A1A1A?text=Nike",
            current_price=11499.0,
            retailer="amazon",
            retailer_url="https://amazon.in/product/nike",
            seller={
                "name": "RetailNet",
                "rating": 4.2,
                "reviews": 1400,
                "reliability": "RELIABLE",
                "returnPolicy": "10-day return",
                "warranty": "6 months manufacturer",
            },
            recommendation="CHECK_ALT",
            confidence="HIGH",
            explanation="The current Amazon price is ₹11,499, but Myntra currently has the exact same shoe for ₹8,999 directly from Nike India.",
            reasons=[
                "Identical SKU available on Myntra for ₹8,999",
                "Save ₹2,500 by purchasing from the alternate retailer",
                "Official Nike India store with 15-day free returns",
                "Amazon price is currently above the 60-day median",
            ],
            buy_point=9200.0,
            trend="STABLE",
            historical_low=8999.0,
            historical_high=11999.0,
            price_history=generate_price_history(10999.0, 11499.0, 90, 300.0),
            competitors=[
                CompetitorOfferSchema(
                    retailer="myntra",
                    seller="Nike India",
                    price=8999.0,
                    isReliable=True,
                    available=True,
                    inStock=True,
                    url="https://myntra.com/product/nike",
                ),
                CompetitorOfferSchema(
                    retailer="flipkart",
                    seller="IndiFlashMart",
                    price=10999.0,
                    isReliable=True,
                    available=True,
                    inStock=True,
                    url="https://flipkart.com/product/nike",
                ),
            ],
            best_offer=BestOfferSchema(
                id="bo_myntra_nike",
                retailer="Myntra",
                price=8999.0,
                seller={"name": "Nike India", "reliability": "RELIABLE"},
                isReliable=True,
                inStock=True,
                available=True,
                url="https://myntra.com/product/nike",
                savings=2500.0,
            ),
        )
        self._products[p3.id] = p3

        # 4. laptop_suspicious_seller (CAUTION)
        p4 = create_product(
            id="laptop_suspicious_seller",
            name="HP Pavilion 14",
            brand="HP",
            category="Computers",
            variant="i5 13th Gen, 16GB RAM, 512GB SSD",
            image="https://placehold.co/300x300/FAF8F5/1A1A1A?text=HP",
            current_price=46999.0,
            retailer="amazon",
            retailer_url="https://amazon.in/product/hp",
            seller={
                "name": "QuickDeal Electro Store",
                "rating": 2.3,
                "reviews": 34,
                "reliability": "RISKY",
                "returnPolicy": "No returns, replacement only",
                "warranty": "Seller warranty only",
            },
            recommendation="CAUTION",
            confidence="MEDIUM",
            explanation="The price is unusually low (₹46,999), but this merchant has a 2.3 rating with multiple reports of refurbished units sold as new.",
            reasons=[
                "Merchant rating is 2.3/5 with high cancellation rate",
                "Recent negative feedback reporting opened boxes and missing accessories",
                "Price is ₹5,000 below authorized distributor pricing",
                "Authorized sellers charge ₹51,999 with valid HP manufacturer warranty",
            ],
            buy_point=51999.0,
            trend="STABLE",
            historical_low=50999.0,
            historical_high=58999.0,
            price_history=generate_price_history(54999.0, 46999.0, 90, 500.0),
            competitors=[
                CompetitorOfferSchema(
                    retailer="croma",
                    seller="Croma Official",
                    price=51999.0,
                    isReliable=True,
                    available=True,
                    inStock=True,
                    url="https://croma.com/product/hp",
                ),
            ],
            best_offer=BestOfferSchema(
                id="bo_croma_hp",
                retailer="Croma",
                price=51999.0,
                seller={"name": "Croma Official", "reliability": "RELIABLE"},
                isReliable=True,
                inStock=True,
                available=True,
                url="https://croma.com/product/hp",
                savings=-5000.0,
            ),
        )
        self._products[p4.id] = p4

        # 5. new_product_no_history (NO_DECISION)
        p5 = create_product(
            id="new_product_no_history",
            name="Canon EOS R50",
            brand="Canon",
            category="Cameras",
            variant="Body Only, Black",
            image="https://placehold.co/300x300/FAF8F5/1A1A1A?text=Canon",
            current_price=74999.0,
            retailer="croma",
            retailer_url="https://croma.com/product/canon",
            seller={
                "name": "Croma Official",
                "rating": 4.8,
                "reviews": 14,
                "reliability": "RELIABLE",
                "returnPolicy": "7-day replacement",
                "warranty": "2 years manufacturer",
            },
            recommendation="NO_DECISION",
            confidence="LOW",
            explanation="This camera was released only 3 days ago. There is not enough historical pricing data to predict whether a discount cycle will occur soon.",
            reasons=[
                "Newly launched product with only 3 days of price tracking",
                "Zero promotional discount cycles observed so far",
                "Currently only available at single authorized retailer",
                "Recommended to wait until multiple retailers list stock",
            ],
            buy_point=None,
            trend="STABLE",
            historical_low=74999.0,
            historical_high=74999.0,
            price_history=generate_price_history(74999.0, 74999.0, 3, 0.0),
            competitors=[],
        )
        self._products[p5.id] = p5

        # 6. stale_price (CAUTION)
        stale_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14)).isoformat()
        p6 = create_product(
            id="stale_price",
            name="Amazon Kindle Paperwhite (16 GB)",
            brand="Amazon",
            category="Electronics",
            variant="16GB, Black, 6.8 inch",
            image="https://placehold.co/300x300/FAF8F5/1A1A1A?text=Kindle",
            current_price=14999.0,
            retailer="amazon",
            retailer_url="https://amazon.in/product/kindle",
            seller={
                "name": "Cocoblu Retail",
                "rating": 4.4,
                "reviews": 8900,
                "reliability": "RELIABLE",
                "returnPolicy": "7-day replacement",
                "warranty": "1 year manufacturer",
            },
            recommendation="CAUTION",
            confidence="LOW",
            explanation="This price was last recorded 14 days ago. Scraper connectivity was interrupted, so live checkout price and stock may differ.",
            reasons=[
                "Price record is 14 days old (stale cache)",
                "Retailer page could not be refreshed in the last 48 hours",
                "Live price might have changed on the store",
                "Verify checkout total directly on retailer page before purchase",
            ],
            buy_point=13499.0,
            trend="STABLE",
            historical_low=12999.0,
            historical_high=14999.0,
            last_checked=stale_date,
            price_history=generate_price_history(13999.0, 14999.0, 90, 200.0),
            competitors=[
                CompetitorOfferSchema(
                    retailer="croma",
                    seller="Croma",
                    price=14999.0,
                    isReliable=True,
                    available=True,
                    inStock=True,
                    url="https://croma.com/product/kindle",
                ),
            ],
        )
        self._products[p6.id] = p6

        # 7. variant_mismatch (CAUTION)
        p7 = create_product(
            id="variant_mismatch",
            name="Apple MacBook Air 13.6-inch M2",
            brand="Apple",
            category="Computers",
            variant="16GB RAM, 512GB SSD, Space Grey",
            image="https://placehold.co/300x300/FAF8F5/1A1A1A?text=MacBook",
            current_price=79990.0,
            retailer="flipkart",
            retailer_url="https://flipkart.com/product/macbook",
            seller={
                "name": "IndiTechRetail",
                "rating": 3.8,
                "reviews": 820,
                "reliability": "MODERATE",
                "returnPolicy": "7-day replacement",
                "warranty": "1 year Apple warranty",
            },
            recommendation="CAUTION",
            confidence="MEDIUM",
            explanation="Potential variant mismatch detected: The listing title states 16GB RAM / 512GB SSD, but the model number and specifications table show 8GB RAM / 256GB SSD.",
            reasons=[
                "Listing title claims 16GB RAM / 512GB SSD configuration",
                "Manufacturer SKU (MLXY3HN/A) corresponds to 8GB / 256GB base model",
                "Price (₹79,990) matches the 8GB base model market rate",
                "High risk of receiving lower specification item",
            ],
            buy_point=89900.0,
            trend="STABLE",
            historical_low=79990.0,
            historical_high=99990.0,
            price_history=generate_price_history(84990.0, 79990.0, 90, 400.0),
            competitors=[
                CompetitorOfferSchema(
                    retailer="amazon",
                    seller="Appario Retail",
                    price=94990.0,
                    isReliable=True,
                    available=True,
                    inStock=True,
                    url="https://amazon.in/product/macbook",
                ),
            ],
        )
        self._products[p7.id] = p7

        # 8. all_sources_failed (NO_DECISION)
        p8 = create_product(
            id="all_sources_failed",
            name="Google Pixel 8 Pro",
            brand="Google",
            category="Electronics",
            variant="128GB, Obsidian",
            image="https://placehold.co/300x300/FAF8F5/1A1A1A?text=Pixel",
            current_price=84999.0,
            retailer="flipkart",
            retailer_url="https://flipkart.com/product/pixel8pro",
            seller={
                "name": "Unverified Source",
                "rating": 0.0,
                "reviews": 0,
                "reliability": "UNKNOWN",
                "returnPolicy": "Unknown",
                "warranty": "Unknown",
            },
            recommendation="NO_DECISION",
            confidence="LOW",
            explanation="All data scrapers and partner API connections failed or timed out. We are unable to confirm current live pricing or stock status.",
            reasons=[
                "All retail scrapers timed out or returned HTTP 503 / 403 blocks",
                "Anti-bot challenge prevented live inventory extraction",
                "Unable to verify active seller or stock availability",
                "Please check the retailer page directly",
            ],
            buy_point=None,
            trend="STABLE",
            historical_low=79999.0,
            historical_high=106999.0,
            price_history=generate_price_history(89999.0, 84999.0, 30, 500.0),
            competitors=[],
        )
        self._products[p8.id] = p8

        # 9. seller_changed (CAUTION)
        p9 = create_product(
            id="seller_changed",
            name="Samsung Galaxy S24 5G",
            brand="Samsung",
            category="Electronics",
            variant="256GB, Onyx Black",
            image="https://placehold.co/300x300/FAF8F5/1A1A1A?text=Samsung",
            current_price=59999.0,
            retailer="amazon",
            retailer_url="https://amazon.in/product/samsung",
            seller={
                "name": "FastGizmos Unlimited",
                "rating": 3.1,
                "reviews": 42,
                "reliability": "MODERATE",
                "returnPolicy": "7-day replacement",
                "warranty": "1 year manufacturer",
            },
            recommendation="CAUTION",
            confidence="MEDIUM",
            explanation="The default Buy Box seller switched in the last 12 hours from verified direct retailer to an unrated third-party merchant with merchant-fulfilled delivery.",
            reasons=[
                "Buy Box merchant changed in the last 12 hours",
                "New seller rating is 3.1★ vs previous verified seller at 4.7★",
                "Order is merchant-fulfilled with 7-day extended delivery estimate",
                "Flipkart and Croma offer direct verified fulfillment for comparable price",
            ],
            buy_point=54999.0,
            trend="STABLE",
            historical_low=52999.0,
            historical_high=64999.0,
            price_history=generate_price_history(59999.0, 59999.0, 90, 500.0),
            competitors=[
                CompetitorOfferSchema(
                    retailer="flipkart",
                    seller="RetailNet",
                    price=60999.0,
                    isReliable=True,
                    available=True,
                    inStock=True,
                    url="https://flipkart.com/product/samsung",
                ),
            ],
        )
        self._products[p9.id] = p9

        # 10. out_of_stock (WAIT)
        p10 = create_product(
            id="out_of_stock",
            name="Sony PlayStation 5 Pro Console",
            brand="Sony",
            category="Gaming",
            variant="2TB, White",
            image="https://placehold.co/300x300/FAF8F5/1A1A1A?text=PS5+Pro",
            current_price=79990.0,
            retailer="amazon",
            retailer_url="https://amazon.in/product/ps5pro",
            seller={
                "name": "ScalperDeals Hub",
                "rating": 3.5,
                "reviews": 18,
                "reliability": "MODERATE",
                "returnPolicy": "No returns",
                "warranty": "Seller warranty only",
            },
            recommendation="WAIT",
            confidence="HIGH",
            explanation="Official stock is currently sold out across all authorized retailers. Only third-party sellers are listing units with a ₹10,000+ markup.",
            reasons=[
                "Out of stock at official retail price (MSRP ₹69,990)",
                "Available listings are unauthorized scalpers with inflated prices",
                "Official restock shipment expected in approximately 2 weeks",
                "Wait for official restock to avoid overpaying",
            ],
            buy_point=69990.0,
            trend="RISING",
            historical_low=69990.0,
            historical_high=84990.0,
            availability_status="OUT_OF_STOCK",
            price_history=generate_price_history(69990.0, 79990.0, 90, 700.0, availability_status="OUT_OF_STOCK"),
            competitors=[
                CompetitorOfferSchema(
                    retailer="flipkart",
                    seller="GamerStore",
                    price=82990.0,
                    isReliable=False,
                    available=False,
                    inStock=False,
                    url="https://flipkart.com/product/ps5pro",
                ),
            ],
        )
        self._products[p10.id] = p10

        # 11. your_call (YOUR_CALL)
        p11 = create_product(
            id="your_call",
            name="boAt Airdopes 141 True Wireless",
            brand="boAt",
            category="Accessories",
            variant="Bold Black",
            image="https://placehold.co/300x300/FAF8F5/1A1A1A?text=boAt",
            current_price=999.0,
            retailer="amazon",
            retailer_url="https://amazon.in/product/boat",
            seller={
                "name": "Cocoblu Retail",
                "rating": 4.3,
                "reviews": 154000,
                "reliability": "RELIABLE",
                "returnPolicy": "7-day replacement",
                "warranty": "1 year manufacturer",
            },
            recommendation="YOUR_CALL",
            confidence="LOW",
            explanation="This is an everyday value item at ₹999. Price fluctuation over the past 90 days has been under ₹100. If you need it today, go ahead.",
            reasons=[
                "Stable everyday price with minimal historical variation (₹899 - ₹1,099)",
                "No major pending discount cycle expected for this model",
                "High volume verified seller with fast dispatch",
                "Reasonable price for immediate purchase",
            ],
            buy_point=999.0,
            trend="STABLE",
            historical_low=899.0,
            historical_high=1299.0,
            price_history=generate_price_history(999.0, 999.0, 90, 50.0),
            competitors=[
                CompetitorOfferSchema(
                    retailer="flipkart",
                    seller="RetailNet",
                    price=999.0,
                    isReliable=True,
                    available=True,
                    inStock=True,
                    url="https://flipkart.com/product/boat",
                ),
            ],
        )
        self._products[p11.id] = p11

        # 12. no_decision (NO_DECISION)
        p12 = create_product(
            id="no_decision",
            name="Nothing Ear (2) Wireless Earbuds",
            brand="Nothing",
            category="Headphones",
            variant="White, Hi-Res Audio",
            image="https://placehold.co/300x300/FAF8F5/1A1A1A?text=Nothing",
            current_price=7499.0,
            retailer="flipkart",
            retailer_url="https://flipkart.com/product/nothing",
            seller={
                "name": "SuperComNet",
                "rating": 4.2,
                "reviews": 3400,
                "reliability": "RELIABLE",
                "returnPolicy": "7-day replacement",
                "warranty": "1 year manufacturer",
            },
            recommendation="NO_DECISION",
            confidence="LOW",
            explanation="Conflicting market signals: Prices have been volatile with frequent erratic swings, and rumors of a successor announcement make a firm call unreliable.",
            reasons=[
                "Volatile price swings between ₹6,499 and ₹8,499 within 30 days",
                "Divergent pricing trends between Flipkart and Amazon",
                "Unconfirmed rumors of a new model release next month",
                "Insufficient consistency to recommend buying or waiting",
            ],
            buy_point=None,
            trend="VOLATILE",
            historical_low=6499.0,
            historical_high=8999.0,
            price_history=generate_price_history(7999.0, 7499.0, 90, 600.0),
            competitors=[
                CompetitorOfferSchema(
                    retailer="amazon",
                    seller="RetailNet",
                    price=7999.0,
                    isReliable=True,
                    available=True,
                    inStock=True,
                    url="https://amazon.in/product/nothing",
                ),
            ],
        )
        self._products[p12.id] = p12

        # Supplementary: oneplus_12 (DONT_RUSH)
        p13 = create_product(
            id="oneplus_12",
            name="OnePlus 12",
            brand="OnePlus",
            category="Electronics",
            variant="256GB, Silky Black",
            image="https://placehold.co/300x300/FAF8F5/1A1A1A?text=OnePlus",
            current_price=69999.0,
            retailer="amazon",
            retailer_url="https://amazon.in/product/oneplus",
            seller={
                "name": "Darshita Electronics",
                "rating": 4.4,
                "reviews": 12000,
                "reliability": "RELIABLE",
                "returnPolicy": "7-day replacement",
                "warranty": "1 year manufacturer",
            },
            recommendation="DONT_RUSH",
            confidence="HIGH",
            explanation="This is currently at its highest price in 60 days. I strongly recommend waiting for a drop.",
            reasons=[
                "Price spiked recently to ₹69,999",
                "Historical data shows it regularly sells for ₹64,999",
                "No promotional incentives or bank discounts currently active",
            ],
            buy_point=64999.0,
            trend="RISING",
            historical_low=62999.0,
            historical_high=69999.0,
            price_history=generate_price_history(64999.0, 69999.0, 90, 600.0),
            competitors=[
                CompetitorOfferSchema(
                    retailer="reliance",
                    seller="Reliance Digital",
                    price=69999.0,
                    isReliable=True,
                    available=True,
                    inStock=True,
                    url="https://reliancedigital.in/product/oneplus",
                ),
            ],
        )
        self._products[p13.id] = p13

        # Supplementary: samsung_s24 (WAIT_SALE)
        p14 = create_product(
            id="samsung_s24",
            name="Samsung Galaxy S24",
            brand="Samsung",
            category="Electronics",
            variant="256GB, Cobalt Violet",
            image="https://placehold.co/300x300/FAF8F5/1A1A1A?text=Samsung",
            current_price=59999.0,
            retailer="amazon",
            retailer_url="https://amazon.in/product/samsung",
            seller={
                "name": "STPL Direct",
                "rating": 4.5,
                "reviews": 18000,
                "reliability": "RELIABLE",
                "returnPolicy": "7-day replacement",
                "warranty": "1 year manufacturer",
            },
            recommendation="WAIT_SALE",
            confidence="MEDIUM",
            explanation="A major festival sale is expected next week. I would wait, as Samsung flagships historically drop ₹5,000–₹7,000.",
            reasons=[
                "Upcoming festival sale detected next week",
                "Current price is at 90-day average",
                "Historical discounts during sale events reached ₹52,999",
            ],
            buy_point=54999.0,
            trend="STABLE",
            historical_low=52999.0,
            historical_high=64999.0,
            price_history=generate_price_history(59999.0, 59999.0, 90, 500.0),
            competitors=[
                CompetitorOfferSchema(
                    retailer="flipkart",
                    seller="RetailNet",
                    price=60999.0,
                    isReliable=True,
                    available=True,
                    inStock=True,
                    url="https://flipkart.com/product/samsung",
                ),
            ],
        )
        self._products[p14.id] = p14

    def get_all(self) -> List[ProductDetailSchema]:
        """Returns all products in the catalog."""
        return list(self._products.values())

    def get_by_id(self, product_id: str) -> Optional[ProductDetailSchema]:
        """Resolves product by direct ID, alias, canonical IDs, or URL."""
        if not product_id:
            return None

        clean_id = product_id.strip()

        # Direct match
        if clean_id in self._products:
            return self._products[clean_id]

        # Alias match
        target_id = self._aliases.get(clean_id)
        if target_id and target_id in self._products:
            return self._products[target_id]

        # Canonical entity match
        for p in self._products.values():
            if p.canonical_product and p.canonical_product.id == clean_id:
                return p
            if p.canonical_variant and p.canonical_variant.id == clean_id:
                return p
            if p.retailer_listing and p.retailer_listing.id == clean_id:
                return p
            if p.seller_offer and p.seller_offer.id == clean_id:
                return p

        # Check if ID is a URL
        if "http://" in clean_id or "https://" in clean_id or ".com" in clean_id or ".in" in clean_id:
            return self.resolve_by_url(clean_id)

        return None

    def resolve_by_url(self, raw_url: str) -> Optional[ProductDetailSchema]:
        """Return an offer extracted from the requested retailer page, never a guessed one."""
        clean_url = (raw_url or "").strip()
        if not clean_url:
            return None
        if not re.match(r"^https?://", clean_url, re.IGNORECASE):
            clean_url = f"https://{clean_url}"

        offer = trigger_handler.handle_url_check_trigger(clean_url)
        if not offer:
            logger.info("No verified live offer available for requested URL")
            return None

        product = offer.to_product_detail(
            explanation=(
                "Showing the last verified retailer observation because a fresh check is unavailable."
                if offer.source_status == "STALE"
                else "Price extracted from the retailer listing."
            ),
            reasons=[
                "This is a previously verified price; check time is shown above."
                if offer.source_status == "STALE"
                else "Price was checked directly on the retailer listing."
            ],
            confidence="MEDIUM",
            data_status=offer.source_status,
        )
        self._products[product.id] = product
        return product

    def resolve_new_product(self, query_or_url: str) -> Optional[ProductDetailSchema]:
        """Resolve known cached products only; keyword searches cannot verify a price."""
        if not query_or_url or not query_or_url.strip():
            return None

        clean_input = query_or_url.strip()
        lower_input = clean_input.lower()

        # Check if already cached from a previous resolution
        slug_id = "prod_" + re.sub(r"[^a-z0-9]+", "_", lower_input).strip("_")[:40]
        if slug_id in self._products:
            logger.info(f"Cache hit for resolved product: {slug_id}")
            return self._products[slug_id]
        logger.info(f"No verified price source for keyword query: '{clean_input[:40]}'")
        return None


    def get_price_history(self, product_id: str) -> List[PriceHistoryPointSchema]:
        """Returns price history for a given product."""
        p = self.get_by_id(product_id)
        if not p:
            return []
        return p.price_history

    def get_offers(self, product_id: str) -> List[Dict[str, Any]]:
        """Returns current retailer offer, best offer, and competitor offers."""
        p = self.get_by_id(product_id)
        if not p:
            return []

        offers = []
        # Main listing offer
        offers.append({
            "retailer": p.retailer,
            "price": p.current_price,
            "seller": p.seller.name if p.seller else "Authorized Merchant",
            "rating": p.seller.rating if p.seller else 4.5,
            "is_reliable": p.seller.reliability == "RELIABLE" if p.seller else True,
            "available": True,
            "in_stock": True,
            "url": p.retailer_url,
            "is_best_offer": p.best_offer is None,
        })

        # Competitors
        for comp in p.competitors:
            seller_name = comp.seller.name if isinstance(comp.seller, SellerSchema) else str(comp.seller)
            offers.append({
                "retailer": comp.retailer,
                "price": comp.price,
                "seller": seller_name,
                "rating": 4.2,
                "is_reliable": comp.is_reliable,
                "available": comp.available,
                "in_stock": comp.in_stock,
                "url": comp.url,
                "is_best_offer": False,
            })

        # Best offer if present
        if p.best_offer:
            best_seller = p.best_offer.seller.name if isinstance(p.best_offer.seller, SellerSchema) else (
                p.best_offer.seller.get("name") if isinstance(p.best_offer.seller, dict) else str(p.best_offer.seller)
            )
            offers.append({
                "retailer": p.best_offer.retailer,
                "price": p.best_offer.price,
                "seller": best_seller,
                "rating": 4.8,
                "is_reliable": p.best_offer.is_reliable,
                "available": p.best_offer.available,
                "in_stock": p.best_offer.in_stock,
                "url": p.best_offer.url,
                "savings": p.best_offer.savings,
                "is_best_offer": True,
            })

        return offers


product_service = ProductService()
