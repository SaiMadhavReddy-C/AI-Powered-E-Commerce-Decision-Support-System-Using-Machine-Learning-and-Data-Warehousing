# ShopQ Manifest V3 Chrome Extension

> **Product Promise:** *"ShopQ is a friend who checks before you buy."*

ShopQ Chrome Extension brings real-time, pre-purchase price checks, seller reliability verification, and cross-retailer deal comparisons directly into your browser using native Chrome Side Panel APIs.

---

## 🔒 Privacy-Conscious Architecture

Unlike traditional shopping extensions that constantly scrape or stream browsing history back to cloud servers:
1. **Zero Background Streaming:** ShopQ does **NOT** log, record, or stream your browsing activity.
2. **Local Evaluation:** The content script (`content.js`) evaluates whether a webpage is a Product Detail Page (PDP) entirely within your local browser sandbox.
3. **Explicit User Action:** Network requests to `POST /api/analyze` are made **only when you explicitly click** the floating ShopQ badge or request an analysis.
4. **Minimal Permissions:** Scoped strictly to supported Indian retailer domains (`amazon.in`, `flipkart.com`, `croma.com`, `reliancedigital.in`, `myntra.com`) with `activeTab`, `sidePanel`, and `storage`.

---

## 📂 Bundle File Structure

```
extension/
├── manifest.json            # Manifest V3 specification (permissions, sidePanel, host_permissions)
├── background.js            # Service worker (sidePanel lifecycle, tab management, action badge)
├── content.js               # Shadow-DOM isolated PDP detection & floating badge indicator
├── content.css              # Host element placement styles
├── sidepanel.html           # Native Chrome Side Panel interface
├── sidepanel.js             # Side panel controller consuming FastAPI POST /api/analyze
├── sidepanel.css            # ShopQ Light Mode Design System styling
├── generate_icons.js        # Standalone Node.js icon generator
├── generate_icons.py        # Standalone Python icon generator
├── test_extension.js        # Node.js automated test & validation suite
├── validate_extension.py    # Python automated test & validation suite
└── README.md                # Documentation & developer guide
```

---

## 🎨 Design System Compliance

The side panel strictly complies with the ShopQ Light Mode Design System:
- **Background:** `#FAF8F5`
- **Card Elements:** `#FFFFFF` with 1px border (`#E8E4E0`) and `8px` border radius
- **Accent:** `#C96B7A` Dusty Rose (hover `#B55A69`, light `#F5E6E9`)
- **Typography:** `Inter`, -apple-system, sans-serif
- **Semantic Feedback:**
  - `BUY` / `GRAB`: `#2D8A56` (Positive)
  - `WAIT` / `WAIT_SALE`: `#C48A1A` (Warning)
  - `CAUTION` / `DONT_RUSH`: `#B54A4A` (Danger)
  - `YOUR_CALL` / `NO_DECISION`: `#8A8A8A` (Neutral)
- **Zero AI Gradients or Glassmorphism:** Clean, trustworthy, humanized shopping advice.

---

## 🚀 Loading into Google Chrome (Developer Mode)

1. Open Google Chrome.
2. Navigate to `chrome://extensions`.
3. In the top-right corner, toggle **Developer mode** to ON.
4. Click **Load unpacked**.
5. Select the `extension/` directory:
   `/Users/sai/.gemini/antigravity/scratch/shopq/extension`
6. Pin the **ShopQ** extension icon to your toolbar.

---

## 🧪 How to Test

### Automated Verification
Run either test runner from your terminal:
```bash
# Using Node.js:
node extension/test_extension.js

# Or using Python:
python3 extension/validate_extension.py
```

### Manual Testing on Supported Retailers
1. Start the ShopQ backend server:
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
2. Open any supported product page in Chrome:
   - Amazon India: e.g. `https://www.amazon.in/dp/B09XS7JWHH`
   - Flipkart: e.g. `https://www.flipkart.com/p/itm...`
   - Croma: e.g. `https://www.croma.com/p/...`
3. Observe the floating **ShopQ · Check Price** pill in the bottom-right corner.
4. Click the badge:
   - The native `chrome.sidePanel` slides open automatically.
   - ShopQ requests `POST /api/analyze` to `http://localhost:8000/api/analyze`.
   - Displays Recommendation verdict badge (`BUY`, `WAIT`, `CAUTION`, etc.), humanized primary reason, target buy point, cross-retailer best offer, and "Open in ShopQ Web App" CTA.
