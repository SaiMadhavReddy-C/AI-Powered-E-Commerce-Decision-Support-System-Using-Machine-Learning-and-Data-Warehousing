import {
  getProductById as mockGetProductById,
  searchProducts as mockSearchProducts,
  getWatchlist as mockGetWatchlist,
  mockProducts,
  resolveProductByUrl as mockResolveProductByUrl,
  setLastSearchedUrl,
  getLastSearchedUrl,
} from './mockData.js';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const ENABLE_MOCK_FALLBACK = import.meta.env.VITE_ENABLE_MOCK_FALLBACK !== 'false';

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function normalizeProduct(data) {
  if (!data) return null;
  const p = data.product || data;
  const d = data.decision || p.decision || {};
  const bo = data.best_offer || data.bestOffer || p.best_offer || p.bestOffer || null;

  const currentPrice = p.currentPrice ?? p.current_price ?? 0;
  const buyPoint = p.buyPoint ?? p.buy_point ?? d.buy_point ?? currentPrice;

  return {
    ...p,
    id: p.id,
    name: p.name || 'Product',
    brand: p.brand || '',
    category: p.category || '',
    variant: p.variant || '',
    image: p.image || p.image_url || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80',
    currentPrice,
    current_price: currentPrice,
    retailer: p.retailer || 'Online Retailer',
    retailerUrl: p.retailerUrl || p.retailer_url || '',
    retailer_url: p.retailerUrl || p.retailer_url || '',
    seller: p.seller || { name: 'Verified Merchant', rating: 4.5, reviewCount: 1000, reliability: 'RELIABLE' },
    recommendation: d.decision || p.recommendation || 'BUY',
    confidence: d.confidence_level || p.confidence || 'HIGH',
    explanation: d.primary_reason || p.explanation || '',
    reasons: d.secondary_reasons || p.reasons || [],
    buyPoint,
    buy_point: buyPoint,
    trend: d.predicted_direction || p.trend || 'STABLE',
    historicalLow: p.historicalLow ?? p.historical_low ?? currentPrice,
    historical_low: p.historicalLow ?? p.historical_low ?? currentPrice,
    historicalHigh: p.historicalHigh ?? p.historical_high ?? currentPrice * 1.2,
    historical_high: p.historicalHigh ?? p.historical_high ?? currentPrice * 1.2,
    lastChecked: p.lastChecked || p.last_checked || d.checked_at || 'Recently',
    last_checked: p.lastChecked || p.last_checked || d.checked_at || 'Recently',
    priceHistory: (p.priceHistory || p.price_history || []).map((pt) => ({
      date: pt.date || pt.observed_at,
      observed_at: pt.observed_at || pt.date,
      collected_at: pt.collected_at,
      price: pt.price,
      shippingCost: pt.shippingCost ?? pt.shipping_cost ?? 0,
      availabilityStatus: pt.availabilityStatus ?? pt.availability_status ?? 'IN_STOCK',
    })),
    price_history: (p.priceHistory || p.price_history || []).map((pt) => ({
      date: pt.date || pt.observed_at,
      observed_at: pt.observed_at || pt.date,
      collected_at: pt.collected_at,
      price: pt.price,
      shippingCost: pt.shippingCost ?? pt.shipping_cost ?? 0,
      availabilityStatus: pt.availabilityStatus ?? pt.availability_status ?? 'IN_STOCK',
    })),
    competitors: p.competitors || [],
    bestOffer: bo && {
      ...bo,
      isReliable: bo.isReliable ?? bo.seller_status === 'RELIABLE',
      inStock: bo.inStock ?? bo.availability === 'IN_STOCK',
    },
    best_offer: bo && {
      ...bo,
      isReliable: bo.isReliable ?? bo.seller_status === 'RELIABLE',
      inStock: bo.inStock ?? bo.availability === 'IN_STOCK',
    },
    decision: d,
  };
}

export async function analyzeProduct(input) {
  if (input && (input.startsWith('http://') || input.startsWith('https://'))) {
    setLastSearchedUrl(input);
  }

  const steps = [
    { message: 'Finding the product...', duration: 150 },
    { message: 'Checking store offers...', duration: 200 },
    { message: 'Checking seller reliability...', duration: 150 },
    { message: 'Looking at recent price trends...', duration: 200 },
    { message: 'Deciding whether to buy or wait...', duration: 150 },
  ];

  return {
    steps,
    execute: async (onStep) => {
      for (let i = 0; i < steps.length; i++) {
        await delay(steps[i].duration);
        if (onStep) onStep(i);
      }
      return findProductFromInput(input);
    },
  };
}

