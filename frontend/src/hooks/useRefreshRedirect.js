import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

/**
 * Custom hook that redirects to the home page (/) when the user:
 * - Presses F5 (refresh key)
 * - Uses browser refresh button
 * - Manually reloads the page
 * 
 * Note: This hook should NOT be used on the Dashboard (/) page itself
 */
export const useRefreshRedirect = () => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Don't apply redirect logic if we're already on the home page
    if (location.pathname === '/') {
      // Clean up any existing refresh markers when on home page
      sessionStorage.removeItem('wasRefreshed');
      sessionStorage.removeItem('lastLocation');
      console.log(`🏠 useRefreshRedirect: Skipping hook for home page`);
      return;
    }

    console.log(`🔧 useRefreshRedirect: HOOK ACTIVE on ${location.pathname}`);

    // Handle F5 key press and Ctrl+R
    const handleKeyDown = (event) => {
      if (event.key === 'F5' || (event.ctrlKey && event.key === 'r') || (event.metaKey && event.key === 'r')) {
        event.preventDefault();
        event.stopPropagation();
        console.log(`🚀 HOOK REDIRECT: F5/Ctrl+R/Cmd+R detected on ${location.pathname}, redirecting to home page`);
        navigate('/', { replace: true });
        return false;
      }
    };

    // Handle browser refresh/reload detection
    const handleBeforeUnload = (event) => {
      console.log(`💾 HOOK STORING: beforeunload event on ${location.pathname}`);
      // Store current location to detect refresh on next load
      sessionStorage.setItem('wasRefreshed', 'true');
      sessionStorage.setItem('lastLocation', location.pathname);
      sessionStorage.setItem('refreshTimestamp', Date.now().toString());
    };

    // Check if page was refreshed and redirect if necessary
    const checkRefreshRedirect = () => {
      const wasRefreshed = sessionStorage.getItem('wasRefreshed');
      const lastLocation = sessionStorage.getItem('lastLocation');
      const refreshTimestamp = sessionStorage.getItem('refreshTimestamp');
      
      console.log(`checkRefreshRedirect: wasRefreshed=${wasRefreshed}, lastLocation=${lastLocation}, currentPath=${location.pathname}`);
      
      // Check if this was a refresh and we're not on the home page
      if (wasRefreshed === 'true' && lastLocation && lastLocation !== '/') {
        // Additional check: only redirect if we're on the same page that was refreshed
        // or if enough time has passed (page reload scenario)
        const timeDiff = Date.now() - parseInt(refreshTimestamp || '0');
        const isRecentRefresh = timeDiff < 5000; // 5 seconds threshold
        
        if (location.pathname === lastLocation || isRecentRefresh) {
          console.log(`Refresh detected! Redirecting from ${lastLocation} to home page`);
          
          // Clear the refresh markers immediately
          sessionStorage.removeItem('wasRefreshed');
          sessionStorage.removeItem('lastLocation');
          sessionStorage.removeItem('refreshTimestamp');
          
          // Navigate to home page
          navigate('/', { replace: true });
          return;
        }
      }
      
      // If we're here and not redirecting, clean up old markers
      if (wasRefreshed === 'true') {
        const timeDiff = Date.now() - parseInt(refreshTimestamp || '0');
        if (timeDiff > 10000) { // Clean up markers older than 10 seconds
          sessionStorage.removeItem('wasRefreshed');
          sessionStorage.removeItem('lastLocation');
          sessionStorage.removeItem('refreshTimestamp');
        }
      }
    };

    // Add event listeners with proper options
    document.addEventListener('keydown', handleKeyDown, { capture: true, passive: false });
    window.addEventListener('beforeunload', handleBeforeUnload, { passive: true });
    
    // Check for refresh redirect immediately on mount
    const timeoutId = setTimeout(checkRefreshRedirect, 100);

    // Cleanup function
    return () => {
      document.removeEventListener('keydown', handleKeyDown, { capture: true });
      window.removeEventListener('beforeunload', handleBeforeUnload);
      clearTimeout(timeoutId);
    };
  }, [navigate, location.pathname]);
};

export default useRefreshRedirect;
