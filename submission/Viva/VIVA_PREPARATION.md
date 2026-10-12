# ShopQ Comprehensive Viva Voce Preparation Guide
## 50 Technical Viva Questions & Detailed Answers

---

### Category 1: Motivation & Project Identity

#### Q1: What is the core problem ShopQ solves?
**Answer**: ShopQ solves e-commerce price opacity, dynamic price volatility, deceptive sales markdown practices, and multi-seller ambiguity across Indian shopping portals. It transforms confusing line graphs into instant, actionable purchasing decisions (`BUY`, `WAIT`, `GRAB`, etc.).

#### Q2: What is the official product promise/identity of ShopQ?
**Answer**: *"ShopQ is a friend who checks before you buy."* It acts as an unbiased consumer advocate checking price trends, seller credibility, and alternative store prices before the user purchases.

#### Q3: Why is ShopQ different from traditional price trackers like CamelCamelCamel or PriceBefore?
**Answer**: Traditional trackers only scrape single store URLs and display flat historical line graphs. ShopQ canonicalizes products across competing stores, evaluates merchant reliability, runs predictive time-series ML models, and enforces 7 mandatory deterministic safety gates to prevent bad advice.

---

### Category 2: Architecture & Framework Choices

#### Q4: Why did you choose FastAPI for the backend instead of Flask or Django?
**Answer**: FastAPI provides asynchronous I/O execution (`asyncio`), high performance comparable to Node.js/Go, automatic OpenAPI documentation, and native Pydantic data validation. Asynchronous execution is essential for handling parallel web scraping and fast analytical database queries.

#### Q5: Why Vite + React 18 for the frontend web application?
**Answer**: Vite provides instant hot module replacement (HMR) and fast production bundling. React 18's component model and state management enable a smooth single-page application (SPA) experience for real-time price analysis, progress indicators, and interactive charts.

#### Q6: Why did you use Vanilla CSS instead of Tailwind CSS or Bootstrap?
**Answer**: Vanilla CSS (`index.css`) gives us 100% granular control over our custom design system tokens (`--bg: #FAF8F5`, `--accent: #C96B7A` Dusty Rose), precise 1px borders, and custom micro-animations without adding heavy third-party framework bundle bloat.

#### Q7: Why did you choose PostgreSQL / Supabase as the database?
**Answer**: PostgreSQL provides robust ACID compliance for operational OLTP entities, JSONB columns for flexible SKU attributes, and native support for Kimball Data Warehousing Star Schema analytical queries. Supabase offers managed cloud hosting with instant REST APIs.

---

### Category 3: Product Identity & Data Modeling

#### Q8: Why separation into a 4-Level Product Identity Hierarchy?
**Answer**: In e-commerce, different retailers list identical products with different titles (e.g., "Sony XM5 Black" vs "Sony WH-1000XM5 Wireless Headphones"). A single table causes duplicate entries. The 4-level model (`canonical_product` $\rightarrow$ `canonical_variant` $\rightarrow$ `retailer_listing` $\rightarrow$ `seller_offer`) decouples global product concepts from specific hardware SKUs, store URLs, and merchant price quotes.

#### Q9: What is the difference between `canonical_product` and `canonical_variant`?
**Answer**: `canonical_product` represents the overall product group (e.g., "iPhone 15 Pro"), while `canonical_variant` represents the specific hardware SKU with distinct attributes like color, storage, or size (e.g., "iPhone 15 Pro - 128GB - Natural Titanium").

#### Q10: What is the difference between `retailer_listing` and `seller_offer`?
**Answer**: A `retailer_listing` is the permanent store webpage URL on Amazon or Flipkart. A `seller_offer` is a point-in-time price quote from a specific third-party merchant selling on that listing, including price, stock, shipping cost, and rating.

---

### Category 4: Data Warehousing & Data Mining (DWDM)

#### Q11: Explain the DWDM architecture in ShopQ.
**Answer**: ShopQ follows Kimball's dimensional modeling:
$$\text{RAW WEB DOM} \rightarrow \text{STAGING} \rightarrow \text{CURATED OFFERS} \rightarrow \text{STAR SCHEMA (FACT/DIM)} \rightarrow \text{ML FEATURES}$$
It separates operational OLTP catalog tables from analytical OLAP star schema dimensions (`dim_product`, `dim_variant`, `dim_retailer`, `dim_seller`, `dim_category`, `dim_date`) and fact tables (`fact_price_history`, `fact_recommendation`).

