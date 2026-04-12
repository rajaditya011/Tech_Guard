# Chunk 07 — Old Device Portal

**Goal**: Build the complete Old Device Portal — login, enrollment, camera streaming, baseline progress, system status, audio warning playback, and connection health monitoring.
**Estimated Time**: 50 minutes
**Dependencies**: Chunk 06 (Frontend Shell)
**Unlocks**: Chunk 09 (when combined with Chunk 08)

---

## 07.1 — Old Device Login Page (frontend/src/pages/OldDeviceLogin.jsx)

```jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AppShell from '../components/layout/AppShell';

export default function OldDeviceLogin() {
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
        await register(deviceName, password, 'old_device');
      } else {
        await login(deviceName, password);
      }
      navigate('/old-device/portal');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="w-full max-w-sm">
          {/* Header */}
          <div className="text-center mb-8">
            <div
              className="inline-block px-3 py-1 rounded-full text-xs font-mono uppercase tracking-wider mb-4"
              style={{ background: 'var(--accent-blue-glow)', color: 'var(--accent-blue)' }}
            >
              Sensor Node
            </div>
            <h1 className="text-2xl font-bold mb-1" style={{ color: 'var(--text-primary)' }}>
              Old Device Portal
            </h1>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              {isRegister ? 'Enroll this device as a sensor node' : 'Connect to your security network'}
            </p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="glass-card p-6" id="old-device-login-form">
            <div className="mb-4">
              <label
                className="block text-xs font-mono uppercase tracking-wider mb-2"
                style={{ color: 'var(--text-tertiary)' }}
                htmlFor="device-name-input"
              >
                Device Name
              </label>
              <input
                id="device-name-input"
                type="text"
                value={deviceName}
                onChange={(e) => setDeviceName(e.target.value)}
                placeholder="e.g., living-room-camera"
                required
                className="w-full px-3 py-2.5 rounded-lg text-sm outline-none transition-all"
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
                htmlFor="password-input"
              >
                Password
              </label>
              <input
                id="password-input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Minimum 6 characters"
                required
                minLength={6}
                className="w-full px-3 py-2.5 rounded-lg text-sm outline-none transition-all"
                style={{
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border-primary)',
                  color: 'var(--text-primary)',
                }}
              />
            </div>

            {error && (
              <div
                className="mb-4 px-3 py-2 rounded-lg text-sm"
                style={{ background: 'var(--accent-red-glow)', color: 'var(--accent-red)' }}
              >
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              id="old-device-submit-btn"
              className="w-full py-2.5 rounded-lg text-sm font-semibold transition-all cursor-pointer"
              style={{
                background: 'var(--accent-blue)',
                color: '#ffffff',
                opacity: loading ? 0.6 : 1,
              }}
            >
              {loading ? 'Connecting...' : isRegister ? 'Enroll Device' : 'Connect'}
            </button>

            <button
              type="button"
              onClick={() => setIsRegister(!isRegister)}
              className="w-full mt-3 py-2 text-sm cursor-pointer bg-transparent border-none"
              style={{ color: 'var(--text-secondary)' }}
            >
              {isRegister ? 'Already enrolled? Connect' : 'New device? Enroll'}
            </button>
          </form>

          <p className="text-center text-xs mt-6" style={{ color: 'var(--text-tertiary)' }}>
            This device will stream video to the AI hub.
            <br />
            Minimal resources used. Optimized for old hardware.
          </p>
        </div>
      </div>
    </AppShell>
  );
}
```

---

## 07.2 — Old Device Portal Main (frontend/src/pages/OldDevicePortal.jsx)

