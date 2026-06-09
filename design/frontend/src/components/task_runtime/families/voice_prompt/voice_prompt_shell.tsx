import { useCallback, useEffect, useRef, useState } from 'react';
import type { CSSProperties, ReactNode } from 'react';
import { useHistory } from 'react-router-dom';
import { IonIcon } from '@ionic/react';
import {
  close as closeIcon,
  helpCircleOutline,
  volumeHighOutline,
  arrowForward,
  micOutline,
} from 'ionicons/icons';

import { colors, radius } from '@/theme/tokens';
import { Button, RecordRing } from '@/components/ui';
import { useIntegrations } from '@/app/providers';
import { useRuntimeStore } from '@/state/stores/runtime_store';
import type { TranscriptionSession } from '@/integrations/ports/transcription_gateway';
import type { ScaffoldStage, TaskRuntime } from '@/types/models';

import type { AttemptController, VoiceCompleteBody } from '../../contract';
import {
  currentStage,
  isFinalStage,
  nextStageIndex,
  phaseSteps,
} from './phase_machine';
import { PhaseBar } from './phase_bar';
import { FeedbackPanel } from './feedback_panel';

export interface VoicePromptShellProps {
  payload: TaskRuntime;
  attempt: AttemptController<VoiceCompleteBody>;
  /** Prompt rendering for the Respond phase (role-chipped messages, technique). */
  promptArea: ReactNode;
  /** When true, render the scaffold stepper and run the multi-take flow. */
  scaffolded?: boolean;
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

const TEXTAREA: CSSProperties = {
  marginTop: 14,
  width: '100%',
  minHeight: 80,
  resize: 'vertical',
  background: colors.surface,
  border: `1px solid ${colors.line}`,
  borderRadius: radius.md,
  padding: '12px 14px',
  fontSize: 14.5,
  lineHeight: 1.55,
  color: colors.text,
  fontFamily: 'inherit',
  boxShadow: '0 6px 16px rgba(17, 24, 39, 0.05)',
};

function formatRemaining(seconds: number): string {
  const s = Math.max(0, Math.ceil(seconds));
  const m = Math.floor(s / 60);
  const rem = s % 60;
  return `${m}:${rem.toString().padStart(2, '0')}`;
}

export function VoicePromptShell({
  payload,
  attempt,
  promptArea,
  scaffolded = false,
  briefIcon,
}: VoicePromptShellProps) {
  const history = useHistory();
  const { transcription } = useIntegrations();

  const phase = useRuntimeStore((s) => s.phase);
  const isRecording = useRuntimeStore((s) => s.isRecording);
  const transcript = useRuntimeStore((s) => s.transcript);
  const interim = useRuntimeStore((s) => s.interimTranscript);
  const stageIndex = useRuntimeStore((s) => s.scaffoldStageIndex);
  const startAttempt = useRuntimeStore((s) => s.startAttempt);
  const setPhase = useRuntimeStore((s) => s.setPhase);
  const setRecording = useRuntimeStore((s) => s.setRecording);
  const setTranscript = useRuntimeStore((s) => s.setTranscript);
  const setInterim = useRuntimeStore((s) => s.setInterim);
  const setScaffoldStageIndex = useRuntimeStore((s) => s.setScaffoldStageIndex);
  const recordStageResponse = useRuntimeStore((s) => s.recordStageResponse);

  const [elapsed, setElapsed] = useState(0);

  const sessionRef = useRef<TranscriptionSession | null>(null);
  const audioRef = useRef<{ audioBase64: string; contentType: string | null } | null>(null);
  const tickRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const ttsRef = useRef<HTMLAudioElement | null>(null);
  const autoplayedRef = useRef(false);
  const stoppingRef = useRef(false);

  const content = payload.content;
  const runtime = payload.payload;
  const stages: ScaffoldStage[] = runtime.scaffoldStages;
  const limit = content.recordingLimitSeconds > 0 ? content.recordingLimitSeconds : 30;
  const stage = scaffolded ? currentStage(stages, stageIndex) : null;
  const finalStage = isFinalStage(scaffolded ? stages : [], stageIndex);

  const clearTick = useCallback(() => {
    if (tickRef.current !== null) {
      clearInterval(tickRef.current);
      tickRef.current = null;
    }
  }, []);

  const stopRecording = useCallback(async (): Promise<void> => {
    if (stoppingRef.current) return;
    stoppingRef.current = true;
    clearTick();
    const session = sessionRef.current;
    sessionRef.current = null;
    setRecording(false);
    try {
      if (session) {
        const result = await session.stop();
        const text = result.transcript.trim();
        if (text) setTranscript(text);
        audioRef.current = result.audioBase64
          ? { audioBase64: result.audioBase64, contentType: result.contentType }
          : null;
      }
    } finally {
      setInterim('');
      stoppingRef.current = false;
    }
  }, [clearTick, setInterim, setRecording, setTranscript]);

  const startRecording = useCallback(async (): Promise<void> => {
    if (isRecording) return;
    setInterim('');
    setElapsed(0);
    setRecording(true);
    try {
      const session = await transcription.startSession({
        recordingLimitSeconds: limit,
        language: 'en',
      });
      sessionRef.current = session;
      session.onInterim?.((t) => setInterim(t));

      const startedAt = Date.now();
      clearTick();
      tickRef.current = setInterval(() => {
        const secs = (Date.now() - startedAt) / 1000;
        setElapsed(secs);
        if (secs >= limit) {
          void stopRecording();
        }
      }, 250);
    } catch {
      // Mic/permission/setup failure — fall back to the always-on text entry.
      setRecording(false);
      sessionRef.current = null;
    }
  }, [clearTick, isRecording, limit, setInterim, setRecording, stopRecording, transcription]);

  const playPrompt = useCallback(() => {
    const b64 = runtime.audio.audioBase64;
    if (!b64) return;
    try {
      const type = runtime.audio.contentType ?? 'audio/mpeg';
      const el = new Audio(`data:${type};base64,${b64}`);
      ttsRef.current = el;
      void el.play().catch(() => {});
    } catch {
      // Best-effort playback; the prompt text is always visible.
    }
  }, [runtime.audio.audioBase64, runtime.audio.contentType]);

  // Reset the machine whenever a new attempt loads.
  useEffect(() => {
    startAttempt(payload.attemptId);
    audioRef.current = null;
    autoplayedRef.current = false;
    setElapsed(0);
  }, [payload.attemptId, startAttempt]);

  // Auto-voice the prompt once when entering Respond (user gesture from Start).
  useEffect(() => {
    if (phase === 'respond' && !autoplayedRef.current && runtime.audio.audioBase64) {
      autoplayedRef.current = true;
      playPrompt();
    }
  }, [phase, playPrompt, runtime.audio.audioBase64]);

  // Teardown on unmount.
  useEffect(() => {
    return () => {
      clearTick();
      void sessionRef.current?.cancel();
      sessionRef.current = null;
      ttsRef.current?.pause();
    };
  }, [clearTick]);

  const exit = useCallback(() => {
    clearTick();
    void sessionRef.current?.cancel();
    ttsRef.current?.pause();
    history.goBack();
  }, [clearTick, history]);

  const handleRingPress = useCallback(() => {
    if (isRecording) {
      void stopRecording();
    } else {
      void startRecording();
    }
  }, [isRecording, startRecording, stopRecording]);

  const saveTake = useCallback(async () => {
    await stopRecording();
    const state = useRuntimeStore.getState();
    const text = state.transcript.trim();
    const here = currentStage(stages, state.scaffoldStageIndex);
    if (here) recordStageResponse({ position: here.position, transcript: text });
    setScaffoldStageIndex(nextStageIndex(stages, state.scaffoldStageIndex));
    setTranscript('');
    setInterim('');
    audioRef.current = null;
    setElapsed(0);
  }, [recordStageResponse, setInterim, setScaffoldStageIndex, setTranscript, stages, stopRecording]);

  const submit = useCallback(async () => {
    await stopRecording();
    const state = useRuntimeStore.getState();
    const finalTranscript = state.transcript.trim();

    let stageResponses: { position: number; transcript: string }[] | undefined;
    if (scaffolded) {
      const here = currentStage(stages, state.scaffoldStageIndex);
      const prior = state.stageResponses.filter((p) => p.position !== here?.position);
      stageResponses = [
        ...prior,
        ...(here ? [{ position: here.position, transcript: finalTranscript }] : []),
      ].sort((a, b) => a.position - b.position);
    }

    const body: VoiceCompleteBody = {
      ...(finalTranscript ? { clientTranscript: finalTranscript } : {}),
      ...(audioRef.current?.audioBase64
        ? { audioBase64: audioRef.current.audioBase64 }
        : {}),
      ...(audioRef.current?.contentType
        ? { contentType: audioRef.current.contentType }
        : {}),
      language: 'en',
      ...(stageResponses ? { stageResponses } : {}),
    };

    try {
      await attempt.complete(body);
      setPhase('reflect');
    } catch {
      // attempt.status === 'error' surfaces below the action bar.
    }
  }, [attempt, scaffolded, setPhase, stages, stopRecording]);

  const onPhaseSelect = useCallback(
    (target: 'brief' | 'respond' | 'reflect') => {
      if (phase === 'reflect') return;
      if (target === 'brief' || target === 'respond') setPhase(target);
    },
    [phase, setPhase],
  );

  const canSubmit = isRecording || transcript.trim().length > 0;
  const hasAudio = Boolean(runtime.audio.audioBase64);

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

      <PhaseBar
        steps={phaseSteps({ scaffolded })}
        current={phase}
        onSelect={phase === 'reflect' ? undefined : onPhaseSelect}
      />
      <div style={{ height: 1, background: colors.line, margin: '0 18px' }} />

      <main style={SCROLL}>
        {phase === 'brief' && (
          <BriefStage
            icon={briefIcon}
            title={payload.task.title}
            what={payload.task.description ?? content.responseInstruction}
            limit={limit}
            scaffolded={scaffolded}
            stages={stages}
          />
        )}

        {phase === 'respond' && (
          <div className="riffy-rise" style={{ display: 'flex', flexDirection: 'column' }}>
            {promptArea}

            {/* The spoken prompt autoplays on entering Respond (see effect below);
                like the legacy app there is no manual play button. A small
                muted-replay affordance lets the user hear it again. */}
            {hasAudio && (
              <button
                type="button"
                onClick={playPrompt}
                className="riffy-pressable"
                aria-label="Replay prompt"
                style={{
                  alignSelf: 'center',
                  marginTop: 10,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '4px 10px',
                  borderRadius: 999,
                  border: 'none',
                  background: 'transparent',
                  color: colors.faint,
                  fontSize: 11.5,
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                <IonIcon icon={volumeHighOutline} aria-hidden />
                Replay
              </button>
            )}

            {scaffolded && stages.length > 0 && (
              <ScaffoldStepper stages={stages} currentIndex={stageIndex} />
            )}

            {content.responseInstruction && (
              <div style={CUE_CHIP}>
                <IonIcon icon={micOutline} aria-hidden />
                {content.responseInstruction}
              </div>
            )}

            <RecordArea
              recording={isRecording}
              progress={elapsed / limit}
              remaining={limit - elapsed}
              interim={interim}
              onPress={handleRingPress}
            />

            <textarea
              style={TEXTAREA}
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder="Type your line — one line is plenty."
              aria-label="Your response"
            />
          </div>
        )}

        {phase === 'reflect' && attempt.result && (
          <FeedbackPanel
            evaluation={attempt.result.result}
            feedbackTabs={content.feedbackTabs}
          />
        )}
      </main>

      <FooterBar
        phase={phase}
        scaffolded={scaffolded}
        finalStage={finalStage}
        canSubmit={canSubmit}
        submitting={attempt.isSubmitting}
        errored={attempt.status === 'error'}
        stageTitle={stage?.title}
        onStart={() => setPhase('respond')}
        onSaveTake={() => void saveTake()}
        onSubmit={() => void submit()}
        onDone={exit}
      />
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
  scaffolded,
  stages,
}: {
  icon: ReactNode;
  title: string;
  what: string | null;
  limit: number;
  scaffolded: boolean;
  stages: ScaffoldStage[];
}) {
  const steps: { tint: string; head: string; body: string }[] = scaffolded
    ? stages.map((s) => ({
        tint: s.isFinalSubmission ? colors.accent : colors.primary,
        head: s.title,
        body: s.isFinalSubmission ? `${s.instruction} (scored)` : s.instruction,
      }))
    : [
        { tint: colors.primary, head: 'Hear the prompt', body: 'It plays out loud — just listen.' },
        { tint: colors.accent, head: 'Your turn', body: `Tap the mic and react — about ${limit}s.` },
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

      {scaffolded && (
        <div
          style={{
            textAlign: 'center',
            fontSize: 10.5,
            fontWeight: 800,
            letterSpacing: 1.1,
            textTransform: 'uppercase',
            color: colors.muted,
            margin: '20px 0 10px',
          }}
        >
          You record each take — only the last is scored
        </div>
      )}

      <div style={{ marginTop: scaffolded ? 0 : 22, display: 'flex', flexDirection: 'column', gap: 11 }}>
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
// Scaffold stepper + captured chips
// ---------------------------------------------------------------------------

function ScaffoldStepper({
  stages,
  currentIndex,
}: {
  stages: ScaffoldStage[];
  currentIndex: number;
}) {
  const stageResponses = useRuntimeStore((s) => s.stageResponses);
  const here = stages[currentIndex];

  return (
    <div style={{ marginTop: 18 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 0 }}>
        {stages.map((s, i) => {
          const status = i < currentIndex ? 'done' : i === currentIndex ? 'cur' : 'upcoming';
          const dotBg =
            status === 'done'
              ? 'rgba(22, 163, 74, 0.12)'
              : status === 'cur'
                ? colors.primary
                : colors.surface;
          const dotColor = status === 'cur' ? '#FFFFFF' : status === 'done' ? colors.green : colors.faint;
          const dotBorder = status === 'cur' ? 'transparent' : status === 'done' ? 'rgba(22, 163, 74, 0.5)' : colors.line;
          return (
            <div key={s.position} style={{ display: 'contents' }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, width: 64, flex: 'none' }}>
                <span
                  style={{
                    width: 34,
                    height: 34,
                    borderRadius: '50%',
                    display: 'grid',
                    placeItems: 'center',
                    fontWeight: 800,
                    fontSize: 14,
                    background: dotBg,
                    border: `2px solid ${dotBorder}`,
                    color: dotColor,
                  }}
                >
                  {status === 'done' ? '✓' : i + 1}
                </span>
                <span style={{ fontSize: 10.5, fontWeight: 700, color: dotColor === '#FFFFFF' ? colors.active : dotColor }}>
                  {s.title}
                </span>
              </div>
              {i < stages.length - 1 && (
                <span
                  style={{
                    flex: 1,
                    height: 3,
                    borderRadius: 3,
                    margin: '0 -2px 22px',
                    background: i < currentIndex ? 'rgba(22, 163, 74, 0.5)' : colors.line,
                  }}
                />
              )}
            </div>
          );
        })}
      </div>

      {stageResponses.length > 0 && (
        <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 9 }}>
          {stageResponses.map((r) => {
            const s = stages.find((x) => x.position === r.position);
            return (
              <div
                key={r.position}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 11,
                  background: 'rgba(22, 163, 74, 0.06)',
                  border: '1px solid rgba(22, 163, 74, 0.28)',
                  borderRadius: 13,
                  padding: '10px 13px',
                }}
              >
                <span style={{ flex: 1, minWidth: 0 }}>
                  <span style={{ fontSize: 9.5, fontWeight: 800, letterSpacing: 0.7, textTransform: 'uppercase', color: colors.green }}>
                    {s?.title ?? `Step ${r.position}`}
                  </span>
                  <span style={{ display: 'block', fontSize: 13.5, fontWeight: 600, color: colors.text, lineHeight: 1.3, marginTop: 1 }}>
                    {r.transcript || '—'}
                  </span>
                </span>
              </div>
            );
          })}
        </div>
      )}

