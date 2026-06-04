import { apiClient } from './client';
import { ApiResponseEnvelope, Workspace, UserContext } from '../types';

export const WorkspaceAPI = {
  /**
   * Resolves the current user's deterministic identity and RBAC boundaries.
   */
  async getActiveContext(): Promise<UserContext> {
    const { data } = await apiClient.get<ApiResponseEnvelope<UserContext>>('/auth/context');
    return data.data;
  },

  /**
   * Retrieves shards mapped to this user.
   */
  async listWorkspaces(): Promise<Workspace[]> {
    const { data } = await apiClient.get<ApiResponseEnvelope<Workspace[]>>('/workspaces');
    return data.data;
  }
};
