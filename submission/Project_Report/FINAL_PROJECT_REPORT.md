# ShopQ: Algorithmic Price Intelligence, Multi-Retailer Data Warehousing & Decision Engine
## Final Academic Project Report

---

### 1. Title Page

**PROJECT TITLE:** ShopQ: Real-Time E-Commerce Price Intelligence, DWDM Star Schema Data Pipeline & Multi-Retailer Decision Engine  
**SUBTITLE:** "ShopQ is a friend who checks before you buy."  
**DEGREE / PROGRAM:** Bachelor of Technology / Master of Technology in Computer Science & Engineering / Data Science  
**ACADEMIC BATCH:** Batch 8 Submission (2025–2026)  
**SUBMITTED BY:** Academic Project Team  
**UNDER THE GUIDANCE OF:** Department of Computer Science & Engineering, Faculty Advisor & Project Guide  
**INSTITUTION:** School of Engineering and Technology  
**DATE OF SUBMISSION:** October 2026  

---

### 2. Certificate / Declaration Placeholders

#### Certificate of Approval
> This is to certify that the project entitled **"ShopQ: Real-Time E-Commerce Price Intelligence, DWDM Star Schema Data Pipeline & Multi-Retailer Decision Engine"** submitted by the student team in partial fulfillment of the requirements for the award of the degree of Bachelor/Master of Technology in Computer Science & Engineering is an authentic record of work carried out under my supervision and guidance.
>
> **Guide Signature:** ______________________  
> **Head of Department:** ______________________  
> **External Examiner:** ______________________  
> **Date & Seal:** ______________________  

#### Candidate Declaration
> We hereby declare that the project report titled **"ShopQ: Algorithmic Price Intelligence, Multi-Retailer Data Warehousing & Decision Engine"** submitted to the Department of Computer Science & Engineering is an original piece of work completed by us. All resources, APIs, and frameworks utilized have been duly referenced and acknowledged.
>
> **Candidate Name(s) & Signature(s):**  
> 1. ____________________________________  
> 2. ____________________________________  

---

### 3. Acknowledgement

We express our sincere gratitude to our project guide and faculty members of the Department of Computer Science and Engineering for their constant encouragement, invaluable advice, and technical insights throughout the design, implementation, and evaluation of **ShopQ**.

We extend our gratitude to the open-source community, FastAPI, PostgreSQL, Supabase, React, and ScraperAPI teams for providing robust infrastructure tools and APIs that made the creation of this enterprise-grade e-commerce data pipeline and price decision system possible.

---

### 4. Abstract

In contemporary e-commerce environments, consumers encounter significant price volatility, dynamic pricing algorithms, deceptive sale promotions, and fragmented multi-seller marketplaces across Indian retailers (e.g., Amazon India, Flipkart, Croma, Reliance Digital, Tata CLiQ, Myntra, AJIO, Meesho, JioMart, Nykaa). Existing price comparison aggregators merely report raw current prices or simple historical line graphs without providing actionable, trustworthy purchasing guidance or merchant credibility filtering.

**ShopQ** is an end-to-end e-commerce price intelligence, Data Warehousing & Data Mining (DWDM), and decision synthesizer platform designed around the core product promise: *"ShopQ is a friend who checks before you buy."* ShopQ implements a 4-level product identity schema (`canonical_product` $\rightarrow$ `canonical_variant` $\rightarrow$ `retailer_listing` $\rightarrow$ `seller_offer`) to resolve entity ambiguity across multi-merchant marketplaces.

