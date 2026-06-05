/**
 * Store Governance & Initialization
 */

export * from './authStore';
export * from './workspaceStore';
export * from './uiStore';

// Initialize the global security daemon
import { useAuthStore } from './authStore';

/**
 * Initializes the security daemon to monitor for idle timeouts and RLS boundaries.
 * Call this exactly once in App.tsx.
 */
export const initializeSecurityDaemon = () => {
  // 1. Monitor UI interactions to reset the idle timer
  const registerActivity = useAuthStore.getState().registerActivity;
  
  const events = ['mousedown', 'keydown', 'scroll', 'touchstart'];
  events.forEach(event => {
    window.addEventListener(event, registerActivity, { passive: true });
  });

  // 2. Poll for idle timeout every 30 seconds
  setInterval(() => {
    useAuthStore.getState().checkIdleTimeout();
  }, 30000);
};
