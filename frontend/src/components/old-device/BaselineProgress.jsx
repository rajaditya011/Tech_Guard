export default function BaselineProgress({ sensorId }) {
  const progress = {
    days_complete: 5, days_required: 14, percent_complete: 35.7,
    zones_learning: ['living_room', 'kitchen', 'hallway', 'front_door'],
    is_complete: false
  };
  return (
    <div className="glass-card p-4" id="baseline-progress-panel">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-mono uppercase tracking-wider" style={{ color: 'var(--text-tertiary)' }}>Baseline Learning</span>
        <span className="text-xs font-mono" style={{ color: 'var(--accent-blue)' }}>{progress.percent_complete.toFixed(1)}%</span>
      </div>
      <div className="h-2 rounded-full overflow-hidden mb-3" style={{ background: 'var(--bg-surface)' }}>
        <div className="h-full rounded-full transition-all duration-500" style={{ width: `${progress.percent_complete}%`, background: progress.is_complete ? 'var(--accent-emerald)' : 'var(--accent-blue)' }} />
      </div>
      <div className="flex justify-between text-xs" style={{ color: 'var(--text-secondary)' }}>
        <span>Day {progress.days_complete} of {progress.days_required}</span>
        <span>{progress.days_required - progress.days_complete} days remaining</span>
      </div>
      <div className="mt-3 flex flex-wrap gap-1.5">
        {progress.zones_learning.map(zone => (
          <span key={zone} className="px-2 py-0.5 rounded text-xs font-mono" style={{ background: 'var(--bg-surface)', color: 'var(--text-secondary)', border: '1px solid var(--border-primary)' }}>
            {zone.replace('_', ' ')}
          </span>
        ))}
      </div>
    </div>
  );
}
