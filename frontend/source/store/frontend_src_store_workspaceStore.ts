import { create } from 'zustand';
import { FeedItem } from '../types';

interface WorkspaceState {
  activeArticle: FeedItem | null;
  openArticle: (item: FeedItem) => void;
  closeArticle: () => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  activeArticle: null,
  openArticle: (item) => set({ activeArticle: item }),
  closeArticle: () => set({ activeArticle: null }),
}));
