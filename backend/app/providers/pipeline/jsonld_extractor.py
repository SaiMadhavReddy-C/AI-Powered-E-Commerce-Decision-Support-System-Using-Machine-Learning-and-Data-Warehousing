"""Stage 1: JSON-LD Structured Data Extractor.

Extracts schema.org Product, Offer, and AggregateRating data from LD+JSON scripts.
Highest deterministic fidelity with zero heuristic ambiguity.
"""

import json
import re
from typing import Dict, Any, Optional, List
from app.core.logging import logger


class JsonLdExtractor:
    """Extracts product attributes from schema.org JSON-LD blocks."""

    JSONLD_PATTERN = re.compile(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        re.IGNORECASE | re.DOTALL,
    )

    def extract(self, html: str) -> Optional[Dict[str, Any]]:
        """Parses LD+JSON blocks in HTML and extracts product details."""
        if not html:
            return None

        scripts = self.JSONLD_PATTERN.findall(html)
        if not scripts:
            return None

        for raw_script in scripts:
            raw_script = raw_script.strip()
            if not raw_script:
                continue
            try:
                data = json.loads(raw_script)
                product_data = self._find_product_node(data)
                if product_data:
                    parsed = self._parse_product_node(product_data)
                    if parsed and parsed.get("price") is not None:
                        parsed["stage"] = "JSON_LD"
                        parsed["confidence"] = 0.95
                        return parsed
            except Exception as e:
                logger.debug(f"JSON-LD parse skip: {str(e)}")
                continue

        return None

    def _find_product_node(self, node: Any) -> Optional[Dict[str, Any]]:
        """Recursively traverses graph/list to locate a schema.org Product node."""
        if isinstance(node, list):
            for item in node:
                found = self._find_product_node(item)
                if found:
                    return found
        elif isinstance(node, dict):
            # Check @graph container
            if "@graph" in node and isinstance(node["@graph"], list):
                return self._find_product_node(node["@graph"])

            node_type = str(node.get("@type", "")).lower()
            if "product" in node_type:
                return node
            # Or if it contains offers with product context
            if "offers" in node and ("name" in node or "title" in node):
                return node
        return None

    def _parse_product_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Maps schema.org attributes to ShopQ internal fields."""
        title = node.get("name") or node.get("title") or ""

        # Brand
        brand = None
        raw_brand = node.get("brand")
        if isinstance(raw_brand, dict):
            brand = raw_brand.get("name")
        elif isinstance(raw_brand, str):
            brand = raw_brand

        # Image
        image = None
        raw_image = node.get("image")
        if isinstance(raw_image, list) and raw_image:
            image = raw_image[0] if isinstance(raw_image[0], str) else raw_image[0].get("url")
        elif isinstance(raw_image, dict):
            image = raw_image.get("url")
        elif isinstance(raw_image, str):
            image = raw_image

        # Price, Currency, Availability, Seller from offers
        price = None
        currency = "INR"
        seller_name = None
        availability = "IN_STOCK"

        offers = node.get("offers")
        offer_node = None
        if isinstance(offers, list) and offers:
            offer_node = offers[0]
        elif isinstance(offers, dict):
            offer_node = offers

        if offer_node:
            raw_price = offer_node.get("price") or offer_node.get("lowPrice")
            if raw_price is not None:
                try:
                    price = float(str(raw_price).replace(",", "").strip())
                except (ValueError, TypeError):
                    price = None

            currency = offer_node.get("priceCurrency") or "INR"

            # Availability
            raw_avail = str(offer_node.get("availability", "")).lower()
            if "outofstock" in raw_avail:
                availability = "OUT_OF_STOCK"
            elif "limited" in raw_avail or "preorder" in raw_avail:
                availability = "LIMITED_STOCK"
            else:
                availability = "IN_STOCK"

            # Seller
            seller_data = offer_node.get("seller") or offer_node.get("offeredBy")
            if isinstance(seller_data, dict):
                seller_name = seller_data.get("name")
            elif isinstance(seller_data, str):
                seller_name = seller_data

        # Aggregate Rating
        rating = 4.5
        review_count = 1000
        rating_node = node.get("aggregateRating")
        if isinstance(rating_node, dict):
            try:
                rating = float(rating_node.get("ratingValue", 4.5))
                review_count = int(rating_node.get("reviewCount") or rating_node.get("ratingCount") or 1000)
            except (ValueError, TypeError):
                pass

        return {
            "title": title.strip() if title else None,
            "brand": brand.strip() if brand else None,
            "image": image,
            "price": price,
            "currency": currency,
            "seller_name": seller_name,
            "availability": availability,
            "rating": rating,
            "review_count": review_count,
            "sku": node.get("sku") or node.get("mpn"),
        }
