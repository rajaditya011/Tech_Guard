import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

const API_URL = import.meta.env.VITE_API_URL || '';

// Demo mode: activated automatically when the backend is unreachable.
// Provides a fully functional frontend experience without a live API.
const DEMO_TOKEN = 'demo_token_homeguardian_ai_2026';
const DEMO_USER = { role: 'new_device', username: 'demo_admin', demo: true };

async function isBackendReachable() {
  try {
    const res = await fetch(`${API_URL}/api/auth/me`, {
      method: 'HEAD',
      signal: AbortSignal.timeout(3000),
    });
    // If we get any HTTP response (even 401), the backend is alive
    return true;
  } catch {
    return false;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('hg-token'));
  const [loading, setLoading] = useState(true);
  const [demoMode, setDemoMode] = useState(false);

  useEffect(() => {
    if (token) {
      // If it's a demo token, restore demo session immediately
      if (token === DEMO_TOKEN) {
        setUser(DEMO_USER);
        setDemoMode(true);
        setLoading(false);
      } else {
        fetchUser();
      }
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const res = await fetch(`${API_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data);
      } else {
        logout();
      }
    } catch {
      logout();
    } finally {
      setLoading(false);
    }
  };

  const enterDemoMode = (role = 'new_device') => {
    const demoUser = { ...DEMO_USER, role };
    setToken(DEMO_TOKEN);
    setUser(demoUser);
    setDemoMode(true);
    localStorage.setItem('hg-token', DEMO_TOKEN);
    localStorage.setItem('hg-refresh', 'demo_refresh');
    localStorage.setItem('hg-role', role);
    return { access_token: DEMO_TOKEN, refresh_token: 'demo_refresh', role };
  };

  const login = async (deviceName, password) => {
    try {
      const res = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_name: deviceName, password })
      });

      if (!res.ok) {
        let errMsg = 'Login failed';
        try { const err = await res.json(); errMsg = err.detail || errMsg; } catch {}
        throw new Error(errMsg);
      }

      const data = await res.json();
      setToken(data.access_token);
      localStorage.setItem('hg-token', data.access_token);
      localStorage.setItem('hg-refresh', data.refresh_token);
      localStorage.setItem('hg-role', data.role);
      setUser({ role: data.role });
      return data;
    } catch (err) {
      // If the backend is unreachable, fall back to demo mode
      const backendUp = await isBackendReachable();
      if (!backendUp) {
        return enterDemoMode('new_device');
      }
      throw err;
    }
  };

  const register = async (deviceName, password, role) => {
    try {
      const res = await fetch(`${API_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_name: deviceName, password, role })
      });

      if (!res.ok) {
        let errMsg = 'Registration failed';
        try { const err = await res.json(); errMsg = err.detail || errMsg; } catch {}
        throw new Error(errMsg);
      }

      const data = await res.json();
      setToken(data.access_token);
      localStorage.setItem('hg-token', data.access_token);
      localStorage.setItem('hg-refresh', data.refresh_token);
      localStorage.setItem('hg-role', data.role);
      setUser({ role: data.role });
      return data;
    } catch (err) {
      // If the backend is unreachable, fall back to demo mode
      const backendUp = await isBackendReachable();
      if (!backendUp) {
        return enterDemoMode(role || 'new_device');
      }
      throw err;
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setDemoMode(false);
    localStorage.removeItem('hg-token');
    localStorage.removeItem('hg-refresh');
    localStorage.removeItem('hg-role');
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, demoMode, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