#### Q12: What is the purpose of the `dim_date` dimension table?
**Answer**: `dim_date` is a conformed dimension storing calendar metadata (`date_key` YYYYMMDD, day of week, month, quarter, weekend/holiday flags). It allows analytical queries to identify pricing trends during weekends, holidays, and promotional sale events without computing expensive date functions at query time.

#### Q13: How does historical price observation support analytical queries and ML?
**Answer**: Observations stored in `fact_price_history` allow analytical queries to calculate 7-day, 14-day, 30-day, and 90-day moving averages, minimum historical baselines, standard deviation volatility, and price drop frequency metrics required by our ML models.

#### Q14: What is the role of Data Mining in ShopQ?
**Answer**: Data mining techniques are used to extract pattern rules from time-series price logs—such as identifying artificial pre-sale price markups, calculating cross-retailer price dispersion, and clustering merchant rating distributions.

---

### Category 5: Data Ingestion & ScraperAPI

#### Q15: Why use ScraperAPI instead of direct Python `requests` or BeautifulSoup?
**Answer**: Major Indian e-commerce sites (Amazon, Flipkart) deploy aggressive anti-bot defenses (Cloudflare, Akamai, Botman) that block direct HTTP requests. ScraperAPI handles automated IP proxy rotation, India geotargeting, CAPTCHA solving, and headless Chrome JavaScript rendering.

#### Q16: How does ShopQ handle the 5-Stage Data Extraction Cascade?
**Answer**: The parser attempts extraction in priority order:
1. `JSON_LD` (Schema.org metadata)
2. `KNOWN_SELECTORS` (Store-specific CSS/XPath)
3. `GENERIC_DOM` (OpenGraph/microdata)
4. `REGEX` (Price pattern text extraction)
5. `LLM_FALLBACK` (Heuristic DOM parsing fallback)

#### Q17: What happens when a web page DOM layout changes?
**Answer**: If store-specific selectors in Stage 2 fail, the parser gracefully falls back to Stage 3 (Generic DOM), Stage 4 (Regex pattern matching), or Stage 5. If all extraction stages fail, the system sets an `all_sources_failed` status and returns a safe `NO_DECISION` recommendation.

#### Q18: How does ShopQ handle ScraperAPI rate limits or credit exhaustion?
**Answer**: The provider registry catches HTTP 429 / quota error responses and gracefully falls back to cached database observations (`fact_price_history`) or `MockProvider` test fixtures, logging a `PARTIAL` provider state without crashing.

---

### Category 6: AI / ML & Price Trend Modeling

#### Q19: Explain the `PriceTrend-v2` prediction model hierarchy.
**Answer**: `PriceTrend-v2` uses a 3-tier fallback hierarchy based on data availability:
- **Tier 3 ($\ge 14$ observations)**: XGBoost / Random Forest time-series forecasting.
- **Tier 2 ($\ge 3$ observations)**: Linear regression trend & slope forecasting.
- **Tier 1 ($< 3$ observations)**: 14-day Exponential Moving Average (EMA).

#### Q20: What outputs are generated by the ML forecasting engine?
**Answer**: The ML model outputs:
1. `predicted_min_price_14d` (Forecasted lowest price point in next 2 weeks).
2. `drop_probability` (Statistical drop probability between $0.0$ and $1.0$).
3. `will_drop` (Boolean flag, `True` if probability $\ge 0.50$).

#### Q21: Why use a temporal train/test split instead of a random train/test split for price modeling?
**Answer**: Price observations are time-series data. A random split causes data leakage by using future prices to predict past prices. A temporal split trains strictly on past timestamps ($t_0$ to $t_{n}$) and evaluates accuracy on future timestamps ($t_{n+1}$ to $t_{n+k}$), mimicking real-world deployment.

#### Q22: How does ShopQ handle price predictions when data is sparse or brand new?
**Answer**: For newly launched products with $< 3$ observations, the engine falls back to Tier 1 EMA modeling, assigns a `LOW` or `MEDIUM` confidence score, and restricts the decision engine from issuing high-risk `BUY` calls.

