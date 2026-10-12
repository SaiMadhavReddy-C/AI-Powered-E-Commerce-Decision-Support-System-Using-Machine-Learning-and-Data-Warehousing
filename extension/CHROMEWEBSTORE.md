# Chrome Web Store Listing: ShopQ

**Last Updated:** October 8, 2026  
**Extension Name:** ShopQ - Check Before You Buy  
**Short Name:** ShopQ  
**Version:** 1.0.0  

---

## 1. Store Listing Details

### Short Description (Max 132 characters)
> Smart pre-purchase shopping advisor for Amazon, Flipkart, Croma, Reliance Digital, and Myntra. Privacy-first, zero telemetry.

### Detailed Description
> **ShopQ is a friend who checks before you buy.**
>
> Ever wonder if a product's "discount" is really a deal, whether you should wait for an upcoming festival sale, or if another verified store has it for less? ShopQ evaluates product pricing, historical trends, and seller credibility before you spend your hard-earned money.
>
> ### Why Shoppers Love ShopQ:
>
> 🛒 **Clear Recommendations:** Instant, human advice — "Buy it", "Wait a little", or "Check another option" backed by real data.
>
> 🎯 **Target Buy Point:** Know exactly what price is fair so you never overpay.
>
> 🛡️ **Seller Reliability Checks:** Avoid questionable third-party sellers with instant verification of ratings and return policies.
>
> 🔍 **Cross-Store Comparisons:** Compares prices across Amazon, Flipkart, Croma, Reliance Digital, and Myntra to spot better options.
>
> 🔒 **100% Privacy-First:** Unlike other shopping assistants, ShopQ never tracks your browsing history or streams your activity. It only runs an analysis when you explicitly click to check a product.

---

## 2. Permissions Justification

| Permission / Host | Why It Is Needed |
| :--- | :--- |
| `activeTab` | Allows ShopQ to read the current product URL when you explicitly open the side panel or click the ShopQ check badge. |
| `sidePanel` | Displays buying advice, price trends, and seller checks in Chrome's native side panel without cluttering your browser window. |
| `storage` | Stores your target price alerts, watched items, and connection preferences locally on your device. |
| `*://*.amazon.in/*` | Detects when you are viewing an Amazon India product page to display the ShopQ badge. |
| `*://*.flipkart.com/*` | Detects when you are viewing a Flipkart product page to display the ShopQ badge. |
| `*://*.croma.com/*` | Detects when you are viewing a Croma product page to display the ShopQ badge. |
| `*://*.reliancedigital.in/*` | Detects when you are viewing a Reliance Digital product page to display the ShopQ badge. |
| `*://*.myntra.com/*` | Detects when you are viewing a Myntra product page to display the ShopQ badge. |

---

## 3. Privacy & Data Use Disclosure

- **Does the extension collect personal data?** No.
- **Does the extension transmit browsing activity?** No. Browsing history is never stored or tracked.
- **When is data processed?** Only when the user explicitly clicks the ShopQ badge or submits a link to analyze.
- **Single Purpose:** Help consumers make informed, safe purchasing decisions across supported Indian e-commerce platforms.

---

## 4. Version History

- **v1.0.0 (2026-10-08):** Initial release featuring Manifest V3 architecture, native Chrome Side Panel, privacy-conscious PDP detection, and FastAPI decision engine integration.
