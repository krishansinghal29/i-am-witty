/**
 * Lesson · Listen — the audiogram runtime view for `lesson_listen_v1`.
 *
 * A pre-recorded audio lesson, no recording or scoring. Faithful to the
 * `lesson-listen.html` mockup: a breathing riffy mark inside a blue→orange
 * progress ring, a waveform that doubles as the scrubber, synced (karaoke)
 * captions driven by the payload's word cues, and a transport row. Plays the
 * hosted `audioUrl` (streams + seeks via CDN range requests). On finishing,
 * it marks the attempt "listened" (non-metered — no streak/usage).
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { CSSProperties, MouseEvent as ReactMouseEvent } from 'react';
import { useHistory } from 'react-router-dom';
import { IonIcon } from '@ionic/react';
import {
  chevronBack,
  play as playIcon,
  pause as pauseIcon,
  playSkipBack,
  playSkipForward,
} from 'ionicons/icons';

import { colors } from '@/theme/tokens';
import type { CaptionCue } from '@/types/models';
import type { TaskRuntimeViewProps } from '../contract';

const WAVE_BARS = 46;
const SKIP_SECONDS = 15;
const SPEEDS = [1, 1.5] as const;
const RING_R = 69;
const RING_C = 2 * Math.PI * RING_R;

/** Deterministic bar heights (same LCG/seed as the mockup) so the wave is stable. */
function waveHeights(n: number): number[] {
  let seed = 7;
  const rnd = () => {
    seed = (seed * 9301 + 49297) % 233280;
    return seed / 233280;
  };
  return Array.from({ length: n }, () => 22 + Math.round(rnd() * 78));
}

function clock(seconds: number): string {
  const s = Math.max(0, Math.floor(seconds));
  const m = Math.floor(s / 60);
  return `${m}:${(s % 60).toString().padStart(2, '0')}`;
}

/** Index of the cue active at `t` (binary search on start times). */
function activeCueIndex(cues: CaptionCue[], t: number): number {
  let lo = 0;
  let hi = cues.length - 1;
  let ans = -1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (cues[mid].start <= t) {
      ans = mid;
      lo = mid + 1;
    } else {
      hi = mid - 1;
    }
  }
  return ans;
}

