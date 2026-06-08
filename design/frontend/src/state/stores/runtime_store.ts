import { create } from 'zustand';

export type RuntimePhase = 'brief' | 'respond' | 'reflect';

/** One captured rehearsal-stage response (scaffolded voice tasks). */
export interface StageResponseEntry {
  position: number;
  transcript: string;
}

interface RuntimeState {
  attemptId: string | null;
  phase: RuntimePhase;
  scaffoldStageIndex: number;
  isRecording: boolean;
  /** The editable, to-be-submitted transcript for the current capture. */
  transcript: string;
  /** Cosmetic live transcript streamed from the gateway while recording. */
  interimTranscript: string;
  /** Earlier scaffold-stage responses collected before the final submission. */
  stageResponses: StageResponseEntry[];

  startAttempt: (attemptId: string) => void;
  setPhase: (phase: RuntimePhase) => void;
  setScaffoldStageIndex: (i: number) => void;
  setRecording: (on: boolean) => void;
  setTranscript: (text: string) => void;
  setInterim: (text: string) => void;
  recordStageResponse: (entry: StageResponseEntry) => void;
  reset: () => void;
}

const initialState = {
  attemptId: null,
  phase: 'brief' as RuntimePhase,
  scaffoldStageIndex: 0,
  isRecording: false,
  transcript: '',
  interimTranscript: '',
  stageResponses: [] as StageResponseEntry[],
};

export const useRuntimeStore = create<RuntimeState>()((set) => ({
  ...initialState,

  startAttempt: (attemptId: string) =>
    set({ ...initialState, attemptId, phase: 'brief' }),
  setPhase: (phase: RuntimePhase) => set({ phase }),
  setScaffoldStageIndex: (i: number) => set({ scaffoldStageIndex: i }),
  setRecording: (on: boolean) => set({ isRecording: on }),
  setTranscript: (text: string) => set({ transcript: text }),
  setInterim: (text: string) => set({ interimTranscript: text }),
  recordStageResponse: (entry: StageResponseEntry) =>
    set((state) => {
      const others = state.stageResponses.filter(
        (s) => s.position !== entry.position,
      );
      return {
        stageResponses: [...others, entry].sort((a, b) => a.position - b.position),
      };
    }),
  reset: () => set(initialState),
}));
