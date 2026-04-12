import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import { I18nProvider } from './contexts/I18nContext';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import OldDeviceLogin from './pages/OldDeviceLogin';
import OldDevicePortal from './pages/OldDevicePortal';
import NewDeviceLogin from './pages/NewDeviceLogin';
import NewDeviceDashboard from './pages/NewDeviceDashboard';
import DemoPage from './pages/DemoPage';
import EnhancedBackgroundPaths from './components/ui/modern-background-paths';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5000,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <I18nProvider>
          <AuthProvider>
            <BrowserRouter>
            <Routes>
              {/* Old Device Portal */}
              <Route path="/old-device/login" element={<OldDeviceLogin />} />
              <Route path="/old-device/portal" element={<OldDevicePortal />} />

              {/* New Device Dashboard */}
              <Route path="/new-device/login" element={<NewDeviceLogin />} />
              <Route path="/new-device/dashboard" element={<NewDeviceDashboard />} />

              {/* Demo Mode */}
              <Route path="/demo" element={<DemoPage />} />

              {/* Default landing page */}
              <Route path="/" element={<EnhancedBackgroundPaths />} />
              <Route path="*" element={<Navigate to="/new-device/login" replace />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
        </I18nProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
