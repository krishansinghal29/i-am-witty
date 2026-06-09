import { create } from 'zustand';

/** The revamped onboarding is two client-side steps: pick a trigger, then sign in. */
export type OnboardingStep = 'trigger' | 'login';

/**
 * Transient onboarding UI state held entirely client-side until completion:
 * the trigger the user tapped and which of the two steps is showing.
 */
interface OnboardingUiStore {
  selectedTrigger: string | null;
  step: OnboardingStep;

  setSelectedTrigger: (trigger: string | null) => void;
  setStep: (step: OnboardingStep) => void;
  reset: () => void;
}

const initialState: Pick<OnboardingUiStore, 'selectedTrigger' | 'step'> = {
  selectedTrigger: null,
  step: 'trigger',
};

export const useOnboardingStore = create<OnboardingUiStore>()((set) => ({
  ...initialState,

  setSelectedTrigger: (selectedTrigger) => set({ selectedTrigger }),
  setStep: (step) => set({ step }),
  reset: () => set(initialState),
}));
