export default function DeviceStatus({ status }) {
  const config = {
    active: { label: 'Active', color: 'var(--accent-emerald)', animate: false },
    learning: { label: 'Learning', color: 'var(--accent-blue)', animate: true },
    alert: { label: 'Alert', color: 'var(--accent-red)', animate: true },
    inactive: { label: 'Inactive', color: 'var(--text-tertiary)', animate: false },
  };
  const current = config[status] || config.inactive;
  return (
    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono uppercase tracking-wider" style={{ background: `${current.color}15`, color: current.color }} id="device-status-badge">
      <span className={`w-1.5 h-1.5 rounded-full ${current.animate ? 'animate-pulse' : ''}`} style={{ background: current.color }} />
      {current.label}
    </div>
  );
}