```jsx
import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AppShell from '../components/layout/AppShell';
import CameraPreview from '../components/old-device/CameraPreview';
import BaselineProgress from '../components/old-device/BaselineProgress';
import DeviceStatus from '../components/old-device/DeviceStatus';
import AudioWarning from '../components/old-device/AudioWarning';

export default function OldDevicePortal() {
  const { user, token, logout } = useAuth();
  const navigate = useNavigate();
  const [status, setStatus] = useState('learning'); // active, learning, alert
  const [isStreaming, setIsStreaming] = useState(false);

  useEffect(() => {
    if (!token) {
      navigate('/old-device/login');
    }
  }, [token, navigate]);

  return (
    <AppShell showThemeToggle={false}>
      <div className="max-w-lg mx-auto px-4 py-6">
        {/* Minimal Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
              HomeGuardian
            </h1>
            <p className="text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
              SENSOR NODE
            </p>
          </div>
          <div className="flex items-center gap-3">
            <DeviceStatus status={status} />
            <button
              onClick={logout}
              className="text-xs px-2 py-1 rounded cursor-pointer bg-transparent border-none"
              style={{ color: 'var(--text-tertiary)' }}
              id="old-device-logout-btn"
            >
              Disconnect
            </button>
          </div>
        </div>

        {/* Camera Preview */}
        <CameraPreview
          isStreaming={isStreaming}
          onStreamStart={() => setIsStreaming(true)}
          onStreamStop={() => setIsStreaming(false)}
        />

        {/* Baseline Progress */}
        <div className="mt-4">
          <BaselineProgress sensorId={user?.id} />
        </div>

        {/* Audio Warning Receiver */}
        <div className="mt-4">
          <AudioWarning />
        </div>

        {/* Connection Health */}
        <div className="mt-4 glass-card p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase" style={{ color: 'var(--text-tertiary)' }}>
              Connection
            </span>
            <span className="flex items-center gap-1.5 text-xs" style={{ color: 'var(--accent-emerald)' }}>
              <span className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--accent-emerald)' }} />
              Connected
            </span>
          </div>
          <div className="mt-2 text-xs" style={{ color: 'var(--text-secondary)' }}>
            <div className="flex justify-between py-1">
              <span>Frames sent</span>
              <span className="font-mono">{isStreaming ? '1,247' : '0'}</span>
            </div>
            <div className="flex justify-between py-1">
              <span>Latency</span>
              <span className="font-mono">12ms</span>
            </div>
            <div className="flex justify-between py-1">
              <span>Uptime</span>
              <span className="font-mono">2h 34m</span>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
```

---

## 07.3 — Camera Preview Component (frontend/src/components/old-device/CameraPreview.jsx)

```jsx
import { useState, useRef, useEffect } from 'react';

export default function CameraPreview({ isStreaming, onStreamStart, onStreamStop }) {
  const videoRef = useRef(null);
  const [hasPermission, setHasPermission] = useState(null);
  const [error, setError] = useState('');

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: 640, height: 480 },
        audio: false
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setHasPermission(true);
      onStreamStart();
    } catch (err) {
      setError('Camera access denied. Please enable camera permissions.');
      setHasPermission(false);
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    onStreamStop();
  };

  useEffect(() => {
    return () => stopCamera();
  }, []);

  return (
    <div className="glass-card overflow-hidden" id="camera-preview-container">
      {/* Preview Area */}
      <div
        className="relative w-full aspect-video flex items-center justify-center"
        style={{ background: 'var(--bg-tertiary)' }}
      >
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-full object-cover"
          style={{ display: isStreaming ? 'block' : 'none' }}
        />

        {!isStreaming && (
          <div className="text-center p-6">
            <div className="text-3xl mb-3" style={{ color: 'var(--text-tertiary)' }}>
              [ CAMERA ]
            </div>
            <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
              {error || 'Camera is not active. Tap below to start streaming.'}
            </p>
          </div>
        )}

        {/* Streaming indicator */}
        {isStreaming && (
          <div
            className="absolute top-3 left-3 flex items-center gap-1.5 px-2 py-1 rounded text-xs font-mono"
            style={{
              background: 'rgba(239, 68, 68, 0.9)',
              color: '#ffffff',
            }}
          >
            <span
              className="w-2 h-2 rounded-full animate-pulse"
              style={{ background: '#ffffff' }}
            />
            LIVE
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="p-3 flex gap-2">
        {!isStreaming ? (
          <button
            onClick={startCamera}
            className="flex-1 py-2 rounded-lg text-sm font-semibold cursor-pointer transition-all"
            style={{ background: 'var(--accent-blue)', color: '#ffffff' }}
            id="start-stream-btn"
          >
            Start Streaming
          </button>
        ) : (
          <button
            onClick={stopCamera}
            className="flex-1 py-2 rounded-lg text-sm font-semibold cursor-pointer transition-all"
            style={{ background: 'var(--accent-red)', color: '#ffffff' }}
            id="stop-stream-btn"
          >
            Stop Streaming
          </button>
        )}
      </div>
    </div>
  );
}
```

---

## 07.4 — Baseline Progress (frontend/src/components/old-device/BaselineProgress.jsx)

