import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('lexai_token'));
  const [loading, setLoading] = useState(true);

  // Restore session on mount
  useEffect(() => {
    if (token) {
      // Demo tokens — restore user from localStorage, no backend call needed
      if (token.startsWith('demo_')) {
        try {
          const saved = JSON.parse(localStorage.getItem('lexai_user') || 'null');
          if (saved) { setUser(saved); }
        } catch { /* ignore */ }
        setLoading(false);
        return;
      }
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      axios.get('/auth/me')
        .then(res => setUser(res.data))
        .catch(() => {
          localStorage.removeItem('lexai_token');
          setToken(null);
          delete axios.defaults.headers.common['Authorization'];
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback((accessToken, userData) => {
    localStorage.setItem('lexai_token', accessToken);
    localStorage.setItem('lexai_user', JSON.stringify(userData));
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
    setToken(accessToken);
    setUser(userData);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('lexai_token');
    localStorage.removeItem('lexai_user');
    delete axios.defaults.headers.common['Authorization'];
    setToken(null);
    setUser(null);
  }, []);

  const isAuthenticated = !!token && !!user;
  const isLawyer = user?.is_lawyer === true;
  const isVerified = user?.is_active === true;
  const isPendingVerification =
    isLawyer && user?.verification_status?.includes('pending');

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      login,
      logout,
      isAuthenticated,
      isLawyer,
      isVerified,
      isPendingVerification,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}
