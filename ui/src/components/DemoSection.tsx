export default function DemoSection() {
  const scenarios = [
    {
      num: 'SCENARIO 01',
      title: 'Normal Morning Routine',
      desc: '14-day baseline established. Owner leaves at 8 AM. Normal kitchen and living room activity detected and classified as routine.',
      phases: 1,
    },
    {
      num: 'SCENARIO 02',
      title: 'Late Night Anomaly',
      desc: '2:43 AM, motion in living room. No baseline match. Risk escalates Medium → High. Clip generated. AI narrative written.',
      phases: 3,
    },
    {
      num: 'SCENARIO 03',
      title: 'Casing Simulation',
      desc: 'Afternoon perimeter sensor detects slow repeated passes at the front door. Watch flag raised. 73% scenario match.',
      phases: 2,
    },
    {
      num: 'SCENARIO 04',
      title: 'Full Intrusion Prediction',
      desc: 'Complete 4-phase sequence: Casing → Entry Probing → Reconnaissance → Intrusion. Critical alert fires during Phase 2.',
      phases: 4,
    },
  ];

  return (
    <section className="content-section fade-in-section" id="demo">
      <div className="section-tag">Zero API Keys Required</div>
      <h2 className="section-title">Demo Mode</h2>
      <p className="section-description">
        Run every feature with synthetic data. No Claude key, no Firebase, no MQTT broker — the system generates realistic simulations.
      </p>

      <div className="demo-scenarios">
        {scenarios.map((s, i) => (
          <div className="demo-card" key={i}>
            <div className="demo-number">{s.num}</div>
            <h4>{s.title}</h4>
            <p>{s.desc}</p>
            <div className="demo-phases">
              {Array.from({ length: s.phases }).map((_, j) => (
                <div
                  className="phase-dot"
                  key={j}
                  style={{
                    opacity: 0.3 + (j / s.phases) * 0.7,
                    background:
                      j === s.phases - 1 && s.phases >= 3
                        ? '#ef4444'
                        : j === s.phases - 1 && s.phases === 2
                        ? '#f59e0b'
                        : '#E5C07B',
                  }}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
