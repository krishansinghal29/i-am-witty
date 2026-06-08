import { create } from 'zustand';
import type { UxStep } from '@/features/onboarding/onboarding_machine';

/**
 * Transient onboarding UI state: the trigger the user tapped (held before it is
 * persisted server-side) and the furthest UX step reached this session. The
 * view-model reconciles this forward against the authoritative backend step.
 */
interface OnboardingUiStore {
  selectedTrigger: string | null;
  uxStep: UxStep;

  setSelectedTrigger: (trigger: string | null) => void;
  setUxStep: (step: UxStep) => void;
  reset: () => void;
}

const initialState: Pick<OnboardingUiStore, 'selectedTrigger' | 'uxStep'> = {
  selectedTrigger: null,
  uxStep: 'trigger',
};

export const useOnboardingStore = create<OnboardingUiStore>()((set) => ({
  ...initialState,

  setSelectedTrigger: (trigger) => set({ selectedTrigger: trigger }),
  setUxStep: (step) => set({ uxStep: step }),
  reset: () => set(initialState),
}));