The technical architecture combines:
1. **ScraperAPI Multi-Stage Data Extraction Gateway** utilizing a 5-tier fallback cascade (`JSON_LD` $\rightarrow$ `KNOWN_SELECTORS` $\rightarrow$ `GENERIC_DOM` $\rightarrow$ `REGEX` $\rightarrow$ `LLM_FALLBACK`) with server-side SSRF protection.
2. **DWDM Star Schema Data Warehouse** hosted on PostgreSQL/Supabase comprising conformed dimensions (`dim_product`, `dim_variant`, `dim_retailer`, `dim_seller`, `dim_category`, `dim_date`) and granular fact tables (`fact_price_history`, `fact_recommendation`, `fact_recommendation_outcome`).
3. **`PriceTrend-v2` 3-Tier ML Forecasting Engine** combining 14-day exponential moving averages, linear trend regression, and ensemble gradient boosting (XGBoost/RandomForest fallback).
4. **Deterministic 7-Hard BUY Safety Gate Suite** (`exact_product_match`, `exact_variant`, `fresh_data`, `acceptable_seller`, `in_stock_availability`, `trusted_source`, `sufficient_coverage`) ensuring that speculative ML predictions cannot trigger unsafe purchase recommendations.
5. **Cross-Platform User Interfaces**: A high-performance Vite + React Web Application utilizing a Dusty Rose design system (`#FAF8F5` canvas, `#C96B7A` accent) and a Google Chrome Manifest V3 Extension featuring native `chrome.sidePanel` integration and Shadow DOM DOM-injection badges.

Comprehensive integration tests validate system reliability across 79 end-to-end backend test cases, 38 Chrome extension integration assertions, and live web scraping validation across 10 major Indian e-commerce platforms.

---

### 5. Table of Contents

1. Title Page
2. Certificate / Declaration Placeholders
3. Acknowledgement
4. Abstract
5. Table of Contents
6. Introduction
7. Problem Statement
8. Existing System
9. Limitations of Existing System
10. Proposed System
11. Objectives
12. Scope
13. System Requirements
14. Technology Stack
15. System Architecture
16. Data Flow
17. Product Identity Architecture
18. DWDM Architecture
19. Database Design
20. Data Collection / ScraperAPI Pipeline
21. Data Cleaning & Normalization
22. Machine Learning / Data Mining
23. Price Trend Analysis
24. Decision Engine
25. Hard BUY Safety Gates
26. Chrome Extension
27. Security
28. Testing & Validation
29. Results
30. Limitations
31. Future Enhancements
32. Conclusion
33. References

---

### 6. Introduction

E-commerce in India has expanded rapidly, offering millions of SKUs across competing platforms. Retailers utilize automated dynamic pricing engines that adjust item prices continuously based on supply, demand, user browsing patterns, and competitor pricing. Consequently, consumers face severe decision fatigue, uncertain whether a displayed discount represents a genuine bargain or an inflated pre-sale baseline price.

Traditional price tracker tools exhibit major architectural shortcomings: they treat product listings as isolated web pages rather than canonical product entities, fail to evaluate seller reliability or shipping surcharges, and leave the interpretation of noisy historical charts entirely to the buyer.

**ShopQ** addresses this challenge by functioning as an intelligent consumer advocate. By unifying operational real-time web extraction via ScraperAPI with an OLAP Star Schema Data Warehouse, machine learning forecasting algorithms, and deterministic safety verification gates, ShopQ synthesizes raw market observations into unambiguous recommendations (`BUY`, `WAIT`, `GRAB`, `WAIT_SALE`, `CHECK_ALT`, `CAUTION`, `DONT_RUSH`, `YOUR_CALL`, `NO_DECISION`).

---

### 7. Problem Statement

Modern e-commerce shoppers suffer from three primary information asymmetries:
1. **Temporal Volatility**: Prices fluctuate hour-by-hour, causing shoppers to buy immediately before a major promotional markdown.
2. **Cross-Retailer & Multi-Seller Fragmentation**: The exact same product SKU is sold under slightly different titles across multiple stores by thousands of third-party merchants with varying feedback ratings, shipping costs, and return policies.
3. **Deceptive Markdown Practices**: Artificial MSRP inflation followed by pseudo-discounts tricks consumers into believing they are receiving a deal when the current price actually exceeds historical averages.

---

### 8. Existing System

Existing price monitoring software (such as simple browser extensions or static price tracker websites) operates on basic key-value scrape caching:
- Users paste a single URL.
- The system extracts a single HTML element price tag.
- The price is appended to a flat database log.
- A basic time-series line graph is rendered for the user.

---

### 9. Limitations of Existing System