export function LessonListenV1({ payload, attempt }: TaskRuntimeViewProps) {
  const history = useHistory();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const { audioUrl, captions, transcript } = payload.payload;

  const [isPlaying, setIsPlaying] = useState(false);
  const [current, setCurrent] = useState(0);
  const [duration, setDuration] = useState(payload.task.durationSeconds ?? 0);
  const [speedIdx, setSpeedIdx] = useState(0);
  const [captionsOn, setCaptionsOn] = useState(true);
  const [ended, setEnded] = useState(false);

  const heights = useMemo(() => waveHeights(WAVE_BARS), []);
  const completedRef = useRef(false);

  const progress = duration > 0 ? Math.min(1, current / duration) : 0;
  const activeIdx = useMemo(
    () => (captions.length ? activeCueIndex(captions, current) : -1),
    [captions, current],
  );

  // -- audio element wiring -------------------------------------------------
  useEffect(() => {
    const el = audioRef.current;
    if (!el) return;
    const onTime = () => setCurrent(el.currentTime);
    const onMeta = () => {
      if (Number.isFinite(el.duration)) setDuration(el.duration);
    };
    const onPlay = () => setIsPlaying(true);
    const onPause = () => setIsPlaying(false);
    const onEnded = () => {
      setIsPlaying(false);
      setEnded(true);
      // Mark the lesson "listened" once (non-metered; ignores errors).
      if (!completedRef.current) {
        completedRef.current = true;
        void attempt.complete({}).catch(() => undefined);
      }
    };
    el.addEventListener('timeupdate', onTime);
    el.addEventListener('loadedmetadata', onMeta);
    el.addEventListener('play', onPlay);
    el.addEventListener('pause', onPause);
    el.addEventListener('ended', onEnded);
    return () => {
      el.removeEventListener('timeupdate', onTime);
      el.removeEventListener('loadedmetadata', onMeta);
      el.removeEventListener('play', onPlay);
      el.removeEventListener('pause', onPause);
      el.removeEventListener('ended', onEnded);
    };
  }, [attempt]);

  useEffect(() => {
    if (audioRef.current) audioRef.current.playbackRate = SPEEDS[speedIdx];
  }, [speedIdx]);

  const togglePlay = useCallback(() => {
    const el = audioRef.current;
    if (!el) return;
    if (el.paused) {
      if (ended) {
        el.currentTime = 0;
        setEnded(false);
      }
      void el.play().catch(() => undefined);
    } else {
      el.pause();
    }
  }, [ended]);

  const seekTo = useCallback(
    (seconds: number) => {
      const el = audioRef.current;
      if (!el || duration <= 0) return;
      el.currentTime = Math.max(0, Math.min(duration, seconds));
      setCurrent(el.currentTime);
    },
    [duration],
  );

  const onWaveClick = useCallback(
    (e: ReactMouseEvent<HTMLDivElement>) => {
      const rect = e.currentTarget.getBoundingClientRect();
      const frac = (e.clientX - rect.left) / rect.width;
      seekTo(frac * duration);
    },
    [duration, seekTo],
  );

  // -- karaoke caption auto-scroll -----------------------------------------
  const activeWordRef = useRef<HTMLSpanElement | null>(null);
  const lastScrolled = useRef(-1);
  useEffect(() => {
    if (!captionsOn || activeIdx < 0 || activeIdx === lastScrolled.current) return;
    lastScrolled.current = activeIdx;
    activeWordRef.current?.scrollIntoView({ block: 'center', behavior: 'smooth' });
  }, [activeIdx, captionsOn]);

  const headBar = Math.round(progress * (WAVE_BARS - 1));

  return (
    <div style={COL}>
      <style>{KEYFRAMES}</style>
      <audio
        ref={audioRef}
        src={audioUrl ?? undefined}
        preload="metadata"
        style={{ display: 'none' }}
      />

      {/* header */}
      <header style={HEADER}>
        <button style={ICON_BTN} aria-label="Back" onClick={() => history.goBack()}>
          <IonIcon icon={chevronBack} style={{ fontSize: 20 }} />
        </button>
        <div style={{ flex: 1, minWidth: 0, textAlign: 'center' }}>
          <div style={EYEBROW}>Lesson</div>
          <h1 style={TITLE}>{payload.task.title}</h1>
        </div>
        <div style={{ width: 40, flex: 'none' }} />
      </header>
      <div style={DIVIDE} />

      {/* content */}
      <main style={CONTENT}>
        <div style={NOW_TAG}>
          <span style={{ ...NOW_DOT, animation: ended ? 'none' : 'ping 1.6s ease-out infinite' }} />
          {ended ? 'Completed' : isPlaying ? 'Now playing' : 'Lesson'}
        </div>

        {/* hero: breathing riffy mark in a blue→orange progress ring */}
        <div style={HERO}>
          <svg viewBox="0 0 150 150" style={RING_SVG}>
            <defs>
              <linearGradient id="lessonRing" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0" stopColor="#3B82F6" />
                <stop offset="1" stopColor="#F97316" />
              </linearGradient>
            </defs>
            <circle cx="75" cy="75" r={RING_R} fill="none" stroke={colors.line} strokeWidth="7" />
            <circle
              cx="75"
              cy="75"
              r={RING_R}
              fill="none"
              stroke="url(#lessonRing)"
              strokeWidth="7"
              strokeLinecap="round"
              strokeDasharray={RING_C}
              strokeDashoffset={RING_C * (1 - progress)}
              style={{ transition: 'stroke-dashoffset 0.3s linear' }}
            />
          </svg>
          <div
            style={{
              ...HERO_CORE,
              animation: isPlaying ? 'breathe 2.6s ease-in-out infinite' : 'none',
            }}
          >
            <svg viewBox="30 18 52 54" style={{ width: 46, height: 'auto', display: 'block' }} aria-label="riffy">
              <g fill={colors.accent}>
                <rect x="35.5" y="35" width="11.5" height="35" rx="5.75" />
                <path d="M42 46 C45 38 52 36.5 60 40.5" fill="none" stroke={colors.accent} strokeWidth="11.5" strokeLinecap="round" />
                <path d="M70 23 C70.8 29 72.6 30.8 79 31.5 C72.6 32.2 70.8 34 70 40 C69.2 34 67.4 32.2 61 31.5 C67.4 30.8 69.2 29 70 23 Z" />
              </g>
            </svg>
            <span style={EQ}>
              {[7, 14, 9, 12, 8].map((h, i) => (
                <i
                  key={i}
                  style={{
                    width: 3,
                    height: h,
                    borderRadius: 2,
                    background: colors.accent,
                    transformOrigin: 'bottom',
                    animation: 'bob 1s ease-in-out infinite',
                    animationDelay: `${[0, 0.16, 0.32, 0.1, 0.26][i]}s`,
                    animationPlayState: isPlaying ? 'running' : 'paused',
                  }}
                />
              ))}
            </span>
          </div>
        </div>

        <div style={{ textAlign: 'center', marginTop: 2 }}>
          <h2 style={{ fontWeight: 800, fontSize: 24, letterSpacing: '-0.5px', color: colors.text }}>
            {payload.task.title}
          </h2>
          {payload.task.description && (
            <p style={{ fontSize: 13.5, color: colors.muted, lineHeight: 1.45, marginTop: 5, maxWidth: '30ch', marginInline: 'auto' }}>
              {payload.task.description}
            </p>
          )}
        </div>

        {/* waveform = scrubber */}
        <div style={WAVE} onClick={onWaveClick} role="slider" aria-label="Seek" aria-valuenow={Math.round(progress * 100)}>
          {heights.map((h, i) => {
            const played = i < headBar;
            const head = i === headBar;
            return (
              <i
                key={i}
                style={{
                  flex: 1,
                  height: `${h}%`,
                  borderRadius: 3,
                  background: head
                    ? colors.active
                    : played
                      ? 'linear-gradient(135deg,#F97316,#F7C13B)'
                      : colors.line,
                  boxShadow: head ? `0 0 0 3px rgba(10,143,242,0.18)` : 'none',
                  transition: 'background 0.2s',
                }}
              />
            );
          })}
        </div>
        <div style={TIMES}>
          <span style={{ color: colors.accent }}>{clock(current)}</span>
          <span style={{ color: colors.faint }}>-{clock(Math.max(0, duration - current))}</span>
        </div>

        {/* synced captions */}
        {captionsOn && (captions.length > 0 || transcript) && (
          <div style={CAPS}>
            <div style={CAPS_LABEL}>Captions</div>
            <p style={{ fontSize: 15, lineHeight: 1.6, fontWeight: 500 }}>
              {captions.length > 0
                ? captions.map((c, i) => {
                    const isActive = i === activeIdx;
                    const isSaid = i < activeIdx;
                    return (
                      <span
                        key={i}
                        ref={isActive ? activeWordRef : undefined}
                        style={
                          isActive
                            ? CAP_NOW
                            : { color: isSaid ? colors.text : colors.faint }
                        }
                      >
                        {c.text}{' '}
                      </span>
                    );
                  })
                : <span style={{ color: colors.text }}>{transcript}</span>}
            </p>
          </div>
        )}

        {/* transport */}
        <div style={TRANSPORT}>
          <button
            style={SPEEDS[speedIdx] === 1 ? CHIP : CHIP_ON}
            onClick={() => setSpeedIdx((i) => (i + 1) % SPEEDS.length)}
            aria-label="Playback speed"
          >
            {SPEEDS[speedIdx]}×
          </button>
          <button style={SKIP} onClick={() => seekTo(current - SKIP_SECONDS)} aria-label="Back 15 seconds">
            <IonIcon icon={playSkipBack} style={{ fontSize: 20 }} />
          </button>
          <button style={PLAY} onClick={togglePlay} aria-label={isPlaying ? 'Pause' : 'Play'}>
            <IonIcon icon={isPlaying ? pauseIcon : playIcon} style={{ fontSize: 30, color: '#fff' }} />
          </button>
          <button style={SKIP} onClick={() => seekTo(current + SKIP_SECONDS)} aria-label="Forward 15 seconds">
            <IonIcon icon={playSkipForward} style={{ fontSize: 20 }} />
          </button>
          <button
            style={captionsOn ? CHIP_ON : CHIP}
            onClick={() => setCaptionsOn((v) => !v)}
            aria-label="Toggle captions"
            aria-pressed={captionsOn}
          >
            CC
          </button>
        </div>
      </main>
    </div>
  );
}

