import { useMutation, useQueryClient } from '@tanstack/react-query';
import { WorkspaceAPI } from '../api';
import { useAuthStore } from '../store/authStore';
import { useUIStore } from '../store/uiStore';
import { SystemApiError } from '../api';

/**
 * Authentication and Session Management Hooks.
 */
export const useAuth = () => {
  const queryClient = useQueryClient();
  const establishSession = useAuthStore((state) => state.establishSession);
  const terminateSession = useAuthStore((state) => state.terminateSession);
  const setRoute = useUIStore((state) => state.setRoute);

  // Note: In a real system, you would post credentials to an /auth/login endpoint first.
  // For this architecture, we validate the token by immediately fetching the UserContext and RLS boundaries.
  const loginMutation = useMutation({
    mutationFn: async (mockToken: string) => {
      // Temporarily set the token to allow the WorkspaceAPI to authorize
      localStorage.setItem('sz_session_token', mockToken);
      const context = await WorkspaceAPI.getActiveContext();
      return { token: mockToken, context };
    },
    onSuccess: (data) => {
      // Mathematically lock in the session
      establishSession(data.token, data.context);
      setRoute('WORKSPACE');
    },
    onError: (error: unknown) => {
      localStorage.removeItem('sz_session_token');
      if (error instanceof SystemApiError) {
        console.error(`[AUTH FATAL] ${error.message}`);
      }
    }
  });

  const logout = () => {
    // 1. Trigger Zustand Kill Switch
    terminateSession('USER_LOGOUT');
    
    // 2. Mathematically destroy the TanStack React Query memory cache
    // This prevents Tenant A's cached data from appearing when Tenant B logs in
    queryClient.clear();
    
    // 3. Reset UI routing
    setRoute('LOGIN');
  };

  return {
    login: loginMutation.mutate,
    isLoggingIn: loginMutation.isPending,
    error: loginMutation.error,
    logout,
  };
};
