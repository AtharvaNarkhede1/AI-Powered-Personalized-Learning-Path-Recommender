import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { api, setAuthToken } from '../api/client';

const AuthContext = createContext(null);
const TOKEN_KEY = 'cp_token';

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) || null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!localStorage.getItem(TOKEN_KEY));

  setAuthToken(token);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setAuthToken(null);
    setToken(null);
    setUser(null);
  }, []);

  const applyToken = useCallback((res) => {
    localStorage.setItem(TOKEN_KEY, res.access_token);
    setAuthToken(res.access_token);
    setToken(res.access_token);
    setUser({ user_id: res.user_id, email: res.email, full_name: res.full_name });
  }, []);

  const login = useCallback(async (email, password) => {
    applyToken(await api.login({ email, password }));
  }, [applyToken]);

  const register = useCallback(async (email, password, full_name) => {
    applyToken(await api.register({ email, password, full_name }));
  }, [applyToken]);

  // hydrate on load / token change
  useEffect(() => {
    if (!token) { setLoading(false); return; }
    let alive = true;
    setAuthToken(token);
    api.me()
      .then((me) => { if (alive) setUser(me); })
      .catch(() => { if (alive) logout(); })
      .finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, [token, logout]);

  useEffect(() => {
    const handler = () => logout();
    window.addEventListener('auth:logout', handler);
    return () => window.removeEventListener('auth:logout', handler);
  }, [logout]);

  return (
    <AuthContext.Provider value={{ token, user, loading, login, register, logout, isAuthed: !!token }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
