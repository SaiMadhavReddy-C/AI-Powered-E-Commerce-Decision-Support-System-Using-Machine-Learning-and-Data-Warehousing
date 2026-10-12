/**
 * ShopQ Mock Data Fixtures and API Service Emulators
 * Conforms to the 4-Level Identity Schema:
 * 1. canonical_product
 * 2. canonical_variant
 * 3. retailer_listing
 * 4. seller_offer
 */

// Global tracker for last detected URL entered in search or visited
let lastDetectedUrl = '';

export function setLastSearchedUrl(url) {
  if (!url) return;
  lastDetectedUrl = url;
  try {
    if (typeof window !== 'undefined' && window.sessionStorage) {
      window.sessionStorage.setItem('shopq_last_searched_url', url);
    }
  } catch {
    // Ignore storage errors in restricted contexts
  }
}

export function getLastSearchedUrl() {
  if (lastDetectedUrl) return lastDetectedUrl;
  try {
    if (typeof window !== 'undefined' && window.sessionStorage) {
      return window.sessionStorage.getItem('shopq_last_searched_url') || '';
    }
  } catch {
    // Ignore storage errors
  }
  return '';
}

// Window submit listener to auto-capture URL submissions from SearchBar without modifying SearchBar UI
if (typeof window !== 'undefined') {
  window.addEventListener(
    'submit',
    (e) => {
      try {
        const input = e.target?.querySelector?.('input');
        if (input?.value && (input.value.startsWith('http://') || input.value.startsWith('https://'))) {
          setLastSearchedUrl(input.value.trim());
        }
      } catch {
        // Ignore event listener errors
      }
    },
    true
  );
}

/**
 * Generates expanded price history points containing:
 * - date (for backward compatibility)
 * - observed_at
 * - collected_at
 * - shipping_cost
 * - availability_status
 */
export const generatePriceHistory = (
  startPrice,
  endPrice,
  days = 90,
  noise = 500,
  options = {}
) => {
  const { shippingCost = 0, availabilityStatus = 'IN_STOCK' } = options;
  const history = [];
  const now = new Date();

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    const observedAt = date.toISOString();
    const collectedAt = new Date(date.getTime() + 120000).toISOString(); // 2 mins later

    const progress = days > 1 ? 1 - i / (days - 1) : 1;
    let price = startPrice + (endPrice - startPrice) * progress;

    if (days > 1 && noise > 0) {
      price += (Math.random() - 0.5) * noise;
    }

    const priceRounded = Math.max(1, Math.round(price));

    history.push({
      date: observedAt, // backward compatibility with PriceChart
      observed_at: observedAt,
      collected_at: collectedAt,
      price: priceRounded,
      shipping_cost: shippingCost,
      availability_status: availabilityStatus,
    });
  }

  if (history.length > 0) {
    history[history.length - 1].price = endPrice;
  }
  return history;
};

/**
 * 4-Level Schema Factory:
 * Synchronizes 4-level identity entities with flat legacy properties.
 */
export function createProduct({
  id,
  name,
  brand,
  category,
  variant,
  image,
  currentPrice,
  retailer,
  retailerUrl,
  seller,
  recommendation,
  confidence,
  explanation,
  reasons = [],
  buyPoint = null,
  trend = 'STABLE',
  historicalLow,
  historicalHigh,
  lastChecked,
  priceHistory = [],
  competitors = [],
  bestOffer = null,
  canonical_product,
  canonical_variant,
  retailer_listing,
  seller_offer,
  availabilityStatus = 'IN_STOCK',
  shippingCost = 0,
  ...extra
}) {
  const sellerNormalized = {
    name: seller?.name || seller_offer?.sellerName || 'Verified Merchant',
    rating: seller?.rating ?? seller_offer?.rating ?? 4.5,
    reviews: seller?.reviews ?? seller?.reviewCount ?? seller_offer?.reviews ?? 1000,
    reviewCount: seller?.reviewCount ?? seller?.reviews ?? seller_offer?.reviewCount ?? 1000,
    reliability: seller?.reliability || seller_offer?.reliability || 'RELIABLE',
    returnPolicy: seller?.returnPolicy || seller_offer?.returnPolicy || '7-day replacement',
    warranty: seller?.warranty || seller_offer?.warranty || '1 year manufacturer',
  };

  const cp = canonical_product || {
    id: `cp_${id}`,
    name,
    title: name,
    brand,
    category,
    model: variant || name,
    description: explanation,
  };

  const cv = canonical_variant || {
    id: `cv_${id}_${(variant || 'std').toLowerCase().replace(/[^a-z0-9]/g, '_')}`,
    productId: cp.id,
    variant: variant || 'Standard',
    color: variant || 'Standard',
    sku: `SKU-${id.toUpperCase()}`,
    image: image || 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=ShopQ',
  };

  const rl = retailer_listing || {
    id: `rl_${retailer}_${id}`,
    variantId: cv.id,
    retailer,
    retailerName: retailer ? retailer.charAt(0).toUpperCase() + retailer.slice(1) : 'Store',
    url: retailerUrl || `https://${retailer}.com/product/${id}`,
    listingSku: `LST-${id.toUpperCase()}`,
    availabilityStatus,
  };

  const so = seller_offer || {
    id: `so_${sellerNormalized.name.toLowerCase().replace(/[^a-z0-9]/g, '_')}_${id}`,
    listingId: rl.id,
    sellerId: `seller_${sellerNormalized.name.toLowerCase().replace(/[^a-z0-9]/g, '_')}`,
    sellerName: sellerNormalized.name,
    price: currentPrice,
    currency: 'INR',
    shippingCost,
    shipping_cost: shippingCost,
    availabilityStatus,
    availability_status: availabilityStatus,
    rating: sellerNormalized.rating,
    reviews: sellerNormalized.reviews,
    reviewCount: sellerNormalized.reviewCount,
    reliability: sellerNormalized.reliability,
    returnPolicy: sellerNormalized.returnPolicy,
    warranty: sellerNormalized.warranty,
  };

  // Ensure competitor sellers are strings with isReliable flag for React rendering compatibility
  const normalizedCompetitors = competitors.map((comp) => {
    const sellerName = typeof comp.seller === 'object' ? comp.seller?.name : comp.seller;
    const isReliable = comp.isReliable !== undefined ? comp.isReliable : comp.seller?.reliability !== 'RISKY';
    return {
      ...comp,
      seller: sellerName || 'Verified Store',
      isReliable,
    };
  });

  return {
    id,
    name,
    brand,
    category,
    variant,
    image: cv.image,
    currentPrice,
    retailer,
    retailerUrl: rl.url,
    seller: sellerNormalized,
    recommendation,
    confidence,
    explanation,
    reasons,
    buyPoint,
    trend,
    historicalLow: historicalLow ?? currentPrice,
    historicalHigh: historicalHigh ?? currentPrice,
    lastChecked: lastChecked || new Date().toISOString(),
    priceHistory,
    competitors: normalizedCompetitors,
    bestOffer,
    // 4-Level Schema
    canonical_product: cp,
    canonical_variant: cv,
    retailer_listing: rl,
    seller_offer: so,
    ...extra,
  };
}

