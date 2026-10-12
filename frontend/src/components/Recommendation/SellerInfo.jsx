import React, { useState } from 'react';
import './SellerInfo.css';

const SellerInfo = ({ seller }) => {
  const [expanded, setExpanded] = useState(false);

  if (!seller) return null;

  return (
    <div className="seller-info">
      <button 
        type="button"
        id="seller-header-toggle"
        className="seller-header" 
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
        aria-controls="seller-details-content"
        aria-label={expanded ? `Collapse seller details for ${seller.name}` : `Expand seller details for ${seller.name}`}
      >
        <div className="seller-title-row">
          <span className="seller-shield" aria-hidden="true">🛡️</span>
          <span className="seller-name-label">Seller: {seller.name}</span>
          <span className="seller-status">{seller.reliability || 'Looks reliable'}</span>
        </div>
        <span className="expand-btn" aria-hidden="true">{expanded ? '−' : '+'}</span>
      </button>
      
      {expanded && (
        <div 
          id="seller-details-content" 
          className="seller-details slide-up"
          role="region"
          aria-labelledby="seller-header-toggle"
        >
          <div className="detail-item">
            <span className="detail-label">Rating:</span>
            <span className="detail-value">{seller.rating} ({seller.reviews ?? seller.reviewCount} reviews)</span>
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
