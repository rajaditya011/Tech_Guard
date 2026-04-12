export default function Sidebar({ activePanel, onPanelChange, collapsed, onToggle, onLogout }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: 'O' },
    { id: 'feeds', label: 'Live Feeds', icon: 'F' },
    { id: 'floorplan', label: 'Floor Plan', icon: 'P' },
    { id: 'alerts', label: 'Alerts', icon: 'A' },
    { id: 'sensors', label: 'Sensors', icon: 'S' },
    { id: 'communicate', label: 'Communicate', icon: 'C' },
    { id: 'reasoning', label: 'AI Reasoning', icon: 'R' },
  ];

  return (
    <aside
      className={`fixed top-0 left-0 h-screen flex flex-col z-50 glass-card rounded-none border-y-0 border-l-0 ${collapsed ? '-translate-x-full md:translate-x-0' : 'translate-x-0'}`}
      style={{
        width: collapsed ? '64px' : '240px',
        borderRight: '1px solid var(--border-primary)',
        transition: 'all 0.3s ease',
      }}
      id="dashboard-sidebar"
    >
      {/* Logo */}
      <div className="p-4 flex items-center gap-3" style={{ borderBottom: '1px solid var(--border-primary)' }}>
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0"
          style={{ background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-violet))', color: '#fff' }}
        >
          HG
        </div>
        {!collapsed && (
          <span className="text-sm font-semibold truncate" style={{ color: 'var(--text-primary)' }}>
            HomeGuardian
          </span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-1">
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => onPanelChange(item.id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm
                       cursor-pointer transition-all border-none`}
            style={{
              background: activePanel === item.id ? 'var(--bg-glass)' : 'transparent',
              color: activePanel === item.id ? 'var(--text-primary)' : 'var(--text-secondary)',
            }}
            id={`nav-${item.id}`}
          >
            <span
              className="w-7 h-7 rounded flex items-center justify-center text-xs font-mono flex-shrink-0"
              style={{
                background: activePanel === item.id ? 'var(--accent-blue)' : 'var(--bg-surface)',
                color: activePanel === item.id ? '#ffffff' : 'var(--text-tertiary)',
              }}
            >
              {item.icon}
            </span>
            {!collapsed && <span className="truncate">{item.label}</span>}
          </button>
        ))}
      </nav>

      {/* Bottom */}
      <div className="p-3 space-y-2" style={{ borderTop: '1px solid var(--border-primary)' }}>
        <button
          onClick={onToggle}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs
                     cursor-pointer bg-transparent border-none"
          style={{ color: 'var(--text-tertiary)' }}
        >
          {collapsed ? '>>' : '<< Collapse'}
        </button>
        <button
          onClick={onLogout}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs
                     cursor-pointer bg-transparent border-none"
          style={{ color: 'var(--accent-red)' }}
          id="dashboard-logout-btn"
        >
          {collapsed ? 'X' : 'Sign Out'}
        </button>
      </div>
    </aside>
  );
}
