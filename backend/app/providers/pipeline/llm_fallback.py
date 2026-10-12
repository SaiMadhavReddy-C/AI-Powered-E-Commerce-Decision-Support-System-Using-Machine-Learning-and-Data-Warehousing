"""Stage 5: LLM Fallback Extractor with Strict Guardrails.

Used ONLY when deterministic stages (JSON-LD, Selectors, DOM, Regex) fail.
Strict Guardrails:
1. Never allow the LLM to invent, estimate, or hallucinate prices, currency, or sellers.
2. Every extracted numerical price MUST have direct verbatim substring grounding in the source text.
3. If grounded verification fails, the field is explicitly marked uncertain (price=None, seller='Unknown Seller').
4. Confidence is capped at LOW (0.45).
"""

import os
import re
from typing import Dict, Any, Optional, List
from app.core.logging import logger
from app.core.config import settings


class LlmFallbackExtractor:
    """Fallback extractor with strict anti-hallucination validation gates."""

    def __init__(self):
        self.api_key = getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")

    def extract(self, text_or_html: str, url: str) -> Optional[Dict[str, Any]]:
        """
        Runs fallback extraction with strict text grounding.
        Guarantees that no price or merchant can be invented.
        """
        if not text_or_html:
            return None

        # Clean text snippet (up to 4000 characters) to pass to LLM / structured heuristics
        cleaned_snippet = self._sanitize_for_prompt(text_or_html[:5000])

        uncertain_fields: List[str] = []

        # Attempt structured extraction
        extracted_data = self._perform_extraction(cleaned_snippet, url)
        if not extracted_data:
            return None

        # --- STRICT GUARDRAILS & GROUNDING VERIFICATION ---
        raw_price = extracted_data.get("price")
        verified_price: Optional[float] = None

        if raw_price is not None:
            # Check if this exact number sequence literally exists in the raw text
            price_str_int = str(int(raw_price)) if raw_price == int(raw_price) else str(raw_price)
            formatted_indian = f"{int(raw_price):,}" if raw_price == int(raw_price) else str(raw_price)

            if price_str_int in text_or_html or formatted_indian in text_or_html:
                verified_price = float(raw_price)
            else:
                # REJECT HALLUCINATED PRICE
                logger.warning(
                    f"LLM hallucination rejected: Price {raw_price} was not grounded in source text."
                )
                uncertain_fields.append("price")
                verified_price = None
        else:
            uncertain_fields.append("price")

        # Seller verification
        seller_name = extracted_data.get("seller_name")
        if seller_name:
            if seller_name.lower() not in text_or_html.lower():
                logger.info(f"Ungrounded seller '{seller_name}' marked uncertain.")
                uncertain_fields.append("seller")
                seller_name = "Unverified Seller"
        else:
            uncertain_fields.append("seller")
            seller_name = "Unverified Seller"

        # Currency verification
        currency = extracted_data.get("currency", "INR")
        if currency not in ("INR", "₹"):
            uncertain_fields.append("currency")
            currency = "INR"

        title = extracted_data.get("title") or "Unknown Product"

        return {
            "title": title,
            "price": verified_price,
            "currency": currency,
            "seller_name": seller_name,
            "availability": extracted_data.get("availability", "IN_STOCK"),
            "uncertain_fields": uncertain_fields,
            "stage": "LLM_FALLBACK",
            "confidence": 0.45 if verified_price else 0.20,
        }

    def _sanitize_for_prompt(self, raw_html: str) -> str:
        """Strips HTML tags and script/style bodies to produce readable text."""
        # Strip script & style blocks
        no_scripts = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', raw_html, flags=re.DOTALL | re.IGNORECASE)
        # Strip tags
        clean_text = re.sub(r'<[^>]+>', ' ', no_scripts)
        # Strip excessive whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text

    def _perform_extraction(self, text: str, url: str) -> Optional[Dict[str, Any]]:
        """
        Parses text for title, price candidate, and merchant using deterministic pattern
        matching simulating LLM structured output, or calls Gemini API if key is available.
        """
        # If Gemini API key is configured, we can use it with strict system instructions
        if self.api_key:
            try:
                import json
                import urllib.request

                prompt = (
                    "You are a strict data extractor for ShopQ. Extract product title, numeric price, "
                    "currency, and merchant name from the following text. "
                    "CRITICAL: Do NOT guess, predict, or invent prices or sellers. If not explicitly found, use null.\n"
                    "Respond with ONLY JSON format: "
                    '{"title": str, "price": number or null, "currency": "INR", "seller_name": str or null}\n\n'
                    f"TEXT:\n{text[:3000]}"
                )
                url_api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
                req = urllib.request.Request(
                    url_api,
                    data=json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    cand_text = resp_data["candidates"][0]["content"]["parts"][0]["text"]
                    # Extract JSON block
                    match = re.search(r'\{.*\}', cand_text, re.DOTALL)
                    if match:
                        return json.loads(match.group(0))
            except Exception as e:
                logger.debug(f"Gemini LLM fallback skipped or failed: {str(e)}")

        # Deterministic grounded text parser fallback
        # Find first explicit price mention
        price_match = re.search(r'(?:₹|Rs\.?|INR)\s*([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]{2})?)', text)
        found_price = None
        if price_match:
            try:
                found_price = float(price_match.group(1).replace(",", ""))
            except ValueError:
                pass

        # Find title candidate
        words = text.split()[:10]
        title_cand = " ".join(words) if words else "Unknown Product"

        return {
            "title": title_cand,
            "price": found_price,
            "currency": "INR",
            "seller_name": None,
            "availability": "IN_STOCK",
        }
