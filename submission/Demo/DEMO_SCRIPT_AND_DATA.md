# ShopQ Live Demo Script & Test Scenarios
## 5–7 Minute Academic Presentation & Live Demonstration Guide

---

### Overview & Setup Instructions

- **Target Duration**: 5 to 7 Minutes.
- **Presenter Role**: Lead Engineer / Presenter.
- **Required Environment**:
  1. FastAPI Backend running locally at `http://localhost:8000` (or production Render URL).
  2. Vite + React Frontend running at `http://localhost:5173`.
  3. Google Chrome Browser with ShopQ Extension loaded in Developer Mode (`chrome://extensions`).
- **Core Product Motto**: *"ShopQ is a friend who checks before you buy."*

---

### Step-by-Step Demo Script & Spoken Transcript

#### Step 1: Introduction & Product Promise (0:00 - 0:45)
- **Action**: Open browser to `http://localhost:5173/`. Display the clean Dusty Rose homepage (`#FAF8F5` background, search bar hero).
- **Presenter Spoken Script**:
  > *"Good morning, esteemed panel and faculty members. Today we present **ShopQ**—an algorithmic e-commerce price intelligence, data warehousing, and purchasing decision platform built around a simple promise: **'ShopQ is a friend who checks before you buy.'**"*
  >
  > *"When shopping online across Amazon, Flipkart, or Croma, buyers are flooded with artificial discounts, fluctuating prices, and unverified sellers. ShopQ replaces guesswork with instant, trustworthy, data-driven buying decisions."*

---

#### Step 2: Product Search & Link Analysis (0:45 - 1:30)
- **Action**: Click on the search input on the Home Page. Paste a test URL (e.g., `https://www.flipkart.com/sony-wh-1000xm5-headphone/p/itm123`) or type `Sony WH-1000XM5` and press Enter / click "Check Price".
- **Visual State**: Transition to `/analyze/sony_wh1000xm5` showing the 3-step animated progress checklist:
  - Step 1: *Gathering store offers...*
  - Step 2: *Checking merchant reliability...*
  - Step 3: *Analyzing price trends...*
- **Presenter Spoken Script**:
  > *"Let's test ShopQ with a popular premium headphone: the Sony WH-1000XM5. As I paste the retailer link and trigger analysis, our FastAPI backend initiates an asynchronous data collection pipeline. It routes the request through ScraperAPI with India geotargeting, extracts structured JSON-LD and CSS DOM metrics, and passes the normalized offer to our machine learning decision synthesizer."*

---

#### Step 3: The Decision Card & "Why" Explanation (1:30 - 2:45)
- **Action**: Show the main Decision Card on `/analyze/sony_wh1000xm5`. Point to the `WAIT` decision badge (Dusty Rose / Coral themed), the confidence badge (`HIGH`), the buy point target (`₹22,999`), and the "Why" explanation panel.
- **Presenter Spoken Script**:
  > *"Here is the core output of ShopQ. Instead of forcing the user to decipher complex charts, ShopQ gives an unambiguous recommendation: **WAIT**. It indicates a high confidence level and identifies a recommended Buy Point of ₹22,999."*
  >
  > *"Below the decision, our 'Why Panel' breaks down the primary reasoning: **'Price is currently elevated near the 90-day peak; ML forecast predicts a price drop within 14 days.'**"*
  >
  > *"Notice that this decision is bounded by our **7 Hard BUY Safety Gates**. If the seller rating was below 4.0 stars or the data was older than 6 hours, the system would automatically block any BUY recommendation and set a CAUTION status."*

---

#### Step 4: Best Offer & Cross-Retailer Comparison (2:45 - 3:45)
- **Action**: Scroll down to the Best Offer card and the Retailer Comparison table. Point out Flipkart (₹23,499), Amazon India (₹23,990), Croma (₹24,990), and Reliance Digital (₹24,990).
- **Presenter Spoken Script**:
  > *"ShopQ resolves listing title variations across competing platforms into a single canonical product entity. Here, the system compares offers across 4 major authorized retailers in real time. We see Flipkart offers the current lowest price at ₹23,499 with a verified 4.8-star seller rating, while Amazon lists it at ₹23,990."*

---

