import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

export default function ReasoningReplay() {
  const { token } = useAuth();
  const [predictions, setPredictions] = useState([]);
  const [timelines, setTimelines] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    let isMounted = true;
    
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    
    fetch(`${API_URL}/api/predictions/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    .then(res => res.json())
    .then(async data => {
      if (!isMounted) return;
      setPredictions(data);
      
      const tlData = {};
      for (const pred of data) {
        try {
          const res = await fetch(`${API_URL}/api/predictions/${pred.id}/timeline`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          const tl = await res.json();
          tlData[pred.id] = tl.entries || [];
        } catch(e) {}
      }
      if (isMounted) {
        setTimelines(tlData);
        setLoading(false);
      }
    })
    .catch(() => { if(isMounted) setLoading(false); });
    
    return () => { isMounted = false; };
  }, [token]);

  return (
    <div className="space-y-4">
      {loading ? (
        <div className="glass-card p-6 text-center animate-pulse">Loading AI reasoning engines...</div>
      ) : predictions.length === 0 ? (
        <div className="glass-card p-6 text-center">
          <p className="text-sm font-mono" style={{ color: 'var(--text-tertiary)' }}>No active predictions available.</p>
        </div>
      ) : (
        predictions.map(pred => (
          <div key={pred.id} className="glass-card p-6" style={{ borderLeft: '4px solid var(--accent-violet)' }}>
            <div className="flex justify-between items-center mb-4">
              <div>
                <h3 className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>{pred.scenario_name || 'Intrusion Engine'}</h3>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>Phase: {pred.matched_phase}</p>
              </div>
              <div className="text-right">
                <span className="text-xs font-mono uppercase bg-[var(--bg-tertiary)] px-2 py-1 rounded" style={{ color: 'var(--accent-emerald)' }}>
                  {(pred.confidence * 100).toFixed(0)}% Confidence
                </span>
                <p className="text-[10px] mt-1" style={{ color: 'var(--text-tertiary)' }}>Next: {pred.predicted_next_phase || 'Action'}</p>
              </div>
            </div>
            
            <div className="space-y-3 pl-2 border-l border-[var(--border-secondary)] my-4 relative">
              {(timelines[pred.id] || []).map((tl, idx) => (
                <div key={idx} className="relative pl-4">
                  <span className="absolute -left-[21px] top-1.5 w-3 h-3 rounded-full border-2 border-[var(--bg-primary)] bg-[var(--accent-violet)]" />
                  <div className="text-[10px] font-mono mb-0.5" style={{ color: 'var(--text-tertiary)' }}>{new Date(tl.timestamp).toLocaleTimeString()}</div>
                  <div className="text-xs font-bold" style={{ color: 'var(--text-primary)' }}>{tl.event_type.toUpperCase()}</div>
                  <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>{tl.data_point}</div>
                  <div className="text-xs" style={{ color: 'var(--accent-blue)' }}>&rarr; {tl.conclusion}</div>
                </div>
              ))}
            </div>
            
            <div className="mt-4 p-3 rounded" style={{ background: 'var(--bg-surface)' }}>
              <span className="text-xs font-bold mr-2 text-[var(--accent-violet)]">AI CONCLUSION:</span>
              <span className="text-xs text-[var(--text-secondary)]">Behavior aligns with intrusion phase. Elevating system risk profile dynamically.</span>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