// Backward-compatible entity extractors
export const getCanonicalProduct = (product) => product?.canonical_product || null;
export const getCanonicalVariant = (product) => product?.canonical_variant || null;
export const getRetailerListing = (product) => product?.retailer_listing || null;
export const getSellerOffer = (product) => product?.seller_offer || null;

/**
 * 12 Required Test Scenarios + Legacy Fixtures
 */
export const mockProducts = [
  // 1. sony_good_deal (BUY)
  createProduct({
    id: 'sony_good_deal',
    name: 'Sony WH-1000XM5',
    brand: 'Sony',
    category: 'Headphones',
    variant: 'Black',
    image: 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Sony',
    currentPrice: 22499,
    retailer: 'amazon',
    retailerUrl: 'https://amazon.in/product/sony',
    seller: {
      name: 'Appario Retail',
      rating: 4.8,
      reviews: 28500,
      reliability: 'RELIABLE',
      returnPolicy: '10-day replacement',
      warranty: '1 year manufacturer',
    },
    recommendation: 'BUY',
    confidence: 'HIGH',
    explanation: 'This is the lowest price recorded in 90 days. Backed by a verified top-tier seller with direct manufacturer warranty.',
    reasons: [
      'Price dropped ₹3,500 today to ₹22,499 (lowest in 90 days)',
      'Top-rated authorized seller (Appario Retail, 4.8★)',
      '10-day replacement policy and 1-year manufacturer warranty',
      'Competitors are priced ₹2,500+ higher',
    ],
    buyPoint: 23999,
    trend: 'FALLING',
    historicalLow: 22499,
    historicalHigh: 29990,
    lastChecked: new Date(Date.now() - 3 * 60000).toISOString(),
    priceHistory: generatePriceHistory(27999, 22499, 90, 600),
    competitors: [
      {
        retailer: 'flipkart',
        seller: 'RetailNet',
        price: 24999,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://flipkart.com/product/sony',
      },
      {
        retailer: 'croma',
        seller: 'Croma',
        price: 26990,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://croma.com/product/sony',
      },
    ],
    bestOffer: null,
  }),

  // 2. iphone_wait (WAIT)
  createProduct({
    id: 'iphone_wait',
    name: 'Apple iPhone 15',
    brand: 'Apple',
    category: 'Electronics',
    variant: '128GB, Blue',
    image: 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=iPhone',
    currentPrice: 65999,
    retailer: 'flipkart',
    retailerUrl: 'https://flipkart.com/product/iphone',
    seller: {
      name: 'SuperComNet',
      rating: 4.6,
      reviews: 54000,
      reliability: 'RELIABLE',
      returnPolicy: '7-day replacement',
      warranty: '1 year Apple warranty',
    },
    recommendation: 'WAIT',
    confidence: 'HIGH',
    explanation: 'Prices recently surged to ₹65,999 near the 90-day peak. A festival sale is expected within 10 days where it often drops below ₹55,000.',
    reasons: [
      'Price jumped 18% over the past week near its 90-day high',
      'Major festival sale scheduled within 10 days',
      'Historical data shows regular drops to ₹54,999 during sales',
      'Target buy price is ₹54,999',
    ],
    buyPoint: 54999,
    trend: 'RISING',
    historicalLow: 52999,
    historicalHigh: 66999,
    lastChecked: new Date(Date.now() - 5 * 60000).toISOString(),
    priceHistory: generatePriceHistory(54999, 65999, 90, 800),
    competitors: [
      {
        retailer: 'amazon',
        seller: 'Appario Retail',
        price: 66490,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://amazon.in/product/iphone',
      },
      {
        retailer: 'reliance',
        seller: 'Reliance Digital',
        price: 65900,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://reliancedigital.in/product/iphone',
      },
    ],
    bestOffer: null,
  }),

  // 3. nike_better_alternative (CHECK_ALT)
  createProduct({
    id: 'nike_better_alternative',
    name: 'Nike Air Max 90',
    brand: 'Nike',
    category: 'Fashion',
    variant: 'White/Black, UK 9',
    image: 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Nike',
    currentPrice: 11499,
    retailer: 'amazon',
    retailerUrl: 'https://amazon.in/product/nike',
    seller: {
      name: 'RetailNet',
      rating: 4.2,
      reviews: 1400,
      reliability: 'RELIABLE',
      returnPolicy: '10-day return',
      warranty: '6 months manufacturer',
    },
    recommendation: 'CHECK_ALT',
    confidence: 'HIGH',
    explanation: 'The current Amazon price is ₹11,499, but Myntra currently has the exact same shoe for ₹8,999 directly from Nike India.',
    reasons: [
      'Identical SKU available on Myntra for ₹8,999',
      'Save ₹2,500 by purchasing from the alternate retailer',
      'Official Nike India store with 15-day free returns',
      'Amazon price is currently above the 60-day median',
    ],
    buyPoint: 9200,
    trend: 'STABLE',
    historicalLow: 8999,
    historicalHigh: 11999,
    lastChecked: new Date(Date.now() - 2 * 60000).toISOString(),
    priceHistory: generatePriceHistory(10999, 11499, 90, 300),
    competitors: [
      {
        retailer: 'myntra',
        seller: 'Nike India',
        price: 8999,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://myntra.com/product/nike',
      },
      {
        retailer: 'flipkart',
        seller: 'IndiFlashMart',
        price: 10999,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://flipkart.com/product/nike',
      },
    ],
    bestOffer: {
      retailer: 'Myntra',
      price: 8999,
      seller: { name: 'Nike India', reliability: 'RELIABLE' },
      isReliable: true,
      inStock: true,
      available: true,
      url: 'https://myntra.com/product/nike',
      savings: 2500,
    },
  }),

  // 4. laptop_suspicious_seller (CAUTION)
  createProduct({
    id: 'laptop_suspicious_seller',
    name: 'HP Pavilion 14',
    brand: 'HP',
    category: 'Computers',
    variant: 'i5 13th Gen, 16GB RAM, 512GB SSD',
    image: 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=HP',
    currentPrice: 46999,
    retailer: 'amazon',
    retailerUrl: 'https://amazon.in/product/hp',
    seller: {
      name: 'QuickDeal Electro Store',
      rating: 2.3,
      reviews: 34,
      reliability: 'RISKY',
      returnPolicy: 'No returns, replacement only',
      warranty: 'Seller warranty only',
    },
    recommendation: 'CAUTION',
    confidence: 'MEDIUM',
    explanation: 'The price is unusually low (₹46,999), but this merchant has a 2.3 rating with multiple reports of refurbished units sold as new.',
    reasons: [
      'Merchant rating is 2.3/5 with high cancellation rate',
      'Recent negative feedback reporting opened boxes and missing accessories',
      'Price is ₹5,000 below authorized distributor pricing',
      'Authorized sellers charge ₹51,999 with valid HP manufacturer warranty',
    ],
    buyPoint: 51999,
    trend: 'STABLE',
    historicalLow: 50999,
    historicalHigh: 58999,
    lastChecked: new Date(Date.now() - 15 * 60000).toISOString(),
    priceHistory: generatePriceHistory(54999, 46999, 90, 500),
    competitors: [
      {
        retailer: 'croma',
        seller: 'Croma Official',
        price: 51999,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://croma.com/product/hp',
      },
      {
        retailer: 'reliance',
        seller: 'Reliance Digital',
        price: 52490,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://reliancedigital.in/product/hp',
      },
    ],
    bestOffer: {
      retailer: 'Croma',
      price: 51999,
      seller: { name: 'Croma Official', reliability: 'RELIABLE' },
      isReliable: true,
      inStock: true,
      available: true,
      url: 'https://croma.com/product/hp',
      savings: -5000,
    },
  }),

  // 5. new_product_no_history (NO_DECISION)
  createProduct({
    id: 'new_product_no_history',
    name: 'Canon EOS R50',
    brand: 'Canon',
    category: 'Cameras',
    variant: 'Body Only, Black',
    image: 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Canon',
    currentPrice: 74999,
    retailer: 'croma',
    retailerUrl: 'https://croma.com/product/canon',
    seller: {
      name: 'Croma Official',
      rating: 4.8,
      reviews: 14,
      reliability: 'RELIABLE',
      returnPolicy: '7-day replacement',
      warranty: '2 years manufacturer',
    },
    recommendation: 'NO_DECISION',
    confidence: 'LOW',
    explanation: 'This camera was released only 3 days ago. There is not enough historical pricing data to predict whether a discount cycle will occur soon.',
    reasons: [
      'Newly launched product with only 3 days of price tracking',
      'Zero promotional discount cycles observed so far',
      'Currently only available at single authorized retailer',
      'Recommended to wait until multiple retailers list stock',
    ],
    buyPoint: null,
    trend: 'STABLE',
    historicalLow: 74999,
    historicalHigh: 74999,
    lastChecked: new Date(Date.now() - 8 * 60000).toISOString(),
    priceHistory: generatePriceHistory(74999, 74999, 3, 0),
    competitors: [],
    bestOffer: null,
  }),

  // 6. stale_price (CAUTION)
  createProduct({
    id: 'stale_price',
    name: 'Amazon Kindle Paperwhite (16 GB)',
    brand: 'Amazon',
    category: 'Electronics',
    variant: '16GB, Black, 6.8 inch',
    image: 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Kindle',
    currentPrice: 14999,
    retailer: 'amazon',
    retailerUrl: 'https://amazon.in/product/kindle',
    seller: {
      name: 'Cocoblu Retail',
      rating: 4.4,
      reviews: 8900,
      reliability: 'RELIABLE',
      returnPolicy: '7-day replacement',
      warranty: '1 year manufacturer',
    },
    recommendation: 'CAUTION',
    confidence: 'LOW',
    explanation: 'This price was last recorded 14 days ago. Scraper connectivity was interrupted, so live checkout price and stock may differ.',
    reasons: [
      'Price record is 14 days old (stale cache)',
      'Retailer page could not be refreshed in the last 48 hours',
      'Live price might have changed on the store',
      'Verify checkout total directly on retailer page before purchase',
    ],
    buyPoint: 13499,
    trend: 'STABLE',
    historicalLow: 12999,
    historicalHigh: 14999,
    lastChecked: new Date(Date.now() - 14 * 24 * 3600 * 1000).toISOString(),
    priceHistory: generatePriceHistory(13999, 14999, 90, 200),
    competitors: [
      {
        retailer: 'croma',
        seller: 'Croma',
        price: 14999,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://croma.com/product/kindle',
      },
    ],
    bestOffer: null,
  }),

  // 7. variant_mismatch (CAUTION)
  createProduct({
    id: 'variant_mismatch',
    name: 'Apple MacBook Air 13.6-inch M2',
    brand: 'Apple',
    category: 'Computers',
    variant: '16GB RAM, 512GB SSD, Space Grey',
    image: 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=MacBook',
    currentPrice: 79990,
    retailer: 'flipkart',
    retailerUrl: 'https://flipkart.com/product/macbook',
    seller: {
      name: 'IndiTechRetail',
      rating: 3.8,
      reviews: 820,
      reliability: 'MODERATE',
      returnPolicy: '7-day replacement',
      warranty: '1 year Apple warranty',
    },
    recommendation: 'CAUTION',
    confidence: 'MEDIUM',
    explanation: 'Potential variant mismatch detected: The listing title states 16GB RAM / 512GB SSD, but the model number and specifications table show 8GB RAM / 256GB SSD.',
    reasons: [
      'Listing title claims 16GB RAM / 512GB SSD configuration',
      'Manufacturer SKU (MLXY3HN/A) corresponds to 8GB / 256GB base model',
      'Price (₹79,990) matches the 8GB base model market rate',
      'High risk of receiving lower specification item',
    ],
    buyPoint: 89900,
    trend: 'STABLE',
    historicalLow: 79990,
    historicalHigh: 99990,
    lastChecked: new Date(Date.now() - 6 * 60000).toISOString(),
    priceHistory: generatePriceHistory(84990, 79990, 90, 400),
    competitors: [
      {
        retailer: 'amazon',
        seller: 'Appario Retail',
        price: 94990,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://amazon.in/product/macbook',
      },
    ],
    bestOffer: null,
  }),

  // 8. all_sources_failed (NO_DECISION)
  createProduct({
    id: 'all_sources_failed',
    name: 'Google Pixel 8 Pro',
    brand: 'Google',
    category: 'Electronics',
    variant: '128GB, Obsidian',
    image: 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Pixel',
    currentPrice: 84999,
    retailer: 'flipkart',
    retailerUrl: 'https://flipkart.com/product/pixel8pro',
    seller: {
      name: 'Unverified Source',
      rating: 0,
      reviews: 0,
      reliability: 'UNKNOWN',
      returnPolicy: 'Unknown',
      warranty: 'Unknown',
    },
    recommendation: 'NO_DECISION',
    confidence: 'LOW',
    explanation: 'All data scrapers and partner API connections failed or timed out. We are unable to confirm current live pricing or stock status.',
    reasons: [
      'All retail scrapers timed out or returned HTTP 503 / 403 blocks',
      'Anti-bot challenge prevented live inventory extraction',
      'Unable to verify active seller or stock availability',
      'Please check the retailer page directly',
    ],
    buyPoint: null,
    trend: 'STABLE',
    historicalLow: 79999,
    historicalHigh: 106999,
    lastChecked: new Date(Date.now() - 60 * 60000).toISOString(),
    priceHistory: generatePriceHistory(89999, 84999, 30, 500),
    competitors: [],
    bestOffer: null,
  }),

  // 9. seller_changed (CAUTION)
  createProduct({
    id: 'seller_changed',
    name: 'Samsung Galaxy S24 5G',
    brand: 'Samsung',
    category: 'Electronics',
    variant: '256GB, Onyx Black',
    image: 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Samsung',
    currentPrice: 59999,
    retailer: 'amazon',
    retailerUrl: 'https://amazon.in/product/samsung',
    seller: {
      name: 'FastGizmos Unlimited',
      rating: 3.1,
      reviews: 42,
      reliability: 'MODERATE',
      returnPolicy: '7-day replacement',
      warranty: '1 year manufacturer',
    },
    recommendation: 'CAUTION',
    confidence: 'MEDIUM',
    explanation: 'The default Buy Box seller switched in the last 12 hours from verified direct retailer to an unrated third-party merchant with merchant-fulfilled delivery.',
    reasons: [
      'Buy Box merchant changed in the last 12 hours',
      'New seller rating is 3.1★ vs previous verified seller at 4.7★',
      'Order is merchant-fulfilled with 7-day extended delivery estimate',
      'Flipkart and Croma offer direct verified fulfillment for comparable price',
    ],
    buyPoint: 54999,
    trend: 'STABLE',
    historicalLow: 52999,
    historicalHigh: 64999,
    lastChecked: new Date(Date.now() - 10 * 60000).toISOString(),
    priceHistory: generatePriceHistory(59999, 59999, 90, 500),
    competitors: [
      {
        retailer: 'flipkart',
        seller: 'RetailNet',
        price: 60999,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://flipkart.com/product/samsung',
      },
      {
        retailer: 'croma',
        seller: 'Croma',
        price: 61999,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://croma.com/product/samsung',
      },
    ],
    bestOffer: null,
  }),

  // 10. out_of_stock (WAIT)
  createProduct({
    id: 'out_of_stock',
    name: 'Sony PlayStation 5 Pro Console',
    brand: 'Sony',
    category: 'Gaming',
    variant: '2TB, White',
    image: 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=PS5+Pro',
    currentPrice: 79990,
    retailer: 'amazon',
    retailerUrl: 'https://amazon.in/product/ps5pro',
    seller: {
      name: 'ScalperDeals Hub',
      rating: 3.5,
      reviews: 18,
      reliability: 'MODERATE',
      returnPolicy: 'No returns',
      warranty: 'Seller warranty only',
    },
    recommendation: 'WAIT',
    confidence: 'HIGH',
    explanation: 'Official stock is currently sold out across all authorized retailers. Only third-party sellers are listing units with a ₹10,000+ markup.',
    reasons: [
      'Out of stock at official retail price (MSRP ₹69,990)',
      'Available listings are unauthorized scalpers with inflated prices',
      'Official restock shipment expected in approximately 2 weeks',
      'Wait for official restock to avoid overpaying',
    ],
    buyPoint: 69990,
    trend: 'RISING',
    historicalLow: 69990,
    historicalHigh: 84990,
    availabilityStatus: 'OUT_OF_STOCK',
    lastChecked: new Date(Date.now() - 7 * 60000).toISOString(),
    priceHistory: generatePriceHistory(69990, 79990, 90, 700, { availabilityStatus: 'OUT_OF_STOCK' }),
    competitors: [
      {
        retailer: 'flipkart',
        seller: 'GamerStore',
        price: 82990,
        isReliable: false,
        available: false,
        inStock: false,
        url: 'https://flipkart.com/product/ps5pro',
      },
    ],
    bestOffer: null,
  }),

  // 11. your_call (YOUR_CALL)
  createProduct({
    id: 'your_call',
    name: 'boAt Airdopes 141 True Wireless',
    brand: 'boAt',
    category: 'Accessories',
    variant: 'Bold Black',
    image: 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=boAt',
    currentPrice: 999,
    retailer: 'amazon',
    retailerUrl: 'https://amazon.in/product/boat',
    seller: {
      name: 'Cocoblu Retail',
      rating: 4.3,
      reviews: 154000,
      reliability: 'RELIABLE',
      returnPolicy: '7-day replacement',
      warranty: '1 year manufacturer',
    },
    recommendation: 'YOUR_CALL',
    confidence: 'LOW',
    explanation: 'This is an everyday value item at ₹999. Price fluctuation over the past 90 days has been under ₹100. If you need it today, go ahead.',
    reasons: [
      'Stable everyday price with minimal historical variation (₹899 - ₹1,099)',
      'No major pending discount cycle expected for this model',
      'High volume verified seller with fast dispatch',
      'Reasonable price for immediate purchase',
    ],
    buyPoint: 999,
    trend: 'STABLE',
    historicalLow: 899,
    historicalHigh: 1299,
    lastChecked: new Date(Date.now() - 1 * 60000).toISOString(),
    priceHistory: generatePriceHistory(999, 999, 90, 50),
    competitors: [
      {
        retailer: 'flipkart',
        seller: 'RetailNet',
        price: 999,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://flipkart.com/product/boat',
      },
    ],
    bestOffer: null,
  }),

  // 12. no_decision (NO_DECISION)
  createProduct({
    id: 'no_decision',
    name: 'Nothing Ear (2) Wireless Earbuds',
    brand: 'Nothing',
    category: 'Headphones',
    variant: 'White, Hi-Res Audio',
    image: 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Nothing',
    currentPrice: 7499,
    retailer: 'flipkart',
    retailerUrl: 'https://flipkart.com/product/nothing',
    seller: {
      name: 'SuperComNet',
      rating: 4.2,
      reviews: 3400,
      reliability: 'RELIABLE',
      returnPolicy: '7-day replacement',
      warranty: '1 year manufacturer',
    },
    recommendation: 'NO_DECISION',
    confidence: 'LOW',
    explanation: 'Conflicting market signals: Prices have been volatile with frequent erratic swings, and rumors of a successor announcement make a firm call unreliable.',
    reasons: [
      'Volatile price swings between ₹6,499 and ₹8,499 within 30 days',
      'Divergent pricing trends between Flipkart and Amazon',
      'Unconfirmed rumors of a new model release next month',
      'Insufficient consistency to recommend buying or waiting',
    ],
    buyPoint: null,
    trend: 'VOLATILE',
    historicalLow: 6499,
    historicalHigh: 8999,
    lastChecked: new Date(Date.now() - 4 * 60000).toISOString(),
    priceHistory: generatePriceHistory(7999, 7499, 90, 600),
    competitors: [
      {
        retailer: 'amazon',
        seller: 'RetailNet',
        price: 7999,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://amazon.in/product/nothing',
      },
      {
        retailer: 'croma',
        seller: 'Croma',
        price: 7499,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://croma.com/product/nothing',
      },
    ],
    bestOffer: null,
  }),

  // Additional scenario: oneplus_12 (DONT_RUSH)
  createProduct({
    id: 'oneplus_12',
    name: 'OnePlus 12',
    brand: 'OnePlus',
    category: 'Electronics',
    variant: '256GB, Silky Black',
    image: 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=OnePlus',
    currentPrice: 69999,
    retailer: 'amazon',
    retailerUrl: 'https://amazon.in/product/oneplus',
    seller: {
      name: 'Darshita Electronics',
      rating: 4.4,
      reviews: 12000,
      reliability: 'RELIABLE',
      returnPolicy: '7-day replacement',
      warranty: '1 year manufacturer',
    },
    recommendation: 'DONT_RUSH',
    confidence: 'HIGH',
    explanation: 'This is currently at its highest price in 60 days. I strongly recommend waiting for a drop.',
    reasons: [
      'Price spiked recently to ₹69,999',
      'Historical data shows it regularly sells for ₹64,999',
      'No promotional incentives or bank discounts currently active',
    ],
    buyPoint: 64999,
    trend: 'RISING',
    historicalLow: 62999,
    historicalHigh: 69999,
    lastChecked: new Date(Date.now() - 4 * 60000).toISOString(),
    priceHistory: generatePriceHistory(64999, 69999, 90, 600),
    competitors: [
      {
        retailer: 'reliance',
        seller: 'Reliance Digital',
        price: 69999,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://reliancedigital.in/product/oneplus',
      },
    ],
    bestOffer: null,
  }),

  // Additional scenario: samsung_s24 (WAIT_SALE)
  createProduct({
    id: 'samsung_s24',
    name: 'Samsung Galaxy S24',
    brand: 'Samsung',
    category: 'Electronics',
    variant: '256GB, Cobalt Violet',
    image: 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Samsung',
    currentPrice: 59999,
    retailer: 'amazon',
    retailerUrl: 'https://amazon.in/product/samsung',
    seller: {
      name: 'STPL Direct',
      rating: 4.5,
      reviews: 18000,
      reliability: 'RELIABLE',
      returnPolicy: '7-day replacement',
      warranty: '1 year manufacturer',
    },
    recommendation: 'WAIT_SALE',
    confidence: 'MEDIUM',
    explanation: 'A major festival sale is expected next week. I would wait, as Samsung flagships historically drop ₹5,000–₹7,000.',
    reasons: [
      'Upcoming festival sale detected next week',
      'Current price is at 90-day average',
      'Historical discounts during sale events reached ₹52,999',
    ],
    buyPoint: 54999,
    trend: 'STABLE',
    historicalLow: 52999,
    historicalHigh: 64999,
    lastChecked: new Date(Date.now() - 10 * 60000).toISOString(),
    priceHistory: generatePriceHistory(59999, 59999, 90, 500),
    competitors: [
      {
        retailer: 'flipkart',
        seller: 'RetailNet',
        price: 60999,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://flipkart.com/product/samsung',
      },
    ],
    bestOffer: null,
  }),

  // Additional scenario: nike_air_max (GRAB)
  createProduct({
    id: 'nike_air_max',
    name: 'Nike Air Max 90',
    brand: 'Nike',
    category: 'Fashion',
    variant: 'White/Black',
    image: 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Nike',
    currentPrice: 8999,
    retailer: 'myntra',
    retailerUrl: 'https://myntra.com/product/nike',
    seller: {
      name: 'Nike India',
      rating: 4.8,
      reviews: 3200,
      reliability: 'RELIABLE',
      returnPolicy: '15-day return',
      warranty: '6 months warranty',
    },
    recommendation: 'GRAB',
    confidence: 'HIGH',
    explanation: 'This is an excellent flash deal! It is selling ₹2,500 below standard retail.',
    reasons: [
      'Flash sale price matches 90-day all-time low',
      'Official Nike India direct fulfillment',
      'Usually sells at ₹11,499 on other marketplaces',
    ],
    buyPoint: 8999,
    trend: 'FALLING',
    historicalLow: 8999,
    historicalHigh: 11499,
    lastChecked: new Date(Date.now() - 2 * 60000).toISOString(),
    priceHistory: generatePriceHistory(11499, 8999, 90, 200),
    competitors: [
      {
        retailer: 'amazon',
        seller: 'RetailNet',
        price: 11499,
        isReliable: true,
        available: true,
        inStock: true,
        url: 'https://amazon.in/product/nike',
      },
    ],
    bestOffer: {
      retailer: 'Myntra',
      price: 8999,
      seller: { name: 'Nike India', reliability: 'RELIABLE' },
      isReliable: true,
      inStock: true,
      available: true,
      url: 'https://myntra.com/product/nike',
      savings: 2500,
    },
  }),
];

