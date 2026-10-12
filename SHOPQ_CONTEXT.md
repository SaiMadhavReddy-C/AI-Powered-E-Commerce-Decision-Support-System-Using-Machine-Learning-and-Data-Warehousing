# SHOPQ PROJECT CONTEXT & ARCHITECTURE (SOURCE OF TRUTH)

**Product Promise:** *"ShopQ is a friend who checks before you buy."*  
**Core UX Journey:** `SEARCH ➡️ CHECK ➡️ DECISION ➡️ WHY ➡️ BEST OPTION ➡️ ACTION ➡️ WATCH ➡️ ALERT`  
**Design System:** Light theme (`#FAF8F5` background, `#FFFFFF` card, `#C96B7A` Dusty Rose accent), Inter typography, 1px borders (`#E8E4E0`), 8px radius. Zero AI gradients or glassmorphism.

---

## A. Repository & Directory Structure
```
/Users/sai/.gemini/antigravity/scratch/shopq/
├── SHOPQ_CONTEXT.md                 # Single source of truth (this file)
├── AGENTS.md                        # Subagent execution rules & bounds
├── frontend/                        # Vite + React + Vanilla CSS Frontend
│   ├── src/
│   │   ├── App.jsx                  # Single global Navbar/BottomNav routing
│   │   ├── index.css                # Design system tokens (--bg, --bg-card, --accent)
│   │   ├── components/
│   │   │   ├── Layout/              # Navbar.jsx, BottomNav.jsx, PageContainer.jsx
│   │   │   ├── Price/               # PriceChart.jsx, PriceSummary.jsx, RetailerComparison.jsx
│   │   │   ├── Product/             # ProductHeader.jsx
│   │   │   ├── Recommendation/      # RecommendationCard.jsx, WhyPanel.jsx, BestOption.jsx, SellerInfo.jsx
│   │   │   ├── Search/              # SearchBar.jsx, SearchResults.jsx
   │   │   ├── Thinking/            # ThinkingScreen.jsx
   │   │   ├── Watchlist/           # WatchButton.jsx, WatchlistCard.jsx
   │   │   └── common/              # EmptyState.jsx
   │   ├── pages/                   # HomePage, AnalyzePage, DetailsPage, WatchlistPage, AlertsPage, PreferencesPage, HowItWorksPage, NotFoundPage
   │   ├── services/                # api.js, mockData.js
   │   └── utils/                   # constants.js, formatPrice.js, retailerDetect.js
└── backend/                         # FastAPI Python Backend
    ├── app/
    │   ├── main.py                  # FastAPI entry point
    │   ├── core/                    # config.py, security.py, logging.py
    │   ├── api/routes/              # health, search, analyze, products, watchlist, alerts, preferences
    │   ├── schemas/                 # product.py, decision.py, offer.py, watchlist.py, etc.
    │   ├── services/                # capture, collect, identity, analytics, ml, decision, advise
    │   └── providers/               # provider_registry.py, amazon, flipkart, croma, mock_provider
    └── database/                    # schema.sql, seed.sql, indexes.sql
```

---

## B. Approved Frontend Routes
- `/` ➡️ `HomePage` (Search-first hero, onboarding helper, recent items, watchlist preview)
- `/search?q=` ➡️ `SearchResultsPage` (Product query results list)
- `/analyze/:id` ➡️ `AnalyzePage` (Fast checklist -> Decision card -> Why -> Best Option -> Action)
- `/analyze/:id/details` ➡️ `DetailsPage` (3-Level breakdown: Level 1 Consumer, Level 2 Logic, Level 3 Technical)
- `/watchlist` ➡️ `WatchlistPage` (Decision Inbox grouped by `BUY_SIGNAL`, `WAITING`, `WATCHING`, `NEEDS_ATTENTION`)
- `/alerts` ➡️ `AlertsPage` (Notification feed)
- `/preferences` ➡️ `PreferencesPage` (Priority, wait tolerance, notification settings)
- `/how-it-works` ➡️ `HowItWorksPage` (Decision logic, seller checks, confidence levels explained)
- `*` ➡️ `NotFoundPage` (404 recovery page)

---

