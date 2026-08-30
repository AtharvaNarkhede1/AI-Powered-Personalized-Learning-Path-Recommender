import React, { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { api } from '../api/client';
import { useAuth } from './AuthContext';

const AppDataContext = createContext(null);

export function AppDataProvider({ children }) {
  const { isAuthed, user } = useAuth();

  const [profile, setProfile] = useState(null);
  const [discovery, setDiscovery] = useState(null);
  const [activePath, setActivePath] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const careerId = profile?.target_career_id || activePath?.career_id || null;

  const loadedFor = useRef(null);

  const refreshProfile = useCallback(async () => {
    const p = await api.getProfile();
    setProfile(p);
    return p;
  }, []);

  const refreshDashboard = useCallback(async (cid = null) => {
    try {
      const d = await api.getDashboardMetrics(cid);
      setDashboard(d);
      if (d?.active_path) setActivePath(d.active_path);
      return d;
    } catch {
      setDashboard(null);
      return null;
    }
  }, []);

  // initial load after auth
  useEffect(() => {
    if (!isAuthed || !user) {
      setProfile(null); setDiscovery(null); setActivePath(null); setDashboard(null);
      loadedFor.current = null;
      return;
    }
    if (loadedFor.current === user.user_id) return;
    loadedFor.current = user.user_id;
    setLoadingProfile(true);
    (async () => {
      try {
        const p = await refreshProfile();
        await refreshDashboard(p?.target_career_id || null);
      } finally {
        setLoadingProfile(false);
      }
    })();
  }, [isAuthed, user, refreshProfile, refreshDashboard]);

  const saveProfile = useCallback(async (data) => {
    const p = await api.saveProfile(data);
    setProfile(p);
    return p;
  }, []);

  const runDiscovery = useCallback(async (mergedProfile) => {
    const p = await api.saveProfile(mergedProfile);
    setProfile(p);
    const d = await api.discoverCareers(mergedProfile);
    setDiscovery(d);
    return d;
  }, []);

  const selectCareer = useCallback(async (cid) => {
    const merged = { ...(profile || {}), target_career_id: cid };
    const path = await api.generatePath(cid, merged);
    setActivePath(path);
    setProfile((prev) => ({ ...(prev || {}), target_career_id: cid }));
    await refreshDashboard(cid);
    return path;
  }, [profile, refreshDashboard]);

  const withPath = (fn) => async (...args) => {
    const path = await fn(...args);
    setActivePath(path);
    refreshDashboard(path.career_id);
    return path;
  };

  const regeneratePath = useCallback(withPath((cid) => api.regeneratePath(cid)), [refreshDashboard]);
  const toggleResource = useCallback(withPath((cid, rid) => api.toggleResource(cid, rid)), [refreshDashboard]);
  const toggleMilestone = useCallback(withPath((cid, mk) => api.toggleMilestone(cid, mk)), [refreshDashboard]);
  const addCourse = useCallback(withPath((cid, courseId, mk) => api.addCourseToPath(cid, courseId, mk)), [refreshDashboard]);
  const removeCourse = useCallback(withPath((cid, rid, mk) => api.removeCourseFromPath(cid, rid, mk)), [refreshDashboard]);

  return (
    <AppDataContext.Provider value={{
      profile, discovery, activePath, dashboard, careerId, loadingProfile,
      setDiscovery,
      refreshProfile, refreshDashboard, saveProfile, runDiscovery, selectCareer,
      regeneratePath, toggleResource, toggleMilestone, addCourse, removeCourse,
    }}>
      {children}
    </AppDataContext.Provider>
  );
}

export function useAppData() {
  const ctx = useContext(AppDataContext);
  if (!ctx) throw new Error('useAppData must be used within AppDataProvider');
  return ctx;
}