// Alias map guaranteeing legacy product IDs resolve to the correct scenario product
const PRODUCT_ALIASES = {
  sony_wh1000xm5: 'sony_good_deal',
  iphone_15: 'iphone_wait',
  hp_laptop: 'laptop_suspicious_seller',
  new_camera: 'new_product_no_history',
  boat_earbuds: 'your_call',
  dont_rush: 'oneplus_12',
  wait_sale: 'samsung_s24',
};

/**
 * Resolves a product by URL matching rules:
 * 1. Exact match with retailerUrl, retailer_listing.url, or competitor url
 * 2. Keyword heuristic in URL path or query
 * 3. Domain heuristic
 * 4. Safe fallback to default demo product (no 404)
 */
export function resolveProductByUrl(rawUrl) {
  if (!rawUrl) return mockProducts[0];
  const url = String(rawUrl).toLowerCase().trim();

  // 1. Direct URL match
  for (const product of mockProducts) {
    if (product.retailerUrl && url.includes(product.retailerUrl.toLowerCase())) {
      return product;
    }
    if (product.retailer_listing?.url && url.includes(product.retailer_listing.url.toLowerCase())) {
      return product;
    }
    if (product.competitors && Array.isArray(product.competitors)) {
      for (const comp of product.competitors) {
        if (comp.url && url.includes(comp.url.toLowerCase())) {
          return product;
        }
      }
    }
  }

  // 2. Keyword heuristics in URL
  if (url.includes('sony') || url.includes('xm5') || url.includes('wh1000xm5') || url.includes('headphones')) {
    return getProductById('sony_good_deal');
  }
  if (url.includes('iphone') || url.includes('apple-phone') || url.includes('iphone-15')) {
    return getProductById('iphone_wait');
  }
  if (url.includes('nike') || url.includes('air-max') || url.includes('airmax') || url.includes('sneaker')) {
    return getProductById('nike_better_alternative');
  }
  if (url.includes('hp') || url.includes('pavilion') || url.includes('laptop')) {
    return getProductById('laptop_suspicious_seller');
  }
  if (url.includes('canon') || url.includes('camera') || url.includes('eos-r50') || url.includes('r50')) {
    return getProductById('new_product_no_history');
  }
  if (url.includes('kindle') || url.includes('paperwhite') || url.includes('ereader')) {
    return getProductById('stale_price');
  }
  if (url.includes('macbook') || url.includes('m2') || url.includes('macbook-air')) {
    return getProductById('variant_mismatch');
  }
  if (url.includes('pixel') || url.includes('pixel8') || url.includes('google-phone')) {
    return getProductById('all_sources_failed');
  }
  if (url.includes('samsung') || url.includes('galaxy') || url.includes('s24')) {
    return getProductById('seller_changed');
  }
  if (url.includes('ps5') || url.includes('playstation') || url.includes('ps5pro') || url.includes('console')) {
    return getProductById('out_of_stock');
  }
  if (url.includes('boat') || url.includes('airdopes') || url.includes('earbuds')) {
    return getProductById('your_call');
  }
  if (url.includes('nothing') || url.includes('ear-2') || url.includes('ear2')) {
    return getProductById('no_decision');
  }
  if (url.includes('oneplus')) {
    return getProductById('oneplus_12');
  }

  // 3. Retailer domain heuristic
  if (url.includes('myntra.com')) {
    return getProductById('nike_better_alternative');
  }
  if (url.includes('flipkart.com')) {
    return getProductById('iphone_wait');
  }
  if (url.includes('croma.com')) {
    return getProductById('new_product_no_history');
  }
  if (url.includes('amazon.in') || url.includes('amazon.com')) {
    return getProductById('sony_good_deal');
  }

  // 4. Default demo fallback
  return getProductById('sony_good_deal') || mockProducts[0];
}

