# Chunk 06 — Frontend Shell and Design System

**Goal**: Initialize the React + Vite project, install all dependencies, set up the full design token system, theme provider, router, and global layout components.
**Estimated Time**: 45 minutes
**Dependencies**: Chunk 02 (Backend Core)
**Unlocks**: Chunk 07 (Old Device Portal), Chunk 08 (New Device Dashboard) — both can start in parallel.

---

## 06.1 — Initialize Vite Project

```bash
cd frontend
npx -y create-vite@latest ./ -- --template react
npm install
npm install react-router-dom@6 zustand@4 @tanstack/react-query@5 framer-motion@10 socket.io-client@4 clsx@2
npm install -D tailwindcss@3 postcss@8 autoprefixer@10
npx tailwindcss init -p
```

---

## 06.2 — Tailwind Configuration (frontend/tailwind.config.js)

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg: {
          primary: 'var(--bg-primary)',
          secondary: 'var(--bg-secondary)',
          tertiary: 'var(--bg-tertiary)',
          surface: 'var(--bg-surface)',
          glass: 'var(--bg-glass)',
        },
        text: {
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          tertiary: 'var(--text-tertiary)',
        },
        accent: {
          blue: 'var(--accent-blue)',
          violet: 'var(--accent-violet)',
          emerald: 'var(--accent-emerald)',
          amber: 'var(--accent-amber)',
          red: 'var(--accent-red)',
        },
        border: {
          primary: 'var(--border-primary)',
          secondary: 'var(--border-secondary)',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        'sm': 'var(--radius-sm)',
        'md': 'var(--radius-md)',
        'lg': 'var(--radius-lg)',
        'xl': 'var(--radius-xl)',
        '2xl': 'var(--radius-2xl)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow-sweep 2s ease-in-out infinite alternate',
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
      },
      keyframes: {
        'glow-sweep': {
          '0%': { opacity: '0.5' },
          '100%': { opacity: '1' },
        },
        'fadeIn': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slideUp': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slideInRight': {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
      },
    },
  },
  plugins: [],
}
```

---

## 06.3 — Global CSS (frontend/src/index.css)

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

/* ============================= */
/* DESIGN TOKEN SYSTEM           */
/* ============================= */

/* --- DARK THEME (default) --- */
:root {
  /* Backgrounds */
  --bg-primary: #08090f;
  --bg-secondary: #0f1119;
  --bg-tertiary: #161822;
  --bg-surface: rgba(255, 255, 255, 0.03);
  --bg-glass: rgba(255, 255, 255, 0.05);
  --bg-glass-hover: rgba(255, 255, 255, 0.08);

  /* Text */
  --text-primary: #f0f0f5;
  --text-secondary: #8b8fa3;
  --text-tertiary: #555870;
  --text-inverse: #08090f;

  /* Accents */
  --accent-blue: #3b82f6;
  --accent-blue-glow: rgba(59, 130, 246, 0.3);
  --accent-violet: #8b5cf6;
  --accent-violet-glow: rgba(139, 92, 246, 0.3);
  --accent-emerald: #10b981;
  --accent-emerald-glow: rgba(16, 185, 129, 0.3);
  --accent-amber: #f59e0b;
  --accent-amber-glow: rgba(245, 158, 11, 0.3);
  --accent-red: #ef4444;
  --accent-red-glow: rgba(239, 68, 68, 0.3);

  /* Borders */
  --border-primary: rgba(255, 255, 255, 0.06);
  --border-secondary: rgba(255, 255, 255, 0.10);
  --border-accent: rgba(59, 130, 246, 0.3);

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);
  --shadow-glow-blue: 0 0 20px rgba(59, 130, 246, 0.2);
  --shadow-glow-violet: 0 0 20px rgba(139, 92, 246, 0.2);
  --shadow-glow-emerald: 0 0 20px rgba(16, 185, 129, 0.2);
  --shadow-glow-red: 0 0 20px rgba(239, 68, 68, 0.3);

  /* Radii */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-2xl: 24px;

  /* Animation */
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* --- LIGHT THEME --- */
[data-theme="light"] {
  --bg-primary: #ffffff;
  --bg-secondary: #f8f9fc;
  --bg-tertiary: #f0f1f5;
  --bg-surface: rgba(0, 0, 0, 0.02);
  --bg-glass: rgba(255, 255, 255, 0.80);
  --bg-glass-hover: rgba(255, 255, 255, 0.90);

  --text-primary: #111827;
  --text-secondary: #6b7280;
  --text-tertiary: #9ca3af;
  --text-inverse: #ffffff;

  --accent-blue: #2563eb;
  --accent-blue-glow: rgba(37, 99, 235, 0.15);
  --accent-violet: #7c3aed;
  --accent-violet-glow: rgba(124, 58, 237, 0.15);
  --accent-emerald: #059669;
  --accent-emerald-glow: rgba(5, 150, 105, 0.15);
  --accent-amber: #d97706;
  --accent-amber-glow: rgba(217, 119, 6, 0.15);
  --accent-red: #dc2626;
  --accent-red-glow: rgba(220, 38, 38, 0.15);

  --border-primary: rgba(0, 0, 0, 0.06);
  --border-secondary: rgba(0, 0, 0, 0.10);
  --border-accent: rgba(37, 99, 235, 0.3);

  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.12);
  --shadow-glow-blue: 0 0 20px rgba(37, 99, 235, 0.1);
  --shadow-glow-violet: 0 0 20px rgba(124, 58, 237, 0.1);
  --shadow-glow-emerald: 0 0 20px rgba(5, 150, 105, 0.1);
  --shadow-glow-red: 0 0 20px rgba(220, 38, 38, 0.15);
}

/* ============================= */
/* BASE STYLES                   */
/* ============================= */

*, *::before, *::after {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.6;
  transition: background-color var(--duration-normal) var(--ease-out),
              color var(--duration-normal) var(--ease-out);
}

/* ============================= */
/* SCROLLBAR                     */
/* ============================= */

::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--border-secondary);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-tertiary);
}

/* ============================= */
/* UTILITY CLASSES               */
/* ============================= */

.glass-card {
  background: var(--bg-glass);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
}

.glass-card:hover {
  background: var(--bg-glass-hover);
  border-color: var(--border-secondary);
}

.gradient-text {
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-violet), var(--accent-emerald));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.glow-blue { box-shadow: var(--shadow-glow-blue); }
.glow-violet { box-shadow: var(--shadow-glow-violet); }
.glow-emerald { box-shadow: var(--shadow-glow-emerald); }
.glow-red { box-shadow: var(--shadow-glow-red); }
```

