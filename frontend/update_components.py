import os

base_dir = "/Users/sai/.gemini/antigravity/scratch/shopq/frontend/src"
components_dir = os.path.join(base_dir, "components")
utils_dir = os.path.join(base_dir, "utils")

utils_constants = """
export const RECOMMENDATION_TYPES = {
  BUY: { label: 'BUY IT', message: "I'd buy this one.", type: 'BUY', emoji: '👍', color: 'var(--positive)' },
  WAIT: { label: 'WAIT A LITTLE', message: "I'd hold off for now.", type: 'WAIT', emoji: '⏳', color: 'var(--warning)' },
  CHANGE: { label: 'CHECK ALT', message: "I found a better option.", type: 'CHANGE', emoji: '🔍', color: 'var(--warning)' },
  UNCERTAIN: { label: 'YOUR CALL', message: "There's no clear winner here.", type: 'UNCERTAIN', emoji: '🤔', color: 'var(--neutral)' }
};

export const CONFIDENCE_LEVELS = {
  HIGH: "I'm pretty confident. 👍",
  MEDIUM: "I'm somewhat confident.",
  LOW: "Take this with a grain of salt."
};

export const TREND_TYPES = {
  FALLING: 'FALLING',
  RISING: 'RISING',
  STABLE: 'STABLE'
};
"""

files = {
    "utils/constants.js": utils_constants,
    "components/Search/SearchResults.jsx": """import React from 'react';
import { Link } from 'react-router-dom';
import { formatPrice } from '../../utils/formatPrice';
import './SearchResults.css';

const SearchResults = ({ results, onSelect }) => {
  if (!results || results.length === 0) return null;

  return (
    <div className="search-results-list fade-in">
      {results.map((result, index) => (
        <div key={result.id || index} className="search-result-item" onClick={() => { if(onSelect) onSelect(result); }}>
          {onSelect ? (
            <div className="result-content">
              <div className="result-info">
                <h3 className="result-name">{result.name}</h3>
                <span className="result-category">{result.category}</span>
              </div>
              <div className="result-price-info">
                <span className="result-price">From {formatPrice(result.currentPrice)}</span>
                {result.trend && (
                  <span className={`result-trend trend-${result.trend.toLowerCase()}`}>
                    {result.trend === 'FALLING' ? '↓ Falling' : result.trend === 'RISING' ? '↑ Rising' : ''}
                  </span>
                )}
              </div>
            </div>
          ) : (
            <Link to={`/analyze/${result.id}`} className="result-content">
              <div className="result-info">
                <h3 className="result-name">{result.name}</h3>
                <span className="result-category">{result.category}</span>
              </div>
              <div className="result-price-info">
                <span className="result-price">From {formatPrice(result.currentPrice)}</span>
                {result.trend && (
                  <span className={`result-trend trend-${result.trend.toLowerCase()}`}>
                    {result.trend === 'FALLING' ? '↓ Falling' : result.trend === 'RISING' ? '↑ Rising' : ''}
                  </span>
                )}
              </div>
            </Link>
          )}
        </div>
      ))}
    </div>
  );
};

export default SearchResults;
""",
    "components/Product/ProductHeader.jsx": """import React from 'react';
import { formatPrice, formatTimeAgo } from '../../utils/formatPrice';
import './ProductHeader.css';

const ProductHeader = ({ product }) => {
  if (!product) return null;

  return (
    <div className="product-header">
      <img src={product.image || 'https://via.placeholder.com/120'} alt={product.name} className="product-image" />
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
    "components/Recommendation/RecommendationCard.jsx": """import React from 'react';
import { formatPrice, formatTimeAgo } from '../../utils/formatPrice';
import { RECOMMENDATION_TYPES, CONFIDENCE_LEVELS } from '../../utils/constants';
import './RecommendationCard.css';

const RecommendationCard = ({ product }) => {
  if (!product || !product.recommendation) return null;
  const recData = RECOMMENDATION_TYPES[product.recommendation] || RECOMMENDATION_TYPES.UNCERTAIN;
  const confText = CONFIDENCE_LEVELS[product.confidence] || product.confidence;

  const getTypeClass = () => {
    switch(recData.type) {
      case 'WAIT': return 'rec-type-wait';
      case 'BUY': return 'rec-type-buy';
      case 'CHANGE': return 'rec-type-change';
      default: return 'rec-type-uncertain';
    }
  };

  return (
    <div className={`recommendation-card slide-up ${getTypeClass()}`}>
      <div className="rec-badge-section">
        <div className="rec-emoji">{recData.emoji}</div>
        <div className="rec-label">{recData.label}</div>
        <div className="rec-timestamp">{formatTimeAgo(product.lastChecked)}</div>
      </div>
      
      <div className="rec-content">
        <h2 className="rec-message">{recData.message}</h2>
        <p className="rec-explanation">{product.explanation}</p>
        <p className="rec-confidence">{confText}</p>
        
        <div className="rec-action">
          {recData.type === 'WAIT' && product.buyPoint && (
            <div className="rec-wait-action">
              <p>I'd reconsider around {formatPrice(product.buyPoint)}.</p>
              <button className="btn-secondary">Watch until {formatPrice(product.buyPoint)}</button>
            </div>
          )}
          
          {recData.type === 'BUY' && product.retailerUrl && (
            <a href={product.retailerUrl} className="btn-primary rec-buy-btn" target="_blank" rel="noopener noreferrer">
              Buy at {formatPrice(product.currentPrice)} →
            </a>
          )}
          
          {recData.type === 'CHANGE' && product.bestOffer && (
            <div className="rec-change-action">
              <p>Better offer found on {product.bestOffer.retailer}.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RecommendationCard;
""",
    "components/Watchlist/WatchlistCard.jsx": """import React from 'react';
import { useNavigate } from 'react-router-dom';
import { formatPrice } from '../../utils/formatPrice';
import './WatchlistCard.css';

const WatchlistCard = ({ product }) => {
  const navigate = useNavigate();
  if (!product) return null;

  const statusInfo = product.watchStatus || { icon: '👀', message: 'Watching', type: 'neutral' };
  
  const statusClass = `status-${statusInfo.type}`;

  return (
    <div className="watchlist-card" onClick={() => navigate(`/analyze/${product.id}`)}>
      <div className="watchlist-card-content">
        <h3 className="watchlist-title">{product.name}</h3>
        <div className="watchlist-price">{formatPrice(product.currentPrice)}</div>
        
        <div className={`watchlist-status ${statusClass}`}>
          <span className="status-icon">{statusInfo.emoji || statusInfo.icon}</span>
          <span>{statusInfo.message}</span>
        </div>
        
        {product.buyPoint && (
          <div className="watchlist-target">
            Target: {formatPrice(product.buyPoint)}
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
        
        {trend && trend !== 'STABLE' && (
          <div className="price-summary-trend">
            <span className={`trend-badge ${trend === 'FALLING' ? 'trend-good' : 'trend-bad'}`}>
              {trend === 'FALLING' ? '↓ Falling' : '↑ Rising'}
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
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    with open(full_path, "w") as f:
        f.write(content)

print("Updates completed successfully.")
