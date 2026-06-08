import { create } from 'zustand';

interface OnboardingState {
  selectedTrigger: string | null;
  stepIndex: number;

  setSelectedTrigger: (trigger: string | null) => void;
  setStepIndex: (i: number) => void;
  reset: () => void;
}

const initialState = {
  selectedTrigger: null,
  stepIndex: 0,
};

export const useOnboardingStore = create<OnboardingState>()((set) => ({
  ...initialState,

  setSelectedTrigger: (trigger: string | null) =>
    set({ selectedTrigger: trigger }),
  setStepIndex: (i: number) => set({ stepIndex: i }),
  reset: () => set(initialState),
}));
