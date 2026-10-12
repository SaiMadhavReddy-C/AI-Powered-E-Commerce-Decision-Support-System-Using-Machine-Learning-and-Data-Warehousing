# ShopQ Backend API

FastAPI-powered decision engine backend for **ShopQ**, providing real-time e-commerce price evaluation, merchant credibility scoring, and actionable purchase signals.

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI application entrypoint & middleware
│   ├── core/
│   │   ├── config.py            # Environment & app configuration
│   │   └── logging.py           # Structured logging setup
│   ├── schemas/                 # Strict Pydantic schemas & contracts
│   │   ├── product.py           # 4-level product schema & analysis responses
│   │   ├── decision.py          # Strict Decision Contract schema
│   │   ├── offer.py             # Sellers, competitor offers, best offer schemas
│   │   ├── watchlist.py         # Watchlist item and CRUD payloads
│   │   ├── alert.py             # User notification alerts
│   │   ├── preferences.py       # User shopping preferences
│   │   ├── search.py            # Search query & response schemas
│   │   └── analyze.py           # Analyze request schema
│   ├── services/                # Decoupled business logic layer
│   │   ├── product_service.py   # Catalog data, 4-level mapping, URL resolution
│   │   ├── decision_service.py  # Pricing logic & decision engine
│   │   ├── search_service.py    # Search & URL token routing
│   │   ├── watchlist_service.py # Watchlist management
│   │   ├── alert_service.py     # Notification alert management
│   │   └── preferences_service.py # Strategy preferences management
│   └── api/
│       └── routes/              # Modular route handlers
│           ├── health.py        # GET /health
│           ├── search.py        # POST /api/search
│           ├── analyze.py       # POST /api/analyze
│           ├── products.py      # GET /api/products/{id} & sub-resources
│           ├── watchlist.py     # GET/POST /api/watchlist, DELETE /api/watchlist/{id}
│           ├── alerts.py        # GET /api/alerts, POST /api/alerts/{id}/read
│           └── preferences.py   # GET /api/preferences, PUT /api/preferences
├── tests/
│   └── test_api.py              # Comprehensive test suite
├── requirements.txt             # Python package dependencies
├── run.py                       # Python launcher script
├── run.sh                       # Shell startup script
└── README.md
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+
- `pip` or `uv`

### 2. Installation
```bash
cd /Users/sai/.gemini/antigravity/scratch/shopq/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Server
Using Python launcher:
```bash
python3 run.py
```
Or using the shell script:
```bash
chmod +x run.sh
./run.sh
```
Or with Uvicorn directly:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server will start on **`http://localhost:8000`**.
Interactive Swagger documentation is available at **`http://localhost:8000/docs`**.

---

## 🧪 Testing

Run the test suite:
```bash
python3 -m unittest tests/test_api.py
```
Or with pytest:
```bash
pytest tests/test_api.py -v
```

---

## 📋 API Contract & Endpoints

### 1. Health
- **`GET /health`**
  ```json
  {
    "status": "healthy",
    "version": "1.0.0",
    "service": "ShopQ API"
  }
  ```

### 2. Search
- **`POST /api/search`**
  - **Body**: `{"query": "Sony WH-1000XM5", "limit": 10}`
  - Also resolves URLs directly (e.g. `{"query": "https://amazon.in/dp/sony..."}`).

### 3. Product Analysis & Details (Strict Contract)
- **`POST /api/analyze`**
  - **Body**: `{"input": "https://amazon.in/product/sony"}` or `{"url": "..."}` or `{"productId": "..."}`
  - Returns:
    ```json
    {
      "product": { ... },
      "decision": {
        "decision": "BUY",
        "confidence_level": "HIGH",
        "primary_reason": "Lowest price recorded in 90 days...",
        "secondary_reasons": ["Price dropped ₹3,500 today to ₹22,499", "..."],
        "buy_point": 23999.0,
        "best_offer_id": "bo_appario_retail_sony_good_deal",
        "data_freshness": "FRESH",
        "data_coverage": "98%",
        "checked_at": "2026-10-07T18:00:00Z",
        "model_version": "shopq-decision-v2.1",
        "decision_rules_version": "rules-2026.10"
      },
      "best_offer": { ... }
    }
    ```
- **`GET /api/products/{id}`**
  - Returns the same structured `{ product, decision, best_offer }` object.
- **`GET /api/products/{id}/analysis`**
  - Returns the `DecisionSchema`.
- **`GET /api/products/{id}/details`**
  - Returns the detailed `ProductDetailSchema` with 4-level identity entities (`canonical_product`, `canonical_variant`, `retailer_listing`, `seller_offer`).
- **`GET /api/products/{id}/offers`**
  - Returns retailer listing, competitor offers, and best offer.
- **`GET /api/products/{id}/price-history`**
  - Returns historical timestamped price series.

### 4. Watchlist
- **`GET /api/watchlist`** - List all tracked products with status tags.
- **`POST /api/watchlist`** - `{"productId": "sony_good_deal", "targetPrice": 22000}`
- **`DELETE /api/watchlist/{id}`** - Removes item from watchlist.

### 5. Alerts
- **`GET /api/alerts`** - List notification alerts.
- **`POST /api/alerts/{id}/read`** - Mark alert as read.

### 6. Preferences
- **`GET /api/preferences`** - Fetch user priority and notification settings.
- **`PUT /api/preferences`** - Update settings.

---

## 🔒 4-Level Identity Schema Conformance
Every product model exposes the 4-level schema:
1. **`canonical_product`**: Abstract product definition (`id`, `name`, `brand`, `category`, `model`).
2. **`canonical_variant`**: Specific SKU variant (`id`, `productId`, `variant`, `color`, `sku`, `image`).
3. **`retailer_listing`**: Retail platform entry (`id`, `variantId`, `retailer`, `url`, `listingSku`, `availabilityStatus`).
4. **`seller_offer`**: Active merchant offer (`id`, `listingId`, `sellerId`, `sellerName`, `price`, `shippingCost`, `rating`, `reliability`, `returnPolicy`, `warranty`).
