# Chunk 08 — New Device Dashboard

**Goal**: Build the complete owner dashboard — login, sidebar, live feed grid, floor plan visualizer, alert feed, AI narrative modal, risk gauge, sensor health, communication panel, and notification history.
**Estimated Time**: 90 minutes
**Dependencies**: Chunk 06 (Frontend Shell)
**Unlocks**: Chunk 09 (Secret Weapon + Security + Deploy)

---

## 08.1 — New Device Login (frontend/src/pages/NewDeviceLogin.jsx)

```jsx
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AppShell from '../components/layout/AppShell';

export default function NewDeviceLogin() {
  const [deviceName, setDeviceName] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isRegister) {
        await register(deviceName, password, 'new_device');
      } else {
        await login(deviceName, password);
      }
      navigate('/new-device/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="w-full max-w-md">
          {/* Branding */}
          <div className="text-center mb-10">
            <h1 className="text-4xl font-extrabold gradient-text mb-2">HomeGuardian AI</h1>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              Understanding behavior, not just detecting movement.
            </p>
          </div>

          {/* Login Card */}
          <div className="glass-card p-8" id="new-device-login-card">
            <div className="mb-6">
              <div
                className="inline-block px-3 py-1 rounded-full text-xs font-mono uppercase tracking-wider mb-4"
                style={{ background: 'var(--accent-violet-glow)', color: 'var(--accent-violet)' }}
              >
                Owner Dashboard
              </div>
              <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
                {isRegister ? 'Create Account' : 'Welcome Back'}
              </h2>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label
                  className="block text-xs font-mono uppercase tracking-wider mb-2"
                  style={{ color: 'var(--text-tertiary)' }}
                  htmlFor="nd-username"
                >
                  Username
                </label>
                <input
                  id="nd-username"
                  type="text"
                  value={deviceName}
                  onChange={(e) => setDeviceName(e.target.value)}
                  placeholder="Your username"
                  required
                  className="w-full px-4 py-3 rounded-lg text-sm outline-none transition-all"
                  style={{
                    background: 'var(--bg-surface)',
                    border: '1px solid var(--border-primary)',
                    color: 'var(--text-primary)',
                  }}
                />
              </div>

              <div className="mb-6">
                <label
                  className="block text-xs font-mono uppercase tracking-wider mb-2"
                  style={{ color: 'var(--text-tertiary)' }}
                  htmlFor="nd-password"
                >
                  Password
                </label>
                <input
                  id="nd-password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Minimum 6 characters"
                  required
                  minLength={6}
                  className="w-full px-4 py-3 rounded-lg text-sm outline-none transition-all"
                  style={{
                    background: 'var(--bg-surface)',
                    border: '1px solid var(--border-primary)',
                    color: 'var(--text-primary)',
                  }}
                />
              </div>

              {error && (
                <div
                  className="mb-4 px-4 py-2.5 rounded-lg text-sm"
                  style={{ background: 'var(--accent-red-glow)', color: 'var(--accent-red)' }}
                >
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                id="nd-submit-btn"
                className="w-full py-3 rounded-lg text-sm font-semibold transition-all cursor-pointer"
                style={{
                  background: loading ? 'var(--bg-surface)' : 'linear-gradient(135deg, var(--accent-blue), var(--accent-violet))',
                  color: '#ffffff',
                  opacity: loading ? 0.7 : 1,
                }}
              >
                {loading ? 'Signing in...' : isRegister ? 'Create Account' : 'Sign In'}
              </button>

              <button
                type="button"
                onClick={() => setIsRegister(!isRegister)}
                className="w-full mt-3 py-2 text-sm cursor-pointer bg-transparent border-none"
                style={{ color: 'var(--text-secondary)' }}
              >
                {isRegister ? 'Already have an account? Sign in' : 'New user? Create account'}
              </button>
            </form>

            {/* Demo Mode Link */}
            <div className="mt-6 pt-6" style={{ borderTop: '1px solid var(--border-primary)' }}>
              <Link
                to="/demo"
                className="block text-center text-sm font-medium no-underline transition-colors"
                style={{ color: 'var(--accent-emerald)' }}
              >
                Try Demo Mode (no account needed)
              </Link>
            </div>
          </div>

          {/* Old Device Link */}
          <p className="text-center text-xs mt-6" style={{ color: 'var(--text-tertiary)' }}>
            Setting up an old device?{' '}
            <Link to="/old-device/login" className="no-underline" style={{ color: 'var(--accent-blue)' }}>
              Old Device Portal
            </Link>
          </p>
        </div>
      </div>
    </AppShell>
  );
}
```

