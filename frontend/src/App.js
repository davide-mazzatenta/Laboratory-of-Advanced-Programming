// src/App.js - Simplified version without AuthCallback
import React, { useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { ThemeContextProvider } from './context/ThemeContext';
import { useAuth } from './context/AuthContext';

import './styles/globals.css';
import './styles/login-scope.css';

import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Projects from './pages/Projects';
import Documents from './pages/Documents';
import AgentsPage from './pages/AgentsPage';

const PrivateRoute = ({ children }) => {
  const { loading, isAuthenticated } = useAuth();

  // Show loader while checking authentication
  if (loading) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          background: '#f5f5f5',
        }}
      >
        <div
          className="loading-spinner"
          style={{
            border: '4px solid rgba(0, 0, 0, 0.1)',
            borderRadius: '50%',
            borderTop: '4px solid #3498db',
            width: '40px',
            height: '40px',
            animation: 'spin 1s linear infinite',
          }}
        >
          <style>{`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}</style>
        </div>
      </div>
    );
  }

  if (!isAuthenticated()) {
    console.log('PrivateRoute: User not authenticated, redirecting to login');
    return <Navigate to="/login" />;
  }

  return children;
};

// Global Refresh Handler Component
const GlobalRefreshHandler = () => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Skip redirect logic for login page and home page
    if (location.pathname === '/login' || location.pathname === '/') {
      console.log(`🏠 GlobalRefreshHandler: Skipping redirect logic for ${location.pathname}`);
      return;
    }

    console.log(`🔄 GlobalRefreshHandler: ACTIVE on ${location.pathname} - F5 and refresh will redirect to dashboard`);

    // Global handler for F5 and Ctrl+R
    const handleGlobalKeyDown = (event) => {
      if (event.key === 'F5' || (event.ctrlKey && event.key === 'r') || (event.metaKey && event.key === 'r')) {
        event.preventDefault();
        event.stopPropagation();
        console.log(`🚀 GLOBAL REDIRECT: F5/Ctrl+R detected on ${location.pathname}, redirecting to dashboard`);
        navigate('/', { replace: true });
        return false;
      }
    };

    // Global handler for page refresh detection
    const handleGlobalBeforeUnload = () => {
      console.log(`💾 STORING REFRESH DATA: beforeunload on ${location.pathname}`);
      sessionStorage.setItem('globalRefreshRedirect', 'true');
      sessionStorage.setItem('globalLastPath', location.pathname);
    };

    // Check for global refresh redirect
    const checkGlobalRefresh = () => {
      const shouldRedirect = sessionStorage.getItem('globalRefreshRedirect');
      const lastPath = sessionStorage.getItem('globalLastPath');
      
      console.log(`🔍 CHECKING REFRESH: shouldRedirect=${shouldRedirect}, lastPath=${lastPath}, currentPath=${location.pathname}`);
      
      if (shouldRedirect === 'true' && lastPath && lastPath !== '/' && lastPath !== '/login') {
        console.log(`🎯 REFRESH REDIRECT TRIGGERED: ${lastPath} → dashboard`);
        sessionStorage.removeItem('globalRefreshRedirect');
        sessionStorage.removeItem('globalLastPath');
        navigate('/', { replace: true });
      }
    };

    // Add global event listeners
    document.addEventListener('keydown', handleGlobalKeyDown, true);
    window.addEventListener('beforeunload', handleGlobalBeforeUnload);
    
    // Check for redirect immediately
    checkGlobalRefresh();

    return () => {
      document.removeEventListener('keydown', handleGlobalKeyDown, true);
      window.removeEventListener('beforeunload', handleGlobalBeforeUnload);
    };
  }, [navigate, location.pathname]);

  return null; // This component doesn't render anything
};

function App() {
  return (
    <ThemeContextProvider>
      <div className="app-root full-width full-height">
        <div className="app-container full-width full-height">
          <GlobalRefreshHandler />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route 
              path="/projects" 
              element={
                <PrivateRoute>
                  <Projects />
                </PrivateRoute>
              } 
            />
            <Route 
              path="/documents/:projectId" 
              element={
                <PrivateRoute>
                  <Documents />
                </PrivateRoute>
              } 
            />
            <Route 
              path="/agents/:projectId" 
              element={
                <PrivateRoute>
                  <AgentsPage />
                </PrivateRoute>
              } 
            />
            <Route
              path="/"
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </div>
    </ThemeContextProvider>
  );
}

export default App;
