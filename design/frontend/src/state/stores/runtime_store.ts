import { create } from 'zustand';

export type RuntimePhase = 'brief' | 'respond' | 'reflect';

interface RuntimeState {
  attemptId: string | null;
  phase: RuntimePhase;
  isRecording: boolean;
  /** The editable, to-be-submitted transcript for the current capture. */
  transcript: string;

  startAttempt: (attemptId: string) => void;
  setPhase: (phase: RuntimePhase) => void;
  setRecording: (on: boolean) => void;
  setTranscript: (text: string) => void;
  reset: () => void;
}

const initialState = {
  attemptId: null,
  phase: 'brief' as RuntimePhase,
  isRecording: false,
  transcript: '',
};

export const useRuntimeStore = create<RuntimeState>()((set) => ({
  ...initialState,

  startAttempt: (attemptId: string) =>
    set({ ...initialState, attemptId, phase: 'brief' }),
  setPhase: (phase: RuntimePhase) => set({ phase }),
  setRecording: (on: boolean) => set({ isRecording: on }),
  setTranscript: (text: string) => set({ transcript: text }),
  reset: () => set(initialState),
}));
