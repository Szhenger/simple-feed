import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { WorkspaceAPI } from '../api';
import { useAuthStore } from '../store/authStore';

/**
 * Hooks for managing the active database shard and RLS boundaries.
 */
export const useWorkspaces = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return useQuery({
    queryKey: ['system', 'workspaces'],
    queryFn: async () => await WorkspaceAPI.listWorkspaces(),
    enabled: isAuthenticated,
    staleTime: 1000 * 60 * 60, // Workspaces rarely change during an active session
  });
};

export const useSwitchTenant = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (newWorkspaceId: string) => {
      // Note: A highly secure architecture verifies tenant access server-side before switching
      localStorage.setItem('sz_active_workspace', newWorkspaceId);
      return newWorkspaceId;
    },
    onSuccess: () => {
      // If the Row-Level Security boundary changes, all existing local memory is mathematically invalid.
      // We must purge the query cache to force a fresh pull from the new shard.
      queryClient.invalidateQueries({ queryKey: ['feedItems'] });
      queryClient.invalidateQueries({ queryKey: ['system', 'telemetry'] });
      
      // Dispatch memory purge for local UI states
      window.dispatchEvent(new Event('sz_axiom_switch'));
    }
  });
};
