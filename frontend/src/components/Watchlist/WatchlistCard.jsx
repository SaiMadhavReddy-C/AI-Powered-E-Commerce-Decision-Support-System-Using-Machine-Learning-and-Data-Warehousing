import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { formatPrice } from '../../utils/formatPrice';
import { removeFromWatchlist } from '../../services/api';
import './WatchlistCard.css';

const WatchlistCard = ({ product, onRemove }) => {
  const navigate = useNavigate();
  const [removed, setRemoved] = useState(false);

  if (!product || removed) return null;

  const statusInfo = product.watchStatus || { icon: '👀', message: 'Watching', type: 'neutral' };
  
  const statusClass = `status-${statusInfo.type}`;

  const handleStopWatching = async (e) => {
    e.stopPropagation();
    try {
      await removeFromWatchlist(product.id);
    } catch (err) {
      console.error('Failed to remove from watchlist', err);
    }
    setRemoved(true);
    if (onRemove) {
      onRemove(product.id);
    }
  };

  const handleKeyDown = (e) => {
    if (e.target !== e.currentTarget && e.target.tagName === 'BUTTON') {
      return;
    }
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      navigate(`/analyze/${product.id}`);
    }
  };

  return (
    <div 
      className="watchlist-card" 
      onClick={() => navigate(`/analyze/${product.id}`)}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
      aria-label={`View analysis for ${product.name}, current price ${formatPrice(product.currentPrice)}`}
    >
      <div className="watchlist-card-content">
        <h3 className="watchlist-title">{product.name}</h3>
        <div className="watchlist-price">{formatPrice(product.currentPrice)}</div>
        
        <div className={`watchlist-status ${statusClass}`}>
          <span className="status-icon" aria-hidden="true">{statusInfo.emoji || statusInfo.icon}</span>
          <span>{statusInfo.message}</span>
        </div>
        
        {product.buyPoint && (
          <div className="watchlist-target">
            Target: {formatPrice(product.buyPoint)}
          </div>
        )}
      </div>
      
      <div className="watchlist-actions">
        <button 
          className="btn-secondary btn-sm" 
          onClick={(e) => { e.stopPropagation(); navigate(`/analyze/${product.id}`); }}
          aria-label={`Check analysis now for ${product.name}`}
        >
          Check now
        </button>
        <button 
          className="link-danger" 
          onClick={handleStopWatching}
          aria-label={`Stop watching ${product.name}`}
        >
          Stop watching
        </button>
      </div>
    </div>
  );
};

export default WatchlistCard;
