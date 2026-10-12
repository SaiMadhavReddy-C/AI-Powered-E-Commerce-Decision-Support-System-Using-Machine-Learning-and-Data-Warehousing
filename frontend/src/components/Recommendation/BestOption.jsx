import React from 'react';
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
