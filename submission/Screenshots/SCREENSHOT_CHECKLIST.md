# ShopQ Project Screenshot & Interface Checklist
## Visual Verification & Demonstration Asset Inventory

---

### Overview

This document provides a structured inventory and description of all UI screens, backend database schemas, and architectural views required for the project submission report, presentation, and viva demonstration.

---

### Screenshot Checklist Inventory

| Figure # | Asset Name | Target Route / Context | Expected Visual Features & Verification Points | Status |
|---|---|---|---|---|
| **Fig 1** | Home / Search Screen | `/` | Dusty Rose theme (`#FAF8F5`), search hero input, onboarding steps, recent items, preview cards | Verified |
| **Fig 2** | Search Results Page | `/search?q=sony` | Product query result cards, store badges, current prices, "Check Price" buttons | Verified |
| **Fig 3** | Analysis Page (Decision: WAIT) | `/analyze/sony_wh1000xm5` | Animated 3-step progress checklist, `WAIT` decision badge, target buy point (₹22,999), confidence rating | Verified |
| **Fig 4** | Analysis Page (Decision: BUY) | `/analyze/macbook_air_m2` | `BUY` decision badge (lowest 90-day price), recommendation details, "Buy Now" CTA | Verified |
| **Fig 5** | "Why" Explanation Panel | `/analyze/:id` | Primary reasoning text, secondary bullet points, 7 Hard BUY Safety Gate pass status indicators | Verified |
| **Fig 6** | Best Offer & Retailer Comparison | `/analyze/:id` | Best Offer summary card, multi-retailer price table (Amazon, Flipkart, Croma, Reliance Digital), seller ratings | Verified |
| **Fig 7** | Interactive Price History Chart | `/analyze/:id` | 90-day time-series SVG line graph, price points, tooltip hover values, historical low/high indicators | Verified |
| **Fig 8** | Technical Details Page | `/analyze/:id/details` | 3-Level breakdown (Level 1 Consumer, Level 2 Decision Rules, Level 3 DWDM & Model Metadata) | Verified |
| **Fig 9** | Watchlist Inbox | `/watchlist` | Decision inbox categorized by `BUY_SIGNAL`, `WAITING`, `WATCHING`, `NEEDS_ATTENTION` | Verified |
| **Fig 10** | Alerts Feed | `/alerts` | Price drop notifications, time-elapsed indicators, alert settings toggles | Verified |
| **Fig 11** | User Preferences | `/preferences` | Target priority toggles, price wait tolerance sliders, store allowlist checkboxes | Verified |
| **Fig 12** | Chrome Extension Side Panel | Extension Context | Chrome native `sidePanel` rendering decision card, why panel, and store price summary alongside Amazon/Flipkart | Verified |
| **Fig 13** | System Architecture Diagram | System Overview | Decoupled 4-tier architecture diagram (Client, FastAPI, ScraperAPI, Supabase DWDM) | Verified |
| **Fig 14** | DWDM Star Schema Diagram | Database Layer | Dimensional model showing `fact_price_history`, `fact_recommendation`, and conformed dimensions | Verified |
| **Fig 15** | Supabase Database Tables | Admin Console | Database console view showing operational tables (`canonical_product`, `seller_offer`) and DW tables | Verified |
| **Fig 16** | ML & Decision Pipeline Flow | Logic Flow | Flowchart showing `PriceTrend-v2` 3-tier prediction hierarchy and 7 Hard BUY Safety Gate checks | Verified |

---

### Visual Guidelines for Presentation & Report Integration

1. **Color Palette Alignment**: Ensure all UI screenshots display the official Dusty Rose design system (`#FAF8F5` background, `#C96B7A` Dusty Rose primary accent, `#2D2B2A` body text, 1px `#E8E4E0` borders).
2. **Typography**: Inter font typography clean and legible.
3. **No Decorative Placeholders**: All screenshots must reflect actual rendered components from Vite frontend and Manifest V3 Chrome Extension.
