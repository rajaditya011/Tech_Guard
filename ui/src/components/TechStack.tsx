export default function TechStack() {
  const techs = [
    { icon: 'Py', label: 'Python / FastAPI', color: '#3b82f6' },
    { icon: 'Re', label: 'React 19 + Vite', color: '#61dafb' },
    { icon: 'SQ', label: 'SQLite + WAL', color: '#10b981' },
    { icon: 'MQ', label: 'MQTT (Mosquitto)', color: '#E5C07B' },
    { icon: 'YL', label: 'YOLOv8 Nano', color: '#8b5cf6' },
    { icon: 'CL', label: 'Claude API', color: '#f59e0b' },
    { icon: 'WS', label: 'WebSocket', color: '#ef4444' },
    { icon: 'FC', label: 'Firebase FCM', color: '#ff9800' },
    { icon: 'CV', label: 'OpenCV', color: '#5c6bc0' },
    { icon: 'SK', label: 'scikit-learn', color: '#ff7043' },
    { icon: 'TW', label: 'TailwindCSS v4', color: '#38bdf8' },
    { icon: 'DK', label: 'Docker Compose', color: '#2196f3' },
  ];

  return (
    <section className="content-section fade-in-section">
      <div className="section-tag">Technology</div>
      <h2 className="section-title">Built With</h2>
      <p className="section-description">
        Every tool chosen for a reason — lightweight, proven, and hackathon-ready.
      </p>
      <div className="tech-grid">
        {techs.map((t, i) => (
          <div className="tech-item" key={i}>
            <div
              className="tech-icon"
              style={{
                background: `${t.color}15`,
                color: t.color,
              }}
            >
              {t.icon}
            </div>
            <span>{t.label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
