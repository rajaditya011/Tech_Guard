import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AppShell from '../components/layout/AppShell';

export default function DemoPage() {
  const [scenarios, setScenarios] = useState([]);
  const [activeSimulation, setActiveSimulation] = useState(null);
  const { login, register, token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    let mounted = true;
    fetch((import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/api/demo/scenarios')
      .then(res => res.json())
      .then(data => { if (mounted) setScenarios(data); })
      .catch(console.error);
    return () => { mounted = false; };
  }, []);

  const runScenario = async (id, name) => {
    try {
      setActiveSimulation(id);
      
      // Auto-login for demo mode if not already authenticated
      if (!token) {
        try {
          await login('demo_user', 'password123');
        } catch (e) {
          // If login fails, try registering the demo user
          await register('demo_user', 'password123', 'new_device');
        }
      }

      await fetch((import.meta.env.VITE_API_URL || 'http://localhost:8000') + `/api/demo/start/${id}`, { method: 'POST' });
      navigate('/new-device/dashboard');
    } catch (e) {
      console.error(e);
      setActiveSimulation(null);
    }
  };

  return (
    <AppShell>
      <div className="flex items-center justify-center min-h-screen px-4 py-8">
        <div className="glass-card p-6 md:p-8 max-w-2xl w-full text-center">
          <h1 className="text-2xl font-bold gradient-text mb-4">Demo Simulation Engine</h1>
          <p className="text-sm mb-6" style={{ color: 'var(--text-secondary)' }}>
            Experience HomeGuardian AI's capabilities safely. This mode
            hooks into backend scenarios to simulate complex sensor data, behavioral analytics, 
            and AI-generated narratives dynamically in real-time.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
            {scenarios.map((scenario) => (
              <div key={scenario.id} className="glass-card p-5 flex flex-col justify-between" style={{ border: '1px solid var(--border-primary)' }}>
                <div>
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-xs font-mono uppercase px-2 py-1 rounded" style={{ background: 'var(--bg-tertiary)', color: 'var(--accent-blue)' }}>
                      Scenario {['A','B','C','D'][scenario.id - 1] || scenario.id}
                    </span>
                    <span className="text-[10px] font-mono text-right" style={{ color: 'var(--text-tertiary)' }}>{scenario.phase_count} PHASES</span>
                  </div>
                  <h3 className="text-sm font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>{scenario.name}</h3>
                  <p className="text-xs mb-4" style={{ color: 'var(--text-secondary)' }}>{scenario.description}</p>
                </div>
                <button 
                  onClick={() => runScenario(scenario.id, scenario.name)}
                  disabled={activeSimulation === scenario.id}
                  className="w-full py-2.5 rounded text-xs font-bold cursor-pointer border-none transition-all"
                  style={{ background: activeSimulation === scenario.id ? 'var(--bg-tertiary)' : 'var(--accent-blue)', color: '#ffffff' }}
                >
                  {activeSimulation === scenario.id ? 'Starting Pipeline...' : 'Run Simulation'}
                </button>
              </div>
            ))}
          </div>
          
          <div className="mt-8 border-t border-[var(--border-secondary)] pt-6">
            <button
              onClick={async () => {
                await fetch((import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/api/demo/clear', { method: 'POST' });
                alert('Demo data wiped!');
              }}
              className="px-4 py-2 rounded text-xs font-mono cursor-pointer border hover:opacity-80 transition-opacity"
              style={{ borderColor: 'var(--accent-red)', color: 'var(--accent-red)', background: 'transparent' }}
            >
              CLEAR DEMO DATA
            </button>
          </div>

          <p className="text-xs mt-6 uppercase font-mono tracking-widest" style={{ color: 'var(--text-tertiary)' }}>
            Diagnostics Check Passed
          </p>
        </div>
      </div>
    </AppShell>
  );
}
