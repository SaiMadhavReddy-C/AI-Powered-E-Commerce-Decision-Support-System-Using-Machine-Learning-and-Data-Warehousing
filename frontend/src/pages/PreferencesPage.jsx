import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import PageContainer from '../components/Layout/PageContainer';

const STORAGE_KEY = 'shopq_user_preferences';

const DEFAULT_PREFERENCES = {
  primaryPriority: 'best_price',
  waitTolerance: 'moderate',
  notifications: {
    priceDrops: true,
    sellerWarnings: true,
    upcomingSales: true,
    dailyDigest: false,
  },
  notificationChannel: 'in_app',
  email: '',
  recommendationMethod: 'balanced',
  autoScanEnabled: false,
  autoScanTime: '09:00',
  autoScanTimezone: 'Asia/Kolkata',
};

export default function PreferencesPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [preferences, setPreferences] = useState(() => {
    try {
      if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
          return { ...DEFAULT_PREFERENCES, ...JSON.parse(saved) };
        }
      }
    } catch (e) {
      console.warn('Failed to load preferences from storage:', e);
    }
    return DEFAULT_PREFERENCES;
  });
  const [saveStatus, setSaveStatus] = useState('');

  const handlePriorityChange = (priority) => {
    setPreferences((prev) => ({ ...prev, primaryPriority: priority }));
  };

  const handleWaitToleranceChange = (tolerance) => {
    setPreferences((prev) => ({ ...prev, waitTolerance: tolerance }));
  };

  const handleNotificationToggle = (key) => {
    setPreferences((prev) => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [key]: !prev.notifications[key],
      },
    }));
  };

  const handleSave = (e) => {
    e?.preventDefault();
    try {
      if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
      }
      setSaveStatus('Preferences saved successfully!');
      const returnTo = location.state?.returnTo;
      if (returnTo) {
        setTimeout(() => navigate(returnTo, { replace: true }), 350);
      } else {
        setTimeout(() => setSaveStatus(''), 3000);
      }
    } catch (e) {
      console.error('Failed to save preferences:', e);
      setSaveStatus('Error saving preferences.');
    }
  };

  const handleReset = () => {
    setPreferences(DEFAULT_PREFERENCES);
    try {
      if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULT_PREFERENCES));
      }
      setSaveStatus('Preferences reset to defaults.');
      setTimeout(() => setSaveStatus(''), 3000);
    } catch (e) {
      console.error('Failed to reset preferences:', e);
    }
  };

  const priorities = [
    {
      id: 'best_price',
      title: 'Lowest Price First',
      description: 'Wait for drops, compare all retailers, prioritize maximum savings.',
      badge: '💰 Value First',
    },
    {
      id: 'balanced',
      title: 'Balanced Approach (Recommended)',
      description: 'Smart trade-off between price savings and highly rated sellers.',
      badge: '⚖️ Optimal',
    },
    {
      id: 'verified_sellers',
      title: 'Verified Sellers Only',
      description: 'Never sacrifice seller reputation or warranty for small discounts.',
      badge: '🛡️ Reliability',
    },
    {
      id: 'speed',
      title: 'Fast & Prime Delivery',
      description: 'Prioritize express shipping and official brand stores.',
      badge: '⚡ Speed',
    },
  ];

  const waitTolerances = [
    {
      id: 'patient',
      label: 'Patient (3–4 weeks)',
      detail: 'Willing to wait for seasonal sales, festival discounts, and historic lows.',
    },
    {
      id: 'moderate',
      label: 'Moderate (1–2 weeks)',
      detail: 'Wait if a price drop is forecasted soon; otherwise recommend buying.',
    },
    {
      id: 'low',
      label: 'Low (Few days)',
      detail: 'Only wait if a price drop is imminent or current price is artificially spiked.',
    },
    {
      id: 'immediate',
      label: 'Immediate (Need it now)',
      detail: 'Always advise buying unless the seller is untrustworthy or price is gouged.',
    },
  ];

  const recommendationMethods = [
    { id: 'balanced', title: 'Balanced (Recommended)', detail: 'Balance price, seller reliability, stock, and timing.' },
    { id: 'price_first', title: 'Price first', detail: 'Prefer the lowest verified price, even with a longer wait.' },
    { id: 'seller_first', title: 'Seller safety first', detail: 'Prefer trusted sellers and warranties over small savings.' },
  ];

  return (
    <PageContainer>
      <div className="fade-in" style={{ maxWidth: '640px', margin: '0 auto', paddingBottom: '80px' }}>
        {/* Navigation & Header */}
        <div style={{ marginBottom: '24px' }}>
          <button
            onClick={() => navigate(-1)}
            className="btn-text"
            style={{ marginBottom: '12px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          >
            ← Back
          </button>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h1 style={{ fontSize: '26px', fontWeight: '700', marginBottom: '4px' }}>Shopping Preferences</h1>
              <p className="text-secondary" style={{ fontSize: '15px' }}>
                Tailor how ShopQ makes decisions and delivers recommendations.
              </p>
            </div>
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '50%',
                backgroundColor: 'var(--accent-light)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--accent)',
                fontWeight: '700',
                fontSize: '18px',
              }}
            >
              U
            </div>
          </div>
        </div>

        {/* Feedback message banner */}
        {saveStatus && (
          <div
            className="fade-in"
            style={{
              padding: '12px 16px',
              backgroundColor: 'var(--positive-light)',
              color: 'var(--positive)',
              borderRadius: 'var(--radius)',
              marginBottom: '20px',
              fontSize: '14px',
              fontWeight: '500',
              border: '1px solid rgba(45, 138, 86, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <span>✓ {saveStatus}</span>
            <button
              onClick={() => setSaveStatus('')}
              style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', fontSize: '16px' }}
            >
              ×
            </button>
          </div>
        )}

        <form onSubmit={handleSave}>
          {/* Section 1: Primary Priority */}
          <div className="card" style={{ marginBottom: '24px' }}>
            <div style={{ marginBottom: '16px' }}>
              <h2 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '4px' }}>1. Primary Priority</h2>
              <p className="text-secondary" style={{ fontSize: '14px' }}>
                What matters most to you when deciding whether to buy?
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {priorities.map((item) => {
                const isSelected = preferences.primaryPriority === item.id;
                return (
                  <label
                    key={item.id}
                    onClick={() => handlePriorityChange(item.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '12px',
                      padding: '14px 16px',
                      borderRadius: 'var(--radius)',
                      border: isSelected ? '2px solid var(--accent)' : '1px solid var(--border)',
                      backgroundColor: isSelected ? 'var(--accent-light)' : 'var(--bg-card)',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <input
                      type="radio"
                      name="primaryPriority"
                      checked={isSelected}
                      onChange={() => handlePriorityChange(item.id)}
                      style={{ marginTop: '3px', accentColor: 'var(--accent)' }}
                    />
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2px' }}>
                        <span style={{ fontWeight: isSelected ? '600' : '500', fontSize: '15px' }}>{item.title}</span>
                        <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{item.badge}</span>
                      </div>
                      <p className="text-secondary" style={{ fontSize: '13px', margin: 0, lineHeight: 1.4 }}>
                        {item.description}
                      </p>
                    </div>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Section 2: Wait Tolerance */}
          <div className="card" style={{ marginBottom: '24px' }}>
            <div style={{ marginBottom: '16px' }}>
              <h2 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '4px' }}>2. Wait Tolerance</h2>
              <p className="text-secondary" style={{ fontSize: '14px' }}>
                How long are you comfortable waiting if a better price is projected?
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {waitTolerances.map((item) => {
                const isSelected = preferences.waitTolerance === item.id;
                return (
                  <label
                    key={item.id}
                    onClick={() => handleWaitToleranceChange(item.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '12px',
                      padding: '12px 16px',
                      borderRadius: 'var(--radius)',
                      border: isSelected ? '2px solid var(--accent)' : '1px solid var(--border)',
                      backgroundColor: isSelected ? 'var(--accent-light)' : 'var(--bg-card)',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <input
                      type="radio"
                      name="waitTolerance"
                      checked={isSelected}
                      onChange={() => handleWaitToleranceChange(item.id)}
                      style={{ marginTop: '3px', accentColor: 'var(--accent)' }}
                    />
                    <div style={{ flex: 1 }}>
                      <span style={{ fontWeight: isSelected ? '600' : '500', fontSize: '14px', display: 'block', marginBottom: '2px' }}>
                        {item.label}
                      </span>
                      <p className="text-secondary" style={{ fontSize: '13px', margin: 0, lineHeight: 1.3 }}>
                        {item.detail}
                      </p>
                    </div>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Section 3: Recommendation method */}
          <div className="card" style={{ marginBottom: '24px' }}>
            <div style={{ marginBottom: '16px' }}>
              <h2 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '4px' }}>3. Recommendation Method</h2>
              <p className="text-secondary" style={{ fontSize: '14px' }}>Choose how ShopQ weighs price and seller risk.</p>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {recommendationMethods.map((item) => (
                <label key={item.id} style={{ display: 'flex', gap: '12px', padding: '12px 16px', borderRadius: 'var(--radius)', border: preferences.recommendationMethod === item.id ? '2px solid var(--accent)' : '1px solid var(--border)', backgroundColor: preferences.recommendationMethod === item.id ? 'var(--accent-light)' : 'var(--bg-card)', cursor: 'pointer' }}>
                  <input type="radio" name="recommendationMethod" checked={preferences.recommendationMethod === item.id} onChange={() => setPreferences((p) => ({ ...p, recommendationMethod: item.id }))} style={{ accentColor: 'var(--accent)' }} />
                  <span><strong>{item.title}</strong><span className="text-secondary" style={{ display: 'block', fontSize: '13px', marginTop: '3px' }}>{item.detail}</span></span>
                </label>
              ))}
            </div>
          </div>

          {/* Section 4: Automatic watchlist scan */}
          <div className="card" style={{ marginBottom: '24px' }}>
            <div style={{ marginBottom: '16px' }}>
              <h2 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '4px' }}>4. Automatic Watchlist Scan</h2>
              <p className="text-secondary" style={{ fontSize: '14px' }}>Set when the watchlist worker should refresh tracked products.</p>
            </div>
            <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '12px' }}>
              <span><strong>Enable scheduled scans</strong><span className="text-secondary" style={{ display: 'block', fontSize: '13px', marginTop: '3px' }}>The scheduled worker will check live prices and update alerts.</span></span>
              <input type="checkbox" checked={preferences.autoScanEnabled} onChange={() => setPreferences((p) => ({ ...p, autoScanEnabled: !p.autoScanEnabled }))} style={{ width: '18px', height: '18px', accentColor: 'var(--accent)' }} />
            </label>
            {preferences.autoScanEnabled && (
              <div style={{ display: 'flex', gap: '12px', marginTop: '16px', flexWrap: 'wrap' }}>
                <label style={{ flex: '1 1 140px', fontSize: '13px' }}>Daily time<input type="time" value={preferences.autoScanTime} onChange={(e) => setPreferences((p) => ({ ...p, autoScanTime: e.target.value }))} className="input" style={{ display: 'block', marginTop: '6px' }} /></label>
                <label style={{ flex: '1 1 180px', fontSize: '13px' }}>Timezone<select value={preferences.autoScanTimezone} onChange={(e) => setPreferences((p) => ({ ...p, autoScanTimezone: e.target.value }))} className="input" style={{ display: 'block', marginTop: '6px' }}><option>Asia/Kolkata</option><option>UTC</option><option>America/New_York</option><option>Europe/London</option></select></label>
              </div>
            )}
          </div>

          {/* Section 5: Notification Preferences */}
          <div className="card" style={{ marginBottom: '28px' }}>
            <div style={{ marginBottom: '16px' }}>
              <h2 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '4px' }}>3. Notification Settings</h2>
              <p className="text-secondary" style={{ fontSize: '14px' }}>
                Control which alerts trigger in your inbox and how you're notified.
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', gap: '12px' }}>
                <div>
                  <span style={{ fontSize: '14px', fontWeight: '500', display: 'block' }}>Price Drop Triggers</span>
                  <span className="text-secondary" style={{ fontSize: '13px' }}>Notify when watched items reach target buy points</span>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.notifications.priceDrops}
                  onChange={() => handleNotificationToggle('priceDrops')}
                  style={{ width: '18px', height: '18px', accentColor: 'var(--accent)' }}
                />
              </label>

              <hr className="divider" style={{ margin: '4px 0' }} />

              <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', gap: '12px' }}>
                <div>
                  <span style={{ fontSize: '14px', fontWeight: '500', display: 'block' }}>Seller Risk Warnings</span>
                  <span className="text-secondary" style={{ fontSize: '13px' }}>Alert when seller ratings decline or buy-box switches</span>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.notifications.sellerWarnings}
                  onChange={() => handleNotificationToggle('sellerWarnings')}
                  style={{ width: '18px', height: '18px', accentColor: 'var(--accent)' }}
                />
              </label>

              <hr className="divider" style={{ margin: '4px 0' }} />

              <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', gap: '12px' }}>
                <div>
                  <span style={{ fontSize: '14px', fontWeight: '500', display: 'block' }}>Sale Event Projections</span>
                  <span className="text-secondary" style={{ fontSize: '13px' }}>Early heads-up about upcoming festival and seasonal sales</span>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.notifications.upcomingSales}
                  onChange={() => handleNotificationToggle('upcomingSales')}
                  style={{ width: '18px', height: '18px', accentColor: 'var(--accent)' }}
                />
              </label>

              <hr className="divider" style={{ margin: '4px 0' }} />

              <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', gap: '12px' }}>
                <div>
                  <span style={{ fontSize: '14px', fontWeight: '500', display: 'block' }}>Daily Watchlist Digest</span>
                  <span className="text-secondary" style={{ fontSize: '13px' }}>One daily morning summary of all tracked items</span>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.notifications.dailyDigest}
                  onChange={() => handleNotificationToggle('dailyDigest')}
                  style={{ width: '18px', height: '18px', accentColor: 'var(--accent)' }}
                />
              </label>
            </div>

            <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border)' }}>
              <span style={{ fontSize: '14px', fontWeight: '500', display: 'block', marginBottom: '8px' }}>
                Preferred Channel
              </span>
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                <button
                  type="button"
                  onClick={() => setPreferences((p) => ({ ...p, notificationChannel: 'in_app' }))}
                  className={`btn ${preferences.notificationChannel === 'in_app' ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ padding: '8px 16px', fontSize: '13px' }}
                >
                  🔔 In-App Alerts
                </button>
                <button
                  type="button"
                  onClick={() => setPreferences((p) => ({ ...p, notificationChannel: 'email' }))}
                  className={`btn ${preferences.notificationChannel === 'email' ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ padding: '8px 16px', fontSize: '13px' }}
                >
                  ✉️ Email + In-App
                </button>
              </div>

              {preferences.notificationChannel === 'email' && (
                <div style={{ marginTop: '12px' }}>
                  <input
                    type="email"
                    className="input"
                    placeholder="Enter your email address"
                    value={preferences.email || ''}
                    onChange={(e) => setPreferences((p) => ({ ...p, email: e.target.value }))}
                    style={{ fontSize: '14px', padding: '10px 14px' }}
                  />
                </div>
              )}
            </div>
          </div>

          {/* Action buttons */}
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'space-between', alignItems: 'center' }}>
            <button
              type="button"
              onClick={handleReset}
              className="btn btn-secondary"
              style={{ fontSize: '14px', padding: '12px 18px' }}
            >
              Reset to Defaults
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              style={{ fontSize: '14px', padding: '12px 24px', fontWeight: '600' }}
            >
              Save Preferences
            </button>
          </div>
        </form>
      </div>
    </PageContainer>
  );
}
