import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import PageContainer from '../components/Layout/PageContainer';
import { useAuth } from '../auth/context';

export default function OtpPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const email = location.state?.email || '';
  const returnTo = location.state?.returnTo || '/watchlist';
  const [code, setCode] = useState('');
  const [seconds, setSeconds] = useState(600);
  const [resendIn, setResendIn] = useState(30);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const { verifyOtp, requestOtp } = useAuth();

  useEffect(() => {
    const timer = setInterval(() => { setSeconds((s) => Math.max(0, s - 1)); setResendIn((s) => Math.max(0, s - 1)); }, 1000);
    return () => clearInterval(timer);
  }, []);

  if (!email) { navigate('/login', { replace: true }); return null; }
  const verify = async (event) => {
    event.preventDefault(); setBusy(true); setError('');
    try { await verifyOtp(email, code); navigate(returnTo, { replace: true }); }
    catch (err) { setError(err.message || 'Invalid or expired code.'); }
    finally { setBusy(false); }
  };
  const resend = async () => { if (resendIn) return; try { const result = await requestOtp(email); setSeconds(result.expiresIn); setResendIn(result.resendIn); setError(''); } catch (err) { setError(err.message || 'Could not resend code.'); } };

  return <PageContainer><div className="auth-page card">
    <h1>Enter your code</h1><p className="text-secondary">We sent a 6-digit code to {email}.</p>
    <form onSubmit={verify} style={{ marginTop: 24 }}>
      <input className="input" inputMode="numeric" pattern="[0-9]{6}" maxLength={6} required value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))} placeholder="000000" aria-label="6-digit login code" />
      <p className="text-secondary" style={{ marginTop: 10 }}>Code expires in {Math.floor(seconds / 60)}:{String(seconds % 60).padStart(2, '0')}</p>
      {error && <p className="text-danger" style={{ marginTop: 10 }}>{error}</p>}
      <button className="btn btn-primary" type="submit" disabled={busy || seconds === 0} style={{ width: '100%', marginTop: 16 }}>{busy ? 'Checking…' : 'Verify and continue'}</button>
    </form>
    <button className="btn-text" type="button" disabled={resendIn > 0} onClick={resend} style={{ marginTop: 16 }}>Resend code{resendIn ? ` in ${resendIn}s` : ''}</button>
  </div></PageContainer>;
}
