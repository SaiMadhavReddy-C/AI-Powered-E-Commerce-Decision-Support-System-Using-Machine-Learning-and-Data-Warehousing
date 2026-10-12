# ShopQ: Academic Project Presentation Slide Deck
## 15-Slide Presentation Deck for Academic Evaluation

> **Design Note for Presenter**: Keep slides clean, visual, and structured with bullet points. Avoid dense paragraphs. Use the exact product identity: *"ShopQ is a friend who checks before you buy."*

---

### Slide 1: Title Slide

# ShopQ
### Real-Time E-Commerce Price Intelligence, DWDM Star Schema Data Pipeline & Multi-Retailer Decision Engine

- **Product Identity**: *"ShopQ is a friend who checks before you buy."*
- **Presented By**: Academic Project Team (Batch 8)
- **Department**: Computer Science & Engineering
- **Technologies**: React 18, FastAPI, PostgreSQL/Supabase, ScraperAPI, Chrome Manifest V3, Machine Learning

---

### Slide 2: Problem Statement

# Problem Statement: E-Commerce Price Opacity

- **Dynamic Pricing Traps**: Prices fluctuate hour-by-hour across retailers, leading to buyer remorse.
- **Deceptive Discounting**: Artificial MSRP inflation followed by pseudo-discounts tricks consumers during sales.
- **Multi-Merchant Fragmentation**: Identical products are listed under conflicting titles across Amazon, Flipkart, Croma, Reliance Digital, etc.
- **Merchant Risks**: Low prices from unverified or fraudulent sellers mislead shoppers.
- **Cognitive Overload**: Raw historical price charts force buyers to manually guess future price drops.

---

### Slide 3: Existing Systems & Limitations

# Existing Systems & Their Limitations

- **Traditional Price Trackers**:
  - Focus on single-URL scraping and simple line graphs.
  - Fail to canonicalize product SKUs across competing stores.
  - Ignore seller credibility, review volume, and shipping surcharges.
  - Lack automated safety checks, recommending out-of-stock or mismatched items.
- **The Core Void**: No existing platform offers **deterministic safety enforcement** combined with **predictive purchasing recommendations**.

---

### Slide 4: Proposed Solution

# Proposed Solution: ShopQ Platform

- **Actionable Purchasing Advice**: Emits unambiguous decisions (`BUY`, `WAIT`, `GRAB`, `CHECK_ALT`, `CAUTION`, etc.).
- **Canonical Product Identity**: 4-Level Schema (`canonical_product` $\rightarrow$ `canonical_variant` $\rightarrow$ `retailer_listing` $\rightarrow$ `seller_offer`).
- **DWDM Star Schema**: PostgreSQL DW storing conformed dimensions and time-series price facts.
- **ScraperAPI Gateway**: Resilient 5-tier web extraction pipeline bypassing anti-bot measures across 10 Indian stores.
- **Deterministic Hard BUY Gates**: 7 mandatory safety checks blocking unsafe ML predictions.
- **Unified UX**: React Web App + Chrome Manifest V3 Extension Side Panel.

---

### Slide 5: Project Objectives

# Key Project Objectives

1. **Entity Canonicalization**: Map fragmented multi-store titles to unified hardware SKUs.
2. **Resilient Data Collection**: Harvest real-time price, stock, seller rating, and shipping metrics across 10 Indian retailers.
3. **Enterprise DWDM Architecture**: Implement Kimball Star Schema for historical analysis and ML feature extraction.
4. **Hierarchical Forecasting**: Implement `PriceTrend-v2` 3-tier ML price prediction (Moving Average $\rightarrow$ Linear Regression $\rightarrow$ XGBoost).
5. **Safety Gate Enforcement**: Guarantee 0% false deal recommendations via 7 deterministic gates.
6. **Cross-Platform Access**: Deliver Web App + Chrome Side Panel integration.

---

### Slide 6: Overall System Architecture

# System Architecture Overview

```
[ User Browser / Chrome Extension MV3 ]
                │
                ▼ (HTTP REST / JSON API)
[ FastAPI Backend Gateway (Security & SSRF Core) ]
      │                   │                     │
      ▼                   ▼                     ▼
[ Provider Registry ]  [ ML & Gates Engine ]  [ Supabase DWDM ]
(ScraperAPI Gateway)  (PriceTrend-v2/Synth)   (OLTP & Star Schema)
      │
      ▼
[ 10 Indian Retailers (Amazon, Flipkart, Croma, etc.) ]
```

- Decoupled, high-performance architecture written in Python FastAPI & React.

---

### Slide 7: Data Collection & ScraperAPI Pipeline

# Data Collection & Web Scraping Pipeline

- **ScraperAPI Integration**:
  - Server-side proxy gateway with India geotargeting.
  - Automated IP rotation & headless Chrome JS rendering.
  - Keeps API key strictly hidden from client code.
- **5-Stage Extraction Cascade**:
  1. `JSON_LD`: Schema.org metadata parsing.
  2. `KNOWN_SELECTORS`: Optimized CSS/XPath rules per retailer.
  3. `GENERIC_DOM`: OpenGraph & microdata fallback.
  4. `REGEX`: Text pattern extraction (`₹\s?[\d,]+`).
  5. `LLM_FALLBACK`: Heuristic DOM structural parser.

---

### Slide 8: DWDM / Data Warehouse Design

# Data Warehousing & Star Schema Architecture

