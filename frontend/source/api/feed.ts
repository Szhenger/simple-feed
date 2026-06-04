import { apiClient } from './client';
import { 
  ApiResponseEnvelope, 
  PaginatedResponse, 
  FeedItem, 
  AxiomCategory, 
  ItemState 
} from '../types';

export const FeedAPI = {
  /**
   * Retrieves the vectorized, strictly-typed feed items.
   * Enforces the τ >= 0.72 pgvector constraint implicitly via the backend route.
   */
  async getWorkspaceItems(category: AxiomCategory | 'ALL'): Promise<FeedItem[]> {
    const params = category !== 'ALL' ? { axiom: category } : undefined;
    
    const { data } = await apiClient.get<ApiResponseEnvelope<PaginatedResponse<FeedItem>>>('/feed/items', { params });
    
    // Unwrap the network envelope and pagination layers
    return data.data.results;
  },

  /**
   * Pushes a FeedItem through the deterministic state machine.
   * e.g., DISCOVERED -> ACTIONABLE
   */
  async transitionItemState(itemId: string, newState: ItemState): Promise<FeedItem> {
    const { data } = await apiClient.post<ApiResponseEnvelope<FeedItem>>(
      `/feed/items/${itemId}/transition`, 
      { state: newState }
    );
    return data.data;
  },

  /**
   * Forces a cold-storage partition push.
   */
  async archiveItem(itemId: string): Promise<void> {
    await apiClient.post(`/feed/items/${itemId}/archive`);
  }
};
