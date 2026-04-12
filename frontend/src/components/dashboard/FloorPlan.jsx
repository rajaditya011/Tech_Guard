import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const INITIAL_ZONES = [
  { id: 'living_room', label: 'Living Room', x: 20, y: 20, w: 180, h: 120, activity: 0.0, status: 'normal' },
  { id: 'kitchen', label: 'Kitchen', x: 220, y: 20, w: 140, h: 120, activity: 0.0, status: 'normal' },
  { id: 'hallway', label: 'Hallway', x: 160, y: 160, w: 60, h: 100, activity: 0.0, status: 'normal' },
  { id: 'bedroom', label: 'Bedroom', x: 20, y: 160, w: 120, h: 100, activity: 0.0, status: 'normal' },
  { id: 'bathroom', label: 'Bathroom', x: 240, y: 160, w: 80, h: 60, activity: 0.0, status: 'normal' },
  { id: 'front_door', label: 'Front Door', x: 380, y: 20, w: 60, h: 60, activity: 0.0, status: 'normal' },
];

export default function FloorPlan({ compact = false }) {
  const { token } = useAuth();
  const [selectedZone, setSelectedZone] = useState(null);
  const [timeRange, setTimeRange] = useState('24h');
  const [zones, setZones] = useState(INITIAL_ZONES);
  const svgRef = useRef(null);
  const [dragState, setDragState] = useState(null);

  const handlePointerDown = (e, id, type) => {
    e.stopPropagation();
    e.target.setPointerCapture(e.pointerId);
    setDragState({ id, type, startX: e.clientX, startY: e.clientY });
  };

  const handlePointerMove = (e) => {
    if (!dragState) return;
    const dx = e.clientX - dragState.startX;
    const dy = e.clientY - dragState.startY;
    setZones(prev => prev.map(z => {
      if (z.id !== dragState.id) return z;
      if (dragState.type === 'move') {
        return { ...z, x: z.x + dx, y: z.y + dy };
      } else {
        return { ...z, w: Math.max(20, z.w + dx), h: Math.max(20, z.h + dy) };
      }
    }));
    setDragState({ ...dragState, startX: e.clientX, startY: e.clientY });
  };

  const handlePointerUp = (e) => {
    if (dragState) {
      e.target.releasePointerCapture(e.pointerId);
      setDragState(null);
    }
  };

  useEffect(() => {
    if (!token) return;
    let isMounted = true;
    
    const fetchHeatmaps = async () => {
      try {
        const API_URL = import.meta.env.VITE_API_URL || '';
        const promises = INITIAL_ZONES.map(z => 
          fetch(`${API_URL}/api/dashboard/heatmap/${z.id}`, {
            headers: { Authorization: `Bearer ${token}` }
          }).then(res => res.json())
        );
        const results = await Promise.all(promises);
        
        if (isMounted) {
          setZones(prev => prev.map(z => {
            const fetched = results.find(r => r.zone === z.id);
            return fetched ? { ...z, activity: fetched.intensity, status: fetched.risk_level === 'high' ? 'anomaly' : fetched.risk_level === 'medium' ? 'elevated' : 'normal' } : z;
          }));
        }
      } catch (err) {
        console.error("Heatmap fetch error:", err);
      }
    };

    fetchHeatmaps();
    const interval = setInterval(fetchHeatmaps, 15000); // 15s refresh
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [token, timeRange]);

  const getZoneColor = (zone) => {
    if (zone.status === 'anomaly') return 'var(--accent-red)';
    if (zone.status === 'elevated') return 'var(--accent-amber)';
    return 'var(--accent-emerald)';
  };
  const getZoneOpacity = (zone) => Math.max(0.05, Math.min(0.6, zone.activity));

  return (
    <div className="glass-card p-6" id="floor-plan-visualizer">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>Floor Plan</h2>
        <div className="flex gap-2">
          {['24h', '7d', '30d'].map(range => (
            <button key={range} onClick={() => setTimeRange(range)}
              className="px-2 py-1 rounded text-xs font-mono cursor-pointer border-none"
              style={{ background: timeRange === range ? 'var(--accent-blue)' : 'var(--bg-surface)', color: timeRange === range ? '#ffffff' : 'var(--text-secondary)' }}>
              {range}
            </button>
          ))}
        </div>
      </div>
      <svg viewBox="0 0 460 280" className="w-full" style={{ background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-lg)', touchAction: 'none' }}
           onPointerMove={handlePointerMove} onPointerUp={handlePointerUp}>
        <defs>
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>
        
        {/* House Exterior Outline */}
        <rect x="12" y="12" width="436" height="256" rx="6" fill="var(--bg-surface)" stroke="var(--border-secondary)" strokeWidth="4" />
        
        {/* Internal Walls (simplistic representation based on gaps) */}
        <line x1="200" y1="12" x2="200" y2="150" stroke="var(--border-secondary)" strokeWidth="4" />
        <line x1="360" y1="12" x2="360" y2="80" stroke="var(--border-secondary)" strokeWidth="4" />
        <line x1="12" y1="150" x2="448" y2="150" stroke="var(--border-secondary)" strokeWidth="4" />
        <line x1="140" y1="150" x2="140" y2="268" stroke="var(--border-secondary)" strokeWidth="4" />
        <line x1="220" y1="150" x2="220" y2="268" stroke="var(--border-secondary)" strokeWidth="4" />
        <line x1="320" y1="150" x2="320" y2="230" stroke="var(--border-secondary)" strokeWidth="4" />

        {zones.map(zone => {
          const isActive = zone.activity > 0.05;
          return (
            <g key={zone.id} onPointerDown={(e) => { setSelectedZone(zone.id); handlePointerDown(e, zone.id, 'move'); }} style={{ cursor: 'move', transition: dragState ? 'none' : 'all 0.3s ease' }}>
              <rect x={zone.x} y={zone.y} width={zone.w} height={zone.h} rx="4"
                fill={getZoneColor(zone)} fillOpacity={getZoneOpacity(zone)}
                stroke={selectedZone === zone.id ? 'var(--accent-blue)' : (isActive ? getZoneColor(zone) : 'transparent')}
                strokeWidth={selectedZone === zone.id ? '2' : (isActive ? '1' : '0')}
                filter={isActive && zone.status !== 'normal' ? 'url(#glow)' : ''}
                style={{ transition: dragState ? 'none' : 'fill-opacity 0.4s ease' }} />
              <text x={zone.x + zone.w / 2} y={zone.y + zone.h / 2} textAnchor="middle" dominantBaseline="middle"
                fill={isActive ? 'var(--text-primary)' : 'var(--text-secondary)'} 
                fontSize="11" fontWeight={isActive ? '600' : '400'} fontFamily="monospace"
                style={{ pointerEvents: 'none' }}>
                {zone.label}
              </text>
              {selectedZone === zone.id && (
                <rect x={zone.x + zone.w - 8} y={zone.y + zone.h - 8} width="16" height="16" fill="var(--accent-blue)" style={{ cursor: 'nwse-resize' }}
                      onPointerDown={(e) => handlePointerDown(e, zone.id, 'resize')} />
              )}
            </g>
          );
        })}
      </svg>
      {selectedZone && (
        <div className="mt-4 p-3 rounded-lg" style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-primary)' }}>
          <h3 className="text-sm font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>{zones.find(z => z.id === selectedZone)?.label}</h3>
          <div className="text-xs space-y-1" style={{ color: 'var(--text-secondary)' }}>
            <div className="capitalize">Status: {zones.find(z => z.id === selectedZone)?.status || 'Unknown'}</div>
            <div>Detected Activity: {Math.round((zones.find(z => z.id === selectedZone)?.activity || 0) * 10)} Events</div>
            <div>Sensors: 1 active</div>
          </div>
        </div>
      )}
    </div>
  );
}
