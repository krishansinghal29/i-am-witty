import { useCallback, useEffect, useRef, useState } from 'react';
import type { CSSProperties, ReactNode } from 'react';
import { useHistory } from 'react-router-dom';
import { IonIcon } from '@ionic/react';
import {
  close as closeIcon,
  helpCircleOutline,
  micOutline,
  mic as micIcon,
} from 'ionicons/icons';

import { colors } from '@/theme/tokens';
import { Button, ExerciseProgressStrip } from '@/components/ui';
import { useIntegrations } from '@/app/providers';
import { useFreeLimit } from '@/features/entitlement/use_free_limit';
import { useAttemptNextRound } from '@/features/task_runtime/use_attempt_next_round';
import { useRuntimeStore } from '@/state/stores/runtime_store';
import type {
  TranscriptionSession,
  TranscriptionWarmup,
} from '@/integrations/ports/transcription_gateway';
import type { Rounds, RuntimePayload, TaskRuntime } from '@/types/models';

import type { AttemptController, VoiceCompleteBody } from '../../contract';
import { FeedbackPanel } from './feedback_panel';
import { ReflectRecap } from './reflect_recap';

export interface VoicePromptShellProps {
  payload: TaskRuntime;
  attempt: AttemptController<VoiceCompleteBody>;
  /**
   * Renders the Respond-phase prompt (role-chipped messages, technique) from the
   * CURRENT rep's runtime payload. A function — not a static node — because a
   * multi-rep session swaps in a fresh scenario on each "Next".
   */
  renderPrompt: (runtime: RuntimePayload) => ReactNode;
  /** Emoji/glyph for the Brief hero. */
  briefIcon?: ReactNode;
}

const COL: CSSProperties = {
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  background: colors.bg,
};

const HEADER: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 12,
  padding: '8px 14px 10px',
};

const ICON_BTN: CSSProperties = {
  width: 40,
  height: 40,
  borderRadius: 13,
  border: `1px solid ${colors.line}`,
  background: colors.surface,
  display: 'grid',
  placeItems: 'center',
  color: colors.muted,
  flex: 'none',
  cursor: 'pointer',
  fontWeight: 700,
};

const TITLE: CSSProperties = {
  flex: 1,
  minWidth: 0,
  textAlign: 'center',
  fontWeight: 700,
  fontSize: 17,
  letterSpacing: '-0.3px',
  whiteSpace: 'nowrap',
  overflow: 'hidden',
  textOverflow: 'ellipsis',
  color: colors.text,
};

const SCROLL: CSSProperties = {
  flex: 1,
  overflowY: 'auto',
  padding: '12px 18px 16px',
  display: 'flex',
  flexDirection: 'column',
};

const FOOTER: CSSProperties = {
  display: 'flex',
  gap: 10,
  padding: '12px 18px calc(14px + env(safe-area-inset-bottom))',
  background: colors.surface,
  borderTop: `1px solid ${colors.line}`,
};

const CUE_CHIP: CSSProperties = {
  alignSelf: 'center',
  marginTop: 16,
  display: 'inline-flex',
  alignItems: 'center',
  gap: 7,
  padding: '7px 14px',
  borderRadius: 999,
  background: 'rgba(249, 115, 22, 0.10)',
  border: '1px solid rgba(249, 115, 22, 0.3)',
  color: colors.accent,
  fontSize: 12,
  fontWeight: 800,
  letterSpacing: 0.3,
  textAlign: 'center',
};

function formatRemaining(seconds: number): string {
  const s = Math.max(0, Math.ceil(seconds));
  const m = Math.floor(s / 60);
  const rem = s % 60;
  return `${m}:${rem.toString().padStart(2, '0')}`;
}

/** Sent to the backend when the timer expires with no typed or spoken answer. */
const NO_RESPONSE_PLACEHOLDER =
  '[No response — the user did not answer within the time limit.]';

/** Join the typed prefix (captured at speak-start) with the final spoken text. */
function joinSpeech(base: string, spoken: string): string {
  const prefix = base.trim();
  return prefix ? `${prefix} ${spoken}` : spoken;
}

