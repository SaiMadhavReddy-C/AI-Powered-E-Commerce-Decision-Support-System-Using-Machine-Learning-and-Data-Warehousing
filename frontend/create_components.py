import os

base_dir = "/Users/sai/.gemini/antigravity/scratch/shopq/frontend/src"
components_dir = os.path.join(base_dir, "components")
utils_dir = os.path.join(base_dir, "utils")

os.makedirs(os.path.join(components_dir, "Layout"), exist_ok=True)
os.makedirs(os.path.join(components_dir, "Search"), exist_ok=True)
os.makedirs(os.path.join(components_dir, "Product"), exist_ok=True)
os.makedirs(os.path.join(components_dir, "Recommendation"), exist_ok=True)
os.makedirs(os.path.join(components_dir, "Price"), exist_ok=True)
os.makedirs(os.path.join(components_dir, "Watchlist"), exist_ok=True)
os.makedirs(os.path.join(components_dir, "Thinking"), exist_ok=True)
os.makedirs(os.path.join(components_dir, "common"), exist_ok=True)
os.makedirs(utils_dir, exist_ok=True)

utils_format_price = """
export const formatPrice = (price) => {
  if (price === undefined || price === null) return '';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(price);
};

export const formatPriceK = (price) => {
    if (price >= 1000) {
        return '₹' + (price / 1000).toFixed(0) + 'K';
    }
    return '₹' + price;
}

export const formatTimeAgo = (timestamp) => {
  if (!timestamp) return '';
  const diff = Date.now() - new Date(timestamp).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'Checked just now';
  if (mins < 60) return `Checked ${mins} min ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `Checked ${hours} hr ago`;
  const days = Math.floor(hours / 24);
  return `Checked ${days} days ago`;
};
"""

utils_constants = """
export const RECOMMENDATION_TYPES = {
  BUY: { color: 'var(--positive)' },
  WAIT: { color: 'var(--warning)' },
  CHANGE: { color: 'var(--warning)' },
  UNCERTAIN: { color: 'var(--neutral)' }
};
"""

