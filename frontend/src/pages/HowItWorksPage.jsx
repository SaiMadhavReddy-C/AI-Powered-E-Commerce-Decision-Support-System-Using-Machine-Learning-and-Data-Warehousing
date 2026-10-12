import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import PageContainer from '../components/Layout/PageContainer';

export default function HowItWorksPage() {
  const navigate = useNavigate();

  const verdicts = [
    {
      badge: 'BUY',
      color: 'var(--positive)',
      bg: 'var(--positive-light)',
      title: 'Buy Now',
      explanation: 'The price is at or near its 90-day low, and the primary seller is verified with positive ratings. Good time to buy.',
    },
    {
      badge: 'WAIT',
      color: 'var(--warning)',
      bg: 'var(--warning-light)',
      title: 'Wait for a Drop',
      explanation: 'Prices are trending downward or a lower price is available through another retailer. We project a better deal soon.',
    },
    {
      badge: 'GRAB',
      color: 'var(--positive)',
      bg: 'var(--positive-light)',
      title: 'Grab Deal',
      explanation: 'A rare flash discount or historic bargain significantly below the regular baseline. Limited-time opportunity.',
    },
    {
      badge: "DON'T RUSH",
      color: 'var(--danger)',
      bg: 'var(--danger-light)',
      title: "Don't Rush",
      explanation: 'The price recently spiked or is near a 60-day high. Historical patterns indicate it will drop back down.',
    },
    {
      badge: 'CHECK SELLER',
      color: 'var(--warning)',
      bg: 'var(--warning-light)',
      title: 'Check the Seller',
      explanation: 'The price tag looks tempting, but the active seller has low ratings or poor return terms. Caution advised.',
    },
  ];

  const sellerCheckpoints = [
    {
      icon: '⭐',
      title: 'Rating & Feedback Volume',
      detail: 'We evaluate aggregate merchant ratings and review counts, distinguishing established sellers from unvetted accounts.',
    },
    {
      icon: '🛡️',
      title: 'Warranty & Authenticity',
      detail: 'We verify whether the listing includes official manufacturer warranty coverage or dubious third-party claims.',
    },
    {
      icon: '🔄',
      title: 'Return & Replacement Terms',
      detail: 'Clear, customer-friendly return windows (e.g., 7–10 days) are prioritized over non-returnable listings.',
    },
    {
      icon: '⚠️',
      title: 'Buy-Box Switch Monitoring',
      detail: 'Retail algorithms frequently switch buy-box sellers. ShopQ flags when a reputable default is replaced by a risky merchant.',
    },
  ];

  const confidenceLevels = [
    {
      level: 'HIGH',
      badgeClass: 'text-positive',
      bgClass: 'var(--positive-light)',
      description: 'Based on 90+ days of price tracking across top retailers with confirmed seller histories. High predictability.',
    },
    {
      level: 'MEDIUM',
      badgeClass: 'text-warning',
      bgClass: 'var(--warning-light)',
      description: 'Moderate historical data or seasonal projection (such as anticipating festival sales). Direction is clear, but exact drop amounts may vary.',
    },
    {
      level: 'LOW',
      badgeClass: 'text-neutral',
      bgClass: 'var(--neutral-light)',
      description: 'Newly launched products or sparse marketplace listings. We clearly state when data is thin instead of giving false certainty.',
    },
  ];

  const examples = [
    { id: 'sony_wh1000xm5', name: 'Sony WH-1000XM5', verdict: 'WAIT', price: '₹23,499' },
    { id: 'iphone_15', name: 'Apple iPhone 15', verdict: 'BUY', price: '₹54,999' },
    { id: 'nike_air_max', name: 'Nike Air Max 90', verdict: 'GRAB', price: '₹8,999' },
  ];

  return (
    <PageContainer>
      <div className="fade-in" style={{ maxWidth: '680px', margin: '0 auto', paddingBottom: '80px' }}>
        {/* Header */}
        <div style={{ marginBottom: '32px' }}>
          <button
            onClick={() => navigate(-1)}
            className="btn-text"
            style={{ marginBottom: '12px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          >
            ← Back
          </button>
          <h1 style={{ fontSize: '28px', fontWeight: '700', marginBottom: '8px' }}>How ShopQ Works</h1>
          <p className="text-secondary" style={{ fontSize: '16px', lineHeight: 1.5 }}>
            Our mission is simple: tell you whether you should buy, wait, or avoid before you check out. Here is the logic behind every recommendation.
          </p>
        </div>

        {/* 3 Step Overview */}
        <div
          className="card"
          style={{
            marginBottom: '32px',
            backgroundColor: 'var(--accent-light)',
            borderColor: 'rgba(201, 107, 122, 0.2)',
          }}
        >
          <h2 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px', color: 'var(--text)' }}>
            The 3-Step Assessment
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px' }}>
            <div style={{ background: 'var(--bg-card)', padding: '16px', borderRadius: 'var(--radius)' }}>
              <span style={{ fontSize: '20px', display: 'block', marginBottom: '8px' }}>1. 🔍</span>
              <strong style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Scan Markets</strong>
              <p className="text-secondary" style={{ fontSize: '12px', margin: 0 }}>
                Track live pricing and 90-day history across Amazon, Flipkart, Croma, and more.
              </p>
            </div>
            <div style={{ background: 'var(--bg-card)', padding: '16px', borderRadius: 'var(--radius)' }}>
              <span style={{ fontSize: '20px', display: 'block', marginBottom: '8px' }}>2. 🛡️</span>
              <strong style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Verify Sellers</strong>
              <p className="text-secondary" style={{ fontSize: '12px', margin: 0 }}>
                Audit merchant ratings, return policies, warranties, and review integrity.
              </p>
            </div>
            <div style={{ background: 'var(--bg-card)', padding: '16px', borderRadius: 'var(--radius)' }}>
              <span style={{ fontSize: '20px', display: 'block', marginBottom: '8px' }}>3. 💡</span>
              <strong style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Clear Decision</strong>
              <p className="text-secondary" style={{ fontSize: '12px', margin: 0 }}>
                Deliver an actionable verdict with transparent confidence and target buy points.
              </p>
            </div>
          </div>
        </div>

        {/* Section 1: Decision Logic */}
        <div style={{ marginBottom: '36px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '6px' }}>1. Decision Logic</h2>
          <p className="text-secondary" style={{ fontSize: '14px', marginBottom: '16px' }}>
            Every product receives an unambiguous verdict based on price trajectory and seller reliability:
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {verdicts.map((v, i) => (
              <div key={i} className="card" style={{ padding: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                  <span
                    style={{
                      display: 'inline-block',
                      padding: '3px 8px',
                      fontSize: '11px',
                      fontWeight: '700',
                      borderRadius: '4px',
                      color: v.color,
                      backgroundColor: v.bg,
                      letterSpacing: '0.5px',
                    }}
                  >
                    {v.badge}
                  </span>
                  <h3 style={{ fontSize: '16px', margin: 0, fontWeight: '600' }}>{v.title}</h3>
                </div>
                <p className="text-secondary" style={{ fontSize: '13px', margin: 0, lineHeight: 1.4 }}>
                  {v.explanation}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Section 2: Seller Checks */}
        <div style={{ marginBottom: '36px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '6px' }}>2. Seller & Reliability Checks</h2>
          <p className="text-secondary" style={{ fontSize: '14px', marginBottom: '16px' }}>
            A low price is worthless if the product is counterfeit, missing warranty, or sold by an untrustworthy vendor:
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '12px' }}>
            {sellerCheckpoints.map((cp, i) => (
              <div key={i} className="card" style={{ padding: '16px' }}>
                <span style={{ fontSize: '20px', display: 'block', marginBottom: '6px' }}>{cp.icon}</span>
                <h3 style={{ fontSize: '15px', fontWeight: '600', marginBottom: '4px' }}>{cp.title}</h3>
                <p className="text-secondary" style={{ fontSize: '13px', margin: 0, lineHeight: 1.4 }}>
                  {cp.detail}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Section 3: Confidence Score */}
        <div style={{ marginBottom: '36px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '6px' }}>3. How Confidence is Calculated</h2>
          <p className="text-secondary" style={{ fontSize: '14px', marginBottom: '16px' }}>
            We only give high confidence when backed by verifiable data. When information is incomplete, we tell you upfront:
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {confidenceLevels.map((lvl, i) => (
              <div key={i} className="card" style={{ padding: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                  <span
                    style={{
                      padding: '2px 8px',
                      fontSize: '11px',
                      fontWeight: '700',
                      borderRadius: '4px',
                      backgroundColor: lvl.bgClass,
                    }}
                    className={lvl.badgeClass}
                  >
                    {lvl.level} CONFIDENCE
                  </span>
                </div>
                <p className="text-secondary" style={{ fontSize: '13px', margin: 0, lineHeight: 1.4 }}>
                  {lvl.description}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Interactive Examples Section */}
        <div className="card" style={{ marginBottom: '32px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>See Decision Logic in Action</h2>
          <p className="text-secondary" style={{ fontSize: '14px', marginBottom: '16px' }}>
            Explore how ShopQ analyzes real-world products right now:
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {examples.map((item) => (
              <div
                key={item.id}
                role="button"
                tabIndex={0}
                aria-label={`View analysis for ${item.name}, current price ${item.price}, recommendation ${item.verdict}`}
                onClick={() => navigate(`/analyze/${item.id}`)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    navigate(`/analyze/${item.id}`);
                  }
                }}
                className="interactive-example-card"
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px 14px',
                  borderRadius: 'var(--radius)',
                  border: '1px solid var(--border)',
                  backgroundColor: 'var(--bg)',
                  cursor: 'pointer',
                  transition: 'border-color 0.15s ease',
                }}
              >
                <div>
                  <strong style={{ fontSize: '14px', display: 'block' }}>{item.name}</strong>
                  <span className="text-secondary" style={{ fontSize: '12px' }}>Current: {item.price}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span
                    style={{
                      fontSize: '11px',
                      fontWeight: '700',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      backgroundColor: item.verdict === 'BUY' ? 'var(--positive-light)' : item.verdict === 'WAIT' ? 'var(--warning-light)' : 'var(--positive-light)',
                      color: item.verdict === 'BUY' ? 'var(--positive)' : item.verdict === 'WAIT' ? 'var(--warning)' : 'var(--positive)',
                    }}
                  >
                    {item.verdict}
                  </span>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>→</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer CTAs */}
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <Link to="/" className="btn btn-secondary">
            Back to Home
          </Link>
          <Link to="/search" className="btn btn-primary">
            Try a Search
          </Link>
        </div>
      </div>
    </PageContainer>
  );
}
