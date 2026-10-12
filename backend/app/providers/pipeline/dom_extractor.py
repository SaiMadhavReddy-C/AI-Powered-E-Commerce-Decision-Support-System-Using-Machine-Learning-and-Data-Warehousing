"""Stage 3: Generic DOM Heuristics Extractor.

Extracts metadata from standard web meta tags: OpenGraph (og:*), Twitter Cards,
Microdata (itemprop), and generic semantic DOM attributes.
Deterministic fallback when LD+JSON or specific retailer selectors are absent.
"""

import re
from typing import Dict, Any, Optional
from app.core.logging import logger


class DomHeuristicsExtractor:
    """Extracts product properties from standard HTML meta tags and microdata."""

    def extract(self, html: str) -> Optional[Dict[str, Any]]:
        """Scans OpenGraph, Microdata, and common price tags."""
        if not html:
            return None

        # 1. OpenGraph / Twitter metadata
        og_title = self._get_meta_content(html, ["og:title", "twitter:title"])
        og_image = self._get_meta_content(html, ["og:image", "twitter:image"])
        og_price = self._get_meta_content(html, ["og:price:amount", "product:price:amount", "price"])
        og_currency = self._get_meta_content(html, ["og:price:currency", "product:price:currency", "currency"]) or "INR"

        # 2. Microdata itemprop
        itemprop_title = self._get_itemprop_content(html, "name")
        itemprop_price = self._get_itemprop_content(html, "price")
        itemprop_curr = self._get_itemprop_content(html, "priceCurrency")
        itemprop_image = self._get_itemprop_content(html, "image")

        title = og_title or itemprop_title
        if not title:
            # Fall back to <title> tag
            title_tag = re.search(r'<title[^>]*>\s*([^<]+?)\s*</title>', html, re.IGNORECASE)
            if title_tag:
                title = title_tag.group(1).strip()

        # Parse numeric price
        price = None
        raw_price = og_price or itemprop_price

        if not raw_price:
            # Generic DOM price class heuristic
            generic_price_match = re.search(
                r'<(?:span|div|p)[^>]*class=["\'][^"\']*(?:price|offer_price|special-price)[^"\']*["\'][^>]*>\s*(?:₹|Rs\.?|INR)?\s*([0-9,]+(?:\.[0-9]{2})?)',
                html,
                re.IGNORECASE,
            )
            if generic_price_match:
                raw_price = generic_price_match.group(1)

        if raw_price:
            try:
                price = float(str(raw_price).replace(",", "").strip())
            except (ValueError, TypeError):
                price = None

        currency = og_currency or itemprop_curr or "INR"
        image = og_image or itemprop_image

        if price is not None or title:
            return {
                "title": title,
                "price": price,
                "currency": currency,
                "image": image,
                "seller_name": "Verified Merchant",
                "availability": "IN_STOCK",
                "stage": "GENERIC_DOM",
                "confidence": 0.75,
            }

        return None

    def _get_meta_content(self, html: str, properties: list) -> Optional[str]:
        """Finds <meta property="..." content="..."> or <meta name="..." content="...">."""
        for prop in properties:
            pattern = re.compile(
                rf'<meta[^>]*(?:property|name)=["\']{re.escape(prop)}["\'][^>]*content=["\']([^"\']+)["\']',
                re.IGNORECASE,
            )
            match = pattern.search(html)
            if match:
                return match.group(1).strip()

            # Reverse attribute order: content="..." property="..."
            pattern_rev = re.compile(
                rf'<meta[^>]*content=["\']([^"\']+)["\'][^>]*(?:property|name)=["\']{re.escape(prop)}["\']',
                re.IGNORECASE,
            )
            match_rev = pattern_rev.search(html)
            if match_rev:
                return match_rev.group(1).strip()
        return None

    def _get_itemprop_content(self, html: str, prop: str) -> Optional[str]:
        """Finds elements with itemprop="prop" and extracts content or inner text."""
        # Check <meta itemprop="prop" content="...">
        meta_match = re.search(
            rf'<meta[^>]*itemprop=["\']{re.escape(prop)}["\'][^>]*content=["\']([^"\']+)["\']',
            html,
            re.IGNORECASE,
        )
        if meta_match:
            return meta_match.group(1).strip()

        # Check <span itemprop="prop">...</span>
        span_match = re.search(
            rf'<[^>]*itemprop=["\']{re.escape(prop)}["\'][^>]*>\s*([^<]+?)\s*<',
            html,
            re.IGNORECASE,
        )
        if span_match:
            return span_match.group(1).strip()

        return None
