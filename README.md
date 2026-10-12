# SHOPQ — "A Friend Who Checks Before You Buy"

> **One-Sentence Product Promise:**  
> *"Give ShopQ a product. ShopQ does the research. You get the answer."*

ShopQ is an intelligent e-commerce pre-purchase decision engine designed for Indian retail platforms (Amazon India, Flipkart, Croma, Reliance Digital, Tata CLiQ, Myntra, AJIO, Meesho, JioMart, Nykaa). Rather than forcing users to browse dozens of tabs, track volatile prices manually, or risk purchasing from suspicious third-party sellers, ShopQ delivers a clear, evidence-based recommendation: **BUY**, **WAIT**, **CHECK ANOTHER**, **CAUTION**, or **NO DECISION**.

---

## 🏛️ System Architecture & Data Flow

```
                      [ USER INTERFACE ]
                React + Vite SPA / Chrome Extension
                               │
                               ▼
                      [ FASTAPI BACKEND ]
                 Security Core & SSRF Protection
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
      [ PROVIDER REGISTRY ]           [ SUPABASE / POSTGRES ]
   ScraperAPI Live Gateway              Star Schema & DWDM
               │                               │
               ▼                               ▼
     [ 10 RETAILER WEBPAGES ]        [ ML & DECISION ENGINE ]
  Extract ➡️ Normalize Offer        PriceTrend-v2 & 7 Safety Gates
               │                               │
               └───────────────┬───────────────┘
                               ▼
                      [ RECOMMENDATION ]
                Structured Decision Output
```

### Data Pipeline Architecture
1. **RAW STAGING**: Live webpage HTML fetched via ScraperAPI (geotargeted `country_code=in`).
2. **CURATED EXTRACTION**: 5-Stage Pipeline (`JSON-LD` ➡️ `KNOWN_SELECTORS` ➡️ `GENERIC_DOM` ➡️ `REGEX` ➡️ `LLM_FALLBACK`).
3. **FACT / DIMENSION STORAGE**: Normalized into 4-Level Identity Schema (`canonical_product`, `canonical_variant`, `retailer_listing`, `seller_offer`) and appended to `fact_price_history`.
4. **ML FEATURE MATRIX**: Time-series features (moving averages, volatility, price delta %, drop probability) fed into `PriceTrend-v2`.
5. **DECISION SYNTHESIS**: Evaluated against the **7 Hard BUY Safety Gates** before emitting structured decision JSON.

---

## 🛒 4-Level Product Identity Schema

ShopQ implements a 4-level entity hierarchy to prevent variant mixing (e.g., confusing 128GB vs 256GB models):

```
Level 1: canonical_product  (e.g., Sony WH-1000XM5 Headphones)
   └── Level 2: canonical_variant  (e.g., Black, SKU-SONY-XM5-BLK)
          └── Level 3: retailer_listing  (e.g., Amazon India Listing B09XS7JWHH)
                 └── Level 4: seller_offer  (e.g., Appario Retail, ₹22,499, 4.8★)
```

---

## 🤖 AI / ML & Decision Engine Architecture

### `PriceTrend-v2` Tiered Prediction Engine
- **Tier 1 (Rule-Based Baseline)**: Used when observations `< 14`. Evaluates moving averages & trend slopes.
- **Tier 2 (Simple ML / Random Forest)**: Used when observations are between `14` and `60`. Predicts 14-day drop probability.
- **Tier 3 (XGBoost Regressor)**: Used when observations `≥ 60`. Predicts 14-day forward minimum price with temporal cross-validation.
- **Chronological Train/Val/Test Split**: Enforces strict `Past -> Train / Later -> Val / Newest -> Test` split to eliminate data leakage.

### The 7 Hard BUY Safety Gates
A **BUY** signal is permitted **ONLY when ALL 7 safety gates pass**:
1. **Exact Product Match Gate**: Verified title match.
2. **Exact Variant Gate**: Verified hardware SKU and color match.
3. **Fresh Data Gate**: Observation timestamp `< 6 hours` old.
4. **Acceptable Seller Gate**: Reliability grade `RELIABLE`/`MODERATE` and rating `≥ 4.0★`.
5. **In-Stock Availability Gate**: Offer status is `IN_STOCK`.
6. **Trusted Source Gate**: Domain is an authorized retailer.
7. **Sufficient Coverage Gate**: Historical observations `≥ 7` points or multi-store coverage.

*Note: ML predictions can NEVER override a failed safety gate.*

---

## 🔍 Data Source Authenticity: Live vs Mock

ShopQ strictly distinguishes between real live observations and offline benchmark data:

- **LIVE RETAILER DATA (`source_type = LIVE_RETAILER`)**:
  - Live data acquired on-demand via ScraperAPI from supported retailer PDPs.
  - Tagged with exact `observed_at` and `collected_at` ISO timestamps.
- **HISTORICAL BENCHMARK DATA (`source_type = HISTORICAL_BENCHMARK`)**:
  - Used for 90-day baseline trend lines when building initial catalog history.
- **MOCK FALLBACK DATA (`source_type = MOCK`)**:
  - Used strictly for offline unit testing, zero-downtime development, and fallback scenarios when external network access is unavailable. No simulated data silently replaces live scraping without explicit source tagging.

---

## 🧩 Chrome Extension (Manifest V3)

- **Privacy-First Architecture**: Operates 100% locally on the client page DOM using Shadow DOM (`#shopq-indicator-host`). Does NOT stream browsing history.
- **Native Side Panel**: Opens native `chrome.sidePanel` interface communicating directly with `/api/analyze`.
- **Supported Retailers**: Amazon India, Flipkart, Croma, Reliance Digital, Tata CLiQ, Myntra, AJIO, Meesho, JioMart, Nykaa.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 18, Vite, Vanilla CSS (`#FAF8F5` theme, Dusty Rose `#C96B7A` accent, Inter font) |
| **Backend API** | Python 3.11, FastAPI, Pydantic V2, Uvicorn |
| **Database / DWDM** | Supabase PostgreSQL, Star Schema (`dim_*`, `fact_*`) |
| **Web Data Gateway** | ScraperAPI (India Geotargeted proxies, `render=false` default) |
| **ML & Analytics** | NumPy, Pandas, Scikit-Learn, XGBoost |
| **Browser Extension** | Chrome Extension Manifest V3, Shadow DOM, `chrome.sidePanel` |

---

## 🚀 Quick Setup & Execution

### 1. Backend Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```
Backend API will listen on `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend development server will listen on `http://localhost:5173`.

### 3. Run Test Suites
```bash
# Backend Test Suite (79 tests)
cd backend && .venv/bin/pytest tests/

# Chrome Extension Validation (38 tests)
python3 extension/validate_extension.py

# End-to-End Production Smoke Test
cd backend && .venv/bin/python scripts/production_smoke_test.py
```