---

## 08.2 — Dashboard Page (frontend/src/pages/NewDeviceDashboard.jsx)

```jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AppShell from '../components/layout/AppShell';
import Sidebar from '../components/layout/Sidebar';
import LiveFeedGrid from '../components/dashboard/LiveFeedGrid';
import FloorPlan from '../components/dashboard/FloorPlan';
import AlertFeed from '../components/dashboard/AlertFeed';
import RiskGauge from '../components/dashboard/RiskGauge';
import SensorHealth from '../components/dashboard/SensorHealth';
import CommPanel from '../components/dashboard/CommPanel';

export default function NewDeviceDashboard() {
  const { user, token, logout } = useAuth();
  const navigate = useNavigate();
  const [activePanel, setActivePanel] = useState('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    if (!token) navigate('/new-device/login');
  }, [token, navigate]);

  const renderPanel = () => {
    switch (activePanel) {
      case 'overview': return <OverviewPanel />;
      case 'feeds': return <LiveFeedGrid />;
      case 'floorplan': return <FloorPlan />;
      case 'alerts': return <AlertFeed />;
      case 'sensors': return <SensorHealth />;
      case 'communicate': return <CommPanel />;
      default: return <OverviewPanel />;
    }
  };

  return (
    <AppShell>
      <div className="flex min-h-screen">
        {/* Sidebar */}
        <Sidebar
          activePanel={activePanel}
          onPanelChange={setActivePanel}
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          onLogout={() => { logout(); navigate('/new-device/login'); }}
        />

        {/* Main Content */}
        <main
          className="flex-1 overflow-y-auto"
          style={{
            marginLeft: sidebarCollapsed ? '64px' : '240px',
            transition: 'margin-left 0.3s ease',
          }}
        >
          {/* Header */}
          <header
            className="sticky top-0 z-40 px-6 py-4 flex items-center justify-between"
            style={{
              background: 'var(--bg-primary)',
              borderBottom: '1px solid var(--border-primary)',
              backdropFilter: 'blur(12px)',
            }}
          >
            <div>
              <h1 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                {activePanel.charAt(0).toUpperCase() + activePanel.slice(1)}
              </h1>
              <p className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
                Real-time security intelligence
              </p>
            </div>
            <div className="flex items-center gap-4">
              <RiskGauge score={12} size="small" />
            </div>
          </header>

          {/* Content */}
          <div className="p-6">
            {renderPanel()}
          </div>
        </main>
      </div>
    </AppShell>
  );
}

/* Overview Panel — shows all key widgets */
function OverviewPanel() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Row 1: Risk + Stats */}
      <div className="lg:col-span-1">
        <div className="glass-card p-6 flex flex-col items-center">
          <RiskGauge score={12} size="large" />
          <p className="text-xs mt-3 font-mono uppercase" style={{ color: 'var(--text-tertiary)' }}>
            System Risk Level
          </p>
        </div>
      </div>
      <div className="lg:col-span-2">
        <div className="grid grid-cols-2 gap-4">
          <StatCard label="Active Sensors" value="3" accent="blue" />
          <StatCard label="Anomalies Today" value="0" accent="emerald" />
          <StatCard label="Alerts Sent" value="0" accent="violet" />
          <StatCard label="Baseline Status" value="35%" accent="amber" />
        </div>
      </div>

      {/* Row 2: Live Feeds */}
      <div className="lg:col-span-2">
        <LiveFeedGrid compact />
      </div>
      <div className="lg:col-span-1">
        <AlertFeed compact />
      </div>

      {/* Row 3: Floor Plan */}
      <div className="lg:col-span-3">
        <FloorPlan compact />
      </div>
    </div>
  );
}

function StatCard({ label, value, accent }) {
  return (
    <div className="glass-card p-4 text-center">
      <div className="text-2xl font-bold mb-1" style={{ color: `var(--accent-${accent})` }}>
        {value}
      </div>
      <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>{label}</div>
    </div>
  );
}
```