---

## 06.4 — Theme Context (frontend/src/contexts/ThemeContext.jsx)

```jsx
import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    const stored = localStorage.getItem('hg-theme');
    return stored || 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('hg-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}
```

---

## 06.5 — Auth Context (frontend/src/contexts/AuthContext.jsx)

```jsx
import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('hg-token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      fetchUser();
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

  const login = async (deviceName, password) => {
    const res = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ device_name: deviceName, password })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Login failed');
    }

    const data = await res.json();
    setToken(data.access_token);
    localStorage.setItem('hg-token', data.access_token);
    localStorage.setItem('hg-refresh', data.refresh_token);
    localStorage.setItem('hg-role', data.role);
    setUser({ role: data.role });
    return data;
  };

  const register = async (deviceName, password, role) => {
    const res = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ device_name: deviceName, password, role })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Registration failed');
    }

    const data = await res.json();
    setToken(data.access_token);
    localStorage.setItem('hg-token', data.access_token);
    localStorage.setItem('hg-refresh', data.refresh_token);
    localStorage.setItem('hg-role', data.role);
    setUser({ role: data.role });
    return data;
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('hg-token');
    localStorage.removeItem('hg-refresh');
    localStorage.removeItem('hg-role');
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
```

---

## 06.6 — Router Setup (frontend/src/App.jsx)

```jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Pages (stub components — built in Chunks 07 and 08)
import OldDeviceLogin from './pages/OldDeviceLogin';
import OldDevicePortal from './pages/OldDevicePortal';
import NewDeviceLogin from './pages/NewDeviceLogin';
import NewDeviceDashboard from './pages/NewDeviceDashboard';
import DemoPage from './pages/DemoPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5000,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              {/* Old Device Portal */}
              <Route path="/old-device/login" element={<OldDeviceLogin />} />
              <Route path="/old-device/portal" element={<OldDevicePortal />} />

              {/* New Device Dashboard */}
              <Route path="/new-device/login" element={<NewDeviceLogin />} />
              <Route path="/new-device/dashboard" element={<NewDeviceDashboard />} />

              {/* Demo Mode */}
              <Route path="/demo" element={<DemoPage />} />

              {/* Default redirect */}
              <Route path="/" element={<Navigate to="/new-device/login" replace />} />
              <Route path="*" element={<Navigate to="/new-device/login" replace />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
```