#### Step 5: Price History & Technical Details (3:45 - 4:30)
- **Action**: Hover over the interactive SVG Price Chart showing the 90-day historical trend. Then click the **"Technical Details"** tab (`/analyze/sony_wh1000xm5/details`) to showcase the 3-Level breakdown: Level 1 Consumer Summary, Level 2 Decision Logic, Level 3 Technical / DWDM Metadata.
- **Presenter Spoken Script**:
  > *"Moving to the Price History chart, we visualize 90 days of price observations extracted from our PostgreSQL Data Warehouse Star Schema. For technical evaluators, clicking 'Technical Details' reveals Level 3 metadata: model version `price-v1`, decision rules version `decision-v1`, data freshness timestamp, and schema keys referencing `fact_price_history`."*

---

#### Step 6: Watchlist & Alert Trigger (4:30 - 5:15)
- **Action**: Click the **"Track Price" / "Add to Watchlist"** button. Navigate to `/watchlist` to show the item stored under `WAITING`. Then navigate to `/alerts` to show an active alert badge notification.
- **Presenter Spoken Script**:
  > *"If the shopper decides to wait, they can click 'Track Price' with a single tap. Navigating to our Watchlist page, the item is categorized under 'WAITING'. When our background scraper detects that the price hits the ₹22,999 target, an automated alert is pushed to the user's Alerts feed."*

---

#### Step 7: Chrome Extension Side Panel Demonstration (5:15 - 6:30)
- **Action**: Open a new browser tab navigating directly to `https://www.amazon.in/dp/B0B3MWQXNP` (or Flipkart product page). Click the ShopQ Chrome Extension icon to open the native **Chrome Side Panel**. Show the Side Panel rendering the exact same decision card, why explanation, and best offer.
- **Presenter Spoken Script**:
  > *"Now, let's observe how ShopQ integrates seamlessly into a shopper's normal browsing workflow using our **Chrome Manifest V3 Extension**. As I view the headphone page on Amazon, I open the native Chrome Side Panel. The extension extracts the active URL, sends a background payload to our FastAPI backend, and renders the exact same ShopQ decision right alongside the store page!"*
  >
  > *"Furthermore, our content script injects a lightweight, isolated Shadow DOM badge directly onto the merchant PDP page without altering the store's original styling."*

---

#### Step 8: Conclusion & Summary of Impact (6:30 - 7:00)
- **Action**: Return to the main Web App home screen.
- **Presenter Spoken Script**:
  > *"In conclusion, ShopQ bridges the gap between raw web data, advanced data warehousing, predictive machine learning, and consumer confidence. By combining ScraperAPI web extraction, a Kimball Star Schema DW, `PriceTrend-v2` forecasting, and 7 deterministic safety gates, ShopQ ensures shoppers never overpay online again."*
  >
  > *"Thank you. We are ready to take your questions!"*

---

### Reproducible Demo Test Scenarios

The following seeded test fixtures in `backend/app/services/mock_provider.py` and `frontend/src/services/mockData.js` allow instant demonstration of all decision states:

| Fixture ID | Product Name | Target Decision | Key Scenario Demonstrated |
|---|---|---|---|
| `sony_wh1000xm5` | Sony WH-1000XM5 Headphones | `WAIT` | Price drop predicted; above recent low |
| `iphone15_pro` | Apple iPhone 15 Pro (128GB) | `WAIT_SALE` | Elevated price near peak; sale upcoming |
| `macbook_air_m2` | Apple MacBook Air M2 | `BUY` | Lowest price in 90 days from verified seller |
| `nike_pegasus_40` | Nike Air Zoom Pegasus 40 | `CHECK_ALT` | Identical item ₹800 cheaper on Flipkart |
| `laptop_suspicious_seller` | Lenovo IdeaPad Slim 3 | `CAUTION` | Blocked by Safety Gate 4 (Seller rating 2.3★) |
| `stale_price` | Samsung Galaxy Tab S9 | `CAUTION` | Blocked by Safety Gate 3 (Price data 14 days old) |
| `new_product_no_history` | Pixel Watch 3 | `YOUR_CALL` / `NO_DECISION` | Limited history ($< 3$ days); fallback to Tier 1 EMA |
| `all_sources_failed` | Generic Wireless Earbuds | `NO_DECISION` | Blocked by Safety Gate 6 & 7 (Scraper timeout) |
