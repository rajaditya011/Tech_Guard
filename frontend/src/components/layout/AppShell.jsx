import ThemeToggle from './ThemeToggle';

export default function AppShell({ children, showThemeToggle = true }) {
  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}
    >
      {showThemeToggle && (
        <div className="fixed top-4 right-4 z-50">
          <ThemeToggle />
        </div>
      )}
      {children}
    </div>
  );
}
