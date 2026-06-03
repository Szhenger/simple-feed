import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { FeedItem, AxiomCategory } from '../types';

interface FetchFeedsParams {
  axiom?: AxiomCategory | 'ALL';
}

export const useFeedItems = ({ axiom }: FetchFeedsParams) => {
  return useQuery({
    queryKey: ['feedItems', axiom],
    queryFn: async async (): Promise<FeedItem[]> => {
      const { data } = await apiClient.get('/feed/items', {
        params: axiom !== 'ALL' ? { category: axiom } : undefined,
      });
      return data;
    },
    // Failsafe empty array while backend is offline during local dev
    initialData: [],
  });
};
