import React, { useEffect, useState } from 'react';
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, UserRound, Compass, BookOpen, Route as RouteIcon,
  LogOut, Menu, X, PanelLeftClose, PanelLeftOpen,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import AssistantWidget from './AssistantWidget';

const LINKS = [
  { to: '/app/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/app/profile', label: 'Profile', icon: UserRound },
  { to: '/app/discover', label: 'Find My Career', icon: Compass },
  { to: '/app/courses', label: 'Course Recommendations', icon: BookOpen },
  { to: '/app/roadmap', label: 'Roadmap', icon: RouteIcon },
];

const COLLAPSE_KEY = 'cp_sidebar_collapsed';

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Desktop: rail vs full sidebar (persisted). Mobile: off-canvas drawer.
  const [collapsed, setCollapsed] = useState(
    () => localStorage.getItem(COLLAPSE_KEY) === '1',
  );
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    localStorage.setItem(COLLAPSE_KEY, collapsed ? '1' : '0');
  }, [collapsed]);

  // Close the mobile drawer on navigation.
  useEffect(() => { setMobileOpen(false); }, [location.pathname]);

  // Close the mobile drawer with Escape.
  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') setMobileOpen(false); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const handleLogout = () => { logout(); navigate('/'); };

  const sidebarClass = [
    'sidebar',
    collapsed ? 'sidebar--collapsed' : '',
    mobileOpen ? 'sidebar--open' : '',
  ].filter(Boolean).join(' ');

  return (
    <div className="app-shell">
      <header className="app-topbar">
        <button
          className="icon-btn"
          aria-label="Open menu"
          onClick={() => setMobileOpen(true)}
        >
          <Menu size={20} />
        </button>
        <div className="app-topbar__title">CareerPath</div>
      </header>

      {mobileOpen && (
        <div className="sidebar-backdrop" onClick={() => setMobileOpen(false)} />
      )}

      <aside className={sidebarClass}>
        <div className="sidebar__head">
          <Link to="/" title="Back to home" className="sidebar__brand">
            <div className="sidebar__brand-name">CareerPath</div>
            <div className="sidebar__brand-sub faint mono">Learning OS</div>
          </Link>
          <button
            className="icon-btn sidebar__mobile-close"
            aria-label="Close menu"
            onClick={() => setMobileOpen(false)}
          >
            <X size={18} />
          </button>
        </div>

        <nav className="sidebar__nav">
          {LINKS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              title={collapsed ? label : undefined}
              className={({ isActive }) =>
                `sidebar__link${isActive ? ' sidebar__link--active' : ''}`
              }
            >
              <Icon size={17} className="sidebar__link-icon" />
              <span className="sidebar__link-label">{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar__foot">
          <button
            className="icon-btn sidebar__collapse-btn"
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            onClick={() => setCollapsed((c) => !c)}
          >
            {collapsed ? <PanelLeftOpen size={17} /> : <PanelLeftClose size={17} />}
            <span className="sidebar__link-label">Collapse</span>
          </button>

          <div className="sidebar__user">
            <div className="sidebar__user-name">{user?.full_name || 'Learner'}</div>
            <div className="sidebar__user-email faint">{user?.email}</div>
          </div>
          <button className="btn-ghost btn-sm sidebar__signout" onClick={handleLogout}>
            <LogOut size={14} /> <span className="sidebar__link-label">Sign out</span>
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