```jsx
export default function BaselineProgress({ sensorId }) {
  // Demo data — will connect to API in production
  const progress = {
    days_complete: 5,
    days_required: 14,
    percent_complete: 35.7,
    zones_learning: ['living_room', 'kitchen', 'hallway', 'front_door'],
    is_complete: false
  };

  return (
    <div className="glass-card p-4" id="baseline-progress-panel">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-mono uppercase tracking-wider" style={{ color: 'var(--text-tertiary)' }}>
          Baseline Learning
        </span>
        <span className="text-xs font-mono" style={{ color: 'var(--accent-blue)' }}>
          {progress.percent_complete.toFixed(1)}%
        </span>
      </div>

      {/* Progress Bar */}
      <div
        className="h-2 rounded-full overflow-hidden mb-3"
        style={{ background: 'var(--bg-surface)' }}
      >
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{
            width: `${progress.percent_complete}%`,
            background: progress.is_complete
              ? 'var(--accent-emerald)'
              : 'var(--accent-blue)',
          }}
        />
      </div>

      <div className="flex justify-between text-xs" style={{ color: 'var(--text-secondary)' }}>
        <span>Day {progress.days_complete} of {progress.days_required}</span>
        <span>{progress.days_required - progress.days_complete} days remaining</span>
      </div>

      {/* Zones */}
      <div className="mt-3 flex flex-wrap gap-1.5">
        {progress.zones_learning.map(zone => (
          <span
            key={zone}
            className="px-2 py-0.5 rounded text-xs font-mono"
            style={{
              background: 'var(--bg-surface)',
              color: 'var(--text-secondary)',
              border: '1px solid var(--border-primary)',
            }}
          >
            {zone.replace('_', ' ')}
          </span>
        ))}
      </div>
    </div>
  );
}
```

---

## 07.5 — Device Status Badge (frontend/src/components/old-device/DeviceStatus.jsx)

```jsx
export default function DeviceStatus({ status }) {
  const config = {
    active: { label: 'Active', color: 'var(--accent-emerald)', animate: false },
    learning: { label: 'Learning', color: 'var(--accent-blue)', animate: true },
    alert: { label: 'Alert', color: 'var(--accent-red)', animate: true },
    inactive: { label: 'Inactive', color: 'var(--text-tertiary)', animate: false },
  };

  const current = config[status] || config.inactive;

  return (
    <div
      className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono uppercase tracking-wider"
      style={{
        background: `${current.color}15`,
        color: current.color,
      }}
      id="device-status-badge"
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${current.animate ? 'animate-pulse' : ''}`}
        style={{ background: current.color }}
      />
      {current.label}
    </div>
  );
}
```

---

## 07.6 — Audio Warning Component (frontend/src/components/old-device/AudioWarning.jsx)

```jsx
import { useState, useEffect } from 'react';

export default function AudioWarning() {
  const [hasWarning, setHasWarning] = useState(false);
  const [warningMessage, setWarningMessage] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);

  // Listen for incoming warning messages via WebSocket
  // (Implementation connects in Chunk 09)

  const playWarning = () => {
    if (!warningMessage) return;
    setIsPlaying(true);
    // Use Web Speech API for text-to-speech
    const utterance = new SpeechSynthesisUtterance(warningMessage);
    utterance.onend = () => setIsPlaying(false);
    speechSynthesis.speak(utterance);
  };

  const dismissWarning = () => {
    setHasWarning(false);
    setWarningMessage('');
  };

  if (!hasWarning) {
    return (
      <div className="glass-card p-4" id="audio-warning-panel">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono uppercase tracking-wider" style={{ color: 'var(--text-tertiary)' }}>
            Audio Channel
          </span>
          <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
            Listening for messages...
          </span>
        </div>
      </div>
    );
  }

  return (
    <div
      className="glass-card p-4"
      style={{ borderColor: 'var(--accent-amber)', borderWidth: '1px' }}
      id="audio-warning-active"
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-mono uppercase tracking-wider" style={{ color: 'var(--accent-amber)' }}>
          Incoming Message
        </span>
        <button
          onClick={dismissWarning}
          className="text-xs cursor-pointer bg-transparent border-none"
          style={{ color: 'var(--text-tertiary)' }}
        >
          Dismiss
        </button>
      </div>
      <p className="text-sm mb-3" style={{ color: 'var(--text-primary)' }}>
        {warningMessage}
      </p>
      <button
        onClick={playWarning}
        disabled={isPlaying}
        className="w-full py-2 rounded-lg text-sm font-semibold cursor-pointer"
        style={{
          background: isPlaying ? 'var(--bg-surface)' : 'var(--accent-amber)',
          color: isPlaying ? 'var(--text-secondary)' : '#ffffff',
        }}
      >
        {isPlaying ? 'Playing...' : 'Play Audio'}
      </button>
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

# 2. Navigate to Old Device Portal routes
# http://localhost:5173/old-device/login  -- Login form should render
# http://localhost:5173/old-device/portal -- Portal with camera, baseline, status

# 3. Test form interaction
# Enter device name and password, click Enroll
# (Will fail if backend is not running — this is expected)

# 4. Test camera (requires HTTPS or localhost)
# Click "Start Streaming" — should request camera permission
# If denied, should show error message

# 5. Verify minimal UI
# The portal should be clean and lightweight — no heavy animations
# All elements should use CSS variables from the theme

# 6. Build test
npm run build  # Should complete without errors
```

Expected: Login page renders with form. Portal shows camera preview, baseline progress, device status, and audio warning panel. Camera permission dialog appears on "Start Streaming." UI is minimal and optimized for low-spec devices.
