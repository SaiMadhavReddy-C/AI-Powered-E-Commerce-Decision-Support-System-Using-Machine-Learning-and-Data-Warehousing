import React from 'react';
import { formatPrice, formatTimeAgo } from '../../utils/formatPrice';
import { RECOMMENDATION_TYPES, CONFIDENCE_LEVELS } from '../../utils/constants';
import './RecommendationCard.css';

const RecommendationCard = ({ product }) => {
  if (!product || !product.recommendation) return null;
  const recData = RECOMMENDATION_TYPES[product.recommendation] || RECOMMENDATION_TYPES.UNCERTAIN;
  const confText = typeof CONFIDENCE_LEVELS[product.confidence] === 'object'
    ? CONFIDENCE_LEVELS[product.confidence]?.label
    : (product.confidence || '');

  const getTypeClass = () => {
    switch (recData.category?.toLowerCase()) {
      case 'wait': return 'rec-type-wait';
      case 'buy': return 'rec-type-buy';
      case 'change': return 'rec-type-change';
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
          {recData.category?.toLowerCase() === 'wait' && product.buyPoint && (
            <div className="rec-wait-action">
              <p>I'd reconsider around {formatPrice(product.buyPoint)}.</p>
              <button className="btn-secondary">Watch until {formatPrice(product.buyPoint)}</button>
            </div>
          )}
          
          {recData.category?.toLowerCase() === 'buy' && product.retailerUrl && (
            <a href={product.retailerUrl} className="btn-primary rec-buy-btn" target="_blank" rel="noopener noreferrer">
              Buy at {formatPrice(product.currentPrice)} →
            </a>
          )}
          
          {recData.category?.toLowerCase() === 'change' && product.bestOffer && (
            <div className="rec-change-action">
              <p>I found a better option on {product.bestOffer.retailer}.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RecommendationCard;
