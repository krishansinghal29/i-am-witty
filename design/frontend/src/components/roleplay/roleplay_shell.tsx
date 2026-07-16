import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import type { CSSProperties } from 'react';
import { useHistory } from 'react-router-dom';
import { IonIcon } from '@ionic/react';
import { close as closeIcon, send as sendIcon, mic as micIcon, play as playIcon } from 'ionicons/icons';

import { colors, gradients } from '@/theme/tokens';
import { Button, Celebration, ExerciseProgressStrip } from '@/components/ui';
import { useIntegrations } from '@/app/providers';
import { useFreeLimit } from '@/features/entitlement/use_free_limit';
import { useAttemptTurn } from '@/features/task_runtime/use_attempt_turn';
import { useRolePlayStore } from '@/state/stores/roleplay_store';
import type { ChatMessage } from '@/state/stores/roleplay_store';
import type { TranscriptionSession } from '@/integrations/ports/transcription_gateway';
import type { FreeLimit, TaskRuntime } from '@/types/models';

import { AvatarScene } from './avatar_scene';

/** Sent when the user submits an empty turn (shouldn't normally happen). */
const EMPTY_LINE = '…';

export interface RolePlayShellProps {
  payload: TaskRuntime;
}

export function RolePlayShell({ payload }: RolePlayShellProps) {
  const history = useHistory();
  const { transcription } = useIntegrations();
  const { handleFreeLimit, handlePaywallRequired } = useFreeLimit();
  const attempt = useAttemptTurn(payload.attemptId);

  const phase = useRolePlayStore((s) => s.phase);
  const messages = useRolePlayStore((s) => s.messages);
  const landedCount = useRolePlayStore((s) => s.landedCount);
  const targetCount = useRolePlayStore((s) => s.targetCount);
  const isRecording = useRolePlayStore((s) => s.isRecording);
  const isAwaitingReply = useRolePlayStore((s) => s.isAwaitingReply);
  const draft = useRolePlayStore((s) => s.draft);
  const currentSample = useRolePlayStore((s) => s.currentSample);
  const nextUserMove = useRolePlayStore((s) => s.nextUserMove);

  const start = useRolePlayStore((s) => s.start);
  const addMessage = useRolePlayStore((s) => s.addMessage);
  const setProgress = useRolePlayStore((s) => s.setProgress);
  const setSample = useRolePlayStore((s) => s.setSample);
  const setNextUserMove = useRolePlayStore((s) => s.setNextUserMove);
  const setAwaitingReply = useRolePlayStore((s) => s.setAwaitingReply);
  const setRecording = useRolePlayStore((s) => s.setRecording);
  const setDraft = useRolePlayStore((s) => s.setDraft);
  const setPhase = useRolePlayStore((s) => s.setPhase);

  const [isConnectingMic, setIsConnectingMic] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const [doneFreeLimit, setDoneFreeLimit] = useState<FreeLimit | null>(null);

  const sessionRef = useRef<TranscriptionSession | null>(null);
  const stoppingRef = useRef(false);
  const actionInFlightRef = useRef(false);
  const chatRef = useRef<HTMLDivElement | null>(null);

  const opening = payload.payload.roleplay;
  const limit =
    payload.content.recordingLimitSeconds > 0
      ? payload.content.recordingLimitSeconds
      : 60;

  // Seed the conversation from the opening turn whenever a new attempt loads.
  useEffect(() => {
    if (!opening) return;
    start(payload.attemptId, opening.targetCount);
    setProgress(opening.landedCount, opening.targetCount);
    setNextUserMove(opening.nextUserMove);
    addMessage({
      id: `she-0`,
      role: 'she',
      narration: opening.narration,
      text: opening.dialogue,
      audioBase64: payload.payload.audio.audioBase64,
      audioContentType: payload.payload.audio.contentType,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [payload.attemptId]);

  // Auto-scroll to the newest message.
  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, isAwaitingReply]);

  // Teardown any open mic on unmount.
  useEffect(() => {
    return () => {
      void sessionRef.current?.cancel();
      sessionRef.current = null;
    };
  }, []);

  const stopRecording = useCallback(async (): Promise<string> => {
    if (stoppingRef.current) return draft;
    stoppingRef.current = true;
    try {
      const session = sessionRef.current;
      sessionRef.current = null;
      setRecording(false);
      if (!session) return draft;
      const result = await session.stop();
      const text = result.transcript.trim();
      // Per spec: no live text while speaking — the full line appears only now.
      if (text) {
        const next = draft.trim() ? `${draft.trim()} ${text}` : text;
        setDraft(next);
        return next;
      }
      return draft;
    } finally {
      stoppingRef.current = false;
    }
  }, [draft, setDraft, setRecording]);

  const startRecording = useCallback(async (): Promise<void> => {
    if (isRecording || isConnectingMic || isAwaitingReply) return;
    setLocalError(null);
    setIsConnectingMic(true);
    try {
      // No `onInterim` registered: the user does NOT see live text while speaking.
      const session = await transcription.startSession({
        recordingLimitSeconds: limit,
        language: 'en-US',
      });
      sessionRef.current = session;
      setRecording(true);
    } catch {
      setRecording(false);
      sessionRef.current = null;
      setLocalError('Mic unavailable — type your line instead.');
    } finally {
      setIsConnectingMic(false);
    }
  }, [isAwaitingReply, isConnectingMic, isRecording, limit, transcription, setRecording]);

  const onMicPress = useCallback(() => {
    if (isConnectingMic) return;
    if (isRecording) {
      void stopRecording();
    } else {
      void startRecording();
    }
  }, [isConnectingMic, isRecording, startRecording, stopRecording]);

  const send = useCallback(async () => {
    if (actionInFlightRef.current || isAwaitingReply) return;
    actionInFlightRef.current = true;
    setLocalError(null);
    try {
      const finalText = (isRecording ? await stopRecording() : draft).trim();
      if (!finalText) return;

      addMessage({ id: `you-${Date.now()}`, role: 'you', text: finalText });
      setDraft('');
      setAwaitingReply(true);

      const result = await attempt.turn({ clientTranscript: finalText || EMPTY_LINE });
      const t = result.turn;
      addMessage({
        id: `she-${Date.now()}`,
        role: 'she',
        narration: t.narration,
        text: t.dialogue,
        landed: t.landed,
        audioBase64: t.audio.audioBase64,
        audioContentType: t.audio.contentType,
      });
      setProgress(t.landedCount, t.targetCount);
      setNextUserMove(t.nextUserMove);
      // (b) Show a model answer for the line they just attempted, from now on.
      setSample(t.sampleAnswer || null);
      if (t.isComplete) {
        setDoneFreeLimit(result.freeLimit);
        setPhase('done');
      }
    } catch (e) {
      if (!handlePaywallRequired(e)) {
        setLocalError('That didn’t go through. Give it another try.');
      }
    } finally {
      setAwaitingReply(false);
      actionInFlightRef.current = false;
    }
  }, [
    attempt,
    addMessage,
    draft,
    handlePaywallRequired,
    isAwaitingReply,
    isRecording,
    setAwaitingReply,
    setDraft,
    setNextUserMove,
    setPhase,
    setProgress,
    setSample,
    stopRecording,
  ]);

  const exit = useCallback(() => {
    void sessionRef.current?.cancel();
    history.goBack();
  }, [history]);

  const finish = useCallback(() => {
    void sessionRef.current?.cancel();
    handleFreeLimit(doneFreeLimit, 'free_limit_reached');
    history.goBack();
  }, [doneFreeLimit, handleFreeLimit, history]);

  const canSend = !isAwaitingReply && (isRecording || draft.trim().length > 0);
  const lastSheId = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i -= 1) {
      if (messages[i].role === 'she') return messages[i].id;
    }
    return null;
  }, [messages]);

  return (
    <div style={COL}>
      <AvatarScene />

      <header style={HEADER}>
        <button type="button" style={ICON_BTN} aria-label="Leave role play" onClick={exit}>
          <IonIcon icon={closeIcon} style={{ fontSize: 20 }} aria-hidden />
        </button>
        <div style={{ flex: 1, minWidth: 0, textAlign: 'center' }}>
          <div style={EYEBROW}>Role play</div>
          <h1 style={TITLE}>{opening?.briefHeading || payload.task.title}</h1>
        </div>
        <span style={{ ...ICON_BTN, visibility: 'hidden' }} aria-hidden />
      </header>

      <TaskStrip
        landed={landedCount}
        target={targetCount}
        sample={currentSample}
        goalTitle={payload.content.responseInstruction}
      />

      <main ref={chatRef} style={CHAT}>
        <div style={CHAT_INNER}>
          {messages.map((m) =>
            m.role === 'she' ? (
              <SheBubble key={m.id} message={m} animate={m.id === lastSheId && phase !== 'done'} />
            ) : (
              <YouBubble key={m.id} text={m.text} />
            ),
          )}
          {isAwaitingReply && <TypingBubble />}
        </div>
      </main>

      {phase !== 'done' && nextUserMove ? <MoveChip move={nextUserMove} /> : null}

      {phase === 'done' ? (
        <DoneBar landed={landedCount} target={targetCount} onDone={finish} />
      ) : (
        <InputBar
          draft={draft}
          recording={isRecording}
          connecting={isConnectingMic}
          awaiting={isAwaitingReply}
          canSend={canSend}
          error={localError}
          onDraftChange={setDraft}
          onMicPress={onMicPress}
          onSend={() => void send()}
        />
      )}

      <Celebration show={phase === 'done'} label="Nice — she’s into it!" />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Task strip (goal + progress dots + hint)
// ---------------------------------------------------------------------------

function TaskStrip({
  landed,
  target,
  sample,
  goalTitle,
}: {
  landed: number;
  target: number;
  sample: string | null;
  goalTitle: string;
}) {
  return (
    <div style={STRIP}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
        <span style={GOAL_ICON} aria-hidden>🎯</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={GOAL_LABEL}>Your task</div>
          <b style={GOAL_TITLE}>{goalTitle}</b>
        </div>
        <span style={{ fontWeight: 800, fontSize: 13, color: colors.active }}>
          {Math.min(landed, target)}
          <span style={{ color: colors.faint, fontWeight: 700, fontSize: 12 }}> / {target}</span>
        </span>
      </div>
      <ExerciseProgressStrip
        completed={landed}
        total={target}
        showCount={false}
        style={{ marginTop: 10 }}
      />
      <div style={HINT}>
        {sample ? (
          <span>
            💡 <b>One way you could&rsquo;ve played it:</b> &ldquo;{sample}&rdquo;
          </span>
        ) : (
          <span>
            💡 <b>Your turn</b> — reply in character. Commit to the bit, don&rsquo;t explain.
          </span>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Move chip (multi-phase roleplays: tells the user what to do this turn)
// ---------------------------------------------------------------------------

/** Human label for a `next_user_move` key. Falls back to a capitalized key so a
 *  new phase added on the backend still renders something sensible. */
const MOVE_LABELS: Record<string, string> = {
  ask: 'Ask her a question',
  tease: 'Tease her answer',
  love: 'Say something you love',
  hate: 'Say something you hate',
};

function moveLabel(move: string): string {
  return MOVE_LABELS[move] ?? move.charAt(0).toUpperCase() + move.slice(1);
}

function MoveChip({ move }: { move: string }) {
  return (
    <div style={MOVE_CHIP_WRAP}>
      <span style={MOVE_CHIP}>
        👉 Your turn: <b>{moveLabel(move)}</b>
      </span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Chat bubbles
// ---------------------------------------------------------------------------

/** Narration + her spoken line as one block: narration, a blank line, then the
 *  spoken line in quotes. The UI never distinguishes the two — it's one text. */
function composeSheText(message: ChatMessage): string {
  const spoken = `“${message.text}”`;
  const narration = message.narration?.trim();
  return narration ? `${narration}\n\n${spoken}` : spoken;
}

function SheBubble({ message, animate }: { message: ChatMessage; animate: boolean }) {
  const fullText = composeSheText(message);
  // The transcript appears as she speaks: revealed in step with the audio (which
  // voices narration + dialogue as one line). Non-newest lines render in full.
  const [shown, setShown] = useState(animate ? '' : fullText);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const rafRef = useRef<number | null>(null);

  const stop = useCallback(() => {
    if (rafRef.current !== null) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    audioRef.current?.pause();
    audioRef.current = null;
  }, []);

  // Play her audio and reveal the transcript in time with it. Falls back to a
  // length-based pace if autoplay is blocked or no duration is available — so
  // the text always finishes appearing. Used for both auto-play and replay.
  const play = useCallback(() => {
    stop();
    const total = fullText.length;
    let durationMs = Math.min(14000, Math.max(1400, total * 55));
    const b64 = message.audioBase64;
    if (b64) {
      const el = new Audio(`data:${message.audioContentType ?? 'audio/mpeg'};base64,${b64}`);
      audioRef.current = el;
      el.onloadedmetadata = () => {
        if (isFinite(el.duration) && el.duration > 0) durationMs = el.duration * 1000;
      };
      void el.play().catch(() => {});
    }
    setShown('');
    const startedAt = performance.now();
    const tick = (now: number) => {
      const frac = Math.min(1, (now - startedAt) / durationMs);
      setShown(fullText.slice(0, Math.ceil(frac * total)));
      if (frac < 1) rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
  }, [fullText, message.audioBase64, message.audioContentType, stop]);

  // Auto-play + reveal the first time her newest line appears. Effect-driven
  // (no surviving ref guard) so React's dev remount cleanly restarts it.
  useEffect(() => {
    if (!animate) {
      setShown(fullText);
      return;
    }
    play();
    return stop;
  }, [animate, fullText, play, stop]);

  return (
    <div style={{ ...MSG, alignSelf: 'flex-start' }} className="riffy-rise">
      <span style={AVATAR_DOT} aria-hidden />
      <div style={SHE_BUBBLE}>
        <div style={WHO}>Her</div>
        {shown}
        {message.audioBase64 && (
          <div style={{ marginTop: 7, textAlign: 'right' }}>
            <button type="button" style={PLAY_BTN} aria-label="Replay her line" onClick={play}>
              <IonIcon icon={playIcon} style={{ fontSize: 12, marginLeft: 1 }} aria-hidden />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function YouBubble({ text }: { text: string }) {
  return (
    <div style={{ ...MSG, alignSelf: 'flex-end', flexDirection: 'row-reverse' }} className="riffy-rise">
      <div style={YOU_BUBBLE}>{text}</div>
    </div>
  );
}

function TypingBubble() {
  return (
    <div style={{ ...MSG, alignSelf: 'flex-start' }}>
      <span style={AVATAR_DOT} aria-hidden />
      <div style={{ ...SHE_BUBBLE, paddingRight: 14 }}>
        <span style={{ display: 'inline-flex', gap: 4 }}>
          <Dot delay={0} /><Dot delay={0.15} /><Dot delay={0.3} />
        </span>
      </div>
    </div>
  );
}

function Dot({ delay }: { delay: number }) {
  return (
    <span
      className="riffy-ring-pulse"
      style={{
        width: 7,
        height: 7,
        borderRadius: '50%',
        background: colors.faint,
        display: 'inline-block',
        animationDelay: `${delay}s`,
      }}
    />
  );
}

// ---------------------------------------------------------------------------
// Input bar
// ---------------------------------------------------------------------------

function InputBar({
  draft,
  recording,
  connecting,
  awaiting,
  canSend,
  error,
  onDraftChange,
  onMicPress,
  onSend,
}: {
  draft: string;
  recording: boolean;
  connecting: boolean;
  awaiting: boolean;
  canSend: boolean;
  error: string | null;
  onDraftChange: (text: string) => void;
  onMicPress: () => void;
  onSend: () => void;
}) {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  // Grow the input to fit its content (up to MAX_INPUT_HEIGHT, then it scrolls).
  // Runs on every draft change — including the transcript dropped in after speech
  // and the reset to empty after Send.
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = `${Math.min(ta.scrollHeight, MAX_INPUT_HEIGHT)}px`;
  }, [draft, recording]);

  return (
    <footer style={{ display: 'flex', flexDirection: 'column', position: 'relative', zIndex: 4 }}>
      {error && (
        <p style={{ color: colors.red, fontSize: 12.5, textAlign: 'center', padding: '0 18px 4px' }}>
          {error}
        </p>
      )}
      <div style={INPUT_BAR}>
        <div style={FIELD}>
          {recording ? (
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 9, width: '100%' }}>
              <span className="riffy-ring-pulse" style={{ width: 8, height: 8, borderRadius: '50%', background: colors.red }} />
              <span style={{ fontSize: 13.5, fontWeight: 700, color: colors.active }}>Listening…</span>
              <Waveform />
            </span>
          ) : (
            <textarea
              ref={textareaRef}
              style={INPUT}
              rows={1}
              value={draft}
              onChange={(e) => onDraftChange(e.target.value)}
              placeholder={connecting ? 'Connecting mic…' : 'Say or type your line…'}
              aria-label="Your line"
              onKeyDown={(e) => {
                // Enter sends; Shift+Enter inserts a newline.
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  if (canSend) onSend();
                }
              }}
            />
          )}
        </div>

        <button
          type="button"
          style={{ ...CIRC, ...MIC_BTN, ...(recording ? MIC_ON : {}) }}
          aria-label={recording ? 'Stop speaking' : 'Speak'}
          onClick={onMicPress}
          disabled={connecting || awaiting}
        >
          <IonIcon icon={micIcon} style={{ fontSize: 22 }} aria-hidden />
        </button>

        {!recording && (
          <button
            type="button"
            style={{ ...CIRC, ...SEND_BTN, opacity: canSend ? 1 : 0.5 }}
            aria-label="Send"
            onClick={onSend}
            disabled={!canSend}
          >
            <IonIcon icon={sendIcon} style={{ fontSize: 20 }} aria-hidden />
          </button>
        )}
      </div>
    </footer>
  );
}

function Waveform() {
  return (
    <span style={{ display: 'inline-flex', alignItems: 'flex-end', gap: 3, height: 18 }}>
      {[0, 0.12, 0.24, 0.08, 0.3, 0.18, 0.26].map((d, i) => (
        <span
          key={i}
          className="riffy-ring-pulse"
          style={{
            width: 3,
            height: 14,
            borderRadius: 2,
            background: colors.active,
            transformOrigin: 'bottom',
            animationDelay: `${d}s`,
          }}
        />
      ))}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Done bar
// ---------------------------------------------------------------------------

function DoneBar({ landed, target, onDone }: { landed: number; target: number; onDone: () => void }) {
  return (
    <footer style={{ display: 'flex', flexDirection: 'column', position: 'relative', zIndex: 4 }}>
      <div style={{ textAlign: 'center', padding: '4px 18px 0', color: colors.green, fontWeight: 800, fontSize: 13 }}>
        {landed >= target ? `You landed all ${target}!` : 'Scene complete'}
      </div>
      <div style={INPUT_BAR}>
        <Button variant="primary" block onClick={onDone}>
          Done
        </Button>
      </div>
    </footer>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const COL: CSSProperties = {
  position: 'relative',
  height: '100%',
  width: '100%',
  display: 'flex',
  flexDirection: 'column',
  overflow: 'hidden',
  background: '#FBE5D6',
};

const HEADER: CSSProperties = {
  position: 'relative',
  zIndex: 3,
  display: 'flex',
  alignItems: 'center',
  gap: 11,
  padding: 'calc(env(safe-area-inset-top, 0px) + 8px) 14px 8px',
};

const ICON_BTN: CSSProperties = {
  width: 40,
  height: 40,
  borderRadius: 13,
  border: '1px solid rgba(255, 255, 255, 0.65)',
  background: 'rgba(255, 255, 255, 0.78)',
  backdropFilter: 'blur(14px)',
  WebkitBackdropFilter: 'blur(14px)',
  display: 'grid',
  placeItems: 'center',
  color: colors.text,
  flex: 'none',
  cursor: 'pointer',
  boxShadow: '0 4px 14px rgba(17, 24, 39, 0.08)',
};

const EYEBROW: CSSProperties = {
  fontSize: 10,
  fontWeight: 800,
  letterSpacing: 0.9,
  textTransform: 'uppercase',
  color: colors.accent,
};

const TITLE: CSSProperties = {
  fontWeight: 800,
  fontSize: 17,
  letterSpacing: '-0.3px',
  whiteSpace: 'nowrap',
  overflow: 'hidden',
  textOverflow: 'ellipsis',
  color: colors.text,
  textShadow: '0 1px 10px rgba(255, 247, 239, 0.7)',
};

const STRIP: CSSProperties = {
  position: 'relative',
  zIndex: 3,
  margin: '2px 14px 0',
  padding: '11px 14px 12px',
  borderRadius: 16,
  background: 'rgba(255, 255, 255, 0.78)',
  border: '1px solid rgba(255, 255, 255, 0.65)',
  backdropFilter: 'blur(16px)',
  WebkitBackdropFilter: 'blur(16px)',
  boxShadow: '0 8px 22px rgba(17, 24, 39, 0.10)',
};

const GOAL_ICON: CSSProperties = {
  width: 28,
  height: 28,
  borderRadius: 9,
  flex: 'none',
  display: 'grid',
  placeItems: 'center',
  fontSize: 15,
  background: 'rgba(249, 115, 22, 0.12)',
  border: '1px solid rgba(249, 115, 22, 0.26)',
};

const GOAL_LABEL: CSSProperties = {
  fontSize: 9.5,
  fontWeight: 800,
  letterSpacing: 0.8,
  textTransform: 'uppercase',
  color: colors.accent,
};

const GOAL_TITLE: CSSProperties = {
  display: 'block',
  fontWeight: 700,
  fontSize: 14,
  color: colors.text,
  lineHeight: 1.2,
  marginTop: 1,
};

const HINT: CSSProperties = {
  display: 'flex',
  alignItems: 'flex-start',
  gap: 7,
  marginTop: 11,
  paddingTop: 10,
  borderTop: '1px dashed rgba(43, 47, 58, 0.14)',
  fontSize: 12,
  color: '#7A5A3A',
  lineHeight: 1.4,
};

const MOVE_CHIP_WRAP: CSSProperties = {
  display: 'flex',
  justifyContent: 'center',
  padding: '0 14px 2px',
  position: 'relative',
  zIndex: 4,
};

const MOVE_CHIP: CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 6,
  padding: '7px 14px',
  borderRadius: 999,
  fontSize: 12.5,
  fontWeight: 700,
  color: colors.text,
  background: 'rgba(255, 255, 255, 0.86)',
  border: '1px solid rgba(249, 115, 22, 0.3)',
  backdropFilter: 'blur(12px)',
  WebkitBackdropFilter: 'blur(12px)',
  boxShadow: '0 4px 12px rgba(17, 24, 39, 0.08)',
};

const CHAT: CSSProperties = {
  position: 'relative',
  zIndex: 2,
  flex: 1,
  minHeight: 0,
  overflowY: 'auto',
  WebkitOverflowScrolling: 'touch',
  display: 'flex',
  flexDirection: 'column',
  padding: '16px 16px 8px',
};

// Anchors the thread to the bottom (via margin-top:auto) while keeping the top
// reachable when it overflows — avoids the flex `justify-content:flex-end`
// scroll-clipping bug, so the user can scroll up through the whole chat.
const CHAT_INNER: CSSProperties = {
  marginTop: 'auto',
  display: 'flex',
  flexDirection: 'column',
  gap: 11,
};

const MSG: CSSProperties = {
  display: 'flex',
  alignItems: 'flex-end',
  gap: 8,
  maxWidth: '86%',
};

const AVATAR_DOT: CSSProperties = {
  width: 30,
  height: 30,
  borderRadius: '50%',
  flex: 'none',
  background: 'radial-gradient(circle at 50% 35%, #FBD9BC, #6A4634)',
  boxShadow: '0 3px 8px rgba(17, 24, 39, 0.18)',
  border: '2px solid #fff',
};

const SHE_BUBBLE: CSSProperties = {
  padding: '11px 14px',
  fontSize: 14,
  lineHeight: 1.42,
  whiteSpace: 'pre-line',
  borderRadius: 18,
  borderBottomLeftRadius: 7,
  background: 'rgba(255, 255, 255, 0.94)',
  backdropFilter: 'blur(8px)',
  WebkitBackdropFilter: 'blur(8px)',
  color: colors.text,
  border: '1px solid rgba(255, 255, 255, 0.7)',
  boxShadow: '0 6px 16px rgba(17, 24, 39, 0.10)',
};

const WHO: CSSProperties = {
  fontSize: 9,
  fontWeight: 800,
  letterSpacing: 0.6,
  textTransform: 'uppercase',
  color: '#FB7185',
  marginBottom: 3,
};

const YOU_BUBBLE: CSSProperties = {
  padding: '11px 14px',
  fontSize: 14,
  lineHeight: 1.42,
  borderRadius: 18,
  borderBottomRightRadius: 7,
  background: 'linear-gradient(135deg, #3B82F6, #0A8FF2)',
  color: '#fff',
  boxShadow: '0 6px 16px rgba(59, 130, 246, 0.25)',
};

const PLAY_BTN: CSSProperties = {
  width: 27,
  height: 27,
  borderRadius: '50%',
  border: 'none',
  display: 'inline-grid',
  placeItems: 'center',
  cursor: 'pointer',
  background: gradients.warmCta,
  color: '#fff',
  boxShadow: '0 4px 11px rgba(249, 115, 22, 0.4)',
};

/** Max height the input grows to before it starts scrolling internally. */
const MAX_INPUT_HEIGHT = 120;

const INPUT_BAR: CSSProperties = {
  display: 'flex',
  alignItems: 'flex-end',
  gap: 9,
  padding: '12px 14px calc(15px + env(safe-area-inset-bottom))',
  background: 'rgba(255, 248, 241, 0.86)',
  backdropFilter: 'blur(18px)',
  WebkitBackdropFilter: 'blur(18px)',
  borderTop: '1px solid rgba(255, 255, 255, 0.7)',
};

const FIELD: CSSProperties = {
  flex: 1,
  minWidth: 0,
  minHeight: 46,
  borderRadius: 23,
  border: '1.5px solid #D8E0EA',
  background: '#fff',
  display: 'flex',
  alignItems: 'center',
  padding: '0 16px',
  boxShadow: '0 4px 12px rgba(17, 24, 39, 0.05)',
};

const INPUT: CSSProperties = {
  border: 'none',
  outline: 'none',
  width: '100%',
  fontSize: 14.5,
  lineHeight: 1.4,
  color: colors.text,
  background: 'transparent',
  fontFamily: 'inherit',
  resize: 'none',
  padding: '12px 0',
  maxHeight: MAX_INPUT_HEIGHT,
  overflowY: 'auto',
  display: 'block',
};

const CIRC: CSSProperties = {
  width: 46,
  height: 46,
  borderRadius: '50%',
  border: 'none',
  flex: 'none',
  display: 'grid',
  placeItems: 'center',
  cursor: 'pointer',
};

const MIC_BTN: CSSProperties = {
  background: '#fff',
  border: '1.5px solid #D8E0EA',
  color: colors.primary,
  boxShadow: '0 4px 12px rgba(17, 24, 39, 0.06)',
};

const MIC_ON: CSSProperties = {
  background: 'linear-gradient(135deg, #3B82F6, #0A8FF2)',
  color: '#fff',
  border: '1.5px solid transparent',
  boxShadow: '0 8px 18px rgba(59, 130, 246, 0.4)',
};

const SEND_BTN: CSSProperties = {
  background: 'linear-gradient(135deg, #3B82F6, #0A8FF2)',
  color: '#fff',
  boxShadow: '0 8px 18px rgba(59, 130, 246, 0.34)',
};
