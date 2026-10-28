import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import PageContainer from '../components/Layout/PageContainer';
import { useAuth } from '../auth/context';

export default function LoginPage({ mode = 'login' }) {
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
      navigate('/login/otp', { state: { email: normalized, mode, returnTo: location.state?.returnTo || '/watchlist' } });
    } catch (err) { setError(err.message || 'Could not send a login code.'); }
    finally { setBusy(false); }
  };

  return <PageContainer><div className="auth-page card">
    <h1>{mode === 'signup' ? 'Create your ShopQ account' : 'Log in to ShopQ'}</h1>
    <p className="text-secondary">Search is free. {mode === 'signup' ? 'Create an account to save a watchlist and receive alerts.' : 'Log in to access your watchlist and alerts.'}</p>
    <form onSubmit={submit} style={{ marginTop: 24 }}>
      <label className="text-secondary" htmlFor="login-email">Email address</label>
      <input id="login-email" className="input" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" style={{ marginTop: 8 }} />
      {error && <p className="text-danger" style={{ marginTop: 10 }}>{error}</p>}
      <button className="btn btn-primary" type="submit" disabled={busy} style={{ width: '100%', marginTop: 16 }}>{busy ? 'Sending code…' : mode === 'signup' ? 'Create account' : 'Log in with email'}</button>
    </form>
    <p className="text-secondary" style={{ textAlign: 'center', marginTop: 18, fontSize: 14 }}>
      {mode === 'signup' ? 'Already have an account? ' : 'New to ShopQ? '}
      <button type="button" className="btn-text" onClick={() => navigate(mode === 'signup' ? '/login' : '/signup', { state: { returnTo: location.state?.returnTo } })}>
        {mode === 'signup' ? 'Log in' : 'Sign up'}
      </button>
    </p>
  </div></PageContainer>;
}
