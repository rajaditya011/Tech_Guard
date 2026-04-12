export default function FeatureCards() {
  const features = [
    {
      icon: 'B',
      iconBg: 'linear-gradient(135deg, rgba(59,130,246,0.2), rgba(59,130,246,0.05))',
      iconColor: '#3b82f6',
      title: 'Behavioral Baseline Engine',
      desc: "14-day passive observation builds per-zone, per-hour activity profiles. The system learns YOUR home's rhythms — when you wake, leave, and sleep.",
      tag: 'ML / Isolation Forest',
      tagBg: 'rgba(59, 130, 246, 0.1)',
      tagColor: '#3b82f6',
    },
    {
      icon: 'V',
      iconBg: 'linear-gradient(135deg, rgba(139,92,246,0.2), rgba(139,92,246,0.05))',
      iconColor: '#8b5cf6',
      title: 'Real-Time Vision Analysis',
      desc: 'YOLOv8 human detection with trajectory tracking. Every frame is analyzed for recognized vs. unknown movement patterns and speed anomalies.',
      tag: 'YOLOv8 + OpenCV',
      tagBg: 'rgba(139, 92, 246, 0.1)',
      tagColor: '#8b5cf6',
    },
    {
      icon: 'C',
      iconBg: 'linear-gradient(135deg, rgba(229,192,123,0.2), rgba(229,192,123,0.05))',
      iconColor: '#E5C07B',
      title: 'Smart Clip Extraction',
      desc: 'Ring buffer continuously captures frames. On anomaly, the engine stitches 5 seconds BEFORE the event + 10 seconds AFTER into a clip with timestamps.',
      tag: 'Ring Buffer + MP4',
      tagBg: 'rgba(229, 192, 123, 0.1)',
      tagColor: '#E5C07B',
    },
    {
      icon: 'N',
      iconBg: 'linear-gradient(135deg, rgba(16,185,129,0.2), rgba(16,185,129,0.05))',
      iconColor: '#10b981',
      title: 'AI Incident Narratives',
      desc: 'Claude API generates human-readable security reports: "At 2:43 AM, unfamiliar movement was detected in the {zone}..." with evidence and risk assessment.',
      tag: 'Claude API',
      tagBg: 'rgba(16, 185, 129, 0.1)',
      tagColor: '#10b981',
    },
    {
      icon: 'F',
      iconBg: 'linear-gradient(135deg, rgba(239,68,68,0.2), rgba(239,68,68,0.05))',
      iconColor: '#ef4444',
      title: 'Multi-Sensor Fusion',
      desc: 'Cross-correlates events across sensors for spatial consistency. Movement in the hallway but not the front door? The system notices — and raises suspicion.',
      tag: 'Cross-Correlation',
      tagBg: 'rgba(239, 68, 68, 0.1)',
      tagColor: '#ef4444',
    },
    {
      icon: 'P',
      iconBg: 'linear-gradient(135deg, rgba(245,158,11,0.2), rgba(245,158,11,0.05))',
      iconColor: '#f59e0b',
      title: 'Predictive Intrusion Engine',
      desc: 'Matches live events against a 4-phase intrusion scenario library: Casing → Entry Probing → Reconnaissance → Intrusion. Alerts during early phases.',
      tag: 'Secret Weapon',
      tagBg: 'rgba(245, 158, 11, 0.15)',
      tagColor: '#f59e0b',
    },
  ];

  return (
    <section className="content-section fade-in-section" id="features">
      <div className="section-tag">Core Capabilities</div>
      <h2 className="section-title">Intelligent by Design</h2>
      <p className="section-description">
        Every component works together to create a system that doesn't just watch — it understands.
      </p>
      <div className="features-grid">
        {features.map((f, i) => (
          <div className="feature-card" key={i}>
            <div
              className="feature-icon"
              style={{ background: f.iconBg, color: f.iconColor }}
            >
              {f.icon}
            </div>
            <h3>{f.title}</h3>
            <p>{f.desc}</p>
            <span
              className="feature-tag"
              style={{ background: f.tagBg, color: f.tagColor }}
            >
              {f.tag}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