      {here && (
        <div style={{ marginTop: 16, textAlign: 'center' }}>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 7,
              padding: '6px 14px',
              borderRadius: 999,
              background: 'rgba(10, 143, 242, 0.10)',
              border: '1px solid rgba(10, 143, 242, 0.3)',
              color: colors.active,
              fontSize: 11.5,
              fontWeight: 800,
              letterSpacing: 0.4,
              textTransform: 'uppercase',
            }}
          >
            {here.label}
            {here.isFinalSubmission ? ' · scored' : ''}
          </span>
          <h3 style={{ fontWeight: 800, fontSize: 22, letterSpacing: '-0.3px', marginTop: 10, color: colors.text }}>
            {here.title}
          </h3>
          <p style={{ fontSize: 13.5, color: colors.muted, lineHeight: 1.45, marginTop: 4, maxWidth: '32ch', marginInline: 'auto' }}>
            {here.instruction}
          </p>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Record area
// ---------------------------------------------------------------------------

function RecordArea({
  recording,
  progress,
  remaining,
  interim,
  onPress,
}: {
  recording: boolean;
  progress: number;
  remaining: number;
  interim: string;
  onPress: () => void;
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10, marginTop: 18 }}>
      {recording && (
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 7,
            fontSize: 11,
            fontWeight: 800,
            letterSpacing: 0.5,
            color: colors.red,
            textTransform: 'uppercase',
          }}
        >
          <span
            className="riffy-ring-pulse"
            style={{ width: 8, height: 8, borderRadius: '50%', background: colors.red, display: 'inline-block' }}
          />
          Recording · your turn
        </span>
      )}

      <RecordRing recording={recording} progress={progress} onPress={onPress} />

      <div style={{ fontWeight: 800, fontSize: 16, color: colors.accent }}>
        {recording ? (
          <>
            {formatRemaining(remaining)}{' '}
            <span style={{ color: colors.faint, fontWeight: 600, fontSize: 13 }}>left · tap to stop</span>
          </>
        ) : (
          <span style={{ color: colors.muted, fontWeight: 600, fontSize: 13 }}>Tap to record — or type below</span>
        )}
      </div>

      {recording && interim && (
        <div
          style={{
            width: '100%',
            background: colors.surface,
            border: `1px solid ${colors.line}`,
            borderRadius: radius.md,
            padding: '10px 13px',
            fontSize: 13.5,
            lineHeight: 1.5,
            color: colors.text,
          }}
        >
          {interim}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Footer
// ---------------------------------------------------------------------------

function FooterBar({
  phase,
  scaffolded,
  finalStage,
  canSubmit,
  submitting,
  errored,
  stageTitle,
  onStart,
  onSaveTake,
  onSubmit,
  onDone,
}: {
  phase: 'brief' | 'respond' | 'reflect';
  scaffolded: boolean;
  finalStage: boolean;
  canSubmit: boolean;
  submitting: boolean;
  errored: boolean;
  stageTitle: string | undefined;
  onStart: () => void;
  onSaveTake: () => void;
  onSubmit: () => void;
  onDone: () => void;
}) {
  return (
    <footer style={{ display: 'flex', flexDirection: 'column' }}>
      {errored && phase === 'respond' && (
        <p style={{ color: colors.red, fontSize: 12.5, textAlign: 'center', padding: '0 18px 6px' }}>
          That didn&rsquo;t go through. Give it another try.
        </p>
      )}
      <div style={FOOTER}>
        {phase === 'brief' && (
          <Button variant="primary" block onClick={onStart}>
            Start
          </Button>
        )}

        {phase === 'respond' && scaffolded && !finalStage && (
          <Button variant="primary" block disabled={!canSubmit} onClick={onSaveTake}>
            Save {stageTitle ?? 'take'} <IonIcon icon={arrowForward} aria-hidden />
          </Button>
        )}

        {phase === 'respond' && (!scaffolded || finalStage) && (
          <Button
            variant="accent"
            block
            loading={submitting}
            disabled={!canSubmit}
            onClick={onSubmit}
          >
            Submit — get feedback
          </Button>
        )}

        {phase === 'reflect' && (
          <Button variant="primary" block onClick={onDone}>
            Done
          </Button>
        )}
      </div>
    </footer>
  );
}
