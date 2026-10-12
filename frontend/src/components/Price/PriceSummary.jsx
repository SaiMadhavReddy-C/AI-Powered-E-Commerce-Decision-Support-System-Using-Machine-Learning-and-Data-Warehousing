import React from 'react';
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
