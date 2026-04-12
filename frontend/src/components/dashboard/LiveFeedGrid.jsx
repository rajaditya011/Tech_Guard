import { useState, useEffect } from 'react';

export default function LiveFeedGrid({ compact = false }) {
  const [isLoading, setIsLoading] = useState(true);
  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1200);
    return () => clearTimeout(timer);
  }, []);
  const feeds = [
    { id: 'phone-001', name: 'Living Room', zone: 'living_room', status: 'active' },
    { id: 'webcam-002', name: 'Front Door', zone: 'front_door', status: 'active' },
    { id: 'cctv-003', name: 'Kitchen', zone: 'kitchen', status: 'learning' },
  ];
  return (
    <div id="live-feed-grid">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>Live Feeds</h2>
        <span className="text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
          {feeds.filter(f => f.status === 'active').length}/{feeds.length} ACTIVE
        </span>
      </div>
      <div className={`grid gap-4 ${compact ? 'grid-cols-2' : 'grid-cols-2 md:grid-cols-3'}`}>
        {feeds.map((feed, idx) => (
          <div key={feed.id} className={`glass-card overflow-hidden ${!compact && idx === 0 ? 'col-span-full md:col-span-2 md:row-span-2' : ''}`}>
            {isLoading ? (
               <div className="w-full aspect-video animate-pulse" style={{ background: 'var(--bg-secondary)' }} />
            ) : (
              <div className="aspect-video flex items-center justify-center relative" style={{ background: 'var(--bg-tertiary)' }}>
                <span className="text-sm font-mono" style={{ color: 'var(--text-tertiary)' }}>[{feed.name}]</span>
                {feed.status === 'active' && (
                  <div className="absolute top-2 left-2 flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono" style={{ background: 'rgba(239, 68, 68, 0.9)', color: '#fff' }}>
                    <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: '#fff' }} />LIVE
                  </div>
                )}
              </div>
            )}
            <div className="p-3 flex items-center justify-between">
              {isLoading ? (
                <div className="w-24 h-4 rounded animate-pulse" style={{ background: 'var(--bg-tertiary)' }} />
              ) : (
                <div>
                  <div className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{feed.name}</div>
                  <div className="text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>{feed.id}</div>
                </div>
              )}
              <span className={`w-2 h-2 rounded-full ${isLoading ? 'animate-pulse' : ''}`} style={{ background: isLoading ? 'var(--bg-tertiary)' : feed.status === 'active' ? 'var(--accent-emerald)' : 'var(--accent-amber)' }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
