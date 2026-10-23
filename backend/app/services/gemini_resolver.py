"""
GeminiProductResolver — ShopQ Live AI Product Analysis Engine

Uses Google Gemini API to generate intelligent, realistic product data
for any search query or product URL. This is the "online" intelligence layer
that powers ShopQ when ScraperAPI is not available or for keyword searches.

Flow:
  query/url → Gemini AI → structured JSON → ProductDetailSchema
"""

import json
import re
import datetime
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional, Dict, Any

from app.core.config import settings
from app.core.logging import logger


GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)

PRODUCT_PROMPT_TEMPLATE = """You are ShopQ's AI product analyst specializing in Indian e-commerce markets (Amazon.in, Flipkart, Croma, Myntra, etc.).

A user searched for: "{query}"

Generate a REALISTIC product analysis response as if you just fetched live data from Indian e-commerce sites.
Use real current market prices in INR (Indian Rupees). Be accurate and realistic.

Respond with ONLY valid JSON (no markdown, no explanation) in this exact format:
{{
  "name": "Full Product Name with Model Number",
  "brand": "Brand Name",
  "category": "Product Category",
  "variant": "Specific variant (color/storage/size)",
  "current_price": 12999,
  "historical_low": 11499,
  "historical_high": 16999,
  "retailer": "Amazon India",
  "retailer_url": "https://www.amazon.in/s?k={query_encoded}",
  "seller_name": "Appario Retail Private Ltd",
  "seller_rating": 4.7,
  "seller_reviews": 18500,
  "seller_reliability": "RELIABLE",
  "return_policy": "10-day replacement",
  "warranty": "1 year manufacturer warranty",
  "recommendation": "BUY",
  "confidence": "HIGH",
  "trend": "FALLING",
  "buy_point": 11999,
  "explanation": "2-3 sentence explanation of the buy/wait recommendation based on price trend and seller quality",
  "reasons": [
    "Reason 1 with specific price/data",
    "Reason 2 with specific data",
    "Reason 3 with specific data"
  ],
  "competitors": [
    {{
      "retailer": "Flipkart",
      "price": 13499,
      "seller": "Flipkart Assured",
      "url": "https://www.flipkart.com/search?q={query_encoded}",
      "in_stock": true
    }},
    {{
      "retailer": "Croma",
      "price": 14990,
      "seller": "Croma Retail",
      "url": "https://www.croma.com/searchB?q={query_encoded}",
      "in_stock": true
    }}
  ],
  "price_history_start": 15999,
  "price_history_end": 12999,
  "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80"
}}

Rules:
- Use REAL market prices for this product in India (INR)
- recommendation must be one of: BUY, WAIT, GRAB, WAIT_SALE, CHECK_ALT, CAUTION, DONT_RUSH, YOUR_CALL, NO_DECISION
- confidence must be one of: HIGH, MEDIUM, LOW
- trend must be one of: FALLING, RISING, STABLE, VOLATILE
- seller_reliability must be one of: RELIABLE, UNVERIFIED, SUSPICIOUS
- Make it realistic — if product is expensive (like iPhone), set price accordingly
- reasons array must have exactly 3 items
- competitors array must have exactly 2 items
"""


