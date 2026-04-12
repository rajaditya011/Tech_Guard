import { useState, useEffect } from 'react';
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
  const [status, setStatus] = useState('learning');
  const [isStreaming, setIsStreaming] = useState(false);

  useEffect(() => {
    if (!token) navigate('/old-device/login');
  }, [token, navigate]);

  return (
    <AppShell showThemeToggle={false}>
      <div className="max-w-lg mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>HomeGuardian</h1>
            <p className="text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>SENSOR NODE</p>
          </div>
          <div className="flex items-center gap-3">
            <DeviceStatus status={status} />
            <button onClick={logout} className="text-xs px-2 py-1 rounded cursor-pointer bg-transparent border-none"
              style={{ color: 'var(--text-tertiary)' }} id="old-device-logout-btn">Disconnect</button>
          </div>
        </div>
        <CameraPreview isStreaming={isStreaming} onStreamStart={() => setIsStreaming(true)} onStreamStop={() => setIsStreaming(false)} />
        <div className="mt-4"><BaselineProgress sensorId={user?.id} /></div>
        <div className="mt-4"><AudioWarning /></div>
        <div className="mt-4 glass-card p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase" style={{ color: 'var(--text-tertiary)' }}>Connection</span>
            <span className="flex items-center gap-1.5 text-xs" style={{ color: 'var(--accent-emerald)' }}>
              <span className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--accent-emerald)' }} />Connected
            </span>
          </div>
          <div className="mt-2 text-xs" style={{ color: 'var(--text-secondary)' }}>
            <div className="flex justify-between py-1"><span>Frames sent</span><span className="font-mono">{isStreaming ? '1,247' : '0'}</span></div>
            <div className="flex justify-between py-1"><span>Latency</span><span className="font-mono">12ms</span></div>
            <div className="flex justify-between py-1"><span>Uptime</span><span className="font-mono">2h 34m</span></div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
