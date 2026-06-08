import { create } from 'zustand';

export type RuntimePhase = 'brief' | 'respond' | 'reflect';

interface RuntimeState {
  attemptId: string | null;
  phase: RuntimePhase;
  scaffoldStageIndex: number;
  isRecording: boolean;
  transcript: string;

  startAttempt: (attemptId: string) => void;
  setPhase: (phase: RuntimePhase) => void;
  setScaffoldStageIndex: (i: number) => void;
  setRecording: (on: boolean) => void;
  setTranscript: (text: string) => void;
  reset: () => void;
}

const initialState = {
  attemptId: null,
  phase: 'brief' as RuntimePhase,
  scaffoldStageIndex: 0,
  isRecording: false,
  transcript: '',
};

export const useRuntimeStore = create<RuntimeState>()((set) => ({
  ...initialState,

  startAttempt: (attemptId: string) =>
    set({ ...initialState, attemptId, phase: 'brief' }),
  setPhase: (phase: RuntimePhase) => set({ phase }),
  setScaffoldStageIndex: (i: number) => set({ scaffoldStageIndex: i }),
  setRecording: (on: boolean) => set({ isRecording: on }),
  setTranscript: (text: string) => set({ transcript: text }),
  reset: () => set(initialState),
}));
