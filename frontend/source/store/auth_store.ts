import { create } from 'zustand';
import { UserContext } from '../types';

/**
 * STRICT SESSION GOVERNANCE
 * This store manages the client-side cryptographic state and RBAC context.
 * It enforces idle timeouts and provides the global 'Kill Switch' for memory purging.
 */

// 15 minutes of inactivity triggers a hard local memory wipe
const IDLE_TIMEOUT_MS = 15 * 60 * 1000;

interface AuthState {
  isAuthenticated: boolean;
  context: UserContext | null;
  lastActivityAt: number;
  
  // Actions
  establishSession: (token: string, context: UserContext) => void;
  terminateSession: (reason?: string) => void;
  registerActivity: () => void;
  checkIdleTimeout: () => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  isAuthenticated: false,
  context: null,
  lastActivityAt: Date.now(),

  establishSession: (token, context) => {
    // Write to local storage for the Axios interceptor
    localStorage.setItem('sz_session_token', token);
    localStorage.setItem('sz_active_workspace', context.activeWorkspaceId);
    
    set({
      isAuthenticated: true,
      context,
      lastActivityAt: Date.now(),
    });
  },

  terminateSession: (reason = 'USER_INITIATED') => {
    console.warn(`[SECURITY] Terminating session. Reason: ${reason}`);
    
    // 1. Destroy cryptographic material
    localStorage.removeItem('sz_session_token');
    localStorage.removeItem('sz_active_workspace');
    
    // 2. Wipe React memory state
    set({
      isAuthenticated: false,
      context: null,
      lastActivityAt: 0,
    });

    // 3. Dispatch global kill event to wipe all other Zustand stores and React Query caches
    window.dispatchEvent(new Event('sz_memory_purge'));
  },

  registerActivity: () => {
    if (get().isAuthenticated) {
      set({ lastActivityAt: Date.now() });
    }
  },

  checkIdleTimeout: () => {
    const state = get();
    if (!state.isAuthenticated) return false;
    
    if (Date.now() - state.lastActivityAt > IDLE_TIMEOUT_MS) {
      state.terminateSession('IDLE_TIMEOUT');
      return true;
    }
    return false;
  }
}));