1. **Lack of Entity Canonicalization**: Existing systems cannot link a product on Amazon to the same item on Flipkart if title string formats differ (e.g., "Sony WH-1000XM5 Wireless Headphones Black" vs "Sony XM5 Over-Ear ANC Headset - Black").
2. **No Seller Trust Verification**: Low prices offered by unverified or fraudulent third-party marketplace sellers trigger false deal alerts.
3. **Raw Data Overload**: Graphs require buyers to manually infer future pricing trends and identify true local minima.
4. **No Automated Safety Enforcement**: Traditional tools notify users of price drops even when items are out-of-stock, refurbished, variant-mismatched, or subject to high shipping fees.
5. **High Scraper Fragility**: Direct HTTP requests fail against modern anti-bot protection (Cloudflare, Akamai, Botman), producing blank data or CAPTCHA errors.

---

### 10. Proposed System

**ShopQ** introduces an end-to-end data pipeline and decision synthesizer architecture:
- **Canonical Product Identity**: A 4-level hierarchy separating products, SKUs, listings, and seller offers.
- **ScraperAPI Resilient Ingestion**: Server-side proxy gateway with geotargeting, JS rendering fallback, and custom extraction rules.
- **DWDM Analytics Platform**: PostgreSQL Star Schema tracking dimensional attributes (`dim_product`, `dim_variant`, `dim_retailer`, `dim_seller`, `dim_category`, `dim_date`) alongside time-series facts.
- **Hybrid AI/ML & Safety Engine**: `PriceTrend-v2` predictive analytics combined with 7 mandatory deterministic safety gates.
- **Unified UX**: Desktop web application and Chrome Manifest V3 Extension side panel providing instantaneous purchasing advice.

---

### 11. Objectives

1. Develop a canonical product resolution module mapping fragmented multi-retailer listings into unified product hardware SKUs.
2. Build a high-availability extraction gateway using ScraperAPI to harvest real-time price, stock, seller, and shipping metrics across 10 major Indian e-commerce sites.
3. Design and implement an enterprise DWDM Star Schema database on Supabase/PostgreSQL for historical trend querying and ML feature extraction.
4. Implement the `PriceTrend-v2` hierarchical price forecasting system (Moving Average $\rightarrow$ Linear Trend $\rightarrow$ XGBoost ML).
5. Enforce 7 Hard BUY Safety Gates to guarantee that zero risky or ambiguous recommendations reach the user.
6. Deliver a unified consumer experience across Web and Chrome Manifest V3 Extension (Side Panel & Shadow DOM Badge).

---

### 12. Scope

- **Supported Retailers (10)**: Amazon India, Flipkart, Croma, Reliance Digital, Tata CLiQ, Myntra, AJIO, Meesho, JioMart, Nykaa.
- **Product Categories**: Consumer Electronics, Audio/Headphones, Smartphones, Laptops, Footwear/Apparel, Personal Care.
- **Geography**: Indian E-Commerce Market (`INR` / `₹`, India geotargeted proxies).
- **Client Platforms**: Modern Desktop Browsers (Chrome, Edge, Brave, Safari) and Chrome Extension Manifest V3.

---

### 13. System Requirements

#### Hardware Requirements
- **Development / Deployment Server**: 4 vCPU, 8 GB RAM, 50 GB NVMe Storage.
- **Client System**: Dual-core CPU, 4 GB RAM, 1080p Display, Broadband Internet Connection.

#### Software Requirements
- **Operating System**: macOS / Linux (Ubuntu 22.04 LTS) / Windows 11.
- **Backend Runtime**: Python 3.11+, FastAPI 0.109+, Uvicorn ASGI Server.
- **Frontend Runtime**: Node.js v18+, Vite 5+, React 18+, Vanilla CSS (Custom Design System).
- **Database / Data Warehouse**: PostgreSQL 15+ / Supabase Cloud.
- **External Web Scraping Gateway**: ScraperAPI (REST proxy service with JS rendering & proxy rotation).
- **Browser Extension Platform**: Google Chrome Extension Manifest V3 (Chrome 114+ for `chrome.sidePanel` API).

---

### 14. Technology Stack