- **Kimball Dimensional Model**:
  - **Conformed Dimensions**: `dim_product`, `dim_variant`, `dim_retailer`, `dim_seller`, `dim_category`, `dim_date`.
  - **Fact Tables**: `fact_price_history`, `fact_recommendation`, `fact_recommendation_outcome`.
- **Analytical ETL Flow**:
  $$\text{RAW HTML} \rightarrow \text{STAGING} \rightarrow \text{CURATED OFFERS} \rightarrow \text{FACT/DIM SCHEMA} \rightarrow \text{ML FEATURES}$$
- Enables fast time-series analytical queries (7d, 14d, 30d, 90d moving averages and price dispersion).

---

### Slide 9: AI/ML & Price Trend Analytics

# AI / ML Price Forecasting Engine (`PriceTrend-v2`)

- **3-Tier Prediction Fallback Hierarchy**:
  - **Tier 3 (Full History $\ge 14$ obs)**: XGBoost / Random Forest Time-Series Model.
  - **Tier 2 (Partial History $\ge 3$ obs)**: Linear Trend & Slope Regression.
  - **Tier 1 (New / Sparse History)**: 14-Day Exponential Moving Average (EMA).
- **Core Output Metrics**:
  - `predicted_min_price_14d`: Forecasted 14-day minimum price.
  - `drop_probability`: Drop likelihood ($0.0 \text{--} 1.0$).
- **Rule**: *"Prediction is evidence. The Decision Engine makes the final recommendation."*

---

### Slide 10: Decision Engine & 7 Hard BUY Safety Gates

# Decision Synthesizer & Hard BUY Safety Gates

- **7 Mandatory Hard BUY Safety Gates** (`HardBuySafetyGate`):
  1. `exact_product_match`: Title matches canonical product.
  2. `exact_variant`: Color/Storage SKU verified.
  3. `fresh_data`: Price data updated within $<6$ hours.
  4. `acceptable_seller`: Seller rating $\ge 4.0\star$, reliability `RELIABLE`.
  5. `in_stock_availability`: Item currently in stock.
  6. `trusted_source`: Retailer domain on trusted allowlist.
  7. `sufficient_coverage`: Market data coverage $\ge 70\%$.
- **Strict Rule**: If ANY safety gate fails, `BUY` is strictly blocked $\rightarrow$ overridden to `CAUTION`, `WAIT`, or `NO_DECISION`.

---

### Slide 11: Chrome Extension Manifest V3

# Chrome Extension (Manifest V3 Integration)

- **Native Side Panel API**:
  - Triggered via `chrome.sidePanel.open()`.
  - Displays instant decision, why panel, best offer, and price trends alongside browsing.
- **Shadow DOM Badge**:
  - Injects isolated micro-badges (`#shopq-badge-root`) directly into retailer product pages.
  - Zero CSS style bleeding into retailer site stylesheets.
- **Privacy & Security**:
  - Operates strictly on allowlisted store URLs. Zero third-party analytics tracking.

---

### Slide 12: Results & System Validation

# System Validation & Test Results

- **Backend Test Suite**:
  - **79/79 PASS** (100% test coverage across API routes, Pydantic schemas, provider fallbacks, safety gates, ML engine, and decision synthesis).
- **Chrome Extension Validation**:
  - **38/38 PASS** (Verified service worker messaging, side panel rendering, DOM badge insertion).
- **Live ScraperAPI Online Validation**:
  - Successfully extracted and normalized live prices across all 10 supported Indian retailers (Amazon, Flipkart, Croma, Reliance Digital, etc.).

---

### Slide 13: Security & Data Privacy

# Security Hardening & Privacy Architecture

- **Server-Side SSRF Protection**:
  - Strict regex domain validation against allowlisted stores.
  - Rejects local/private IPs (`127.0.0.1`, `10.x.x.x`, `169.254.169.254`).
- **Scraped Content Sanitization**:
  - Defangs all extracted web strings to prevent stored XSS attacks in frontend panels.
- **Credential Isolation**:
  - ScraperAPI key and Supabase credentials remain backend-only.
- **CORS Control**:
  - Restricts API access to verified client web origins and extension IDs.

---

### Slide 14: Demo & UI Walkthrough

# Live System Demonstration

- **Demonstration Flow**:
  1. Open ShopQ Web App (`/`).
  2. Paste product URL (e.g., Sony WH-1000XM5).
  3. View 3-Step Decision Checklist $\rightarrow$ Decision Card (`WAIT` / `BUY`).
  4. Inspect "Why" Explanation & Safety Gate Status.
  5. Explore Cross-Retailer Price Comparison & Historical Chart.
  6. Add to Watchlist & simulate Alert trigger.
  7. Open Retailer Store page $\rightarrow$ Trigger Chrome Side Panel displaying identical decision.

---

### Slide 15: Conclusion & Future Scope

# Conclusion & Future Scope

- **Summary of Achievements**:
  - Developed a full-stack e-commerce decision intelligence system.
  - Created a 4-level canonical product schema and Kimball Star Schema data warehouse.
  - Implemented `PriceTrend-v2` ML forecasting bounded by 7 deterministic safety gates.
  - Delivered Web & Chrome Extension Side Panel consumer tools.
- **Future Roadmap**:
  - Automated WebPush/Email Price Drop Alerts.
  - Instant Bank Card / Coupon Discount Synthesis.
  - Multi-Region expansion (US `USD`, European `EUR`).
  - LLM-based customer review defect sentiment mining.

---

### End of Slide Deck
**Thank You! Questions & Discussion.**
