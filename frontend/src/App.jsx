import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';

import { useAuth } from './context/AuthContext';
import AppLayout from './components/AppLayout';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ProfilePage from './pages/ProfilePage';
import DiscoverPage from './pages/DiscoverPage';
import CoursesPage from './pages/CoursesPage';
import RoadmapPage from './pages/RoadmapPage';

function RequireAuth({ children }) {
  const { isAuthed, loading } = useAuth();
  if (loading) return <div className="page">Loading…</div>;
  if (!isAuthed) return <Navigate to="/login" replace />;
  return children;
}

function RedirectIfAuthed({ children }) {
  const { isAuthed, loading } = useAuth();
  if (loading) return <div className="page">Loading…</div>;
  if (isAuthed) return <Navigate to="/app/dashboard" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<RedirectIfAuthed><LoginPage /></RedirectIfAuthed>} />
      <Route path="/register" element={<RedirectIfAuthed><RegisterPage /></RedirectIfAuthed>} />

      <Route path="/app" element={<RequireAuth><AppLayout /></RequireAuth>}>
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="discover" element={<DiscoverPage />} />
        <Route path="courses" element={<CoursesPage />} />
        <Route path="roadmap" element={<RoadmapPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