files = {
    "utils/formatPrice.js": utils_format_price,
    "utils/constants.js": utils_constants,
    "components/Layout/Navbar.jsx": """import React from 'react';
import { NavLink } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-container container">
        <NavLink to="/" className="navbar-logo">
          Shop<span className="navbar-logo-highlight">Q</span>
        </NavLink>
        <div className="navbar-links">
          <NavLink to="/watchlist" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
            Watchlist
          </NavLink>
          <div className="user-icon-placeholder">
            <span className="user-initial">U</span>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
""",
    "components/Layout/Navbar.css": """.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: var(--background);
  border-bottom: 1px solid var(--border);
  height: 64px;
  display: flex;
  align-items: center;
}

.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.navbar-logo {
  font-size: 24px;
  font-weight: 700;
  color: var(--text);
  text-decoration: none;
}

.navbar-logo-highlight {
  color: var(--accent);
}

.navbar-links {
  display: flex;
  align-items: center;
  gap: 24px;
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  font-size: 15px;
  transition: color 0.2s ease;
}

.nav-link:hover, .nav-link.active {
  color: var(--accent);
}

.user-icon-placeholder {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--accent-light);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent);
  font-weight: 600;
  font-size: 14px;
}
""",
    "components/Layout/PageContainer.jsx": """import React from 'react';
import Navbar from './Navbar';

const PageContainer = ({ children }) => {
  return (
    <div className="page-wrapper fade-in" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <main className="container" style={{ padding: '32px 16px', flex: 1 }}>
        {children}
      </main>
    </div>
  );
};

export default PageContainer;
""",
    "components/Search/SearchBar.jsx": """import React, { useState } from 'react';
import './SearchBar.css';

const SearchBar = ({ onSubmit }) => {
  const [query, setQuery] = useState('');
  const [detectedRetailer, setDetectedRetailer] = useState('');

  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    
    if (value.includes('amazon.in')) setDetectedRetailer('Amazon India');
    else if (value.includes('flipkart.com')) setDetectedRetailer('Flipkart');
    else if (value.includes('croma.com')) setDetectedRetailer('Croma');
    else if (value.includes('myntra.com')) setDetectedRetailer('Myntra');
    else setDetectedRetailer('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && onSubmit) {
      onSubmit(query.trim());
    }
  };

  return (
    <div className="search-bar-container">
      <form className="search-form" onSubmit={handleSubmit}>
        <div className="search-input-wrapper">
          <input
            type="text"
            className="search-input"
            placeholder="Paste a product link or search for a product"
            value={query}
            onChange={handleInputChange}
          />
          <button type="submit" className="search-button">
            Check with ShopQ
          </button>
        </div>
      </form>
      {detectedRetailer && (
        <div className="detected-retailer fade-in">
          Looking up on {detectedRetailer}...
        </div>
      )}
    </div>
  );
};

export default SearchBar;
""",
    "components/Search/SearchBar.css": """.search-bar-container {
  width: 100%;
  max-width: 720px;
  margin: 0 auto;
}

.search-input-wrapper {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 16px 20px;
  font-size: 18px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background-color: var(--card);
  color: var(--text);
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.search-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-light);
}

.search-input::placeholder {
  color: var(--text-secondary);
}

.search-button {
  padding: 16px 24px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  background-color: var(--accent);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  white-space: nowrap;
  transition: background-color 0.2s ease;
}

.search-button:hover {
  background-color: var(--accent-hover);
}

.detected-retailer {
  margin-top: 12px;
  font-size: 14px;
  color: var(--text-secondary);
  text-align: left;
  padding-left: 20px;
}

@media (max-width: 600px) {
  .search-input-wrapper {
    flex-direction: column;
  }
  .search-button {
    width: 100%;
  }
}
""",
    "components/Search/SearchResults.jsx": """import React from 'react';
import { Link } from 'react-router-dom';
import { formatPrice } from '../../utils/formatPrice';
import './SearchResults.css';

const SearchResults = ({ results }) => {
  if (!results || results.length === 0) return null;

  return (
    <div className="search-results-list fade-in">
      {results.map((result, index) => (
        <Link to={`/analyze/${result.id}`} key={result.id || index} className="search-result-item">
          <div className="result-info">
            <h3 className="result-name">{result.name}</h3>
            <span className="result-category">{result.category}</span>
          </div>
          <div className="result-price-info">
            <span className="result-price">From {formatPrice(result.startingPrice)}</span>
            {result.trend && (
              <span className={`result-trend trend-${result.trend.direction}`}>
                {result.trend.direction === 'down' ? '↓ Falling' : '↑ Rising'}
              </span>
            )}
          </div>
        </Link>
      ))}
    </div>
  );
};

export default SearchResults;
""",
    "components/Search/SearchResults.css": """.search-results-list {
  display: flex;
  flex-direction: column;
  border-top: 1px solid var(--border);
  margin-top: 24px;
}

.search-result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid var(--border);
  text-decoration: none;
  color: inherit;
  transition: opacity 0.2s ease;
}

.search-result-item:hover {
  opacity: 0.7;
}

.result-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.result-name {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: var(--text);
}

.result-category {
  font-size: 14px;
  color: var(--text-secondary);
}

.result-price-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.result-price {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
}

.result-trend {
  font-size: 13px;
  font-weight: 500;
}

.trend-down {
  color: var(--positive);
}

.trend-up {
  color: var(--danger);
}
""",
    "components/Product/ProductHeader.jsx": """import React from 'react';
import { formatPrice, formatTimeAgo } from '../../utils/formatPrice';
import './ProductHeader.css';

const ProductHeader = ({ product }) => {
  if (!product) return null;

  return (
    <div className="product-header">
      <img src={product.imageUrl || 'https://via.placeholder.com/120'} alt={product.name} className="product-image" />
      <div className="product-header-details">
        <h1 className="product-name">{product.name}</h1>
        <div className="product-meta">
          {product.brand && <span>{product.brand}</span>}
          {product.brand && product.category && <span> · </span>}
          {product.category && <span>{product.category}</span>}
          {product.category && product.variant && <span> · </span>}
          {product.variant && <span>{product.variant}</span>}
        </div>
        <div className="product-price-row">
          <span className="product-price">{formatPrice(product.currentPrice)}</span>
          <span className="product-timestamp">{formatTimeAgo(product.lastChecked)}</span>
        </div>
      </div>
    </div>
  );
};

export default ProductHeader;
""",
    "components/Product/ProductHeader.css": """.product-header {
  display: flex;
  align-items: flex-start;
  gap: 24px;
  padding: 24px 0;
}

.product-image {
  width: 120px;
  height: 120px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid var(--border);
  background-color: white;
}

.product-header-details {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.product-name {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text);
  line-height: 1.3;
}

.product-meta {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.product-price-row {
  display: flex;
  align-items: baseline;
  gap: 16px;
}

.product-price {
  font-size: 28px;
  font-weight: 700;
  color: var(--text);
}

.product-timestamp {
  font-size: 13px;
  color: var(--text-secondary);
}

@media (max-width: 600px) {
  .product-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .product-price-row {
    justify-content: center;
  }
}
""",
    "components/Recommendation/RecommendationCard.jsx": """import React from 'react';
import { formatPrice, formatTimeAgo } from '../../utils/formatPrice';
import './RecommendationCard.css';

const RecommendationCard = ({ product }) => {
  if (!product || !product.recommendation) return null;
  const { type, label, message, explanation, confidence, emoji, targetPrice, buyUrl, bestOffer } = product.recommendation;

  const getTypeClass = () => {
    switch(type) {
      case 'WAIT': return 'rec-type-wait';
      case 'BUY': return 'rec-type-buy';
      case 'CHANGE': return 'rec-type-change';
      default: return 'rec-type-uncertain';
    }
  };

  return (
    <div className={`recommendation-card slide-up ${getTypeClass()}`}>
      <div className="rec-badge-section">
        <div className="rec-emoji">{emoji || '🤔'}</div>
        <div className="rec-label">{label}</div>
        <div className="rec-timestamp">{formatTimeAgo(product.lastChecked)}</div>
      </div>
      
      <div className="rec-content">
        <h2 className="rec-message">{message}</h2>
        <p className="rec-explanation">{explanation}</p>
        <p className="rec-confidence">{confidence}</p>
        
        <div className="rec-action">
          {type === 'WAIT' && targetPrice && (
            <div className="rec-wait-action">
              <p>I'd reconsider around {formatPrice(targetPrice)}.</p>
              <button className="btn-secondary">Watch until {formatPrice(targetPrice)}</button>
            </div>
          )}
          
          {type === 'BUY' && buyUrl && (
            <a href={buyUrl} className="btn-primary rec-buy-btn" target="_blank" rel="noopener noreferrer">
              Buy at {formatPrice(product.currentPrice)} →
            </a>
          )}
          
          {type === 'CHANGE' && bestOffer && (
            <div className="rec-change-action">
              <p>Better offer found on {bestOffer.retailer}.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RecommendationCard;
""",
    "components/Recommendation/RecommendationCard.css": """.recommendation-card {
  background-color: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 24px;
}

.rec-type-wait .rec-label { color: var(--warning); }
.rec-type-buy .rec-label { color: var(--positive); }
.rec-type-change .rec-label { color: var(--warning); }
.rec-type-uncertain .rec-label { color: var(--neutral); }

.rec-badge-section {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.rec-emoji {
  font-size: 40px;
  margin-bottom: 8px;
}

.rec-label {
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.rec-timestamp {
  font-size: 12px;
  color: var(--text-secondary);
}

.rec-content {
  text-align: center;
}

.rec-message {
  font-size: 22px;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 16px 0;
  line-height: 1.4;
}

.rec-explanation {
  font-size: 16px;
  color: var(--text);
  margin: 0 0 8px 0;
  line-height: 1.5;
}

.rec-confidence {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 24px 0;
}

.rec-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.rec-wait-action p {
  margin: 0 0 12px 0;
  font-size: 15px;
  font-weight: 500;
}

.btn-secondary {
  padding: 12px 20px;
  background-color: transparent;
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  font-weight: 500;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background-color: var(--background);
  border-color: var(--text-secondary);
}

.btn-primary {
  padding: 14px 24px;
  background-color: var(--accent);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
  display: inline-block;
}

.btn-primary:hover {
  background-color: var(--accent-hover);
}
""",
    "components/Recommendation/WhyPanel.jsx": """import React, { useState } from 'react';
import './WhyPanel.css';

const WhyPanel = ({ reasons, recommendationLabel }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!reasons || reasons.length === 0) return null;

  return (
    <div className="why-panel">
      <button className="why-toggle" onClick={() => setIsOpen(!isOpen)}>
        Why I said this {isOpen ? '↑' : '↓'}
      </button>
      
      {isOpen && (
        <div className="why-content slide-up">
          <ul className="why-list">
            {reasons.map((reason, idx) => (
              <li key={idx} className="why-item">
                <span className="why-icon">✓</span>
                <span className="why-text">{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default WhyPanel;
""",
    "components/Recommendation/WhyPanel.css": """.why-panel {
  margin-bottom: 32px;
  border-top: 1px solid var(--border);
  padding-top: 16px;
}

.why-toggle {
  background: none;
  border: none;
  color: var(--accent);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  padding: 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.why-toggle:hover {
  text-decoration: underline;
}

.why-content {
  margin-top: 16px;
  padding: 20px;
  background-color: var(--background);
  border-radius: 8px;
  border: 1px solid var(--border);
}

.why-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.why-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.why-icon {
  color: var(--positive);
  font-weight: bold;
}

.why-text {
  font-size: 15px;
  color: var(--text);
  line-height: 1.4;
}
""",
    "components/Recommendation/BestOption.jsx": """import React from 'react';
import { formatPrice } from '../../utils/formatPrice';
import './BestOption.css';

const BestOption = ({ bestOffer, currentPrice, onCompareClick }) => {
  if (!bestOffer) return null;

  const savings = currentPrice - bestOffer.price;

  return (
    <div className="best-option">
      <h3 className="best-option-title">Best option I found</h3>
      <div className="best-option-card">
        <div className="best-option-details">
          <div className="best-option-price">{formatPrice(bestOffer.price)}</div>
          <div className="best-option-retailer">{bestOffer.retailer}</div>
          <div className="best-option-badges">
            {bestOffer.isReliable && <span className="badge-reliable">🛡️ Looks reliable</span>}
            {bestOffer.inStock && <span className="badge-stock">In stock</span>}
          </div>
        </div>
        <div className="best-option-actions">
          <a href={bestOffer.url} target="_blank" rel="noopener noreferrer" className="btn-secondary">
            View offer →
          </a>
        </div>
      </div>
      
      {savings > 0 && (
        <div className="best-option-savings">
          That's {formatPrice(savings)} less.
        </div>
      )}
      
      <button className="compare-link" onClick={onCompareClick}>
        Compare all stores →
      </button>
    </div>
  );
};

export default BestOption;
""",
    "components/Recommendation/BestOption.css": """.best-option {
  margin-bottom: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
}

.best-option-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 16px 0;
}

.best-option-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background-color: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 12px;
}

.best-option-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.best-option-price {
  font-size: 24px;
  font-weight: 700;
  color: var(--text);
}

.best-option-retailer {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-secondary);
}

.best-option-badges {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.badge-reliable, .badge-stock {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  background-color: var(--background);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.best-option-savings {
  font-size: 14px;
  color: var(--positive);
  font-weight: 500;
  margin-bottom: 16px;
}

.compare-link {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  padding: 0;
}

.compare-link:hover {
  color: var(--accent);
  text-decoration: underline;
}

@media (max-width: 500px) {
  .best-option-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  .best-option-actions {
    width: 100%;
  }
  .btn-secondary {
    width: 100%;
    text-align: center;
  }
}
""",
    "components/Price/PriceSummary.jsx": """import React from 'react';
import { formatPrice } from '../../utils/formatPrice';
import './PriceSummary.css';

const PriceSummary = ({ trend, currentPrice, historicalLow, onViewHistory }) => {
  return (
    <div className="price-summary">
      <h3 className="price-summary-title">Price lately</h3>
      <div className="price-summary-row">
        <div className="price-summary-current">
          <span className="price-summary-label">Currently</span>
          <span className="price-summary-val">{formatPrice(currentPrice)}</span>
        </div>
        
        {trend && (
          <div className="price-summary-trend">
            <span className={`trend-badge ${trend.direction === 'down' ? 'trend-good' : 'trend-bad'}`}>
              {trend.direction === 'down' ? '↓ Falling' : '↑ Rising'}
            </span>
          </div>
        )}
      </div>
      
      {historicalLow && (
        <div className="price-summary-low">
          Lowest recently: {formatPrice(historicalLow)}
        </div>
      )}
      
      {onViewHistory && (
        <button className="view-history-link" onClick={onViewHistory}>
          View price history →
        </button>
      )}
    </div>
  );
};

export default PriceSummary;
""",
    "components/Price/PriceSummary.css": """.price-summary {
  padding: 24px 0;
  border-top: 1px solid var(--border);
  margin-bottom: 24px;
}

.price-summary-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px 0;
}

.price-summary-row {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 12px;
}

.price-summary-current {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.price-summary-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.price-summary-val {
  font-size: 20px;
  font-weight: 600;
}

.trend-badge {
  font-size: 13px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
}

.trend-good {
  background-color: var(--positive-light);
  color: var(--positive);
}

.trend-bad {
  background-color: var(--danger-light);
  color: var(--danger);
}

.price-summary-low {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.view-history-link {
  background: none;
  border: none;
  color: var(--accent);
  font-size: 14px;
  cursor: pointer;
  padding: 0;
}

.view-history-link:hover {
  text-decoration: underline;
}
""",
    "components/Price/PriceChart.jsx": """import React, { useState, useRef } from 'react';
import { formatPriceK, formatPrice } from '../../utils/formatPrice';
import './PriceChart.css';

const PriceChart = ({ priceHistory, buyPoint, currentPrice }) => {
  const [tooltip, setTooltip] = useState(null);
  const svgRef = useRef(null);

  if (!priceHistory || priceHistory.length < 2) return null;

  const width = 600;
  const height = 240;
  const padding = { top: 20, right: 20, bottom: 30, left: 50 };
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;

  const prices = priceHistory.map(d => d.price);
  if (buyPoint) prices.push(buyPoint);
  const minPrice = Math.min(...prices) * 0.95;
  const maxPrice = Math.max(...prices) * 1.05;
  
  const minDate = new Date(priceHistory[0].date).getTime();
  const maxDate = new Date(priceHistory[priceHistory.length - 1].date).getTime();

  const getX = (dateStr) => {
    const time = new Date(dateStr).getTime();
    return padding.left + ((time - minDate) / (maxDate - minDate)) * innerWidth;
  };

  const getY = (price) => {
    return padding.top + innerHeight - ((price - minPrice) / (maxPrice - minPrice)) * innerHeight;
  };

  // Path generation
  const d = priceHistory.map((pt, i) => `${i === 0 ? 'M' : 'L'} ${getX(pt.date)} ${getY(pt.price)}`).join(' ');
  const areaD = `${d} L ${getX(priceHistory[priceHistory.length-1].date)} ${height - padding.bottom} L ${padding.left} ${height - padding.bottom} Z`;

  const handleMouseMove = (e) => {
    if (!svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    
    if (x < padding.left || x > width - padding.right) {
      setTooltip(null);
      return;
    }
    
    const ratio = (x - padding.left) / innerWidth;
    const time = minDate + ratio * (maxDate - minDate);
    
    // Find closest point
    let closest = priceHistory[0];
    let minDist = Math.abs(new Date(closest.date).getTime() - time);
    
    for (const pt of priceHistory) {
      const dist = Math.abs(new Date(pt.date).getTime() - time);
      if (dist < minDist) {
        minDist = dist;
        closest = pt;
      }
    }
    
    setTooltip({
      x: getX(closest.date),
      y: getY(closest.price),
      date: new Date(closest.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }),
      price: closest.price
    });
  };

  return (
    <div className="price-chart-container">
      <svg 
        ref={svgRef}
        viewBox={`0 0 ${width} ${height}`} 
        className="price-chart-svg"
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setTooltip(null)}
      >
        {/* Y Axis Grid & Labels */}
        {[0, 0.5, 1].map(tick => {
          const p = minPrice + (maxPrice - minPrice) * tick;
          const y = getY(p);
          return (
            <g key={tick}>
              <line x1={padding.left} y1={y} x2={width - padding.right} y2={y} stroke="var(--border)" opacity="0.3" />
              <text x={padding.left - 10} y={y + 4} textAnchor="end" fontSize="11" fill="var(--text-secondary)">
                {formatPriceK(p)}
              </text>
            </g>
          );
        })}

        {/* X Axis Line */}
        <line x1={padding.left} y1={height - padding.bottom} x2={width - padding.right} y2={height - padding.bottom} stroke="var(--border)" />
        
        {/* X Axis Labels (every 15 days roughly) */}
        {priceHistory.filter((_, i) => i % Math.ceil(priceHistory.length / 5) === 0).map((pt, i) => (
          <text key={i} x={getX(pt.date)} y={height - padding.bottom + 15} textAnchor="middle" fontSize="11" fill="var(--text-secondary)">
             {new Date(pt.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
          </text>
        ))}

        {/* Area */}
        <path d={areaD} fill="var(--accent-light)" opacity="0.4" />
        
        {/* Line */}
        <path d={d} fill="none" stroke="var(--text)" strokeWidth="2" />

        {/* Buy Point Line */}
        {buyPoint && (
          <line 
            x1={padding.left} y1={getY(buyPoint)} 
            x2={width - padding.right} y2={getY(buyPoint)} 
            stroke="var(--positive)" strokeWidth="1" strokeDasharray="4 4" 
          />
        )}

        {/* Last Point */}
        <circle cx={getX(priceHistory[priceHistory.length-1].date)} cy={getY(priceHistory[priceHistory.length-1].price)} r="4" fill="var(--accent)" />

        {/* Tooltip */}
        {tooltip && (
          <g>
            <line x1={tooltip.x} y1={padding.top} x2={tooltip.x} y2={height - padding.bottom} stroke="var(--accent)" strokeDasharray="2 2" opacity="0.5" />
            <circle cx={tooltip.x} cy={tooltip.y} r="5" fill="white" stroke="var(--accent)" strokeWidth="2" />
            <rect x={tooltip.x > width/2 ? tooltip.x - 100 : tooltip.x + 10} y={tooltip.y - 40} width="90" height="40" rx="4" fill="white" stroke="var(--border)" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.1))" />
            <text x={tooltip.x > width/2 ? tooltip.x - 55 : tooltip.x + 55} y={tooltip.y - 24} textAnchor="middle" fontSize="12" fontWeight="600" fill="var(--text)">
              {formatPrice(tooltip.price)}
            </text>
            <text x={tooltip.x > width/2 ? tooltip.x - 55 : tooltip.x + 55} y={tooltip.y - 10} textAnchor="middle" fontSize="10" fill="var(--text-secondary)">
              {tooltip.date}
            </text>
          </g>
        )}
      </svg>
    </div>
  );
};

export default PriceChart;
""",
    "components/Price/PriceChart.css": """.price-chart-container {
  width: 100%;
  margin: 24px 0;
  background: var(--card);
  border-radius: 8px;
  border: 1px solid var(--border);
  padding: 16px;
  overflow: hidden;
}

.price-chart-svg {
  width: 100%;
  height: auto;
  display: block;
}
""",
    "components/Price/RetailerComparison.jsx": """import React from 'react';
import { formatPrice } from '../../utils/formatPrice';
import './RetailerComparison.css';

const RetailerComparison = ({ competitors }) => {
  if (!competitors || competitors.length === 0) return null;

  // Find lowest price
  const lowestPrice = Math.min(...competitors.map(c => c.price));

  return (
    <div className="retailer-comparison">
      <h3 className="retailer-comparison-title">Compare stores</h3>
      <div className="retailer-table-container">
        <table className="retailer-table">
          <thead>
            <tr>
              <th>Store</th>
              <th>Price</th>
              <th>Seller & Reliability</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {competitors.map((comp, idx) => (
              <tr key={idx} className={comp.price === lowestPrice ? 'best-price-row' : ''}>
                <td>
                  <div className="retailer-name-cell">
                    <span className="retailer-dot"></span>
                    {comp.retailer}
                  </div>
                </td>
                <td className="price-cell">
                  {formatPrice(comp.price)}
                </td>
                <td>
                  <div className="seller-cell">
                    <span className="seller-name">{comp.seller}</span>
                    <span className={`reliability-badge ${comp.isReliable ? 'rel-good' : 'rel-warn'}`}>
                      {comp.isReliable ? 'Looks reliable' : 'Check seller'}
                    </span>
                  </div>
                </td>
                <td className="action-cell">
                  <a href={comp.url} target="_blank" rel="noopener noreferrer" className="view-link">
                    View →
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default RetailerComparison;
""",
    "components/Price/RetailerComparison.css": """.retailer-comparison {
  margin: 32px 0;
}

.retailer-comparison-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 16px 0;
}

.retailer-table-container {
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: 8px;
  background-color: var(--card);
}

.retailer-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.retailer-table th, .retailer-table td {
  padding: 16px;
  border-bottom: 1px solid var(--border);
}

.retailer-table th {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  background-color: var(--background);
}

.retailer-table tr:last-child td {
  border-bottom: none;
}

.best-price-row {
  background-color: var(--positive-light);
}

.retailer-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.retailer-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--text-secondary);
}

.best-price-row .retailer-dot {
  background-color: var(--positive);
}

.price-cell {
  font-weight: 600;
  font-size: 15px;
}

.seller-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.seller-name {
  font-size: 14px;
}

.reliability-badge {
  font-size: 12px;
  display: inline-block;
  padding: 2px 6px;
  border-radius: 4px;
  width: max-content;
}

.rel-good {
  background-color: rgba(45, 138, 86, 0.1);
  color: var(--positive);
}

.rel-warn {
  background-color: rgba(196, 138, 26, 0.1);
  color: var(--warning);
}

.view-link {
  color: var(--accent);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}

.view-link:hover {
  text-decoration: underline;
}
""",
    "components/Watchlist/WatchButton.jsx": """import React, { useState } from 'react';
import { formatPrice } from '../../utils/formatPrice';
import './WatchButton.css';

const WatchButton = ({ targetPrice, productName, initialWatching = false }) => {
  const [isWatching, setIsWatching] = useState(initialWatching);

  const toggleWatch = () => {
    setIsWatching(!isWatching);
  };

  return (
    <div className="watch-button-container">
      <button 
        className={`watch-btn ${isWatching ? 'is-watching' : ''}`}
        onClick={toggleWatch}
      >
        {isWatching ? '✓ Watching' : targetPrice ? `👀 Watch until ${formatPrice(targetPrice)}` : '👀 Watch this'}
      </button>
      
      {isWatching && (
        <p className="watch-subtext">
          I'll let you know when the price reaches a good buying point.
        </p>
      )}
    </div>
  );
};

export default WatchButton;
""",
    "components/Watchlist/WatchButton.css": """.watch-button-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  margin: 24px 0;
}

.watch-btn {
  padding: 12px 20px;
  background-color: transparent;
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  font-weight: 500;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.watch-btn:hover:not(.is-watching) {
  background-color: var(--background);
  border-color: var(--text-secondary);
}

.is-watching {
  background-color: var(--background);
  color: var(--text-secondary);
  border-color: var(--border);
}

.watch-subtext {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
}
""",
    "components/Watchlist/WatchlistCard.jsx": """import React from 'react';
import { useNavigate } from 'react-router-dom';
import { formatPrice } from '../../utils/formatPrice';
import './WatchlistCard.css';

const WatchlistCard = ({ product }) => {
  const navigate = useNavigate();
  if (!product) return null;

  const getStatusDisplay = (status) => {
    switch(status) {
      case 'waiting': return { icon: '⏳', text: 'Waiting for a better price', class: 'status-waiting' };
      case 'dropped': return { icon: '🔥', text: 'Price dropped', class: 'status-dropped' };
      case 'good': return { icon: '🟢', text: 'Good time to buy', class: 'status-good' };
      default: return { icon: '👀', text: 'Watching', class: 'status-neutral' };
    }
  };

  const statusInfo = getStatusDisplay(product.watchStatus);

  return (
    <div className="watchlist-card" onClick={() => navigate(`/analyze/${product.id}`)}>
      <div className="watchlist-card-content">
        <h3 className="watchlist-title">{product.name}</h3>
        <div className="watchlist-price">{formatPrice(product.currentPrice)}</div>
        
        <div className={`watchlist-status ${statusInfo.class}`}>
          <span className="status-icon">{statusInfo.icon}</span>
          <span>{statusInfo.text}</span>
        </div>
        
        {product.targetPrice && (
          <div className="watchlist-target">
            Target: {formatPrice(product.targetPrice)}
          </div>
        )}
      </div>
      
      <div className="watchlist-actions">
        <button className="btn-secondary btn-sm" onClick={(e) => { e.stopPropagation(); navigate(`/analyze/${product.id}`); }}>
          Check now
        </button>
        <button className="link-danger" onClick={(e) => { e.stopPropagation(); }}>
          Stop watching
        </button>
      </div>
    </div>
  );
};

export default WatchlistCard;
""",
    "components/Watchlist/WatchlistCard.css": """.watchlist-card {
  background-color: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.watchlist-card:hover {
  border-color: var(--text-secondary);
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

.watchlist-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  line-height: 1.4;
}

.watchlist-price {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 12px;
}

.watchlist-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 6px;
  margin-bottom: 8px;
  width: max-content;
}

.status-waiting { background: var(--warning-light); color: var(--warning); }
.status-dropped, .status-good { background: var(--positive-light); color: var(--positive); }
.status-neutral { background: var(--background); color: var(--text-secondary); }

.watchlist-target {
  font-size: 13px;
  color: var(--text-secondary);
}

.watchlist-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

.btn-sm {
  padding: 8px 16px;
  font-size: 13px;
}

.link-danger {
  background: none;
  border: none;
  color: var(--danger);
  font-size: 13px;
  cursor: pointer;
}

.link-danger:hover {
  text-decoration: underline;
}
""",
    "components/Thinking/ThinkingScreen.jsx": """import React from 'react';
import './ThinkingScreen.css';

const ThinkingScreen = ({ productName, steps, currentStep, complete }) => {
  return (
    <div className="thinking-screen fade-in">
      <h2 className="thinking-title">
        {complete ? "I've got it." : `Checking ${productName}...`}
      </h2>
      
      <div className="thinking-steps">
        {steps.map((step, idx) => {
          const isComplete = complete || idx < currentStep;
          const isActive = !complete && idx === currentStep;
          const isPending = !complete && idx > currentStep;
          
          return (
            <div key={idx} className={`thinking-step ${isComplete ? 'step-complete' : ''} ${isActive ? 'step-active' : ''} ${isPending ? 'step-pending' : ''}`}>
              <div className="step-icon">
                {isComplete && <span className="icon-check">✓</span>}
                {isActive && <span className="icon-pulse"></span>}
              </div>
              <span className="step-text">{step}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ThinkingScreen;
""",
    "components/Thinking/ThinkingScreen.css": """.thinking-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  padding: 40px 20px;
  text-align: center;
}

.thinking-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 40px;
  transition: opacity 0.3s ease;
}

.thinking-steps {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 20px;
  width: 100%;
  max-width: 300px;
}

.thinking-step {
  display: flex;
  align-items: center;
  gap: 16px;
  transition: opacity 0.3s ease;
}

.step-pending {
  opacity: 0.3;
}

.step-active {
  opacity: 1;
}

.step-complete {
  opacity: 0.7;
}

.step-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-check {
  color: var(--positive);
  font-weight: bold;
  font-size: 16px;
  animation: fadeIn 0.3s ease;
}

.icon-pulse {
  width: 8px;
  height: 8px;
  background-color: var(--accent);
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

.step-text {
  font-size: 16px;
  color: var(--text);
  font-weight: 500;
}

@keyframes pulse {
  0% { transform: scale(0.8); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(0.8); opacity: 0.5; }
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}
""",
    "components/common/EmptyState.jsx": """import React from 'react';

const EmptyState = ({ emoji, title, description, actionLabel, onAction }) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '64px 20px',
      textAlign: 'center'
    }} className="fade-in">
      <div style={{ fontSize: '48px', marginBottom: '24px' }}>{emoji || '🤔'}</div>
      <h2 style={{ fontSize: '20px', margin: '0 0 12px 0', color: 'var(--text)' }}>{title}</h2>
      <p style={{ fontSize: '15px', color: 'var(--text-secondary)', margin: '0 0 24px 0', maxWidth: '400px' }}>
        {description}
      </p>
      {actionLabel && onAction && (
        <button 
          onClick={onAction}
          style={{
            padding: '12px 24px',
            backgroundColor: 'transparent',
            border: '1px solid var(--border)',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '15px',
            fontWeight: '500'
          }}
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
};

export default EmptyState;
""",
    "components/Recommendation/SellerInfo.jsx": """import React, { useState } from 'react';
import './SellerInfo.css';

const SellerInfo = ({ seller }) => {
  const [expanded, setExpanded] = useState(false);

  if (!seller) return null;

  return (
    <div className="seller-info">
      <div className="seller-header" onClick={() => setExpanded(!expanded)}>
        <div className="seller-title-row">
          <span className="seller-shield">🛡️</span>
          <span className="seller-name-label">Seller: {seller.name}</span>
          <span className="seller-status">{seller.reliability || 'Looks reliable'}</span>
        </div>
        <button className="expand-btn">{expanded ? '−' : '+'}</button>
      </div>
      
      {expanded && (
        <div className="seller-details slide-up">
          <div className="detail-item">
            <span className="detail-label">Rating:</span>
            <span className="detail-value">{seller.rating} ({seller.reviewCount} reviews)</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Returns:</span>
            <span className="detail-value">{seller.returnPolicy}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Warranty:</span>
            <span className="detail-value">{seller.warranty}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default SellerInfo;
""",
    "components/Recommendation/SellerInfo.css": """.seller-info {
  border: 1px solid var(--border);
  border-radius: 8px;
  background-color: var(--background);
  margin: 16px 0;
  overflow: hidden;
}

.seller-header {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.seller-header:hover {
  background-color: var(--card);
}

.seller-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.seller-name-label {
  font-weight: 500;
  font-size: 14px;
}

.seller-status {
  font-size: 12px;
  color: var(--positive);
  background-color: var(--positive-light);
  padding: 2px 8px;
  border-radius: 12px;
}

.expand-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: var(--text-secondary);
  cursor: pointer;
}

.seller-details {
  padding: 0 16px 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-top: 1px solid var(--border);
  margin-top: 8px;
  padding-top: 16px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.detail-label {
  color: var(--text-secondary);
}

.detail-value {
  font-weight: 500;
  color: var(--text);
}
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    with open(full_path, "w") as f:
        f.write(content)

print("All components created successfully.")