#### Q23: Do you claim a specific ML model accuracy percentage?
**Answer**: No fabricated accuracy claims are made. Model accuracy is evaluated empirically on historical validation datasets using Root Mean Squared Error (RMSE) and Directional Accuracy metrics. In live deployment, prediction outputs are treated as evidence bounded by safety rules.

---

### Category 7: Decision Engine & Hard BUY Safety Gates

#### Q24: What is the fundamental relationship between the ML prediction and the Decision Engine?
**Answer**: *"Prediction is evidence. The Decision Engine makes the final recommendation."* The ML model forecasts price trends, but the Decision Engine evaluates safety gates, competitor prices, and merchant reliability before issuing a decision.

#### Q25: What are the 7 Hard BUY Safety Gates?
**Answer**:
1. `exact_product_match`: Title matches canonical product.
2. `exact_variant`: Hardware SKU verified.
3. `fresh_data`: Price data updated within last 6 hours.
4. `acceptable_seller`: Seller rating $\ge 4.0\star$, reliability `RELIABLE` or `MODERATE`.
5. `in_stock_availability`: Item currently in stock.
6. `trusted_source`: Store domain on authorized allowlist.
7. `sufficient_coverage`: Data coverage $\ge 70\%$.

#### Q26: What happens if any of the 7 Hard BUY Safety Gates fail?
**Answer**: `BUY` is **strictly blocked**. The ML model cannot override hard safety gates. The decision is automatically overridden to `CAUTION`, `WAIT` (if out of stock), or `NO_DECISION` (if untrusted source or low coverage).

#### Q27: How does ShopQ decide between `BUY`, `GRAB`, `WAIT`, `WAIT_SALE`, `CHECK_ALT`, `CAUTION`, `DONT_RUSH`, `YOUR_CALL`, and `NO_DECISION`?
**Answer**:
- `BUY`: Lowest price in 90 days, verified seller, all 7 gates pass.
- `GRAB`: Sudden steep discount below historical low.
- `WAIT`: ML drop probability $\ge 60\%$.
- `WAIT_SALE`: Item near peak price with an upcoming promotional event.
- `CHECK_ALT`: Identical item is $\ge 5\%$ cheaper on another verified retailer.
- `CAUTION`: Failed seller rating or stale data.
- `DONT_RUSH`: Mild downward drift; purchase at convenience.
- `YOUR_CALL`: Stable market price; fair value.
- `NO_DECISION`: Scraper failure or insufficient history.

#### Q28: How is seller reliability evaluated?
**Answer**: Seller reliability is graded by rating ($\ge 4.0\star$), review volume, authorization status, and return policy. Sellers rated $< 4.0\star$ or flagged as `RISKY` trigger Safety Gate 4 failure.

---

### Category 8: Security, Privacy & Extension Architecture

#### Q29: How does ShopQ prevent Server-Side Request Forgery (SSRF)?
**Answer**: The backend security module validates every incoming URL against a strict regex domain allowlist (`amazon.in`, `flipkart.com`, etc.) and explicitly blocks private IP address ranges (`127.0.0.1`, `10.x.x.x`, `192.168.x.x`, `169.254.169.254`).

#### Q30: How does ShopQ sanitize scraped content against Cross-Site Scripting (XSS)?
**Answer**: All scraped HTML titles and seller strings are passed through defanging routines that escape HTML entities (`<script>`, `javascript:`, `onload=`) before storing them or returning them in API JSON payloads.

#### Q31: Why Chrome Extension Manifest V3 instead of Manifest V2?
**Answer**: Manifest V3 is Google's mandatory modern extension platform. It improves security, performance, and privacy by replacing persistent background pages with ephemeral service workers and providing native APIs like `chrome.sidePanel`.

#### Q32: What is the advantage of using Chrome's native `sidePanel` API?
**Answer**: `chrome.sidePanel` renders a dedicated UI panel alongside browser tabs without altering the active webpage's DOM layout or injecting heavy external iframe scripts.

#### Q33: How does the Extension inject badges into store pages without styling conflicts?
**Answer**: The content script uses **Shadow DOM** (`element.attachShadow({ mode: 'open' })`). Shadow DOM encapsulates extension CSS styles completely, preventing store page styles from breaking the badge or vice versa.

