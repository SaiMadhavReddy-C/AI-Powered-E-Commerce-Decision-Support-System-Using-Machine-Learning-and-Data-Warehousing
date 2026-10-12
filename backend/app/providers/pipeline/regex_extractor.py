"""Stage 4: Normalization and Regex Heuristic Extractor.

Performs robust text extraction, currency normalization, Indian comma numbering
resolution, merchant name regex matching, and ambiguity tagging.
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from app.core.logging import logger


class RegexExtractor:
    """Regex pattern extractor and normalizer."""

    CURRENCY_PRICE_PATTERNS = [
        # ₹ 22,499 or ₹22499
        re.compile(r'₹\s*([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]{1,2})?)'),
        # Rs. 22,499 or Rs 22,499
        re.compile(r'(?:Rs\.?|INR)\s*([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]{1,2})?)', re.IGNORECASE),
        # Price: 22499 or Deal Price: 22,499
        re.compile(r'(?:Price|Offer|Deal|Cost)\s*[:\-]\s*(?:₹|Rs\.?|INR)?\s*([0-9]{1,3}(?:,[0-9]{2,3})*)', re.IGNORECASE),
    ]

    SELLER_PATTERNS = [
        re.compile(r'(?:Sold by|Merchant|Seller|Fulfilled by)\s*[:\-]?\s*<[^>]+>?\s*([A-Za-z0-9\s&.\-]+?)(?:<|\n|,|\||\.)', re.IGNORECASE),
        re.compile(r'(?:Sold by|Merchant|Seller)\s*[:\-]?\s*([A-Za-z0-9\s&.\-]{3,35})(?:\s*\(|\n|,|\||$)', re.IGNORECASE),
    ]

    DISCOUNT_PATTERN = re.compile(r'([0-9]{1,2})%\s*(?:off|discount|OFF)', re.IGNORECASE)

    TITLE_CLEANER = re.compile(
        r'\s*(?:\|\s*(?:Flipkart|Amazon|Croma|Reliance Digital|Myntra).*|'
        r':\s*Buy .* Online at Low Prices in India.*|'
        r'-\s*(?:Amazon\.in|Flipkart\.com|Croma|Myntra)).*$',
        re.IGNORECASE,
    )

    def extract(self, text: str) -> Optional[Dict[str, Any]]:
        """Applies regex heuristics over raw text or HTML."""
        if not text:
            return None

        uncertain_fields: List[str] = []

        # 1. Price extraction
        price, price_uncertain = self.parse_first_price(text)
        if price_uncertain:
            uncertain_fields.append("price")

        # 2. Seller extraction
        seller_name = self.extract_seller(text)
        if not seller_name or seller_name == "Unknown Seller":
            uncertain_fields.append("seller")
            seller_name = "Verified Merchant"

        # 3. Discount extraction
        discount = self.extract_discount(text)

        if price is not None:
            return {
                "price": price,
                "currency": "INR",
                "seller_name": seller_name,
                "discount_percentage": discount,
                "uncertain_fields": uncertain_fields,
                "stage": "REGEX_NORMALIZATION",
                "confidence": 0.70 if not uncertain_fields else 0.55,
            }

        return None

    def clean_title(self, raw_title: str) -> str:
        """Removes retailer trailing watermarks, promotional tags, and extra spaces."""
        if not raw_title:
            return ""
        cleaned = self.TITLE_CLEANER.sub("", raw_title)
        # Normalize double whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def parse_first_price(self, text: str) -> Tuple[Optional[float], bool]:
        """
        Parses the most prominent price occurrence.
        Returns (price_float, is_uncertain).
        """
        if not text:
            return None, True

        found_prices: List[float] = []
        for pattern in self.CURRENCY_PRICE_PATTERNS:
            for match in pattern.finditer(text):
                raw_num = match.group(1).replace(",", "").strip()
                try:
                    val = float(raw_num)
                    if 10.0 <= val <= 2000000.0:  # Reasonable price sanity gate
                        found_prices.append(val)
                except ValueError:
                    continue

        if not found_prices:
            return None, True

        # If multiple very different prices exist without clear delimiter, mark uncertain
        primary = found_prices[0]
        is_uncertain = False
        if len(found_prices) > 3 and max(found_prices) > primary * 3:
            is_uncertain = True

        return primary, is_uncertain

    def extract_seller(self, text: str) -> Optional[str]:
        """Extracts merchant or seller entity."""
        if not text:
            return None
        for pattern in self.SELLER_PATTERNS:
            match = pattern.search(text)
            if match:
                candidate = match.group(1).strip().rstrip(". ,;:!?")
                # Discard noise strings
                if candidate.lower() not in ("free delivery", "cash on delivery", "in stock", "rating"):
                    return candidate
        return None

    def extract_discount(self, text: str) -> Optional[float]:
        """Extracts promotional discount percentage."""
        if not text:
            return None
        match = self.DISCOUNT_PATTERN.search(text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return None