// ---------------------------------------------------------------------------
// styles
// ---------------------------------------------------------------------------

const KEYFRAMES = `
@keyframes breathe { 0%,100% { transform: scale(1); } 50% { transform: scale(1.04); } }
@keyframes bob { 0%,100% { transform: scaleY(0.55); } 50% { transform: scaleY(1); } }
@keyframes ping { 0% { box-shadow: 0 0 0 0 rgba(249,115,22,0.45); } 70% { box-shadow: 0 0 0 7px rgba(249,115,22,0); } 100% { box-shadow: 0 0 0 0 rgba(249,115,22,0); } }
`;

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
};

const EYEBROW: CSSProperties = {
  fontSize: 10,
  fontWeight: 800,
  letterSpacing: '1.2px',
  textTransform: 'uppercase',
  color: colors.accent,
};

const TITLE: CSSProperties = {
  fontWeight: 700,
  fontSize: 17,
  letterSpacing: '-0.3px',
  lineHeight: 1.12,
  whiteSpace: 'nowrap',
  overflow: 'hidden',
  textOverflow: 'ellipsis',
  color: colors.text,
};

const DIVIDE: CSSProperties = { height: 1, background: colors.line, margin: '8px 18px 0' };

const CONTENT: CSSProperties = {
  flex: 1,
  overflowY: 'auto',
  padding: '14px 20px calc(24px + env(safe-area-inset-bottom))',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
};

