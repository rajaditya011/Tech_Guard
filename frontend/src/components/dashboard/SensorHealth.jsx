export default function SensorHealth() {
  const sensors = [
    { id: 'phone-001', name: 'Living Room Camera', type: 'phone', status: 'active', lastHeartbeat: '2s ago', quality: 'excellent', battery: 85 },
    { id: 'webcam-002', name: 'Front Door Webcam', type: 'webcam', status: 'active', lastHeartbeat: '5s ago', quality: 'good', battery: null },
    { id: 'cctv-003', name: 'Kitchen CCTV', type: 'cctv', status: 'learning', lastHeartbeat: '8s ago', quality: 'good', battery: null },
  ];
  const statusColors = { active: 'var(--accent-emerald)', learning: 'var(--accent-blue)', alert: 'var(--accent-red)', inactive: 'var(--text-tertiary)' };

  return (
    <div id="sensor-health-panel">
      <h2 className="text-base font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Sensor Network Health</h2>
      <div className="space-y-3">
        {sensors.map(sensor => (
          <div key={sensor.id} className="glass-card p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: statusColors[sensor.status] }} />
              <div>
                <div className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{sensor.name}</div>
                <div className="text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>{sensor.id} | {sensor.type.toUpperCase()}</div>
              </div>
            </div>
            <div className="text-right flex flex-col items-end">
              <div className="text-xs font-mono uppercase" style={{ color: statusColors[sensor.status] }}>{sensor.status}</div>
              <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>{sensor.lastHeartbeat}</div>
              {sensor.battery !== null && (
                <div className="text-[10px] mt-1 font-mono flex items-center gap-1" style={{ color: sensor.battery > 20 ? 'var(--accent-emerald)' : 'var(--accent-red)' }}>
                  <span className="border rounded-sm px-0.5 border-current">[{sensor.battery}%]</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
