import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import PageContainer from '../components/Layout/PageContainer';
import SearchBar from '../components/Search/SearchBar';

export default function NotFoundPage() {
  const navigate = useNavigate();

  const handleSearch = (query) => {
    if (!query) return;
    if (query.startsWith('http://') || query.startsWith('https://')) {
      navigate('/analyze/url-match-id');
    } else {
      navigate(`/search?q=${encodeURIComponent(query)}`);
    }
  };

  const popularProducts = [
    { id: 'sony_wh1000xm5', name: 'Sony WH-1000XM5' },
    { id: 'iphone_15', name: 'Apple iPhone 15' },
    { id: 'nike_air_max', name: 'Nike Air Max 90' },
  ];

  return (
    <PageContainer>
      <div className="fade-in" style={{ maxWidth: '580px', margin: '0 auto', textAlign: 'center', padding: '40px 16px 80px' }}>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '72px',
            height: '72px',
            borderRadius: '50%',
            backgroundColor: 'var(--accent-light)',
            color: 'var(--accent)',
            fontSize: '32px',
            marginBottom: '20px',
          }}
        >
          🔍
        </div>

        <span
          style={{
            display: 'block',
            fontSize: '13px',
            fontWeight: '700',
            letterSpacing: '1px',
            color: 'var(--accent)',
            textTransform: 'uppercase',
            marginBottom: '8px',
          }}
        >
          404 · Page Not Found
        </span>

        <h1 style={{ fontSize: '28px', fontWeight: '700', marginBottom: '12px' }}>
          We couldn't find that page
        </h1>

        <p className="text-secondary" style={{ fontSize: '15px', lineHeight: 1.5, marginBottom: '32px' }}>
          The link you followed may be broken, or the page may have been moved. Try searching for a product or return to home.
        </p>

        {/* Quick Search */}
        <div style={{ marginBottom: '32px', textAlign: 'left' }}>
          <SearchBar onSubmit={handleSearch} placeholder="Search for a product or paste a link..." />
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap', marginBottom: '40px' }}>
          <Link to="/" className="btn btn-primary" style={{ padding: '12px 24px' }}>
            Go to Home
          </Link>
          <Link to="/search" className="btn btn-secondary" style={{ padding: '12px 24px' }}>
            Browse Search
          </Link>
          <Link to="/watchlist" className="btn btn-secondary" style={{ padding: '12px 24px' }}>
            View Watchlist
          </Link>
        </div>

        {/* Popular Suggestions */}
        <div className="card" style={{ textAlign: 'left', padding: '20px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px', color: 'var(--text-secondary)' }}>
            Or explore popular items:
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {popularProducts.map((p) => (
              <button
                key={p.id}
                onClick={() => navigate(`/analyze/${p.id}`)}
                className="btn-text"
                style={{
                  textAlign: 'left',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '6px 0',
                  color: 'var(--text)',
                }}
              >
                <span>{p.name}</span>
                <span className="text-accent" style={{ fontSize: '13px' }}>View analysis →</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
