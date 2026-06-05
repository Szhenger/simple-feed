import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { SystemAPI } from '../api';
import { useAuthStore } from '../store/authStore';

export const useTelemetry = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const activeWorkspaceId = useAuthStore((state) => state.context?.activeWorkspaceId);

  return useQuery({
    // Cache is strictly bound to the active shard/workspace
    queryKey: ['system', 'telemetry', activeWorkspaceId],
    queryFn: async () => await SystemAPI.getTelemetry(),
    enabled: isAuthenticated && activeWorkspaceId !== undefined,
    refetchInterval: 15000, // Background polling every 15s to keep the dashboard live
  });
};

export const useVectorThreshold = () => {
  const queryClient = useQueryClient();
  const activeWorkspaceId = useAuthStore((state) => state.context?.activeWorkspaceId);

  return useMutation({
    mutationFn: async (tau: number) => await SystemAPI.updateVectorThreshold(tau),
    onSuccess: () => {
      // Invalidate both telemetry and feed items, as changing the threshold 
      // fundamentally alters which items bypass the triage gate.
      queryClient.invalidateQueries({ queryKey: ['system', 'telemetry', activeWorkspaceId] });
      queryClient.invalidateQueries({ queryKey: ['feedItems', activeWorkspaceId] });
    }
  });
};