const NOW_TAG: CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 7,
  padding: '5px 12px',
  borderRadius: 999,
  background: 'rgba(10,143,242,0.08)',
  border: '1px solid rgba(10,143,242,0.22)',
  color: colors.active,
  fontSize: 10.5,
  fontWeight: 800,
  letterSpacing: '0.7px',
  textTransform: 'uppercase',
};

const NOW_DOT: CSSProperties = { width: 6, height: 6, borderRadius: '50%', background: colors.accent };

const HERO: CSSProperties = {
  position: 'relative',
  width: 168,
  height: 168,
  margin: '26px 0 8px',
  display: 'grid',
  placeItems: 'center',
};

const RING_SVG: CSSProperties = {
  position: 'absolute',
  inset: 0,
  width: '100%',
  height: '100%',
  transform: 'rotate(-90deg)',
};

const HERO_CORE: CSSProperties = {
  width: 116,
  height: 116,
  borderRadius: '50%',
  background: 'radial-gradient(120% 120% at 30% 25%,#fff,#F3F6FB)',
  boxShadow: `0 12px 28px rgba(249,115,22,0.16), inset 0 0 0 1px ${colors.line}`,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 8,
};

const EQ: CSSProperties = { display: 'flex', alignItems: 'flex-end', gap: 3, height: 14 };

const WAVE: CSSProperties = {
  width: '100%',
  marginTop: 20,
  display: 'flex',
  alignItems: 'center',
  gap: 2.5,
  height: 46,
  cursor: 'pointer',
};

const TIMES: CSSProperties = {
  width: '100%',
  display: 'flex',
  justifyContent: 'space-between',
  marginTop: 7,
  fontSize: 11.5,
  fontWeight: 700,
};

const CAPS: CSSProperties = {
  width: '100%',
  marginTop: 16,
  maxHeight: 132,
  overflowY: 'auto',
  background: colors.surface,
  border: `1px solid ${colors.line}`,
  borderRadius: 16,
  padding: '13px 15px',
  boxShadow: '0 6px 16px rgba(17,24,39,0.05)',
};

const CAPS_LABEL: CSSProperties = {
  fontSize: 9.5,
  fontWeight: 800,
  letterSpacing: '0.9px',
  textTransform: 'uppercase',
  color: colors.muted,
  marginBottom: 7,
};

const CAP_NOW: CSSProperties = {
  color: '#fff',
  background: colors.accent,
  borderRadius: 6,
  padding: '1px 5px',
  fontWeight: 700,
  boxShadow: '0 4px 10px rgba(249,115,22,0.28)',
};

const TRANSPORT: CSSProperties = {
  width: '100%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 16,
  marginTop: 'auto',
  paddingTop: 24,
};

const CHIP: CSSProperties = {
  minWidth: 42,
  height: 34,
  padding: '0 11px',
  borderRadius: 11,
  border: `1px solid ${colors.line}`,
  background: colors.surface,
  color: colors.muted,
  fontWeight: 800,
  fontSize: 12.5,
  display: 'grid',
  placeItems: 'center',
  cursor: 'pointer',
};

const CHIP_ON: CSSProperties = {
  ...CHIP,
  color: colors.active,
  borderColor: 'rgba(10,143,242,0.4)',
  background: 'rgba(10,143,242,0.08)',
};

const SKIP: CSSProperties = {
  width: 48,
  height: 48,
  borderRadius: '50%',
  border: `1px solid ${colors.line}`,
  background: colors.surface,
  color: colors.text,
  display: 'grid',
  placeItems: 'center',
  cursor: 'pointer',
};

const PLAY: CSSProperties = {
  width: 74,
  height: 74,
  borderRadius: '50%',
  border: 'none',
  background: 'linear-gradient(135deg,#3B82F6,#0A8FF2)',
  display: 'grid',
  placeItems: 'center',
  cursor: 'pointer',
  boxShadow: '0 14px 28px rgba(59,130,246,0.36)',
};
