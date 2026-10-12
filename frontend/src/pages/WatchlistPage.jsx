import React, { useState, useEffect } from 'react';
import { fetchWatchlist } from '../services/api';
import PageContainer from '../components/Layout/PageContainer';
import WatchlistCard from '../components/Watchlist/WatchlistCard';
import EmptyState from '../components/common/EmptyState';
import './WatchlistPage.css';

export default function WatchlistPage() {
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWatchlist().then(data => {
      setWatchlist(data || []);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setWatchlist([]);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <PageContainer><div className="watchlist-page-container"><p>Loading watchlist...</p></div></PageContainer>;
  }

  return (
    <PageContainer>
      <div className="watchlist-page-container fade-in">
        <div className="watchlist-header">
          <h1>Watchlist</h1>
          <p className="subtitle">Products you're keeping an eye on.</p>
        </div>

        {watchlist.length > 0 ? (
          <div className="watchlist-grid">
            {watchlist.map(item => (
              <WatchlistCard key={item.id} product={item} />
            ))}
          </div>
        ) : (
          <div className="empty-state-wrapper">
            <EmptyState 
              emoji="👀"
              title="Nothing here yet" 
              description="When you find something you're thinking about buying, add it here." 
            />
          </div>
        )}
      </div>
    </PageContainer>
  );
}
