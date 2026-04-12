export default function Architecture() {
  return (
    <section className="content-section fade-in-section" id="architecture">
      <div className="section-tag">System Design</div>
      <h2 className="section-title">Architecture</h2>
      <p className="section-description">
        A dual-portal system connecting old devices (sensors) with new devices (command dashboard) through an intelligent AI hub.
      </p>

      <div className="arch-diagram">
        {/* Layer 1: Old Devices */}
        <div className="arch-label">SENSOR LAYER</div>
        <div className="arch-row">
          <div className="arch-node" style={{ borderColor: 'rgba(59,130,246,0.3)', color: '#3b82f6' }}>
            Old Phone<br/><span style={{ fontSize: '0.6rem', opacity: 0.6 }}>Camera + Mic</span>
          </div>
          <div className="arch-node" style={{ borderColor: 'rgba(59,130,246,0.3)', color: '#3b82f6' }}>
            Old Tablet<br/><span style={{ fontSize: '0.6rem', opacity: 0.6 }}>Wide Angle</span>
          </div>
          <div className="arch-node" style={{ borderColor: 'rgba(59,130,246,0.3)', color: '#3b82f6' }}>
            Webcam<br/><span style={{ fontSize: '0.6rem', opacity: 0.6 }}>USB Camera</span>
          </div>
        </div>

        <div className="arch-arrow-down">↓ MQTT + WebSocket ↓</div>

        {/* Layer 2: AI Hub */}
        <div className="arch-label">AI HUB</div>
        <div className="arch-row">
          <div className="arch-node" style={{ borderColor: 'rgba(139,92,246,0.3)', color: '#8b5cf6' }}>
            YOLOv8<br/><span style={{ fontSize: '0.6rem', opacity: 0.6 }}>Detection</span>
          </div>
          <div className="arch-arrow">→</div>
          <div className="arch-node" style={{ borderColor: 'rgba(229,192,123,0.3)', color: '#E5C07B' }}>
            Baseline<br/><span style={{ fontSize: '0.6rem', opacity: 0.6 }}>Comparison</span>
          </div>
          <div className="arch-arrow">→</div>
          <div className="arch-node" style={{ borderColor: 'rgba(239,68,68,0.3)', color: '#ef4444' }}>
            Anomaly<br/><span style={{ fontSize: '0.6rem', opacity: 0.6 }}>Scoring</span>
          </div>
          <div className="arch-arrow">→</div>
          <div className="arch-node" style={{ borderColor: 'rgba(16,185,129,0.3)', color: '#10b981' }}>
            Response<br/><span style={{ fontSize: '0.6rem', opacity: 0.6 }}>Clip + Alert</span>
          </div>
        </div>

        <div className="arch-arrow-down">↓ Real-Time Push ↓</div>

        {/* Layer 3: Dashboard */}
        <div className="arch-label">OWNER DASHBOARD</div>
        <div className="arch-row">
          <div className="arch-node" style={{ borderColor: 'rgba(245,158,11,0.3)', color: '#f59e0b' }}>
            Live Feeds<br/><span style={{ fontSize: '0.6rem', opacity: 0.6 }}>Multi-Camera</span>
          </div>
          <div className="arch-node" style={{ borderColor: 'rgba(245,158,11,0.3)', color: '#f59e0b' }}>
            Floor Plan<br/><span style={{ fontSize: '0.6rem', opacity: 0.6 }}>Heat Zones</span>
          </div>
          <div className="arch-node" style={{ borderColor: 'rgba(245,158,11,0.3)', color: '#f59e0b' }}>
            AI Narratives<br/><span style={{ fontSize: '0.6rem', opacity: 0.6 }}>Incident Reports</span>
          </div>
        </div>
      </div>
    </section>
  );
}