---

## 06.7 — Layout Components

### ThemeToggle (frontend/src/components/layout/ThemeToggle.jsx)

```jsx
import { useTheme } from '../../contexts/ThemeContext';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      id="theme-toggle-btn"
      onClick={toggleTheme}
      className="glass-card px-3 py-1.5 text-xs font-mono uppercase tracking-wider
                 cursor-pointer transition-all duration-200
                 hover:border-[var(--accent-blue)]"
      style={{
        color: 'var(--text-secondary)',
        border: '1px solid var(--border-secondary)',
      }}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
    >
      {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
    </button>
  );
}
```

### AppShell (frontend/src/components/layout/AppShell.jsx)

```jsx
import ThemeToggle from './ThemeToggle';

export default function AppShell({ children, showThemeToggle = true }) {
  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}
    >
      {showThemeToggle && (
        <div className="fixed top-4 right-4 z-50">
          <ThemeToggle />
        </div>
      )}
      {children}
    </div>
  );
}
```

---

## 06.8 — Stub Pages (for routing to work)

Create minimal stub files for pages. These will be fully built in Chunks 07 and 08.

### frontend/src/pages/OldDeviceLogin.jsx
```jsx
import AppShell from '../components/layout/AppShell';

export default function OldDeviceLogin() {
  return (
    <AppShell>
      <div className="flex items-center justify-center min-h-screen">
        <div className="glass-card p-8 max-w-md w-full mx-4">
          <h1 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
            Old Device Portal
          </h1>
          <p style={{ color: 'var(--text-secondary)' }}>Login page — built in Chunk 07</p>
        </div>
      </div>
    </AppShell>
  );
}
```

### frontend/src/pages/OldDevicePortal.jsx
```jsx
import AppShell from '../components/layout/AppShell';
export default function OldDevicePortal() {
  return <AppShell><div className="p-8"><h1>Old Device Portal — Chunk 07</h1></div></AppShell>;
}
```

### frontend/src/pages/NewDeviceLogin.jsx
```jsx
import AppShell from '../components/layout/AppShell';
export default function NewDeviceLogin() {
  return (
    <AppShell>
      <div className="flex items-center justify-center min-h-screen">
        <div className="glass-card p-8 max-w-md w-full mx-4">
          <h1 className="text-2xl font-bold gradient-text mb-2">HomeGuardian AI</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Owner login — built in Chunk 08</p>
        </div>
      </div>
    </AppShell>
  );
}
```

### frontend/src/pages/NewDeviceDashboard.jsx
```jsx
import AppShell from '../components/layout/AppShell';
export default function NewDeviceDashboard() {
  return <AppShell><div className="p-8"><h1>Dashboard — Chunk 08</h1></div></AppShell>;
}
```

### frontend/src/pages/DemoPage.jsx
```jsx
import AppShell from '../components/layout/AppShell';
export default function DemoPage() {
  return <AppShell><div className="p-8"><h1>Demo Mode — Chunk 09</h1></div></AppShell>;
}
```

---

## 06.9 — Entry Point (frontend/src/main.jsx)

```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

---

## 06.10 — HTML Entry (frontend/index.html)

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="HomeGuardian AI — Adaptive Intelligence Security System" />
    <title>HomeGuardian AI</title>
    <link rel="icon" type="image/x-icon" href="/favicon.ico" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

---

## Verification

```bash
# 1. Start the frontend dev server
cd frontend
npm run dev

# 2. Open browser
# Navigate to http://localhost:5173
# Should see the New Device Login stub page with dark theme
# Click theme toggle — should switch to light theme

# 3. Test routes
# http://localhost:5173/old-device/login  -- Old Device Portal stub
# http://localhost:5173/new-device/login  -- New Device Login stub
# http://localhost:5173/new-device/dashboard  -- Dashboard stub
# http://localhost:5173/demo  -- Demo page stub

# 4. Verify design tokens
# Open DevTools > Elements > Computed
# Check that CSS variables are applied correctly

# 5. Verify build
npm run build
# Should complete without errors
```

Expected: Frontend dev server starts on port 5173. All five routes render correctly. Theme toggle switches between dark and light. CSS variables apply throughout. Build succeeds.
