import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Check } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const POINTS = [
  'Describe your goal in plain words — we handle the keywords',
  'Get scored career matches and skill-gap analysis',
  'Follow a prerequisite-ordered course roadmap',
];

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [err, setErr] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setErr(null);
    if (password.length < 6) { setErr('Password must be at least 6 characters.'); return; }
    setBusy(true);
    try {
      await register(email, password, fullName);
      navigate('/app/profile');
    } catch (e2) {
      setErr(e2.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-wrap">
      <aside className="auth-aside">
        <div style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '1.1rem', letterSpacing: '-0.02em' }}>CareerPath</div>
        <h2>Your roadmap starts with one sentence.</h2>
        <ul>
          {POINTS.map((p) => (
            <li key={p}><Check size={16} style={{ flexShrink: 0, marginTop: 3 }} /> {p}</li>
          ))}
        </ul>
      </aside>

      <div className="auth-panel">
        <div className="auth-card">
          <Link to="/" className="faint" style={{ fontSize: '0.82rem' }}>← Back to home</Link>
          <h1 style={{ fontSize: '1.5rem', margin: '0.75rem 0 0.35rem' }}>Create your account</h1>
          <p className="muted" style={{ fontSize: '0.86rem', marginBottom: '1.4rem' }}>
            Then describe yourself once and we&apos;ll set up your profile.
          </p>
          <form onSubmit={submit} style={{ display: 'grid', gap: '0.9rem' }}>
            <div>
              <label>Full name</label>
              <input value={fullName} onChange={(e) => setFullName(e.target.value)} required autoFocus />
            </div>
            <div>
              <label>Email</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div>
              <label>Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
              <p className="faint" style={{ fontSize: '0.76rem', marginTop: '0.3rem' }}>At least 6 characters.</p>
            </div>
            {err && <div className="badge badge-bad" style={{ padding: '0.5rem 0.7rem' }}>{err}</div>}
            <button className="btn-primary" type="submit" disabled={busy} style={{ width: '100%' }}>
              {busy ? 'Creating…' : 'Create account'}
            </button>
          </form>
          <p className="muted" style={{ fontSize: '0.85rem', marginTop: '1.1rem' }}>
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