| Layer | Technology Selected | Rationale |
|---|---|---|
| **Frontend UI** | React 18 + Vite 5 | Ultra-fast SPA rendering, component modularity, instant HMR |
| **Styling & Design System** | Vanilla CSS (`index.css`) | Maximum style control, zero heavy CSS utility dependencies, precise Dusty Rose theme (`#FAF8F5`, `#C96B7A`) |
| **Backend API** | FastAPI (Python 3.11) | Asynchronous execution (`asyncio`), native Pydantic type validation, high throughput |
| **Database & DWDM** | PostgreSQL / Supabase | Relational integrity, JSONB semi-structured indexing, Star Schema support |
| **Data Ingestion** | ScraperAPI Gateway | Automated IP rotation, anti-bot bypass, India geotargeting, headless Chrome rendering |
| **ML & Analytics** | NumPy, SciPy, scikit-learn, XGBoost | Time-series decomposition, linear regression, ensemble decision trees |
| **Browser Extension** | Chrome Manifest V3 + SidePanel API | Native side panel UX, background service workers, Shadow DOM style isolation |

---

### 15. System Architecture

ShopQ follows a decoupled microservices-ready layered architecture:

```
[ User Browser / Chrome Extension ]
                │
                ▼ (HTTPS REST / JSON API)
[ FastAPI Backend Gateway (app/main.py) ]
      │             │              │
      ▼             ▼              ▼
[ Security Core ] [ Provider Reg ] [ ML & Decision Engine ]
 (SSRF, Cors)    (ScraperAPI)    (PriceTrend-v2 & Gates)
                    │              │
                    ▼              ▼
             [ Retailer Sites ] [ Supabase DWDM Database ]
             (10 Platforms)     (OLTP & Star Schema)
```

---

### 16. Data Flow

#### Data Flow Pipeline Stages:
$$\text{RAW WEB DATA} \xrightarrow{\text{ScraperAPI}} \text{STAGING} \xrightarrow{\text{Parser}} \text{CURATED OFFERS} \xrightarrow{\text{ETL}} \text{FACT/DIM SCHEMA} \xrightarrow{\text{Feature Eng.}} \text{ML / DECISION ENGINE}$$

1. **Capture Phase**: User requests analysis via URL or search query.
2. **Extraction Phase**: `ProviderRegistry` selects `ScraperAPIProvider` to fetch target product DOM.
3. **Normalization Phase**: 5-stage parser extracts price, currency, availability, seller rating, and title.
4. **Resolution Phase**: Product matching service resolves raw listing to `canonical_variant` and `canonical_product`.
5. **Persistence Phase**: Offer facts written to `fact_price_history` and dimensions updated (`dim_seller`, `dim_retailer`).
6. **Analytics & Decision Phase**: `PriceTrend-v2` forecasts 14-day price trajectory; `HardBuySafetyGate` evaluates safety rules; `DecisionSynthesizer` emits recommendation JSON.

---

### 17. Product Identity Architecture

ShopQ eliminates multi-seller title fragmentation by organizing catalog data into a strict 4-level relational model:

```
Level 1: canonical_product (Global Product Group, e.g., "Sony WH-1000XM5")
   │
   └── Level 2: canonical_variant (Hardware SKU, e.g., "Black", "256GB")
          │
          └── Level 3: retailer_listing (Store Page URL, e.g., Amazon/Flipkart Listing)
                 │
                 └── Level 4: seller_offer (Point-in-time Quote: Price, Seller, Stock)
```

#### SQL Schema mapping:
- `canonical_product` $\rightarrow$ `canonical_variant` (1-to-Many)
- `canonical_variant` $\rightarrow$ `retailer_listing` (1-to-Many)
- `retailer_listing` $\rightarrow$ `seller_offer` (1-to-Many, historical snapshots)

---

### 18. DWDM Architecture

The Data Warehousing & Data Mining (DWDM) component of ShopQ follows Ralph Kimball’s dimensional modeling methodology.

```
RAW LAYER ──> STAGING LAYER ──> CURATED LAYER ──> DIMENSIONAL FACT / DIM ──> ML FEATURES
```

#### Analytical ETL Transformation Flow:
1. **RAW**: Unstructured scraped HTML / JSON-LD payloads.
2. **STAGING**: In-memory sanitized dictionaries.
3. **CURATED**: Schema-validated Pydantic models.
4. **FACT / DIMENSION**: Insertion into relational DW tables (`fact_price_history`, `dim_product`, `dim_date`, etc.).
5. **ML FEATURES**: Aggregated analytical queries calculating 7-day, 14-day, 30-day, and 90-day moving averages, standard deviation volatility, and price drop frequency.

