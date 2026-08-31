import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Check } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const POINTS = [
  'Career matches scored against real engineering roles',
  'Ranked courses from a large public catalog',
  'A prerequisite-ordered roadmap you track course by course',
];

export default function LoginPage() {
  const { login, resetPassword } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState('login'); // 'login' | 'reset'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [err, setErr] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setErr(null);

    if (mode === 'reset') {
      if (password.length < 6) { setErr('Password must be at least 6 characters.'); return; }
      if (password !== confirm) { setErr('Passwords do not match.'); return; }
    }

    setBusy(true);
    try {
      if (mode === 'login') {
        await login(email, password);
      } else {
        await resetPassword(email, password);
      }
      navigate('/app/dashboard');
    } catch (e2) {
      setErr(e2.message);
    } finally {
      setBusy(false);
    }
  };

  const switchMode = (next) => {
    setMode(next);
    setErr(null);
    setPassword('');
    setConfirm('');
  };

  const isReset = mode === 'reset';

  return (
    <div className="auth-wrap">
      <aside className="auth-aside">
        <div style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '1.1rem', letterSpacing: '-0.02em' }}>CareerPath</div>
        <h2>Welcome back.</h2>
        <ul>
          {POINTS.map((p) => (
            <li key={p}><Check size={16} style={{ flexShrink: 0, marginTop: 3 }} /> {p}</li>
          ))}
        </ul>
      </aside>

      <div className="auth-panel">
        <div className="auth-card">
          <Link to="/" className="faint" style={{ fontSize: '0.82rem' }}>← Back to home</Link>
          <h1 style={{ fontSize: '1.5rem', margin: '0.75rem 0 0.35rem' }}>
            {isReset ? 'Reset your password' : 'Sign in'}
          </h1>
          <p className="muted" style={{ fontSize: '0.86rem', marginBottom: '1.4rem' }}>
            {isReset
              ? 'Enter your account email and a new password.'
              : 'Continue building your roadmap.'}
          </p>
          <form onSubmit={submit} style={{ display: 'grid', gap: '0.9rem' }}>
            <div>
              <label>Email</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoFocus />
            </div>
            <div>
              <label>{isReset ? 'New password' : 'Password'}</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            {isReset && (
              <div>
                <label>Confirm new password</label>
                <input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required />
              </div>
            )}
            {err && <div className="badge badge-bad" style={{ padding: '0.5rem 0.7rem' }}>{err}</div>}
            <button className="btn-primary" type="submit" disabled={busy} style={{ width: '100%' }}>
              {busy
                ? (isReset ? 'Updating…' : 'Signing in…')
                : (isReset ? 'Set new password' : 'Sign in')}
            </button>
          </form>

          <p className="muted" style={{ fontSize: '0.85rem', marginTop: '1.1rem' }}>
            {isReset ? (
              <>Remembered it? <button type="button" className="link-btn" onClick={() => switchMode('login')}>Back to sign in</button></>
            ) : (
              <>Forgot your password? <button type="button" className="link-btn" onClick={() => switchMode('reset')}>Reset it</button></>
            )}
          </p>
          <p className="muted" style={{ fontSize: '0.85rem', marginTop: '0.3rem' }}>
            New here? <Link to="/register">Create an account</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