/**
 * Gets product by ID, URL, or alias.
 * Solves 'url-match-id' by resolving to the last detected searched URL or demo default.
 */
export function getProductById(id) {
  if (!id) return undefined;

  // Handle URL router placeholder
  if (id === 'url-match-id') {
    const lastUrl = getLastSearchedUrl();
    return resolveProductByUrl(lastUrl || 'https://amazon.in/product/sony');
  }

  // Handle passed URL or encoded URL
  if (
    id.startsWith('http://') ||
    id.startsWith('https://') ||
    id.includes('amazon.in') ||
    id.includes('flipkart.com') ||
    id.includes('myntra.com') ||
    id.includes('croma.com')
  ) {
    return resolveProductByUrl(decodeURIComponent(id));
  }

  // Direct match
  const directMatch = mockProducts.find((p) => p.id === id);
  if (directMatch) return directMatch;

  // Check alias map
  const targetId = PRODUCT_ALIASES[id];
  if (targetId) {
    const aliasMatch = mockProducts.find((p) => p.id === targetId);
    if (aliasMatch) return aliasMatch;
  }

  // Check 4-level canonical IDs
  const canonicalMatch = mockProducts.find(
    (p) =>
      p.canonical_product?.id === id ||
      p.canonical_variant?.id === id ||
      p.retailer_listing?.id === id ||
      p.seller_offer?.id === id
  );
  if (canonicalMatch) return canonicalMatch;

  return undefined;
}

