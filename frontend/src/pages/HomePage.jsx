import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { fetchWatchlist, analyzeProduct } from '../services/api';
import PageContainer from '../components/Layout/PageContainer';
import SearchBar from '../components/Search/SearchBar';
import EmptyState from '../components/common/EmptyState';
import './HomePage.css';

export default function HomePage() {
  const navigate = useNavigate();
  const [watchlist, setWatchlist] = useState([]);
  const [hasHistory, setHasHistory] = useState(false); // Mock state for new user
  const [isFirstSession, setIsFirstSession] = useState(true);

  useEffect(() => {
    fetchWatchlist().then(data => {
      setWatchlist(data || []);
      // If they have watchlist items, maybe they aren't a new user
      if (data && data.length > 0) {
        setHasHistory(true);
        setIsFirstSession(false);
      }
    }).catch(err => {
      console.error('Failed to load watchlist', err);
      setWatchlist([]);
    });
  }, []);

  const handleSearch = async (query) => {
    if (!query) return;
    
    setHasHistory(true);
    setIsFirstSession(false);

    const trimmed = query.trim();
    if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
      try {
        const analysis = await analyzeProduct(trimmed);
        const product = await analysis.execute(() => {});
        if (product && product.id) {
          navigate(`/analyze/${encodeURIComponent(product.id)}`);
          return;
        }
      } catch (err) {
        console.error('URL analysis failed', err);
      }
    }

    navigate(`/search?q=${encodeURIComponent(trimmed)}`);
  };

  const handleTryExample = () => {
    navigate('/analyze/sony_wh1000xm5');
  };

  return (
    <PageContainer>
      <div className="home-page-container fade-in">
        <div className="editorial-hero">
          <h1 className="editorial-title">Should you buy it?</h1>
          <p className="editorial-subtitle">I'll check before you decide.</p>
          
          <div className="search-wrapper">
            <SearchBar onSubmit={handleSearch} placeholder="Paste a product link or search a product" />
          </div>

          {isFirstSession && (
            <div className="first-use-helper">
              <strong>New to ShopQ?</strong> Give me a product &rarr; I check prices, sellers and recent history &rarr; I tell you what I'd do.
            </div>
          )}

          <div className="recent-searches">
            {hasHistory ? (
              <div className="recent-list">
                <span className="recent-label">Recent</span>
                <button className="recent-chip" onClick={() => navigate('/analyze/sony_wh1000xm5')} aria-label="View recent item: Sony WH-1000XM5">Sony WH-1000XM5</button>
                <button className="recent-chip" onClick={() => navigate('/analyze/iphone_15')} aria-label="View recent item: iPhone 15">iPhone 15</button>
                <button className="recent-chip" onClick={() => navigate('/analyze/nike_air_max')} aria-label="View recent item: Nike Air Max 90">Nike Air Max 90</button>
              </div>
            ) : (
              <div className="example-prompt">
                <button className="btn-text" onClick={handleTryExample}>
                  Try an example: Sony WH-1000XM5
                </button>
              </div>
            )}
          </div>
        </div>

        <hr className="divider" style={{ margin: '48px 0 32px 0' }} />

        <div className="watchlist-preview-section">
          <div className="watchlist-header">
            <h2>Watching</h2>
            <Link to="/watchlist" className="see-all-link">See all &rarr;</Link>
          </div>
          
          {watchlist.length > 0 ? (
            <div className="inbox-preview-grid">
              {watchlist.slice(0, 2).map(item => (
                <div 
                  key={item.id} 
                  className="inbox-preview-card" 
                  role="button"
                  tabIndex={0}
                  aria-label={`View analysis for ${item.name}, ₹${item.currentPrice.toLocaleString('en-IN')}`}
                  onClick={() => navigate('/analyze/' + item.id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      navigate('/analyze/' + item.id);
                    }
                  }}
                >
                  <img src={item.image} alt={item.name} className="editorial-img-thumb" />
                  <div className="inbox-preview-details">
                    <span className="inbox-preview-title">{item.name}</span>
                    <span className="inbox-preview-price">₹{item.currentPrice.toLocaleString('en-IN')}</span>
                    <span className="inbox-preview-status">{item.watchStatus?.emoji || item.watchMessage?.charAt(0) || '👀'} {item.watchGroup === 'WAITING' ? 'Waiting' : 'Watching'}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState 
              emoji="👀"
              title="Nothing here yet" 
              description="When you find something you're thinking about buying, add it here." 
            />
          )}
        </div>
      </div>
    </PageContainer>
  );
}