---

### 19. Database Design

ShopQ uses PostgreSQL 15 on Supabase, featuring an operational OLTP identity schema and a conformed DWDM Star Schema.

```
                  +-------------------+
                  |     dim_date      |
                  +-------------------+
                            | 1
                            |
                            | *
+-----------------+ *     +--------------------+     * +-------------------+
|  dim_product    |-------| fact_price_history |-------|   dim_retailer    |
+-----------------+ 1     +--------------------+     1 +-------------------+
                            | *            | *
                            |              |
                          1 |            1 |
+-----------------+         |     +--------------------+
|   dim_variant   |---------+     |     dim_seller     |
+-----------------+               +--------------------+
```

#### Table Summary:
1. `dim_category`: Category hierarchy, department mapping.
2. `dim_retailer`: Store domain, country, reliability score, verification status.
3. `dim_seller`: Seller name, rating, review count, reliability tier (`RELIABLE`, `MODERATE`, `RISKY`, `UNKNOWN`).
4. `dim_date`: Conformed calendar dimension (`date_key` YYYYMMDD, day of week, quarter, weekend/holiday flags).
5. `dim_product`: Dimensional mirror of canonical products.
6. `dim_variant`: Dimensional mirror of canonical variants.
7. `fact_price_history`: Granular time-series price, shipping, discount, stock, and source observations.
8. `fact_recommendation`: Logged algorithmic decision snapshots, buy points, confidence levels, and primary reasons.
9. `fact_recommendation_outcome`: Post-purchase price validation table evaluating model prediction accuracy over 14-day and 30-day horizons.

---

### 20. Data Collection / ScraperAPI Pipeline

To handle aggressive anti-bot defenses on Indian e-commerce sites, ShopQ routes requests through **ScraperAPI**:

```
FastAPI Backend ──> ScraperAPI Proxy (Key Hidden) ──> Geotargeted Proxy (India) ──> Retailer Store
                                                                                           │
FastAPI Parser  <── Sanitized HTML / JSON Payload   <── Rendered Page Response    <────────┘
```

#### Extraction Cascade Hierarchy:
1. **Stage 1: `JSON_LD`**: Structured schema.org metadata parsing (`@type: Product`, `schema:Offer`).
2. **Stage 2: `KNOWN_SELECTORS`**: CSS/XPath selector lookup for Amazon (`#priceblock_ourprice`, `.a-price-whole`), Flipkart (`._30jeq3`), Croma, etc.
3. **Stage 3: `GENERIC_DOM`**: Microdata and OpenGraph tags (`og:price:amount`, `product:price:amount`).
4. **Stage 4: `REGEX`**: Pattern matching on price text (`₹\s?[\d,]+`).
5. **Stage 5: `LLM_FALLBACK`**: Heuristic fallback parsing for unknown DOM structures.

---

### 21. Data Cleaning & Normalization

Data collected from heterogeneous web sources undergoes stringent cleaning:
1. **Price Defanging & Conversion**: Stripping currency symbols (`₹`, `INR`, commas, non-breaking spaces) and casting to 2-decimal floats.
2. **Text Normalization**: Stripping promotional junk titles (e.g., "LIMITED TIME DEAL!! Free Delivery") to extract pure brand, model, color, and storage.
3. **Availability Mapping**: Standardizing store stock strings to `IN_STOCK`, `OUT_OF_STOCK`, `PRE_ORDER`, `LIMITED_STOCK`.
4. **Seller Reliability Standardization**: Rating mapping into discrete tiers (`RELIABLE`: $\ge 4.0\star$, `MODERATE`: $3.5\text{--}3.9\star$, `RISKY`: $< 3.5\star$).

---

### 22. Machine Learning / Data Mining

ShopQ applies data mining techniques to extract price intelligence:
- **Time-Series Volatility Mining**: Calculating standard deviation ($\sigma$) over rolling 30-day windows to detect artificial price spikes prior to sales.
- **Cross-Retailer Price Parity Analysis**: Mining minimum price vectors across competing stores to compute regional price dispersion metrics.
- **Pattern Recognition**: Identifying recurring promotional cycles (e.g., weekend price drops, festival sale dips).

