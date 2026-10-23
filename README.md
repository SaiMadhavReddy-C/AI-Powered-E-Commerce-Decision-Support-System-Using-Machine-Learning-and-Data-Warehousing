<div align="center">

# 🛍️ ShopQ
### AI-Powered E-Commerce Decision Support System
#### *"A Friend Who Checks Before You Buy"*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![Gemini AI](https://img.shields.io/badge/Gemini_AI-2.0_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**B.Tech Final Year Project | Computer Science & Engineering**

[Live Demo](#-live-demo) • [Architecture](#-system-architecture) • [Features](#-key-features) • [Setup](#-quick-setup) • [API Docs](#-api-reference)

</div>

---

## 📌 Overview

**ShopQ** is an end-to-end AI-powered e-commerce decision support system that helps Indian consumers make smarter purchase decisions. Instead of manually browsing multiple shopping tabs, comparing prices, or risking purchases from suspicious sellers — ShopQ analyzes any product in seconds and delivers a clear, data-backed recommendation.

> **One-line value:** *Give ShopQ a product name or URL. It analyzes pricing trends, seller reliability, and market data across 10 Indian retailers — then tells you exactly: BUY, WAIT, or CAUTION.*

### The Problem
- Indian e-commerce users waste **47+ minutes** comparing products across Amazon, Flipkart, Croma, etc.
- **68% of online buyers** regret purchases due to price drops within 30 days (RedSeer, 2024)
- Fake discounts, unverified sellers, and variant confusion cost consumers ₹4,800+ crore annually

### The Solution
ShopQ combines **machine learning price prediction**, **real-time web intelligence via Gemini AI**, and a **7-gate safety engine** to deliver one confident recommendation with full transparency.

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **Gemini AI Product Analysis** | Search ANY product — AI fetches real INR prices and gives live buy/wait advice |
| 📈 **90-Day Price History Chart** | Visual price trend with historical low/high markers |
| 🏪 **10-Retailer Coverage** | Amazon.in, Flipkart, Croma, Reliance Digital, Tata CLiQ, Myntra, AJIO, Meesho, JioMart, Nykaa |
| 🛡️ **7-Gate Safety Engine** | Every BUY passes seller, stock, freshness, variant, and trust checks |
| 🤖 **PriceTrend-v2 ML Model** | 3-tier tiered ML: Rules → Random Forest → XGBoost based on data density |
| 🧩 **Chrome Extension (MV3)** | Instant overlay on any product page — no data sent to third parties |
| 📊 **DWDM Star Schema** | PostgreSQL data warehouse with dimension and fact tables |
| 📦 **4-Level Identity Schema** | Prevents variant mixing (128GB vs 256GB, Black vs Silver, etc.) |
| ⚡ **FastAPI Backend** | Sub-100ms response via async endpoints with rate limiting & SSRF protection |
| 📱 **Responsive UI** | Mobile-first React SPA with smooth animations and dark-ready design |

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                              │
│          React + Vite SPA              Chrome Extension (MV3)        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP / REST
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FASTAPI BACKEND                               │
│   Security Core │ SSRF Guard │ Rate Limiter │ CORS │ Request ID      │
│                                                                      │
│   /api/analyze  /api/search  /api/products  /api/watchlist           │
└───────────────────┬──────────────────────┬──────────────────────────┘
                    │                      │
          ┌─────────▼──────────┐  ┌────────▼───────────────────────┐
          │  PROVIDER LAYER    │  │   ML & DECISION ENGINE         │
          │                    │  │                                 │
          │  • Gemini AI       │  │  PriceTrend-v2 (3-Tier Model)  │
          │  • ScraperAPI      │  │  ┌──────────────────────────┐  │
          │  • Amazon Adapter  │  │  │ Tier 1: Rule-Based       │  │
          │  • Flipkart Adapter│  │  │ Tier 2: Random Forest    │  │
          │  • Croma Adapter   │  │  │ Tier 3: XGBoost          │  │
          │  • + 5 more        │  │  └──────────────────────────┘  │
          │  • Mock Fallback   │  │  7 Hard BUY Safety Gates       │
          └─────────┬──────────┘  └────────┬───────────────────────┘
                    │                      │
                    └──────────┬───────────┘
                               ▼
          ┌────────────────────────────────────────────┐
          │          SUPABASE / POSTGRESQL              │
          │                                            │
          │  Identity Layer:                           │
          │  canonical_product → canonical_variant      │
          │     → retailer_listing → seller_offer       │
          │                                            │
          │  Star Schema (DWDM):                       │
          │  dim_product  dim_retailer  dim_seller      │
          │  fact_price_history  fact_recommendation    │
          └────────────────────────────────────────────┘
                               │
                               ▼
                   ┌─────────────────────┐
                   │   RECOMMENDATION    │
                   │  BUY / WAIT / GRAB  │
                   │  CAUTION / CHECK_ALT│
                   └─────────────────────┘
```

---

## 🔬 Data Pipeline — 5-Stage Extraction

```
RAW HTML (via ScraperAPI / Web)
       │
       ▼
Stage 1: JSON-LD Parser        → Structured schema.org/Product data
       │ (fail)
       ▼
Stage 2: Known Selectors       → Retailer-specific CSS/XPath patterns
       │ (fail)
       ▼
Stage 3: Generic DOM Extractor → Price pattern heuristics across DOM
       │ (fail)
       ▼
Stage 4: Regex Extractor       → Fallback price/title patterns
       │ (fail)
       ▼
Stage 5: Gemini AI (LLM)       → Last-resort intelligent extraction
       │
       ▼
Normalized ProviderOffer → fact_price_history → ML Feature Matrix
```

---

## 🤖 ML & Decision Engine

### PriceTrend-v2 — Tiered Price Prediction

| Tier | Trigger | Algorithm | Output |
|------|---------|-----------|--------|
| **Tier 1** | `< 14` observations | Rule-Based (Moving Average + Trend Slope) | Direction: RISING/FALLING/STABLE |
| **Tier 2** | `14–59` observations | Random Forest Classifier | Drop probability (14-day window) |
| **Tier 3** | `≥ 60` observations | XGBoost Regressor | Predicted minimum price (14-day) |

> **Anti-leakage**: Strict chronological train/val/test split enforced — future data never leaks into training.

### 7 Hard BUY Safety Gates

A **BUY** decision is emitted **ONLY if ALL 7 gates pass**. ML predictions cannot override a failed gate.

```
Gate 1: ✅ Exact Product Match    — Title similarity ≥ 85%
Gate 2: ✅ Exact Variant Match    — SKU / color / storage verified
Gate 3: ✅ Fresh Data             — Observed within last 6 hours
Gate 4: ✅ Acceptable Seller      — Reliability: RELIABLE/MODERATE, Rating ≥ 4.0★
Gate 5: ✅ In Stock               — Availability status: IN_STOCK
Gate 6: ✅ Trusted Source         — Domain in authorized retailer allowlist
Gate 7: ✅ Sufficient Coverage    — ≥ 7 historical observations OR multi-store data
```

### Decision States

| Decision | Meaning |
|----------|---------|
| `BUY` | All gates pass. Price is at/near historical low. |
| `GRAB` | Flash deal — price unusually low, act fast. |
| `WAIT` | Price predicted to drop. Hold off. |
| `WAIT_SALE` | Festival/sale event approaching. |
| `CHECK_ALT` | Better alternative exists at a different retailer. |
| `CAUTION` | Seller reliability flags detected. |
| `DONT_RUSH` | Price is stable. No urgency either way. |
| `YOUR_CALL` | Insufficient data for a strong signal. |
| `NO_DECISION` | All sources failed or product unverifiable. |

---

## 📦 4-Level Product Identity Schema

Prevents cross-variant price contamination (e.g., mixing iPhone 15 128GB with 256GB prices):

```
Level 1  canonical_product      → Apple iPhone 15
           │
Level 2  canonical_variant      → iPhone 15, 128GB, Midnight Black
           │                       (SKU: APPL-IP15-128-BLK)
Level 3  retailer_listing       → Amazon India B0CHX2FMDB
           │
Level 4  seller_offer           → Appario Retail, ₹69,999, 4.8★, IN_STOCK
```

---

## 🧩 Chrome Extension (Manifest V3)

- **Privacy-First**: Operates entirely in local DOM via Shadow DOM (`#shopq-indicator-host`). Zero browsing history leakage.
- **Native Side Panel**: Uses `chrome.sidePanel` for a seamless in-browser experience.
- **SSRF Protected**: Content scripts only communicate with `https://shopq-backend.onrender.com`.
- **Supported Retailers**: Amazon.in, Flipkart, Croma, Reliance Digital, Tata CLiQ, Myntra, AJIO, Meesho, JioMart, Nykaa.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React 18, Vite 5, Vanilla CSS | SPA with price charts, decision UI |
| **Backend API** | Python 3.11, FastAPI, Pydantic V2, Uvicorn | REST API, business logic |
| **AI / Online Data** | Google Gemini 2.0 Flash API | Live product intelligence, LLM fallback |
| **Web Scraping** | ScraperAPI (India geo-targeted) | Live e-commerce page extraction |
| **Database / DWDM** | PostgreSQL (Supabase), Star Schema | Data warehouse, analytics |
| **ML Engine** | NumPy, Scikit-Learn, XGBoost | Price prediction, trend analysis |
| **Browser Extension** | Chrome MV3, Shadow DOM | In-browser product overlay |
| **Deployment** | Vercel (frontend), Render (backend) | Cloud-native production hosting |
| **Security** | SSRF protection, CORS, Rate limiting, Pydantic validation | API hardening |

---

## 🚀 Quick Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- A free **Gemini API Key** → [Get it here (free)](https://aistudio.google.com/apikey)

### 1. Clone & Configure

```bash
git clone https://github.com/SaiMadhavReddy-C/AI-Powered-E-Commerce-Decision-Support-System-Using-Machine-Learning-and-Data-Warehousing.git
cd AI-Powered-E-Commerce-Decision-Support-System-Using-Machine-Learning-and-Data-Warehousing
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set: GEMINI_API_KEY=your_key_here

# Start server
python run.py
```

✅ Backend running at `http://localhost:8000`  
📖 Swagger API Docs at `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

✅ Frontend running at `http://localhost:5173`

### 4. Run Tests

```bash
# Backend test suite
cd backend && .venv/bin/pytest tests/ -v

# Chrome Extension validation
python3 extension/validate_extension.py

# Production smoke test
cd backend && .venv/bin/python scripts/production_smoke_test.py
```

---

## 🌐 Production Deployment

### Frontend → Vercel

```bash
cd frontend
# Set in Vercel Dashboard → Environment Variables:
# VITE_API_BASE_URL = https://shopq-backend.onrender.com
# VITE_ENABLE_MOCK_FALLBACK = true
```

### Backend → Render (Docker)

```bash
# Set in Render Dashboard → Environment Variables:
# GEMINI_API_KEY = your_gemini_api_key
# ENVIRONMENT = production
# PORT = 10000
```

See [`render.yaml`](render.yaml) for full configuration.

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health check |
| `POST` | `/api/analyze` | Analyze product by URL, ID, or keyword |
| `POST` | `/api/search` | Search products across catalog |
| `GET` | `/api/products/{id}` | Get product details |
| `GET` | `/api/products/{id}/price-history` | Get 90-day price history |
| `GET` | `/api/products/{id}/offers` | Get all retailer offers |
| `GET/POST` | `/api/watchlist` | Manage watchlist |
| `GET` | `/api/alerts` | Get price drop alerts |
| `GET/PUT` | `/api/preferences` | User preferences |

### Sample Request

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Sony WH-1000XM5 headphones"}'
```

### Sample Response

```json
{
  "product": {
    "id": "sony_good_deal",
    "name": "Sony WH-1000XM5",
    "brand": "Sony",
    "currentPrice": 22499.0,
    "retailer": "Amazon India",
    "historicalLow": 22499.0,
    "historicalHigh": 29990.0
  },
  "decision": {
    "decision": "BUY",
    "confidence_level": "HIGH",
    "primary_reason": "Lowest price in 90 days. All 7 safety gates passed.",
    "predicted_direction": "FALLING",
    "safety_gates_passed": 7,
    "safety_gates_total": 7
  },
  "bestOffer": {
    "retailer": "Amazon India",
    "price": 22499.0,
    "seller": "Appario Retail",
    "savings": 7491.0
  }
}
```

---

## 🔒 Security Architecture

- **SSRF Protection**: Strict allowlist of 10 Indian retail domains. All private IPs and localhost blocked.
- **Rate Limiting**: `/api/analyze` limited to 10 RPM per IP sliding window.
- **Input Validation**: Full Pydantic V2 schema validation on all endpoints.
- **CORS Policy**: Configurable origin allowlist — no wildcard in production.
- **No Credential Storage**: API keys held only in environment variables, never in code.
- **Request ID Tracing**: Every request tagged with UUID for full audit trail.

---

## 🗄️ DWDM Star Schema

```sql
-- Dimension Tables
dim_product      (product_id, name, brand, category, model)
dim_variant      (variant_id, product_id, color, storage, sku)
dim_retailer     (retailer_id, name, domain, country)
dim_seller       (seller_id, name, rating, reliability_grade)
dim_date         (date_id, date, day_of_week, month, quarter, is_festival)

-- Fact Tables
fact_price_history      (history_id, product_id, retailer_id, seller_id, date_id,
                         price, shipping_cost, availability_status, source_type,
                         observed_at, collected_at)
fact_recommendation     (rec_id, product_id, date_id, decision, confidence,
                         safety_gates_passed, ml_tier_used, predicted_price)
fact_recommendation_outcome  (outcome_id, rec_id, actual_price_7d,
                              actual_price_30d, was_correct)
```

---

## 📊 Data Source Transparency

| Source Type | Tag | When Used |
|-------------|-----|-----------|
| **GEMINI_AI** | `source_type = GEMINI_AI` | Live AI-powered product intelligence |
| **SCRAPERAPI** | `source_type = SCRAPERAPI` | Live web extraction (with API key) |
| **MOCK** | `source_type = MOCK` | Offline unit testing & CI/CD fallback only |

> ShopQ **never silently** substitutes mock data for live data. Every response is tagged with its source type.

---

## 📁 Project Structure

```
shopq/
├── backend/                     # FastAPI Backend
│   ├── app/
│   │   ├── api/routes/          # REST endpoint handlers
│   │   ├── core/                # Config, logging, security middleware
│   │   ├── providers/           # ScraperAPI, adapters, extraction pipeline
│   │   │   ├── adapters/        # Amazon, Flipkart, Croma, etc.
│   │   │   └── pipeline/        # 5-stage extraction (JSON-LD→LLM)
│   │   ├── schemas/             # Pydantic V2 models
│   │   └── services/
│   │       ├── gemini_resolver.py   # 🆕 Live AI product intelligence
│   │       ├── product_service.py   # Catalog + resolution engine
│   │       ├── decision_service.py  # Main analysis orchestrator
│   │       └── decision/
│   │           ├── synthesizer.py   # Decision synthesis
│   │           ├── safety_gate.py   # 7 BUY safety gates
│   │           └── confidence_engine.py
│   ├── database/
│   │   ├── schema.sql           # Full DWDM star schema
│   │   ├── seed.sql             # Demo data
│   │   └── indexes.sql          # Performance indexes
│   └── tests/                   # 79 unit + integration tests
│       ├── test_api.py
│       ├── test_ml_decision.py
│       ├── test_providers.py
│       └── test_security.py
│
├── frontend/                    # React + Vite SPA
│   └── src/
│       ├── pages/               # HomePage, SearchResults, AnalyzePage, etc.
│       ├── components/          # RecommendationCard, PriceChart, etc.
│       └── services/
│           ├── api.js           # Backend integration layer
│           └── mockData.js      # 12 test scenario fixtures
│
├── extension/                   # Chrome Extension MV3
│   ├── manifest.json
│   ├── background.js
│   └── content.js
│
├── submission/                  # Academic project report
│   └── ShopQ_Project_Report.md
│
├── render.yaml                  # Render (backend) deployment config
└── README.md
```

---

## 🧪 Test Coverage

| Suite | Tests | Coverage |
|-------|-------|---------|
| `test_api.py` | 18 tests | All REST endpoints |
| `test_ml_decision.py` | 24 tests | Decision engine, safety gates, ML tiers |
| `test_providers.py` | 21 tests | ScraperAPI, extraction pipeline, SSRF |
| `test_security.py` | 16 tests | CORS, rate limiting, input validation |
| **Total** | **79 tests** | Full backend coverage |

---

## 👤 Author

**Sai Madhav Reddy C**  
B.Tech Computer Science & Engineering  
*AI-Powered E-Commerce Decision Support System Using Machine Learning and Data Warehousing*

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**⭐ Star this repo if it helped you | 🍴 Fork it to build your own**

Made with ❤️ for smarter shopping in India

</div>
