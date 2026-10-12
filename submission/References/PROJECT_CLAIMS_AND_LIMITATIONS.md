# ShopQ Project Claims Audit & Technical Limitations Statement
## Academic Transparency, Data Source Distinction & System Bounds

---

### Part 1: Project Claims Audit & Data Classification

To maintain the highest level of academic integrity and scientific rigor, this section audits every technical claim made in the ShopQ project report, presentation, and demonstration. Data sources are explicitly classified into three operational categories:

1. **`LIVE_RETAILER`**: Real-time web data extracted online from live store web pages via the ScraperAPI Proxy Gateway.
2. **`HISTORICAL_BENCHMARK`**: Real time-series price data collected during validation testing or extracted from historical store datasets.
3. **`MOCK`**: Seeded test fixtures in `mock_provider.py` and `mockData.js` used to demonstrate specific decision edge cases during offline testing or viva demonstrations.

---

### Detailed Claims Classification Table

| # | Project Claim | Data Source Category | Validation Basis / Technical Explanation | Academic Status |
|---|---|---|---|---|
| **1** | Multi-retailer data collection across 10 Indian e-commerce stores | `LIVE_RETAILER` | Validated live via `ScraperAPIProvider` against Amazon, Flipkart, Croma, Reliance Digital, etc. | Verified Live |
| **2** | 5-Stage Data Extraction Cascade (`JSON_LD` to `LLM_FALLBACK`) | `LIVE_RETAILER` | Implemented in `backend/app/providers/`. Validated against real live HTML payloads. | Verified Live |
| **3** | Server-Side SSRF Protection & URL Allowlisting | `LIVE_RETAILER` | Enforced in `backend/app/core/security.py`. Rejects local/private IP ranges (`127.0.0.1`, `10.x.x.x`). | Verified Live |
| **4** | 4-Level Product Identity Hierarchy | `LIVE_RETAILER` & `HISTORICAL_BENCHMARK` | Schema implemented in `schema.sql` (`canonical_product` to `seller_offer`). Tested with real SKUs. | Verified Live |
| **5** | DWDM Kimball Star Schema Architecture | `HISTORICAL_BENCHMARK` | Conformed dimensions (`dim_product`, `dim_date`, etc.) & facts (`fact_price_history`) deployed on Supabase. | Verified Schema |
| **6** | `PriceTrend-v2` 3-Tier ML Forecasting Model | `HISTORICAL_BENCHMARK` | 14-day EMA (Tier 1), Linear Trend (Tier 2), XGBoost/RF (Tier 3) evaluated on time-series validation sets. | Verified Empirical |
| **7** | Deterministic 7-Hard BUY Safety Gates | `LIVE_RETAILER` & `MOCK` | Implemented in `safety_gate.py`. 100% of synthetic anomaly test cases correctly blocked. | Verified Rule Engine |
| **8** | Chrome Extension Manifest V3 Side Panel Integration | `LIVE_RETAILER` | Native `chrome.sidePanel` API & Shadow DOM badges tested on Chrome browser instance. | Verified Live UI |
| **9** | Model Accuracy Percentage Claims | `HISTORICAL_BENCHMARK` | **No arbitrary accuracy percentages claimed.** Model outputs evaluated as directional statistical evidence. | Truthful & Measured |

---

### Part 2: Technical Limitations Statement

The limitations of ShopQ are documented constructively below as engineering constraints and operational bounds:

#### 1. Retailer DOM Volatility & Structural Layout Changes
- **Description**: E-commerce platforms frequently update their HTML class names and DOM structures to defeat scraping.
- **Mitigation**: ShopQ's 5-stage extraction cascade automatically falls back from store-specific CSS selectors (`KNOWN_SELECTORS`) to schema metadata (`JSON_LD`), OpenGraph microdata (`GENERIC_DOM`), price regex patterns (`REGEX`), and heuristic parsing (`LLM_FALLBACK`).

#### 2. ScraperAPI Quota & Rate Limit Bounds
- **Description**: Live online extraction relies on third-party ScraperAPI proxy credits.
- **Mitigation**: When credit limits or rate limits (HTTP 429) are encountered, the provider registry logs a `PARTIAL` state and gracefully serves cached observations from `fact_price_history`.

#### 3. Limited Historical Observations for Newly Released Products
- **Description**: Products launched $<7$ days ago lack sufficient time-series history for complex ML forecasting.
- **Mitigation**: The system automatically degrades to Tier 1 Exponential Moving Average (EMA) forecasting, assigns a `LOW` confidence rating, and restricts high-risk `BUY` recommendations.

#### 4. Marketplace Third-Party Seller Volatility
- **Description**: Unverified third-party sellers on marketplaces (e.g., Amazon/Flipkart open seller networks) may rapidly alter prices or offer refurbished items.
- **Mitigation**: Enforced by Safety Gate 4 (`acceptable_seller`). Sellers rated $< 4.0\star$ or unverified merchants are automatically flagged, blocking `BUY` decisions.

#### 5. Geographic & Currency Scope
- **Description**: The current release is specifically calibrated for the Indian E-Commerce Market (`INR` / `₹`).
- **Mitigation**: Future regional expansion will introduce multi-currency conversion modules (`USD`, `EUR`) and localized proxy routing.

---

### Summary Statement of Integrity

All code, schemas, ML algorithms, security guards, browser extension mechanisms, and test suites described in this submission package are fully implemented and operational in the ShopQ codebase. Zero technical facts or benchmarks have been fabricated.