---

## 08.3 — Sidebar (frontend/src/components/layout/Sidebar.jsx)

```jsx
export default function Sidebar({ activePanel, onPanelChange, collapsed, onToggle, onLogout }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: 'O' },
    { id: 'feeds', label: 'Live Feeds', icon: 'F' },
    { id: 'floorplan', label: 'Floor Plan', icon: 'P' },
    { id: 'alerts', label: 'Alerts', icon: 'A' },
    { id: 'sensors', label: 'Sensors', icon: 'S' },
    { id: 'communicate', label: 'Communicate', icon: 'C' },
  ];

  return (
    <aside
      className="fixed top-0 left-0 h-screen flex flex-col z-50"
      style={{
        width: collapsed ? '64px' : '240px',
        background: 'var(--bg-secondary)',
        borderRight: '1px solid var(--border-primary)',
        transition: 'width 0.3s ease',
      }}
      id="dashboard-sidebar"
    >
      {/* Logo */}
      <div className="p-4 flex items-center gap-3" style={{ borderBottom: '1px solid var(--border-primary)' }}>
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0"
          style={{ background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-violet))', color: '#fff' }}
        >
          HG
        </div>
        {!collapsed && (
          <span className="text-sm font-semibold truncate" style={{ color: 'var(--text-primary)' }}>
            HomeGuardian
          </span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-1">
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => onPanelChange(item.id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm
                       cursor-pointer transition-all border-none`}
            style={{
              background: activePanel === item.id ? 'var(--bg-glass)' : 'transparent',
              color: activePanel === item.id ? 'var(--text-primary)' : 'var(--text-secondary)',
            }}
            id={`nav-${item.id}`}
          >
            <span
              className="w-7 h-7 rounded flex items-center justify-center text-xs font-mono flex-shrink-0"
              style={{
                background: activePanel === item.id ? 'var(--accent-blue)' : 'var(--bg-surface)',
                color: activePanel === item.id ? '#ffffff' : 'var(--text-tertiary)',
              }}
            >
              {item.icon}
            </span>
            {!collapsed && <span className="truncate">{item.label}</span>}
          </button>
        ))}
      </nav>

      {/* Bottom */}
      <div className="p-3 space-y-2" style={{ borderTop: '1px solid var(--border-primary)' }}>
        <button
          onClick={onToggle}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs
                     cursor-pointer bg-transparent border-none"
          style={{ color: 'var(--text-tertiary)' }}
        >
          {collapsed ? '>>' : '<< Collapse'}
        </button>
        <button
          onClick={onLogout}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs
                     cursor-pointer bg-transparent border-none"
          style={{ color: 'var(--accent-red)' }}
          id="dashboard-logout-btn"
        >
          {collapsed ? 'X' : 'Sign Out'}
        </button>
      </div>
    </aside>
  );
}
```

---

## 08.4 — Live Feed Grid (frontend/src/components/dashboard/LiveFeedGrid.jsx)

```jsx
export default function LiveFeedGrid({ compact = false }) {
  // Demo data
  const feeds = [
    { id: 'phone-001', name: 'Living Room', zone: 'living_room', status: 'active' },
    { id: 'webcam-002', name: 'Front Door', zone: 'front_door', status: 'active' },
    { id: 'cctv-003', name: 'Kitchen', zone: 'kitchen', status: 'learning' },
  ];

  return (
    <div id="live-feed-grid">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>
          Live Feeds
        </h2>
        <span className="text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
          {feeds.filter(f => f.status === 'active').length}/{feeds.length} ACTIVE
        </span>
      </div>

      <div className={`grid gap-4 ${compact ? 'grid-cols-2' : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'}`}>
        {feeds.map(feed => (
          <div key={feed.id} className="glass-card overflow-hidden">
            <div
              className="aspect-video flex items-center justify-center relative"
              style={{ background: 'var(--bg-tertiary)' }}
            >
              <span className="text-sm font-mono" style={{ color: 'var(--text-tertiary)' }}>
                [{feed.name}]
              </span>
              {feed.status === 'active' && (
                <div
                  className="absolute top-2 left-2 flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono"
                  style={{ background: 'rgba(239, 68, 68, 0.9)', color: '#fff' }}
                >
                  <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: '#fff' }} />
                  LIVE
                </div>
              )}
            </div>
            <div className="p-3 flex items-center justify-between">
              <div>
                <div className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{feed.name}</div>
                <div className="text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>{feed.id}</div>
              </div>
              <span
                className="w-2 h-2 rounded-full"
                style={{ background: feed.status === 'active' ? 'var(--accent-emerald)' : 'var(--accent-amber)' }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 08.5 — Floor Plan Visualizer (frontend/src/components/dashboard/FloorPlan.jsx)

```jsx
import { useState } from 'react';

export default function FloorPlan({ compact = false }) {
  const [selectedZone, setSelectedZone] = useState(null);
  const [timeRange, setTimeRange] = useState('24h');

  const zones = [
    { id: 'living_room', label: 'Living Room', x: 20, y: 20, w: 180, h: 120, activity: 0.3, status: 'normal' },
    { id: 'kitchen', label: 'Kitchen', x: 220, y: 20, w: 140, h: 120, activity: 0.5, status: 'normal' },
    { id: 'hallway', label: 'Hallway', x: 160, y: 160, w: 60, h: 100, activity: 0.2, status: 'normal' },
    { id: 'bedroom', label: 'Bedroom', x: 20, y: 160, w: 120, h: 100, activity: 0.1, status: 'normal' },
    { id: 'bathroom', label: 'Bathroom', x: 240, y: 160, w: 80, h: 60, activity: 0.0, status: 'normal' },
    { id: 'front_door', label: 'Front Door', x: 380, y: 20, w: 60, h: 60, activity: 0.1, status: 'normal' },
  ];

  const getZoneColor = (zone) => {
    if (zone.status === 'anomaly') return 'var(--accent-red)';
    if (zone.status === 'elevated') return 'var(--accent-amber)';
    if (zone.activity > 0.4) return 'var(--accent-emerald)';
    if (zone.activity > 0.1) return 'var(--accent-emerald)';
    return 'var(--text-tertiary)';
  };

  const getZoneOpacity = (zone) => {
    return Math.max(0.05, Math.min(0.4, zone.activity));
  };

  return (
    <div className="glass-card p-6" id="floor-plan-visualizer">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>
          Floor Plan
        </h2>
        <div className="flex gap-2">
          {['24h', '7d', '30d'].map(range => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className="px-2 py-1 rounded text-xs font-mono cursor-pointer border-none"
              style={{
                background: timeRange === range ? 'var(--accent-blue)' : 'var(--bg-surface)',
                color: timeRange === range ? '#ffffff' : 'var(--text-secondary)',
              }}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      <svg
        viewBox="0 0 460 280"
        className="w-full"
        style={{ background: 'var(--bg-surface)', borderRadius: 'var(--radius-lg)' }}
      >
        {zones.map(zone => (
          <g key={zone.id} onClick={() => setSelectedZone(zone.id)} style={{ cursor: 'pointer' }}>
            <rect
              x={zone.x} y={zone.y}
              width={zone.w} height={zone.h}
              rx="4"
              fill={getZoneColor(zone)}
              fillOpacity={getZoneOpacity(zone)}
              stroke={selectedZone === zone.id ? 'var(--accent-blue)' : 'var(--border-secondary)'}
              strokeWidth={selectedZone === zone.id ? '2' : '1'}
            />
            <text
              x={zone.x + zone.w / 2}
              y={zone.y + zone.h / 2}
              textAnchor="middle"
              dominantBaseline="middle"
              fill="var(--text-secondary)"
              fontSize="10"
              fontFamily="var(--font-mono)"
            >
              {zone.label}
            </text>
          </g>
        ))}
      </svg>

      {selectedZone && (
        <div className="mt-4 p-3 rounded-lg" style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-primary)' }}>
          <h3 className="text-sm font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>
            {zones.find(z => z.id === selectedZone)?.label}
          </h3>
          <div className="text-xs space-y-1" style={{ color: 'var(--text-secondary)' }}>
            <div>Status: Normal</div>
            <div>Last activity: 5 min ago</div>
            <div>Sensors: 1 active</div>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## 08.6 — Alert Feed (frontend/src/components/dashboard/AlertFeed.jsx)

```jsx
export default function AlertFeed({ compact = false }) {
  // Demo data — no alerts in initial state
  const alerts = [];

  return (
    <div className="glass-card p-4" id="alert-feed-panel">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>
          Alert Feed
        </h2>
        <span className="text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
          {alerts.length} ALERTS
        </span>
      </div>

      {alerts.length === 0 ? (
        <div className="py-8 text-center">
          <div className="text-2xl mb-2" style={{ color: 'var(--text-tertiary)' }}>[ ]</div>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>No alerts</p>
          <p className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>
            System is monitoring normally
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map(alert => (
            <div key={alert.id} className="p-3 rounded-lg" style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-primary)' }}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-mono" style={{ color: 'var(--accent-red)' }}>
                  {alert.risk_level.toUpperCase()}
                </span>
                <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
                  {alert.timestamp}
                </span>
              </div>
              <p className="text-sm" style={{ color: 'var(--text-primary)' }}>{alert.summary}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## 08.7 — Risk Gauge (frontend/src/components/dashboard/RiskGauge.jsx)

```jsx
import { useEffect, useRef } from 'react';

export default function RiskGauge({ score = 0, size = 'large' }) {
  const canvasRef = useRef(null);
  const dimensions = size === 'large' ? 180 : 48;
  const lineWidth = size === 'large' ? 12 : 4;

  const getRiskColor = (s) => {
    if (s >= 76) return 'var(--accent-red)';
    if (s >= 51) return 'var(--accent-amber)';
    if (s >= 26) return 'var(--accent-amber)';
    return 'var(--accent-emerald)';
  };

  const getRiskLabel = (s) => {
    if (s >= 76) return 'CRITICAL';
    if (s >= 51) return 'HIGH';
    if (s >= 26) return 'MEDIUM';
    return 'LOW';
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const center = dimensions / 2;
    const radius = center - lineWidth;

    ctx.clearRect(0, 0, dimensions, dimensions);

    // Background arc
    ctx.beginPath();
    ctx.arc(center, center, radius, 0.75 * Math.PI, 2.25 * Math.PI);
    ctx.strokeStyle = 'var(--border-primary)';
    ctx.lineWidth = lineWidth;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Score arc
    const scoreAngle = 0.75 * Math.PI + (score / 100) * 1.5 * Math.PI;
    ctx.beginPath();
    ctx.arc(center, center, radius, 0.75 * Math.PI, scoreAngle);

    const style = getComputedStyle(document.documentElement);
    const color = score >= 76 ? style.getPropertyValue('--accent-red').trim()
      : score >= 51 ? style.getPropertyValue('--accent-amber').trim()
      : score >= 26 ? style.getPropertyValue('--accent-amber').trim()
      : style.getPropertyValue('--accent-emerald').trim();

    ctx.strokeStyle = color || '#10b981';
    ctx.lineWidth = lineWidth;
    ctx.lineCap = 'round';
    ctx.stroke();
  }, [score, dimensions, lineWidth]);

  if (size === 'small') {
    return (
      <div className="flex items-center gap-2" id="risk-gauge-small">
        <canvas ref={canvasRef} width={dimensions} height={dimensions} />
        <span className="text-xs font-mono" style={{ color: getRiskColor(score) }}>
          {score}
        </span>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center" id="risk-gauge-large">
      <div className="relative">
        <canvas ref={canvasRef} width={dimensions} height={dimensions} />
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold" style={{ color: getRiskColor(score) }}>
            {score}
          </span>
          <span className="text-xs font-mono uppercase" style={{ color: 'var(--text-tertiary)' }}>
            {getRiskLabel(score)}
          </span>
        </div>
      </div>
    </div>
  );
}
```

---

## 08.8 — Sensor Health Panel (frontend/src/components/dashboard/SensorHealth.jsx)

```jsx
export default function SensorHealth() {
  const sensors = [
    { id: 'phone-001', name: 'Living Room Camera', type: 'phone', status: 'active', lastHeartbeat: '2s ago', quality: 'excellent' },
    { id: 'webcam-002', name: 'Front Door Webcam', type: 'webcam', status: 'active', lastHeartbeat: '5s ago', quality: 'good' },
    { id: 'cctv-003', name: 'Kitchen CCTV', type: 'cctv', status: 'learning', lastHeartbeat: '8s ago', quality: 'good' },
  ];

  const statusColors = {
    active: 'var(--accent-emerald)',
    learning: 'var(--accent-blue)',
    alert: 'var(--accent-red)',
    inactive: 'var(--text-tertiary)',
  };

  return (
    <div id="sensor-health-panel">
      <h2 className="text-base font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
        Sensor Network Health
      </h2>
      <div className="space-y-3">
        {sensors.map(sensor => (
          <div key={sensor.id} className="glass-card p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ background: statusColors[sensor.status] }}
              />
              <div>
                <div className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                  {sensor.name}
                </div>
                <div className="text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
                  {sensor.id} | {sensor.type.toUpperCase()}
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-xs font-mono uppercase" style={{ color: statusColors[sensor.status] }}>
                {sensor.status}
              </div>
              <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
                {sensor.lastHeartbeat}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 08.9 — Communication Panel (frontend/src/components/dashboard/CommPanel.jsx)

```jsx
import { useState } from 'react';

export default function CommPanel() {
  const [selectedDevice, setSelectedDevice] = useState('');
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);

  const devices = [
    { id: 'phone-001', name: 'Living Room Camera' },
    { id: 'webcam-002', name: 'Front Door Webcam' },
    { id: 'cctv-003', name: 'Kitchen CCTV' },
  ];

  const handleSend = async () => {
    if (!selectedDevice || !message) return;
    setSending(true);
    // API call will be connected via Chunk 09
    setTimeout(() => {
      setSending(false);
      setMessage('');
    }, 1000);
  };

  return (
    <div id="comm-panel">
      <h2 className="text-base font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
        Two-Way Communication
      </h2>
      <div className="glass-card p-6">
        <div className="mb-4">
          <label className="block text-xs font-mono uppercase tracking-wider mb-2"
            style={{ color: 'var(--text-tertiary)' }}>
            Target Device
          </label>
          <select
            value={selectedDevice}
            onChange={(e) => setSelectedDevice(e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg text-sm outline-none"
            style={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-primary)',
              color: 'var(--text-primary)',
            }}
            id="comm-device-select"
          >
            <option value="">Select a device</option>
            {devices.map(d => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>
        </div>

        <div className="mb-4">
          <label className="block text-xs font-mono uppercase tracking-wider mb-2"
            style={{ color: 'var(--text-tertiary)' }}>
            Message
          </label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type a message to send through the device speaker..."
            rows={3}
            className="w-full px-3 py-2.5 rounded-lg text-sm outline-none resize-none"
            style={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-primary)',
              color: 'var(--text-primary)',
            }}
            id="comm-message-input"
          />
        </div>

        <button
          onClick={handleSend}
          disabled={!selectedDevice || !message || sending}
          className="w-full py-2.5 rounded-lg text-sm font-semibold cursor-pointer transition-all"
          style={{
            background: (selectedDevice && message && !sending)
              ? 'var(--accent-blue)' : 'var(--bg-surface)',
            color: (selectedDevice && message && !sending)
              ? '#ffffff' : 'var(--text-tertiary)',
            border: 'none',
          }}
          id="comm-send-btn"
        >
          {sending ? 'Sending...' : 'Send Message'}
        </button>
      </div>
    </div>
  );
}
```

---

## Verification

```bash
# 1. Start frontend
cd frontend
npm run dev

# 2. Test New Device Login
# http://localhost:5173/new-device/login
# Should show premium login card with gradient branding and demo mode link

# 3. Test Dashboard (navigate directly)
# http://localhost:5173/new-device/dashboard
# Should show sidebar, header with risk gauge, overview panel with stat cards,
# live feed grid placeholders, alert feed (empty), and floor plan SVG

# 4. Test sidebar navigation
# Click each nav item — panel content should switch
# Click collapse button — sidebar should shrink

# 5. Test floor plan
# Click zones on the SVG — zone details should appear below

# 6. Test theme toggle
# Click theme button — all components should switch between dark and light

# 7. Build test
npm run build  # Should complete without errors
```

Expected: Login page renders with premium gradient branding. Dashboard shows all panels with proper layout. Sidebar navigation works. Floor plan zones are clickable. Risk gauge renders with arc animation. All components respect the theme system.
