import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import PageContainer from '../components/Layout/PageContainer';
import { useAuth } from '../auth/context';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { requestOtp } = useAuth();

  const submit = async (event) => {
    event.preventDefault();
    setBusy(true); setError('');
    try {
      const normalized = email.trim().toLowerCase();
      await requestOtp(normalized);
      navigate('/login/otp', { state: { email: normalized, returnTo: location.state?.returnTo || '/watchlist' } });
    } catch (err) { setError(err.message || 'Could not send a login code.'); }
    finally { setBusy(false); }
  };

  return <PageContainer><div className="auth-page card">
    <h1>Sign in to ShopQ</h1>
    <p className="text-secondary">Search is free. Sign in to save a watchlist and receive alerts.</p>
    <form onSubmit={submit} style={{ marginTop: 24 }}>
      <label className="text-secondary" htmlFor="login-email">Email address</label>
      <input id="login-email" className="input" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" style={{ marginTop: 8 }} />
      {error && <p className="text-danger" style={{ marginTop: 10 }}>{error}</p>}
      <button className="btn btn-primary" type="submit" disabled={busy} style={{ width: '100%', marginTop: 16 }}>{busy ? 'Sending code…' : 'Continue with email'}</button>
    </form>
  </div></PageContainer>;
}
