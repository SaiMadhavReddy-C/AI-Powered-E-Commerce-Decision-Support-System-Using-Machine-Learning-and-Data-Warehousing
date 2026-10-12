import React from 'react';
import { Link } from 'react-router-dom';
import { formatPrice } from '../../utils/formatPrice';
import './SearchResults.css';

const SearchResults = ({ results, onSelect }) => {
  if (!results || results.length === 0) return null;

  return (
    <div className="search-results-list fade-in" role="list">
      {results.map((result, index) => {
        const key = result.id || index;
        const trendText = result.trend === 'FALLING' ? '↓ Falling' : result.trend === 'RISING' ? '↑ Rising' : '';
        const itemContent = (
          <div className="result-content">
            <div className="result-info">
              <h3 className="result-name">{result.name}</h3>
              <span className="result-category">{result.category}</span>
            </div>
            <div className="result-price-info">
              <span className="result-price">From {formatPrice(result.currentPrice)}</span>
              {result.trend && (
                <span className={`result-trend trend-${result.trend.toLowerCase()}`}>
                  {trendText}
                </span>
              )}
            </div>
          </div>
        );

        if (onSelect) {
          return (
            <div 
              key={key} 
              role="button"
              tabIndex={0}
              className="search-result-item" 
              onClick={() => onSelect(result)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onSelect(result);
                }
              }}
              aria-label={`Select ${result.name}, price from ${formatPrice(result.currentPrice)}`}
            >
              {itemContent}
            </div>
          );
        }

        return (
          <Link 
            key={key} 
            to={`/analyze/${result.id}`} 
            className="search-result-item"
            aria-label={`View analysis for ${result.name}, price from ${formatPrice(result.currentPrice)}`}
          >
            {itemContent}
          </Link>
        );
      })}
    </div>
  );
};

export default SearchResults;
