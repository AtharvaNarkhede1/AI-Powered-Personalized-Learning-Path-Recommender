import React from 'react';
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom';
import { LayoutDashboard, UserRound, Compass, BookOpen, Route as RouteIcon, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import AssistantWidget from './AssistantWidget';

const LINKS = [
  { to: '/app/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/app/profile', label: 'Profile', icon: UserRound },
  { to: '/app/discover', label: 'Find My Career', icon: Compass },
  { to: '/app/courses', label: 'Course Recommendations', icon: BookOpen },
  { to: '/app/roadmap', label: 'Roadmap', icon: RouteIcon },
];

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => { logout(); navigate('/'); };

  return (
    <div className="app-shell">
      <aside style={{
        width: 244, flexShrink: 0, borderRight: '1px solid var(--border)',
        background: 'var(--surface)', display: 'flex', flexDirection: 'column',
        position: 'sticky', top: 0, height: '100vh',
      }}>
        <Link to="/" title="Back to home"
          style={{ display: 'block', padding: '1.25rem 1.25rem 1rem', borderBottom: '1px solid var(--border)', textDecoration: 'none' }}>
          <div style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '1.05rem', letterSpacing: '-0.02em', color: 'var(--text)' }}>
            CareerPath
          </div>
          <div className="faint mono" style={{ fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Learning OS
          </div>
        </Link>

        <nav style={{ padding: '0.75rem', display: 'grid', gap: 2, flex: 1 }}>
          {LINKS.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} style={({ isActive }) => ({
              display: 'flex', alignItems: 'center', gap: '0.6rem',
              padding: '0.55rem 0.7rem', borderRadius: 'var(--radius-sm)',
              fontSize: '0.88rem', fontWeight: 500, textDecoration: 'none',
              color: isActive ? 'var(--accent)' : 'var(--muted)',
              background: isActive ? 'var(--accent-weak)' : 'transparent',
            })}>
              <Icon size={17} /> {label}
            </NavLink>
          ))}
        </nav>

        <div style={{ padding: '0.9rem', borderTop: '1px solid var(--border)' }}>
          <div style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {user?.full_name || 'Learner'}
          </div>
          <div className="faint" style={{ fontSize: '0.74rem', marginBottom: '0.6rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {user?.email}
          </div>
          <button className="btn-ghost btn-sm" onClick={handleLogout} style={{ width: '100%' }}>
            <LogOut size={14} /> Sign out
          </button>
        </div>
      </aside>

      <main className="app-main">
        <Outlet />
      </main>

      <AssistantWidget />
    </div>
  );
}