export async function findProductFromInput(input) {
  if (!input) {
    return normalizeProduct(mockProducts[0]);
  }

  const trimmed = input.trim();

  // Try real local backend API first
  try {
    const res = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: trimmed, url: trimmed, product_id: trimmed }),
    });

    if (res.ok) {
      const data = await res.json();
      const norm = normalizeProduct(data);
      if (norm && norm.id) return norm;
    }
  } catch (err) {
    console.warn('Backend /api/analyze request failed, checking fallback', err);
  }

  // Fallback to local resolver if backend is unavailable or mock fallback enabled
  if (ENABLE_MOCK_FALLBACK) {
    if (
      trimmed.startsWith('http://') ||
      trimmed.startsWith('https://') ||
      trimmed.includes('amazon.in') ||
      trimmed.includes('flipkart.com') ||
      trimmed.includes('myntra.com') ||
      trimmed.includes('croma.com')
    ) {
      setLastSearchedUrl(trimmed);
      return normalizeProduct(mockResolveProductByUrl(trimmed));
    }

    const direct = mockGetProductById(trimmed);
    if (direct) return normalizeProduct(direct);

    const results = mockSearchProducts(trimmed);
    if (results.length > 0) return normalizeProduct(results[0]);
  }

  return null;
}

export async function fetchProduct(id) {
  if (!id) return undefined;

  // Try local backend API
  try {
    const res = await fetch(`${API_BASE_URL}/api/products/${encodeURIComponent(id)}`);
    if (res.ok) {
      const data = await res.json();
      return normalizeProduct(data);
    }
  } catch (err) {
    console.warn(`Backend GET /api/products/${id} failed`, err);
  }

  // Fallback mode
  if (ENABLE_MOCK_FALLBACK) {
    if (
      id.startsWith('http://') ||
      id.startsWith('https://') ||
      id.includes('amazon.in') ||
      id.includes('flipkart.com') ||
      id.includes('myntra.com') ||
      id.includes('croma.com')
    ) {
      return normalizeProduct(mockResolveProductByUrl(decodeURIComponent(id)));
    }

    const mockItem = mockGetProductById(id);
    if (mockItem) return normalizeProduct(mockItem);
  }

  return null;
}

export async function fetchSearchResults(query) {
  if (!query) return [];

  try {
    const res = await fetch(`${API_BASE_URL}/api/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query.trim(), limit: 20 }),
    });

    if (res.ok) {
      const data = await res.json();
      if (data && Array.isArray(data.results)) {
        return data.results.map(normalizeProduct);
      }
    }
  } catch (err) {
    console.warn('Backend POST /api/search failed', err);
  }

  if (ENABLE_MOCK_FALLBACK) {
    return mockSearchProducts(query).map(normalizeProduct);
  }

  return [];
}

export async function fetchProductDetails(id) {
  if (!id) return null;

  try {
    const res = await fetch(`${API_BASE_URL}/api/products/${encodeURIComponent(id)}/details`);
    if (res.ok) {
      const data = await res.json();
      return normalizeProduct(data);
    }
  } catch (err) {
    console.warn(`Backend GET /api/products/${id}/details failed`, err);
  }

  return fetchProduct(id);
}

export async function fetchProductPriceHistory(id) {
  if (!id) return [];

  try {
    const res = await fetch(`${API_BASE_URL}/api/products/${encodeURIComponent(id)}/price-history`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn(`Backend GET /api/products/${id}/price-history failed`, err);
  }

  const p = await fetchProduct(id);
  return p ? p.priceHistory : [];
}

export async function fetchWatchlist() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/watchlist`);
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data)) {
        return data.map(normalizeProduct);
      }
    }
  } catch (err) {
    console.warn('Backend GET /api/watchlist failed', err);
  }

  if (ENABLE_MOCK_FALLBACK) {
    return mockGetWatchlist().map(normalizeProduct);
  }
  return [];
}

export async function addToWatchlist(productId, targetPrice) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/watchlist`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: productId, target_price: targetPrice }),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Backend POST /api/watchlist failed', err);
  }
  return { success: true, productId, targetPrice };
}

export async function removeFromWatchlist(productId) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/watchlist/${encodeURIComponent(productId)}`, {
      method: 'DELETE',
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn(`Backend DELETE /api/watchlist/${productId} failed`, err);
  }
  return { success: true, productId };
}

export function resolveProductByUrl(url) {
  return normalizeProduct(mockResolveProductByUrl(url));
}

export { setLastSearchedUrl, getLastSearchedUrl };
