'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { api } from './api-client';

interface User {
  id: string;
  email: string;
  full_name: string;
  tenant_id: string;
  tenant_name: string;
  roles: string[];
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  loading: true,
  login: async () => {},
  logout: () => {},
  isAuthenticated: false,
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = async () => {
    try {
      const userData = await api.getCurrentUser();
      setUser(userData);
    } catch (err) {
      console.error('Failed to fetch current user', err);
      setUser(null);
      setToken(null);
      if (typeof window !== 'undefined') {
        localStorage.removeItem('investops_token');
      }
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string) => {
    setLoading(true);
    try {
      const data = await api.login(email);
      const authToken = data.access_token;
      setToken(authToken);
      if (typeof window !== 'undefined') {
        localStorage.setItem('investops_token', authToken);
      }
      await fetchUser();
    } catch (err) {
      setLoading(false);
      throw err;
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('investops_token');
    }
  };

  useEffect(() => {
    const existingToken = typeof window !== 'undefined' ? localStorage.getItem('investops_token') : null;
    if (existingToken) {
      setToken(existingToken);
      fetchUser();
    } else {
      // Auto-login default demo user for seamless demo experience
      login('approver@investops.ai').catch((err) => {
        console.warn('Auto-login fallback:', err);
        setLoading(false);
      });
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
