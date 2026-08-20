import { createContext, useContext, useEffect, useState } from 'react';
import client, { getApiErrorMessage } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadMe = async ({ clearInvalidToken = true, throwOnError = false } = {}) => {
    const token = localStorage.getItem('token');
    if (!token) {
      setLoading(false);
      return null;
    }

    try {
      const { data } = await client.get('/auth/me');
      setUser(data);
      return data;
    } catch (error) {
      if (clearInvalidToken) localStorage.removeItem('token');
      setUser(null);
      if (throwOnError) throw error;
      return null;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMe();
  }, []);

  const login = async (username, password) => {
    try {
      const form = new URLSearchParams();
      form.append('username', username);
      form.append('password', password);
      const { data } = await client.post('/auth/login', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      localStorage.setItem('token', data.access_token);
      await loadMe({ clearInvalidToken: true, throwOnError: true });
    } catch (error) {
      localStorage.removeItem('token');
      setUser(null);
      const normalized = new Error(getApiErrorMessage(error, 'No se pudo iniciar sesión.'));
      normalized.cause = error;
      throw normalized;
    }
  };

  const register = async (payload) => {
    await client.post('/auth/register', payload);
    await login(payload.username, payload.password);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