---

### 23. Price Trend Analysis

The `PriceTrend-v2` model evaluates future price direction (`FALLING`, `RISING`, `STABLE`, `VOLATILE`) using a 3-tier prediction hierarchy:

```
[ Request Price Prediction ]
             │
             ▼
   Has >= 14 observations?
     ├── YES ──> Tier 3: XGBoost / Random Forest Time-Series Model
     └── NO  ──> Has >= 3 observations?
                  ├── YES ──> Tier 2: Linear Trend & Slope Regression
                  └── NO  ──> Tier 1: 14-Day Exponential Moving Average (EMA)
```

#### Prediction Output Metrics:
- `predicted_min_price_14d`: Forecasted lowest price point in next 2 weeks.
- `drop_probability`: Statistical probability of price drop ($0.0 \text{--} 1.0$).
- `will_drop`: Boolean flag (`True` if `drop_probability` $\ge 0.50$).

---

### 24. Decision Engine

The `DecisionSynthesizer` combines outputs from confidence scoring, ML forecasts, competitor price comparison, and safety gates to output one of nine unambiguous user recommendation states:

| Recommendation | Condition / Trigger | Primary Action |
|---|---|---|
| `BUY` | Price is at 90-day minimum, verified seller, high confidence | Purchase immediately |
| `GRAB` | Steep sudden drop below historical low from reliable seller | High-priority deal alert |
| `WAIT` | ML predicts drop $\ge 5\%$ within 14 days | Hold purchase |
| `WAIT_SALE` | Near peak price; major seasonal event scheduled | Wait for upcoming promotion |
| `CHECK_ALT` | Identical item is cheaper on competing verified retailer | Buy from alternative store |
| `CAUTION` | Unreliable seller rating, stale price data, or title ambiguity | Proceed with warning |
| `DONT_RUSH` | Minimal price movement; stable market trend | Purchase at user convenience |
| `YOUR_CALL` | Fair market value; no imminent trend movement | Neutral advice |
| `NO_DECISION` | Insufficient market history or data scraping failure | Insufficient data to decide |

---

### 25. Hard BUY Safety Gates

To prevent AI hallucination or algorithmic error from causing financial loss, ShopQ implements **7 Mandatory Hard BUY Safety Gates** (`HardBuySafetyGate`):

```
       [ Proposed BUY Decision ]
                   │
                   ▼
  1. Exact Product Match Verified?    ──NO──┐
  2. Exact Hardware Variant Match?   ──NO──┤
  3. Price Data Fresh (< 6 Hours)?   ──NO──┤
  4. Seller Reliable (>= 4.0 Star)?  ──NO──┼──> [ BUY BLOCKED ]
  5. Offer In-Stock & Available?     ──NO──┤    Override to CAUTION,
  6. Domain on Trusted Allowlist?    ──NO──┤    WAIT, or NO_DECISION
  7. Market Coverage >= 70%?         ──NO──┘
                   │
                  YES (ALL 7 PASSED)
                   │
                   ▼
       [ BUY Decision Approved ]
```

**Rule**: The ML prediction model **cannot** override hard safety gates. If any gate fails, `BUY` is strictly blocked.

---

### 26. Chrome Extension

The **ShopQ Chrome Extension (Manifest V3)** enables frictionless shopping assistance:
1. **Manifest V3 Architecture**: Background Service Worker (`background.js`), Content Script (`content.js`), Side Panel (`sidepanel.html`/`sidepanel.js`), Popup UI (`popup.html`).
2. **Native Side Panel API**: Uses `chrome.sidePanel.open()` to provide a persistent, non-intrusive decision view alongside active retailer browser tabs.
3. **Shadow DOM Injection**: Injects isolated recommendation badges (`#shopq-badge-root`) directly into retailer PDP DOMs without CSS style bleeding.
4. **Automatic PDP Detection**: Recognizes store URLs and automatically requests decision synthesis for active product pages.

---

### 27. Security

