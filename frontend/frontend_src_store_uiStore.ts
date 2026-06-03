import { create } from 'zustand';
import { AxiomCategory } from '../types';

interface UIState {
  isSidebarOpen: boolean;
  activeAxiom: AxiomCategory | 'ALL';
  toggleSidebar: () => void;
  setActiveAxiom: (axiom: AxiomCategory | 'ALL') => void;
}

export const useUIStore = create<UIState>((set) => ({
  isSidebarOpen: true,
  activeAxiom: 'ALL',
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  setActiveAxiom: (axiom) => set({ activeAxiom: axiom }),
}));
