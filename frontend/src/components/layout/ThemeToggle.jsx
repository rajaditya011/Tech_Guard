import { useTheme } from '../../contexts/ThemeContext';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      id="theme-toggle-btn"
      onClick={toggleTheme}
      className="glass-card px-3 py-1.5 text-xs font-mono uppercase tracking-wider
                 cursor-pointer transition-all duration-200
                 hover:border-[var(--accent-blue)]"
      style={{
        color: 'var(--text-secondary)',
        border: '1px solid var(--border-secondary)',
      }}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
    >
      {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
    </button>
  );
}