/**
 * Search products by query or URL
 */
export function searchProducts(query) {
  if (!query) return [];
  const trimmed = query.trim();

  // If query is a URL, save it and return resolved product
  if (trimmed.startsWith('http://') || trimmed.startsWith('https://') || trimmed.includes('.com') || trimmed.includes('.in')) {
    setLastSearchedUrl(trimmed);
    const resolved = resolveProductByUrl(trimmed);
    return resolved ? [resolved] : [];
  }

  const lower = trimmed.toLowerCase();
  return mockProducts.filter(
    (p) =>
      p.name.toLowerCase().includes(lower) ||
      p.brand.toLowerCase().includes(lower) ||
      p.category.toLowerCase().includes(lower) ||
      p.id.toLowerCase().includes(lower) ||
      (p.variant && p.variant.toLowerCase().includes(lower))
  );
}

/**
 * Watchlist items with rich watchStatus, watchGroup, and actions
 */
export function getWatchlist() {
  const iphone = getProductById('iphone_wait') || getProductById('iphone_15');
  const sony = getProductById('sony_good_deal') || getProductById('sony_wh1000xm5');
  const samsung = getProductById('seller_changed') || getProductById('samsung_s24');
  const camera = getProductById('new_product_no_history') || getProductById('new_camera');

  return [
    {
      ...iphone,
      watchGroup: 'BUY_SIGNAL',
      watchMessage: "🔥 Price dropped to ₹54,999. I'd buy it now.",
      watchStatus: {
        emoji: '🔥',
        icon: '🔥',
        message: "Price dropped to ₹54,999. I'd buy it now.",
        type: 'positive',
      },
      actionLabel: 'Buy now',
      lastCheckedText: 'Last checked 2 min ago',
    },
    {
      ...sony,
      watchGroup: 'WAITING',
      watchMessage: "⏳ Still waiting. I'd reconsider around ₹22,999.",
      watchStatus: {
        emoji: '⏳',
        icon: '⏳',
        message: "Still waiting. I'd reconsider around ₹22,999.",
        type: 'warning',
      },
      actionLabel: 'Check now',
      lastCheckedText: 'Last checked 4 min ago',
    },
    {
      ...samsung,
      watchGroup: 'NEEDS_ATTENTION',
      watchMessage: "⚠️ The seller changed. I'd check the new listing before buying.",
      watchStatus: {
        emoji: '⚠️',
        icon: '⚠️',
        message: "The seller changed. I'd check the new listing before buying.",
        type: 'danger',
      },
      actionLabel: 'Review',
      lastCheckedText: 'Last checked 1 hr ago',
    },
    {
      ...camera,
      watchGroup: 'WATCHING',
      watchMessage: '👀 Monitoring prices. No major drops yet.',
      watchStatus: {
        emoji: '👀',
        icon: '👀',
        message: 'Monitoring prices. No major drops yet.',
        type: 'neutral',
      },
      actionLabel: 'Check now',
      lastCheckedText: 'Last checked 3 hrs ago',
    },
  ];
}

export const mockAlerts = [
  {
    id: 1,
    title: 'Price Drop Alert',
    message: 'Apple iPhone 15 has dropped to your target price of ₹54,999.',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    read: false,
    productId: 'iphone_wait',
  },
  {
    id: 2,
    title: 'Seller Warning',
    message: 'The default seller for HP Pavilion 14 has changed to a lower-rated seller.',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    read: true,
    productId: 'laptop_suspicious_seller',
  },
  {
    id: 3,
    title: 'Sale Predicted',
    message: 'A major festival sale is expected next week for Samsung Galaxy S24.',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    read: true,
    productId: 'seller_changed',
  },
];

export function getAlerts() {
  return mockAlerts;
}