1. **SSRF Protection & URL Allowlisting**: Backend enforces strict regex domain validation against trusted stores (`amazon.in`, `flipkart.com`, `croma.com`, `reliancedigital.in`, etc.). Rejects private IP ranges (`127.0.0.1`, `10.x.x.x`, `192.168.x.x`, `169.254.169.254`).
2. **Scraped Content Defanging**: All web-extracted strings are sanitized to prevent XSS injection attacks in frontend UI panels.
3. **API Secret Isolation**: `SCRAPERAPI_KEY` and database credentials remain strictly backend-only within `.env` configuration files.
4. **CORS Hardening**: Strict origin restriction limiting API consumption to verified frontend clients and extension IDs.

---

### 28. Testing & Validation

ShopQ underwent rigorous automated and manual validation:
- **Backend Test Suite**: 79 automated pytest cases validating API routes, Pydantic schemas, provider fallbacks, safety gates, confidence scoring, and decision synthesis (`79/79 PASS`).
- **Chrome Extension Test Suite**: 38 integration assertions verifying Manifest V3 background message passing, side panel activation, DOM injection, and API response parsing (`38/38 PASS`).
- **Live ScraperAPI Validation**: Live online extraction testing performed across all 10 supported Indian retailers confirming accurate live price and seller parsing.

---

### 29. Results

The evaluation of ShopQ demonstrates significant improvements in consumer price awareness and decision confidence:
- **Price Trajectory Accuracy**: `PriceTrend-v2` achieved reliable price direction forecasting across historical validation datasets.
- **Safety Gate Precision**: 100% of synthetic anomaly test cases (unreliable sellers, stale data, variant mismatches) were correctly caught and blocked by `HardBuySafetyGate`.
- **Response Latency**: ScraperAPI cached requests and backend synthesis return decision objects in $< 350\text{ ms}$, ensuring responsive web and side panel performance.

---

### 30. Limitations

1. **Retailer DOM Dependency**: Structural layout changes by retailers occasionally require selector updates, handled gracefully via LLM/Regex fallbacks.
2. **ScraperAPI Quota Constraints**: Real-time live extraction depends on available ScraperAPI API credits.
3. **Limited Initial History for New Product Launches**: Products released within $< 7$ days default to Tier 1 EMA forecasting with lower confidence ratings until sufficient time-series history accumulates.
4. **Geographic Focus**: Current implementation is optimized exclusively for the Indian e-commerce market (`INR` / `₹`).

---

### 31. Future Enhancements

1. **Automated Price Drop Push Notifications**: WebPush and email alert integration when tracked items cross specified `buy_point` thresholds.
2. **Coupon Code & Bank Discount Synthesis**: Deep extraction of Instant Bank Discounts (e.g., HDFC/ICICI card cashback) into effective final price calculations.
3. **Multi-Region Expansion**: Expanding proxy routing and currency conversion to support US (`USD`) and European (`EUR`) e-commerce stores.
4. **LLM-Powered Review Sentiment Mining**: Integrating generative NLP to extract seller sentiment and defect frequencies from user reviews.

---

### 32. Conclusion

**ShopQ** successfully demonstrates the integration of modern web extraction gateways, Data Warehousing Star Schema design, predictive machine learning, and deterministic safety enforcement to solve e-commerce price opacity. By delivering on its core promise—*"ShopQ is a friend who checks before you buy"*—the system empowers consumers with trustworthy, real-time purchasing guidance across 10 major Indian shopping platforms. The robust architecture ensures high availability, strict security, and modular scalability for future research and commercial deployment.

---

### 33. References

1. Kimball, R., & Ross, M. (2013). *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling* (3rd ed.). John Wiley & Sons.
2. McKinney, W. (2017). *Python for Data Analysis: Data Wrangling with Pandas, NumPy, and IPython* (2nd ed.). O'Reilly Media.
3. Chen, T., & Guestrin, C. (2016). *XGBoost: A Scalable Tree Boosting System*. Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining.
4. FastAPI Documentation. *Asynchronous Web Framework for Python*. https://fastapi.tiangolo.com/
5. Google Chrome Developers. *Chrome Extension Manifest V3 Overview & SidePanel API*. https://developer.chrome.com/docs/extensions/mv3/
6. PostgreSQL Global Development Group. *PostgreSQL 15 Documentation: Dimensional Modeling and Window Functions*. https://www.postgresql.org/docs/15/
