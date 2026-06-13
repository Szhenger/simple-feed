import { create } from 'zustand';

interface FeedEvent {
  id: string;
  pillar: 'EDUCATION' | 'FINANCE' | 'PLANNING';
  title: string;
  payload: any;
  priority: number;
  timestamp: number;
}

interface FeedState {
  events: FeedEvent[];
  unreadCount: number;
  connect: (workspaceId: string) => void;
  markAllRead: () => void;
}

export const useFeedStore = create<FeedState>((set, get) => ({
  events: [],
  unreadCount: 0,
  
  connect: (workspaceId: string) => {
    const ws = new WebSocket(`ws://localhost:8000/ws/feed/${workspaceId}/`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const newEvent: FeedEvent = {
        id: crypto.randomUUID(),
        ...data
      };
      
      set((state) => ({
        events: [newEvent, ...state.events].slice(0, 100), // Keep a ring buffer of last 100 events
        unreadCount: state.unreadCount + 1
      }));
    };
  },
  
  markAllRead: () => set({ unreadCount: 0 })
}));
