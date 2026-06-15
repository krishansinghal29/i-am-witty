import { create } from 'zustand';

export type RolePlayPhase = 'chatting' | 'done';
export type ChatRole = 'she' | 'you';

/** One rendered chat bubble. For `she`, `narration` is the (un-spoken) scene
 *  line shown above her spoken `text`; for `you`, only `text` is used. */
export interface ChatMessage {
  id: string;
  role: ChatRole;
  narration?: string;
  text: string;
  /** Whether this exchange landed a misinterpretation (drives subtle styling). */
  landed?: boolean;
  /** Spoken-line audio for `she` messages (TTS), used for playback + reveal sync. */
  audioBase64?: string | null;
  audioContentType?: string | null;
}

interface RolePlayState {
  attemptId: string | null;
  phase: RolePlayPhase;
  messages: ChatMessage[];
  landedCount: number;
  targetCount: number;
  /** True while a turn request is in flight. */
  isAwaitingReply: boolean;
  isRecording: boolean;
  /** The editable line shown in the input box (filled after the user stops speaking). */
  draft: string;

  start: (attemptId: string, targetCount: number) => void;
  addMessage: (message: ChatMessage) => void;
  setProgress: (landedCount: number, targetCount: number) => void;
  setAwaitingReply: (on: boolean) => void;
  setRecording: (on: boolean) => void;
  setDraft: (text: string) => void;
  setPhase: (phase: RolePlayPhase) => void;
  reset: () => void;
}

const initialState = {
  attemptId: null,
  phase: 'chatting' as RolePlayPhase,
  messages: [] as ChatMessage[],
  landedCount: 0,
  targetCount: 5,
  isAwaitingReply: false,
  isRecording: false,
  draft: '',
};

export const useRolePlayStore = create<RolePlayState>()((set) => ({
  ...initialState,

  start: (attemptId, targetCount) =>
    set({ ...initialState, attemptId, targetCount }),
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  setProgress: (landedCount, targetCount) => set({ landedCount, targetCount }),
  setAwaitingReply: (on) => set({ isAwaitingReply: on }),
  setRecording: (on) => set({ isRecording: on }),
  setDraft: (text) => set({ draft: text }),
  setPhase: (phase) => set({ phase }),
  reset: () => set(initialState),
}));