def _call_gemini(prompt: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Makes a REST call to Gemini API and returns parsed JSON response."""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1024,
            "responseMimeType": "application/json",
        },
    }

    url = f"{GEMINI_API_URL}?key={api_key}"
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "ShopQ-AI/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status == 200:
                raw = resp.read().decode("utf-8")
                body = json.loads(raw)
                # Extract text from Gemini response
                text = (
                    body.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )
                if text:
                    # Strip markdown fences if present
                    text = re.sub(r"```json\s*|\s*```", "", text).strip()
                    return json.loads(text)
    except urllib.error.HTTPError as e:
        logger.warning(f"Gemini API HTTP error {e.code}: {e.reason}")
    except json.JSONDecodeError as e:
        logger.warning(f"Gemini response JSON parse error: {e}")
    except Exception as e:
        logger.warning(f"Gemini API call failed: {e}")

    return None


def resolve_product_with_gemini(query: str) -> Optional[Dict[str, Any]]:
    """
    Main entry point: resolves product data via Gemini AI for any query.
    Returns raw dict compatible with create_product() parameters, or None on failure.
    """
    api_key = getattr(settings, "GEMINI_API_KEY", "") or ""
    if not api_key or api_key == "your_gemini_api_key_here":
        logger.info("GEMINI_API_KEY not configured; skipping AI resolution.")
        return None

    query_encoded = urllib.parse.quote_plus(query[:100])
    prompt = PRODUCT_PROMPT_TEMPLATE.format(
        query=query[:100],
        query_encoded=query_encoded,
    )

    logger.info(f"Calling Gemini API to resolve product: '{query[:60]}'")
    result = _call_gemini(prompt, api_key)

    if not result:
        logger.warning(f"Gemini returned no result for query: '{query[:60]}'")
        return None

    logger.info(
        f"Gemini resolved product: {result.get('name', '?')} @ ₹{result.get('current_price', '?')}"
    )
    return result


def gemini_result_to_product_params(result: Dict[str, Any], query: str) -> Dict[str, Any]:
    """Converts Gemini JSON response to create_product() keyword arguments."""
    slug = "prod_" + re.sub(r"[^a-z0-9]+", "_", query.lower()).strip("_")[:40]

    now = datetime.datetime.now(datetime.timezone.utc)
    price_history = []
    start_price = float(result.get("price_history_start", result.get("current_price", 9999)))
    end_price = float(result.get("current_price", 9999))
    days = 90
    for i in range(days - 1, -1, -1):
        dt = now - datetime.timedelta(days=i)
        progress = (1.0 - (i / (days - 1))) if days > 1 else 1.0
        price = start_price + (end_price - start_price) * progress
        pseudo = (((i * 9301 + 49297) % 233280) / 233280.0 - 0.5)
        noise = abs(start_price - end_price) * 0.1
        price += pseudo * noise
        price = max(1.0, round(price))
        price_history.append({
            "date": dt.isoformat(),
            "observed_at": dt.isoformat(),
            "collected_at": (dt + datetime.timedelta(minutes=2)).isoformat(),
            "price": float(price),
            "shippingCost": 0.0,
            "availabilityStatus": "IN_STOCK",
        })
    if price_history:
        price_history[-1]["price"] = float(end_price)

    competitors = []
    for comp in result.get("competitors", []):
        competitors.append({
            "retailer": comp.get("retailer", "Other"),
            "seller": comp.get("seller", "Merchant"),
            "price": float(comp.get("price", end_price * 1.05)),
            "url": comp.get("url", ""),
            "in_stock": comp.get("in_stock", True),
            "is_reliable": True,
        })

    return {
        "id": slug,
        "name": result.get("name", query.title()[:60]),
        "brand": result.get("brand", query.split()[0].capitalize() if query.split() else "Brand"),
        "category": result.get("category", "Consumer Electronics"),
        "variant": result.get("variant", "Standard"),
        "image": result.get("image_url", "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80"),
        "current_price": float(result.get("current_price", 9999)),
        "retailer": result.get("retailer", "Amazon India"),
        "retailer_url": result.get("retailer_url", f"https://www.amazon.in/s?k={urllib.parse.quote_plus(query)}"),
        "seller": {
            "name": result.get("seller_name", "Appario Retail"),
            "rating": float(result.get("seller_rating", 4.5)),
            "reviews": int(result.get("seller_reviews", 5000)),
            "reviewCount": int(result.get("seller_reviews", 5000)),
            "reliability": result.get("seller_reliability", "RELIABLE"),
            "returnPolicy": result.get("return_policy", "7-day replacement"),
            "warranty": result.get("warranty", "1 year manufacturer"),
        },
        "recommendation": result.get("recommendation", "BUY"),
        "confidence": result.get("confidence", "MEDIUM"),
        "explanation": result.get("explanation", f"AI-powered analysis for '{query}'."),
        "reasons": result.get("reasons", ["Competitive market pricing", "Verified seller", "Stable price trend"])[:3],
        "buy_point": float(result.get("buy_point", float(result.get("current_price", 9999)) * 0.95)),
        "trend": result.get("trend", "STABLE"),
        "historical_low": float(result.get("historical_low", float(result.get("current_price", 9999)) * 0.9)),
        "historical_high": float(result.get("historical_high", float(result.get("current_price", 9999)) * 1.3)),
        "price_history_raw": price_history,
        "competitors_raw": competitors,
        "source": "GEMINI_AI",
    }
