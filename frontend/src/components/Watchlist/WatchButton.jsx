import React, { useState } from 'react';
import { formatPrice } from '../../utils/formatPrice';
import { addToWatchlist, fetchWatchlist, removeFromWatchlist } from '../../services/api';
import './WatchButton.css';

const WatchButton = ({ productId, targetPrice, productName, initialWatching = false }) => {
  const [isWatching, setIsWatching] = useState(initialWatching);
  const [isSaving, setIsSaving] = useState(false);

  React.useEffect(() => {
    let active = true;
    if (!productId || initialWatching) return undefined;
    fetchWatchlist().then((items) => {
      if (active) setIsWatching(items.some((item) => item.id === productId));
    }).catch(() => {});
    return () => { active = false; };
  }, [productId, initialWatching]);

  const toggleWatch = async () => {
    if (isSaving) return;
    setIsSaving(true);
    try {
      if (isWatching) {
        await removeFromWatchlist(productId);
      } else {
        await addToWatchlist(productId, targetPrice);
      }
      setIsWatching((watching) => !watching);
    } catch (error) {
      console.error('Could not update watchlist', error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="watch-button-container">
      <button 
        type="button"
        className={`watch-btn ${isWatching ? 'is-watching' : ''}`}
        onClick={toggleWatch}
        disabled={isSaving || !productId}
        aria-pressed={isWatching}
        aria-label={isWatching ? `Stop watching ${productName || 'product'}` : `Watch ${productName || 'product'}${targetPrice ? ` until ${formatPrice(targetPrice)}` : ''}`}
      >
        {isSaving ? 'Saving…' : isWatching ? '✓ Watching' : targetPrice ? `Watch until ${formatPrice(targetPrice)}` : 'Watch this'}
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