#### Q34: How is user privacy protected in the Chrome Extension?
**Answer**: The extension operates strictly on allowlisted e-commerce store URLs. It does not track user browsing history, collect personal identity data, or transmit information to third-party analytics trackers.

---

### Category 9: Operations, Failure Handling & Scaling

#### Q35: What happens when a user submits an unsupported retailer URL?
**Answer**: Security validation rejects the URL, returning HTTP 400 with `INVALID_RETAILER_DOMAIN`. The frontend renders a helpful error message listing supported stores.

#### Q36: How does ShopQ handle out-of-stock products?
**Answer**: Safety Gate 5 (`in_stock_availability`) flags the item as unavailable, blocking `BUY` recommendations and setting the recommendation state to `WAIT` with an explanation.

#### Q37: How does ShopQ scale to millions of daily price observations?
**Answer**: PostgreSQL partitioning on `fact_price_history` by `date_key` (monthly/yearly partitions), B-Tree indexes on `(variant_id, observed_at)`, and PgBouncer connection pooling ensure high-throughput query execution.

#### Q38: What is the function of the `fact_recommendation_outcome` table?
**Answer**: It logs post-purchase price realizations to continuously evaluate whether past `BUY` or `WAIT` recommendations were accurate (`ACCURATE`, `MISSED_OPPORTUNITY`, `FALSE_ALARM`), creating a feedback loop for ML retraining.

---

### Category 10: General Engineering Viva Questions

#### Q39: What was the hardest technical challenge in building ShopQ?
**Answer**: Resolving entity ambiguity across multi-retailer store titles (mapping messy retailer strings to canonical hardware SKUs) while maintaining real-time scraping latency under 1 second.

#### Q40: What happens if two retailers have slightly different price currency formatting?
**Answer**: The cleaning pipeline normalizes all currencies to standard ISO codes (`INR`) and converts localized string formatting (`₹ 23,499.00`) to standard floats (`23499.00`).

#### Q41: Can the ML model generate negative price predictions?
**Answer**: No. Price predictions are bounded by zero floor constraints (`max(predicted_price, 0)`) and realistic lower bounds based on historical minimums.

#### Q42: What is a conformed dimension in Data Warehousing?
**Answer**: A conformed dimension (e.g., `dim_date`, `dim_product`) is a shared dimension table designed identically across multiple fact tables, enabling consistent cross-subject analytical queries.

#### Q43: How does the system handle temporary retailer network timeouts?
**Answer**: The provider gateway enforces a 10-second timeout, retries up to 2 times, and falls back to recent cached facts in `fact_price_history`.

#### Q44: What is the role of `Pydantic` in FastAPI?
**Answer**: Pydantic defines strong data schemas for request and response validation, ensuring that invalid types return clear HTTP 422 errors instead of internal runtime exceptions.

#### Q45: How are background alerts processed for watched items?
**Answer**: Scheduled background jobs query `fact_recommendation` and `fact_price_history` for items where `current_price <= buy_point`, inserting alert notifications into the user's feed.

#### Q46: How does ShopQ ensure brand styling consistency?
**Answer**: Design system CSS variables (`--bg`, `--bg-card`, `--accent`, `--text`) enforce uniform Dusty Rose aesthetics (`#FAF8F5`, `#C96B7A`, `#2D2B2A`) across all views and components.

#### Q47: Why are ScraperAPI credentials stored in environment variables (`.env`)?
**Answer**: Storing secrets in environment variables prevents credential leaks in version control repositories and allows safe configuration changes between development, staging, and production environments.

#### Q48: What is the difference between `WAIT` and `WAIT_SALE`?
**Answer**: `WAIT` is triggered by algorithmic ML price drop forecasts over a 14-day horizon. `WAIT_SALE` is triggered when an item is priced near its 90-day peak and a known major sale event (e.g., Diwali Sale, Big Billion Days) is scheduled.

#### Q49: What is the difference between `BUY` and `GRAB`?
**Answer**: `BUY` indicates the current price is optimal at or near the 90-day minimum. `GRAB` indicates an extraordinary price drop below historical minimums requiring immediate action before stock depletes.

#### Q50: What is the key takeaway of the ShopQ project?
**Answer**: ShopQ demonstrates that combining resilient data acquisition, enterprise dimensional warehousing, machine learning forecasting, and deterministic safety rules produces a trustworthy consumer tool that eliminates e-commerce price opacity.
