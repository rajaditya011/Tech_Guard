import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useI18n } from '../contexts/I18nContext';
import AppShell from '../components/layout/AppShell';
import LiveFeedGrid from '../components/dashboard/LiveFeedGrid';
import FloorPlan from '../components/dashboard/FloorPlan';
import AlertFeed from '../components/dashboard/AlertFeed';
import RiskGauge from '../components/dashboard/RiskGauge';
import SensorHealth from '../components/dashboard/SensorHealth';
import CommPanel from '../components/dashboard/CommPanel';
import ReasoningReplay from '../components/dashboard/ReasoningReplay';
import Sidebar from '../components/layout/Sidebar';

export default function NewDeviceDashboard() {
  const { user, token, logout } = useAuth();
  const { lang, setLang, t } = useI18n();
  const navigate = useNavigate();
  const [activePanel, setActivePanel] = useState('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      // Auto-register/login for demo if token is missing
      // For now, redirect to login
      navigate('/new-device/login');
    }
  }, [token, navigate]);

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1200);
    return () => clearTimeout(timer);
  }, []);

  const renderPanel = () => {
    switch (activePanel) {
      case 'overview': return <OverviewPanel isLoading={isLoading} />;
      case 'feeds': return <LiveFeedGrid />;
      case 'floorplan': return <FloorPlan />;
      case 'alerts': return <AlertFeed />;
      case 'sensors': return <SensorHealth />;
      case 'communicate': return <CommPanel />;
      case 'reasoning': return <ReasoningReplay />;
      default: return <OverviewPanel isLoading={isLoading} />;
    }
  };

  return (
    <AppShell>
      <div className="flex min-h-screen">
        <Sidebar activePanel={activePanel} onPanelChange={setActivePanel}
          collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          onLogout={() => { logout(); navigate('/new-device/login'); }} />
        <main 
          style={{ transition: 'margin-left 0.3s ease' }}
          className={`flex-1 overflow-y-auto ${sidebarCollapsed ? 'ml-0 md:ml-[64px]' : 'ml-0 md:ml-[240px]'}`}
        >
          <header className="sticky top-0 z-40 px-4 md:px-6 py-4 flex items-center justify-between glass-card rounded-none border-t-0 border-x-0"
            style={{ borderBottom: '1px solid var(--border-primary)', backdropFilter: 'blur(12px)' }}>
            <div className="flex items-center gap-3">
              <button 
                className="md:hidden p-2 rounded glass-card text-xs cursor-pointer border-none"
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                style={{ color: 'var(--text-primary)' }}
              >
                {sidebarCollapsed ? '☰' : '✕'}
              </button>
              <div>
                <h1 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                  {t(activePanel.charAt(0).toUpperCase() + activePanel.slice(1))}
                </h1>
                <p className="text-xs hidden sm:block" style={{ color: 'var(--text-tertiary)' }}>{t('Real-time security intelligence')}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button 
                onClick={() => setLang(lang === 'en' ? 'es' : 'en')}
                className="text-xs font-mono px-2 py-1 rounded cursor-pointer glass-card border-none"
                style={{ color: 'var(--text-primary)' }}
              >
                {lang.toUpperCase()}
              </button>
              <RiskGauge score={12} size="small" />
            </div>
          </header>
          <div className="p-4 md:p-6">{renderPanel()}</div>
        </main>
      </div>
    </AppShell>
  );
}

function OverviewPanel({ isLoading }) {
  return (
    <div className="flex flex-col space-y-6 max-w-5xl">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="glass-card p-8 flex flex-col items-center justify-center h-full min-h-[240px]">
            <RiskGauge score={12} size="large" />
            <p className="text-xs mt-5 font-mono uppercase tracking-widest" style={{ color: 'var(--text-tertiary)' }}>System Risk Level</p>
          </div>
        </div>
        <div className="lg:col-span-2">
          <div className="grid grid-cols-2 gap-4 md:gap-6 h-full">
            <StatCard label="Active Sensors" value="3" accent="blue" isLoading={isLoading} />
            <StatCard label="Anomalies Today" value="0" accent="emerald" isLoading={isLoading} />
            <StatCard label="Alerts Sent" value="0" accent="violet" isLoading={isLoading} />
            <StatCard label="Baseline Status" value="35%" accent="amber" isLoading={isLoading} />
          </div>
        </div>
      </div>
      
      <div className="w-full">
        <AlertFeed compact />
      </div>
    </div>
  );
}

function StatCard({ label, value, accent, isLoading }) {
  return (
    <div className="glass-card p-4 text-center flex flex-col items-center justify-center">
      {isLoading ? (
        <>
          <div className="w-12 h-8 rounded animate-pulse mb-2" style={{ background: 'var(--bg-tertiary)' }} />
          <div className="w-16 h-3 rounded animate-pulse" style={{ background: 'var(--bg-tertiary)' }} />
        </>
      ) : (
        <>
          <div className="text-2xl font-bold mb-1" style={{ color: `var(--accent-${accent})` }}>{value}</div>
          <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>{label}</div>
        </>
      )}
    </div>
  );
}