## C. Approved API Contract (`/api/analyze` & `/api/products/{id}`)
Backend returns structured JSON object ONLY. Never raw model internals or unformatted strings.
```json
{
  "product": {
    "id": "sony_wh1000xm5",
    "name": "Sony WH-1000XM5",
    "brand": "Sony",
    "category": "Headphones",
    "variant": "Black",
    "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80",
    "current_price": 23499,
    "currency": "INR"
  },
  "decision": {
    "decision": "WAIT",
    "confidence_level": "HIGH",
    "primary_reason": "PRICE_TREND_FALLING",
    "secondary_reasons": ["ABOVE_RECENT_LOW", "BETTER_TIMING_POSSIBLE"],
    "buy_point": 22999,
    "best_offer_id": "offer_123",
    "data_freshness": "FRESH",
    "data_coverage": "MEDIUM",
    "checked_at": "2026-10-07T23:55:00Z",
    "model_version": "price-v1",
    "matching_model_version": "match-v1",
    "decision_rules_version": "decision-v1"
  },
  "best_offer": {
    "id": "offer_123",
    "retailer": "Flipkart",
    "price": 22999,
    "seller_status": "RELIABLE",
    "availability": "IN_STOCK",
    "url": "https://flipkart.com/..."
  }
}
```

---

## D. Approved Database & DWDM Schema (PostgreSQL / Supabase)
1. **Identity Hierarchy**:
   - `canonical_product` (id, brand, canonical_name, category_id, canonical_image_url)
   - `canonical_variant` (id, product_id, model_number, variant_name, attributes_json)
   - `retailer_listing` (id, variant_id, retailer_id, external_product_id, title, product_url)
   - `seller_offer` (id, listing_id, seller_id, price, shipping_cost, availability, observed_at, collected_at)
2. **Star Schema Dimensions**: `dim_product`, `dim_variant`, `dim_retailer`, `dim_seller`, `dim_category`, `dim_date`
3. **Fact Tables**:
   - `fact_price_history` (price_observation_id, variant_id, retailer_id, seller_id, observed_at, collected_at, price, shipping_cost, availability_status)
   - `fact_recommendation` (recommendation_id, product_id, timestamp, decision, buy_point, confidence_level, primary_reason, data_freshness, data_coverage)
   - `fact_recommendation_outcome` (outcome_id, recommendation_id, observed_future_price, outcome_status)

---

## E. Security & Provider Rules
1. **URL Allowlisting & SSRF Protection**: Only allow `amazon.in`, `flipkart.com`, `croma.com`, `reliancedigital.in`, `myntra.com`. Reject `127.0.0.1`, `localhost`, private IPs (`10.x`, `172.16-31.x`, `192.168.x`), metadata IPs (`169.254.169.254`).
2. **Scraped Content**: Treat all retailer scraped HTML/text as untrusted data (sanitize against XSS and prompt injection).
3. **Provider Fallbacks**: Providers have states (`LIVE`, `PARTIAL`, `MOCK`, `UNAVAILABLE`). Gracefully fall back to `MockProvider` or recent cache when scrapers fail. Never fabricate live prices or sellers.

---

## F. Exact Subagent Ownership & Bounds
- **`shopq-core-fixer`**: Frontend bug files (`RetailerComparison.jsx`, `RecommendationCard.jsx`, `SellerInfo.jsx`, `BottomNav.jsx`, `WatchlistCard.jsx`).
- **`shopq-data-engineer`**: `src/services/mockData.js`, `src/services/api.js`, `src/utils/constants.js`.
- **`shopq-journey-builder`**: `src/App.jsx`, `src/pages/PreferencesPage.jsx`, `src/pages/HowItWorksPage.jsx`, `src/pages/NotFoundPage.jsx`, `src/components/Layout/Navbar.jsx`.
- **`shopq-experience-designer`**: `src/index.css`, `src/components/Layout/PageContainer.jsx`, all component & page CSS files.
- **`shopq-accessibility`**: `src/components/Price/PriceChart.jsx`, `src/components/Recommendation/WhyPanel.jsx`, `src/components/Recommendation/SellerInfo.jsx`, interactive card components.
- **`shopq-backend-engineer`**: `backend/app/` (FastAPI routes, schemas, services, main.py).
- **`shopq-database-dwdm-engineer`**: `backend/database/` (schema.sql, seed.sql, indexes.sql).
- **`shopq-security-engineer`**: `backend/app/core/security.py` (SSRF, URL allowlist, sanitization, CORS, error handling).
- **`shopq-provider-data-engineer`**: `backend/app/providers/` (ProviderRegistry, MockProvider, extraction heuristics).
- **`shopq-cloud-devops-engineer`**: `backend/Dockerfile`, deployment config, `.env.example`.
- **`shopq-ml-decision-engineer`**: `backend/app/services/ml/` & `decision/` (PriceTrend-v2 model, Buy safety gates, confidence engine).
- **`shopq-extension-engineer`**: `extension/` (Manifest V3 extension, `chrome.sidePanel`, popup, content script).
- **`shopq-integration-engineer`**: `frontend/src/services/api.js` (Wiring frontend to FastAPI backend endpoints).
- **`shopq-final-qa`**: Adversarial QA, build verification, and end-to-end path testing.
