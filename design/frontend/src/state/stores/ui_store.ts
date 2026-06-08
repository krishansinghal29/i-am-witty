import { create } from 'zustand';

interface UiState {
  paywallOpen: boolean;
  paywallReason: string | null;
  supportOpen: boolean;
  supportSourceScreen: string | null;
  attentionDot: boolean;

  openPaywall: (reason?: string) => void;
  closePaywall: () => void;
  openSupport: (sourceScreen?: string) => void;
  closeSupport: () => void;
  setAttentionDot: (on: boolean) => void;
}

export const useUiStore = create<UiState>()((set) => ({
  paywallOpen: false,
  paywallReason: null,
  supportOpen: false,
  supportSourceScreen: null,
  attentionDot: false,

  openPaywall: (reason?: string) =>
    set({ paywallOpen: true, paywallReason: reason ?? null }),
  closePaywall: () => set({ paywallOpen: false, paywallReason: null }),

  openSupport: (sourceScreen?: string) =>
    set({ supportOpen: true, supportSourceScreen: sourceScreen ?? null }),
  closeSupport: () => set({ supportOpen: false, supportSourceScreen: null }),

  setAttentionDot: (on: boolean) => set({ attentionDot: on }),
}));
