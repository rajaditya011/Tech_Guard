import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

export default function AlertFeed({ compact = false }) {
  const { token } = useAuth();
  const [alerts, setAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    let isMounted = true;
    const fetchAlerts = async () => {
      try {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const res = await fetch(`${API_URL}/api/anomalies/?limit=10`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        if (isMounted) {
          setAlerts(data);
          setIsLoading(false);
        }
      } catch (e) {
        if (isMounted) setIsLoading(false);
      }
    };
    fetchAlerts();
    const intv = setInterval(fetchAlerts, 15000);
    return () => { isMounted = false; clearInterval(intv); };
  }, [token]);

  return (
    <div className="glass-card p-4" id="alert-feed-panel">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Anomaly Timeline</h2>
        <div className="flex gap-2 items-center">
          <button onClick={() => window.print()} className="text-[10px] font-mono px-2 py-1 rounded border cursor-pointer glass-card" style={{ color: 'var(--accent-blue)', borderColor: 'var(--border-primary)' }}>
            EXPORT PDF
          </button>
          <span className="text-[10px] font-mono" style={{ color: 'var(--text-tertiary)' }}>{alerts.length} EVENTS</span>
        </div>
      </div>
      
      {isLoading ? (
        <div className="space-y-4">
          {[1,2,3].map(i => <div key={i} className="h-16 rounded animate-pulse" style={{ background: 'var(--bg-tertiary)' }} />)}
        </div>
      ) : alerts.length === 0 ? (
        <div className="py-6 text-center">
          <div className="text-xl mb-1" style={{ color: 'var(--text-tertiary)' }}>[ ]</div>
          <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>No anomalies detected</p>
          <p className="text-[10px] mt-0.5" style={{ color: 'var(--text-tertiary)' }}>System is monitoring normally</p>
        </div>
      ) : (
        <div className="relative pl-4 space-y-4 before:absolute before:inset-y-0 before:left-[7px] before:w-0.5 before:bg-[var(--border-primary)]">
          {alerts.map((alert) => (
            <div key={alert.id} className="relative">
              <span className="absolute -left-[19px] top-1.5 w-3 h-3 rounded-full border-2" 
                style={{ 
                  background: 'var(--bg-primary)', 
                  borderColor: alert.risk_level === 'high' || alert.risk_level === 'critical' ? 'var(--accent-red)' : 'var(--accent-amber)' 
                }} 
              />
              <div className="p-3 rounded-lg ml-2" style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-primary)' }}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded" 
                    style={{ background: 'var(--bg-tertiary)', color: alert.risk_level === 'high' || alert.risk_level === 'critical' ? 'var(--accent-red)' : 'var(--accent-amber)' }}>
                    {alert.risk_level.toUpperCase()}
                  </span>
                  <span className="text-[10px]" style={{ color: 'var(--text-tertiary)' }}>
                    {new Date(alert.detected_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                  </span>
                </div>
                <p className="text-xs font-semibold mb-0.5" style={{ color: 'var(--text-primary)' }}>{alert.zone}</p>
                <p className="text-xs leading-tight" style={{ color: 'var(--text-secondary)' }}>
                  {alert.classification || 'Unknown anomaly detected in zone.'}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
