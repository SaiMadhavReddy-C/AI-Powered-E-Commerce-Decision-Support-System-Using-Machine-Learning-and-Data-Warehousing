import React, { useState } from 'react';
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
        type="button"
        className={`watch-btn ${isWatching ? 'is-watching' : ''}`}
        onClick={toggleWatch}
        aria-pressed={isWatching}
        aria-label={isWatching ? `Stop watching ${productName || 'product'}` : `Watch ${productName || 'product'}${targetPrice ? ` until ${formatPrice(targetPrice)}` : ''}`}
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