export function VoicePromptShell({
  payload,
  attempt,
  renderPrompt,
  briefIcon,
}: VoicePromptShellProps) {
  const history = useHistory();
  const { transcription } = useIntegrations();
  const { handleFreeLimit } = useFreeLimit();
  const nextRoundCtl = useAttemptNextRound(payload.attemptId);

  const phase = useRuntimeStore((s) => s.phase);
  const isRecording = useRuntimeStore((s) => s.isRecording);
  const transcript = useRuntimeStore((s) => s.transcript);
  const startAttempt = useRuntimeStore((s) => s.startAttempt);
  const setPhase = useRuntimeStore((s) => s.setPhase);
  const setRecording = useRuntimeStore((s) => s.setRecording);
  const setTranscript = useRuntimeStore((s) => s.setTranscript);

  const [remainingSeconds, setRemainingSeconds] = useState(0);
  const [localError, setLocalError] = useState<string | null>(null);
  const [isConnectingMic, setIsConnectingMic] = useState(false);
  /** True once the prompt TTS has finished speaking (or there is none). Gates
   * the response timer so the countdown starts after the prompt, not during. */
  const [promptDone, setPromptDone] = useState(false);

  const sessionRef = useRef<TranscriptionSession | null>(null);
  const warmupRef = useRef<TranscriptionWarmup | null>(null);
  /** Textarea contents when the current speech session started (typed prefix to preserve). */
  const speechBaseRef = useRef('');
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const ttsRef = useRef<HTMLAudioElement | null>(null);
  const autoplayedRef = useRef(false);
  const stoppingRef = useRef(false);
  const stopPromiseRef = useRef<Promise<void> | null>(null);
  const actionInFlightRef = useRef(false);

  // The active rep's scenario + the session counter. Held locally (not read
  // straight off props) so "Next" can swap in a fresh prompt without a reload.
  const [runtime, setRuntime] = useState<RuntimePayload>(payload.payload);
  const [rounds, setRounds] = useState<Rounds>(payload.rounds);

  const content = payload.content;
  const limit = content.recordingLimitSeconds > 0 ? content.recordingLimitSeconds : 30;

  const clearTimer = useCallback(() => {
    if (timerRef.current !== null) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const beginWarmup = useCallback(() => {
    void warmupRef.current?.cancel();
    warmupRef.current = transcription.warmup({ language: 'en-US' });
  }, [transcription]);

  const stopRecording = useCallback(async (): Promise<void> => {
    if (stoppingRef.current) {
      await stopPromiseRef.current;
      return;
    }
    stoppingRef.current = true;
    stopPromiseRef.current = (async () => {
      const session = sessionRef.current;
      sessionRef.current = null;
      setRecording(false);
      if (session) {
        const result = await session.stop();
        // Per spec: no live text while speaking — the full line appears only now.
        const text = result.transcript.trim();
        if (text) {
          setTranscript(joinSpeech(speechBaseRef.current, text));
        }
      }
      if (phase === 'respond') {
        beginWarmup();
      }
    })();

    try {
      await stopPromiseRef.current;
    } finally {
      stopPromiseRef.current = null;
      stoppingRef.current = false;
    }
  }, [beginWarmup, phase, setRecording, setTranscript]);

  const startRecording = useCallback(async (): Promise<void> => {
    if (isRecording || isConnectingMic) return;
    // Tapping record commits to answering now: silence the prompt and start the
    // response window even if the TTS hasn't finished playing.
    ttsRef.current?.pause();
    setPromptDone(true);
    setLocalError(null);
    speechBaseRef.current = useRuntimeStore.getState().transcript;
    setIsConnectingMic(true);

    const warmup = warmupRef.current;
    warmupRef.current = null;

    try {
      // No `onInterim` registered: the user does NOT see live text while speaking.
      const session = await transcription.startSession({
        recordingLimitSeconds: limit,
        language: 'en-US',
        warmup: warmup ?? undefined,
      });
      sessionRef.current = session;
      setRecording(true);
    } catch {
      // Mic/permission/setup failure — fall back to the always-on text entry.
      setRecording(false);
      sessionRef.current = null;
      setLocalError('Mic unavailable — type your line instead.');
      beginWarmup();
    } finally {
      setIsConnectingMic(false);
    }
  }, [beginWarmup, isConnectingMic, isRecording, limit, setRecording, transcription]);

  const playPrompt = useCallback(() => {
    const b64 = runtime.audio.audioBase64;
    if (!b64) {
      setPromptDone(true);
      return;
    }
    try {
      const type = runtime.audio.contentType ?? 'audio/mpeg';
      const el = new Audio(`data:${type};base64,${b64}`);
      ttsRef.current = el;
      // Start the response window when the prompt finishes — or right away if
      // playback fails (e.g. autoplay blocked) so the timer never hangs.
      el.onended = () => setPromptDone(true);
      el.onerror = () => setPromptDone(true);
      void el.play().catch(() => setPromptDone(true));
    } catch {
      // Best-effort playback; the prompt text is always visible.
      setPromptDone(true);
    }
  }, [runtime.audio.audioBase64, runtime.audio.contentType]);

  // Reset the machine whenever a new attempt loads. Keyed on attemptId only —
  // a "Next" prompt swap keeps the same attempt, so it must not reset here.
  useEffect(() => {
    startAttempt(payload.attemptId);
    setRuntime(payload.payload);
    setRounds(payload.rounds);
    actionInFlightRef.current = false;
    autoplayedRef.current = false;
    setRemainingSeconds(0);
    setLocalError(null);
    setPromptDone(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [payload.attemptId, startAttempt]);

  // Auto-voice the prompt once when entering Respond (user gesture from Start).
  // With no prompt audio there is nothing to wait for, so release the timer.
  useEffect(() => {
    if (phase !== 'respond' || autoplayedRef.current) return;
    autoplayedRef.current = true;
    if (runtime.audio.audioBase64) {
      playPrompt();
    } else {
      setPromptDone(true);
    }
  }, [phase, playPrompt, runtime.audio.audioBase64]);

  // Pre-warm the token + mic while the user reads the prompt (the AudioContext
  // and socket are created on tap, inside the gesture — see startSession).
  useEffect(() => {
    if (phase !== 'respond') {
      void warmupRef.current?.cancel();
      warmupRef.current = null;
      return;
    }
    beginWarmup();
    return () => {
      void warmupRef.current?.cancel();
      warmupRef.current = null;
    };
  }, [beginWarmup, phase]);

  // Teardown on unmount.
  useEffect(() => {
    return () => {
      clearTimer();
      void sessionRef.current?.cancel();
      sessionRef.current = null;
      void warmupRef.current?.cancel();
      warmupRef.current = null;
      ttsRef.current?.pause();
    };
  }, [clearTimer]);

  const exit = useCallback(() => {
    clearTimer();
    void sessionRef.current?.cancel();
    ttsRef.current?.pause();
    history.goBack();
  }, [clearTimer, history]);

  const finish = useCallback(() => {
    clearTimer();
    void sessionRef.current?.cancel();
    ttsRef.current?.pause();
    if (attempt.paywallOnDone) {
      handleFreeLimit(attempt.result?.freeLimit, 'free_limit_reached');
    }
    history.goBack();
  }, [attempt.paywallOnDone, attempt.result?.freeLimit, clearTimer, handleFreeLimit, history]);

  const onMicPress = useCallback(() => {
    if (isConnectingMic) return;
    if (isRecording) {
      void stopRecording();
    } else {
      void startRecording();
    }
  }, [isConnectingMic, isRecording, startRecording, stopRecording]);

  const submit = useCallback(async () => {
    if (actionInFlightRef.current) return;
    actionInFlightRef.current = true;
    clearTimer();
    setLocalError(null);
    try {
      await stopRecording();
      const text =
        useRuntimeStore.getState().transcript.trim() || NO_RESPONSE_PLACEHOLDER;
      try {
        const result = await attempt.complete({ clientTranscript: text });
        setRounds(result.rounds);
        setPhase('reflect');
      } catch {
        // attempt.status === 'error' surfaces above the input bar.
      }
    } finally {
      actionInFlightRef.current = false;
    }
  }, [attempt, clearTimer, setPhase, stopRecording]);

  // "Next" between reps: pull a fresh scenario, swap it in, and re-arm Respond.
  const onNext = useCallback(async () => {
    if (actionInFlightRef.current) return;
    actionInFlightRef.current = true;
    setLocalError(null);
    try {
      const res = await nextRoundCtl.nextRound();
      setRuntime(res.payload);
      setRounds(res.rounds);
      setTranscript('');
      setRemainingSeconds(0);
      autoplayedRef.current = false;
      setPromptDone(false);
      setPhase('respond');
    } catch {
      setLocalError('Couldn’t load the next one. Give it another try.');
    } finally {
      actionInFlightRef.current = false;
    }
  }, [nextRoundCtl, setPhase, setTranscript]);

  useEffect(() => {
    clearTimer();
    if (phase !== 'respond' || attempt.isSubmitting) {
      return;
    }

    // Show the full window, but hold the countdown until the prompt has finished
    // speaking (or the user taps record to answer early — see startRecording).
    setRemainingSeconds(limit);
    if (!promptDone) {
      return;
    }

    const startedAt = Date.now();
    timerRef.current = setInterval(() => {
      const elapsed = (Date.now() - startedAt) / 1000;
      const nextRemaining = Math.max(0, limit - elapsed);
      setRemainingSeconds(nextRemaining);
      if (nextRemaining <= 0) {
        clearTimer();
        void submit();
      }
    }, 250);

    return clearTimer;
  }, [attempt.isSubmitting, clearTimer, limit, phase, promptDone, submit]);

  const onPhaseSelect = useCallback(
    (target: 'brief' | 'respond' | 'reflect') => {
      if (phase === 'reflect') return;
      if (target === 'brief' || target === 'respond') setPhase(target);
    },
    [phase, setPhase],
  );

  const canSubmit = isRecording || transcript.trim().length > 0;

  return (
    <div style={COL}>
      <header style={HEADER}>
        <button type="button" style={ICON_BTN} aria-label="Exit" onClick={exit}>
          <IonIcon icon={closeIcon} style={{ fontSize: 20 }} aria-hidden />
        </button>
        <h1 style={TITLE}>{payload.task.title}</h1>
        <button
          type="button"
          style={ICON_BTN}
          aria-label="How it works"
          onClick={() => onPhaseSelect('brief')}
        >
          <IonIcon icon={helpCircleOutline} style={{ fontSize: 20 }} aria-hidden />
        </button>
      </header>

      <ExerciseProgressStrip
        completed={rounds.completed}
        total={rounds.total}
        label="Reps"
        style={ROUNDS_STRIP}
      />

      <main style={SCROLL}>
        {phase === 'brief' && (
          <BriefStage
            icon={briefIcon}
            title={payload.task.title}
            what={payload.task.description ?? content.responseInstruction}
            limit={limit}
          />
        )}

        {phase === 'respond' && (
          <div className="riffy-rise" style={{ display: 'flex', flexDirection: 'column' }}>
            {renderPrompt(runtime)}

            {content.responseInstruction && (
              <div style={CUE_CHIP}>
                <IonIcon icon={micOutline} aria-hidden />
                {content.responseInstruction}
              </div>
            )}
          </div>
        )}

        {phase === 'reflect' && attempt.result && (
          <>
            <ReflectRecap
              promptMessages={runtime.prompt.messages}
              promptLabel={content.promptLabel || undefined}
              userAnswer={transcript}
            />
            <FeedbackPanel
              evaluation={attempt.result.result}
              feedbackTabs={content.feedbackTabs}
            />
          </>
        )}
      </main>

      {phase === 'respond' ? (
        <RespondDock
          timerText={formatRemaining(remainingSeconds)}
          transcript={transcript}
          recording={isRecording}
          connecting={isConnectingMic}
          canSubmit={canSubmit}
          submitting={attempt.isSubmitting}
          errored={attempt.status === 'error'}
          localError={localError}
          onDraftChange={(text) => {
            setLocalError(null);
            setTranscript(text);
          }}
          onMicPress={onMicPress}
          onSubmit={() => void submit()}
        />
      ) : (
        <FooterBar
          phase={phase}
          onStart={() => setPhase('respond')}
          onDone={finish}
          onNext={() => void onNext()}
          sessionComplete={attempt.result?.isSessionComplete ?? true}
          nextLoading={nextRoundCtl.isSubmitting}
          error={localError}
        />
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Brief
// ---------------------------------------------------------------------------

const STEP_CARD: CSSProperties = {
  display: 'flex',
  alignItems: 'flex-start',
  gap: 13,
  background: colors.surface,
  border: `1px solid ${colors.line}`,
  borderRadius: 15,
  padding: '13px 15px',
  boxShadow: '0 6px 16px rgba(17, 24, 39, 0.05)',
};

function BriefStage({
  icon,
  title,
  what,
  limit,
}: {
  icon: ReactNode;
  title: string;
  what: string | null;
  limit: number;
}) {
  const steps: { tint: string; head: string; body: string }[] = [
    { tint: colors.primary, head: 'Hear the prompt', body: 'It plays out loud — just listen.' },
    { tint: colors.accent, head: 'Your turn', body: `Speak or type before the ${limit}s timer ends.` },
    { tint: colors.green, head: 'Gentle feedback', body: 'Plus sharper lines you can borrow.' },
  ];

  return (
    <div className="riffy-rise" style={{ display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 7, marginTop: 6 }}>
        <div
          style={{
            width: 72,
            height: 72,
            borderRadius: 22,
            display: 'grid',
            placeItems: 'center',
            fontSize: 34,
            background: 'linear-gradient(150deg, #FFFFFF, #F3F6FB)',
            border: `1px solid ${colors.line}`,
            boxShadow: '0 12px 28px rgba(17, 24, 39, 0.08)',
          }}
          aria-hidden
        >
          {icon ?? '🎭'}
        </div>
        <h2 style={{ fontWeight: 800, fontSize: 23, letterSpacing: '-0.4px', marginTop: 8, color: colors.text }}>
          {title}
        </h2>
        {what && (
          <p style={{ fontSize: 14.5, color: colors.muted, lineHeight: 1.5, maxWidth: '32ch' }}>{what}</p>
        )}
      </div>

      <div style={{ marginTop: 22, display: 'flex', flexDirection: 'column', gap: 11 }}>
        {steps.map((s, i) => (
          <div key={i} style={STEP_CARD}>
            <span
              style={{
                width: 38,
                height: 38,
                borderRadius: 12,
                flex: 'none',
                display: 'grid',
                placeItems: 'center',
                fontWeight: 800,
                color: '#FFFFFF',
                background: s.tint,
              }}
              aria-hidden
            >
              {i + 1}
            </span>
            <span>
              <b style={{ fontWeight: 700, fontSize: 14.5, color: colors.text, display: 'block' }}>{s.head}</b>
              <p style={{ fontSize: 12.5, color: colors.muted, lineHeight: 1.42, marginTop: 2 }}>{s.body}</p>
            </span>
          </div>
        ))}
      </div>

      <div
        style={{
          marginTop: 16,
          background: 'linear-gradient(150deg, rgba(249, 115, 22, 0.09), #FFFFFF 72%)',
          border: '1px dashed rgba(249, 115, 22, 0.45)',
          borderRadius: 14,
          padding: '12px 14px',
          fontSize: 12.5,
          color: '#7A5A3A',
          lineHeight: 1.5,
          textAlign: 'center',
        }}
      >
        React, don&rsquo;t rehearse — one line is plenty. Commit to the bit.
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Respond dock — plain countdown + roleplay-style field with an inline mic
// ---------------------------------------------------------------------------

/** Max height the input grows to before it starts scrolling internally. */
const MAX_INPUT_HEIGHT = 120;

function RespondDock({
  timerText,
  transcript,
  recording,
  connecting,
  canSubmit,
  submitting,
  errored,
  localError,
  onDraftChange,
  onMicPress,
  onSubmit,
}: {
  timerText: string;
  transcript: string;
  recording: boolean;
  connecting: boolean;
  canSubmit: boolean;
  submitting: boolean;
  errored: boolean;
  localError: string | null;
  onDraftChange: (text: string) => void;
  onMicPress: () => void;
  onSubmit: () => void;
}) {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  // Grow the input to fit its content (up to MAX_INPUT_HEIGHT, then it scrolls).
  // Runs on every change — including the transcript dropped in after speech.
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = `${Math.min(ta.scrollHeight, MAX_INPUT_HEIGHT)}px`;
  }, [transcript, recording]);

  return (
    <footer style={{ display: 'flex', flexDirection: 'column' }}>
      <div style={DOCK}>
        <div style={TIMER_LINE}>
          {timerText}{' '}
          <span style={{ color: colors.faint, fontWeight: 600, fontSize: 13 }}>left</span>
        </div>

        {(errored || localError) && (
          <p style={{ color: colors.red, fontSize: 12.5, textAlign: 'center', margin: '0 0 8px' }}>
            {localError ?? 'That didn’t go through. Give it another try.'}
          </p>
        )}

        <div style={FIELD_ROW}>
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
                value={transcript}
                onChange={(e) => onDraftChange(e.target.value)}
                placeholder={connecting ? 'Connecting mic…' : 'Say or type your line…'}
                aria-label="Your response"
              />
            )}
          </div>

          <button
            type="button"
            style={{ ...CIRC, ...MIC_BTN, ...(recording ? MIC_ON : {}) }}
            aria-label={recording ? 'Stop speaking' : 'Speak'}
            onClick={onMicPress}
            disabled={connecting || submitting}
          >
            <IonIcon icon={micIcon} style={{ fontSize: 22 }} aria-hidden />
          </button>
        </div>
      </div>

      <div style={FOOTER}>
        <Button
          variant="accent"
          block
          loading={submitting}
          disabled={!canSubmit}
          onClick={onSubmit}
        >
          Submit — get feedback
        </Button>
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
// Footer (Brief / Reflect)
// ---------------------------------------------------------------------------

function FooterBar({
  phase,
  onStart,
  onDone,
  onNext,
  sessionComplete,
  nextLoading,
  error,
}: {
  phase: 'brief' | 'respond' | 'reflect';
  onStart: () => void;
  onDone: () => void;
  onNext: () => void;
  /** False mid-session: the Reflect footer offers "Next" instead of "Done". */
  sessionComplete: boolean;
  nextLoading: boolean;
  error: string | null;
}) {
  return (
    <footer style={{ display: 'flex', flexDirection: 'column' }}>
      {phase === 'reflect' && !sessionComplete && error && (
        <p style={{ color: colors.red, fontSize: 12.5, textAlign: 'center', padding: '0 18px 4px' }}>
          {error}
        </p>
      )}
      <div style={FOOTER}>
        {phase === 'brief' && (
          <Button variant="primary" block onClick={onStart}>
            Start
          </Button>
        )}

        {phase === 'reflect' &&
          (sessionComplete ? (
            <Button variant="primary" block onClick={onDone}>
              Done
            </Button>
          ) : (
            <Button variant="accent" block loading={nextLoading} onClick={onNext}>
              Next round
            </Button>
          ))}
      </div>
    </footer>
  );
}

// ---------------------------------------------------------------------------
// Respond-dock styles (mirrors the roleplay input bar)
// ---------------------------------------------------------------------------

const ROUNDS_STRIP: CSSProperties = {
  padding: '12px 18px 0',
};

const DOCK: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  padding: '12px 18px 4px',
  background: colors.surface,
  borderTop: `1px solid ${colors.line}`,
};

const TIMER_LINE: CSSProperties = {
  textAlign: 'center',
  fontWeight: 800,
  fontSize: 16,
  color: colors.accent,
  marginBottom: 10,
};

const FIELD_ROW: CSSProperties = {
  display: 'flex',
  alignItems: 'flex-end',
  gap: 9,
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
