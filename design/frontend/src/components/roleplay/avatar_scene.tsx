import type { CSSProperties } from 'react';

/**
 * Static stylized avatar scene rendered full-bleed behind the roleplay chat —
 * a warm gradient, soft party-light bokeh, a simple illustrated avatar, and
 * top/bottom scrims so the frosted-glass chrome stays legible. Intentionally
 * generic (same for every character) for v1.
 */
export function AvatarScene() {
  return (
    <div style={SCENE} aria-hidden>
      <svg viewBox="0 0 392 850" preserveAspectRatio="xMidYMin slice" style={SVG}>
        <defs>
          <linearGradient id="rp-bg" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#FFF3E6" />
            <stop offset="0.4" stopColor="#FFE3CB" />
            <stop offset="0.74" stopColor="#FBCBA4" />
            <stop offset="1" stopColor="#F4B488" />
          </linearGradient>
          <linearGradient id="rp-hair" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#6A4634" />
            <stop offset="1" stopColor="#4A2E22" />
          </linearGradient>
          <linearGradient id="rp-skin" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#FBD9BC" />
            <stop offset="1" stopColor="#F3C29C" />
          </linearGradient>
          <linearGradient id="rp-top" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#74A9F2" />
            <stop offset="1" stopColor="#4C82D8" />
          </linearGradient>
          <filter id="rp-soft" x="-60%" y="-60%" width="220%" height="220%">
            <feGaussianBlur stdDeviation="7" />
          </filter>
        </defs>

        <rect width="392" height="850" fill="url(#rp-bg)" />
        <g filter="url(#rp-soft)" opacity="0.85">
          <circle cx="52" cy="120" r="20" fill="#FFC178" opacity=".55" />
          <circle cx="124" cy="66" r="13" fill="#FFE2B4" opacity=".6" />
          <circle cx="330" cy="150" r="24" fill="#FFB3C6" opacity=".5" />
          <circle cx="360" cy="78" r="15" fill="#FFD9A8" opacity=".6" />
          <circle cx="288" cy="58" r="10" fill="#FFEAC6" opacity=".7" />
          <circle cx="70" cy="320" r="17" fill="#FFCBE0" opacity=".4" />
          <circle cx="352" cy="320" r="22" fill="#FFCE9A" opacity=".42" />
        </g>

        {/* avatar */}
        <ellipse cx="196" cy="252" rx="116" ry="140" fill="url(#rp-hair)" />
        <path d="M22 612 C 32 502 92 430 196 430 C 300 430 360 502 370 612 L 370 640 L 22 640 Z" fill="url(#rp-top)" />
        <path d="M174 322 C 174 372 178 396 196 404 C 214 396 218 372 218 322 Z" fill="url(#rp-skin)" />
        <ellipse cx="196" cy="262" rx="74" ry="86" fill="url(#rp-skin)" />
        <ellipse cx="158" cy="288" rx="13" ry="7.5" fill="#F2889B" opacity=".32" />
        <ellipse cx="234" cy="288" rx="13" ry="7.5" fill="#F2889B" opacity=".32" />
        <path d="M152 232 Q 172 224 190 232" fill="none" stroke="#4A2E22" strokeWidth="4.5" strokeLinecap="round" />
        <path d="M202 232 Q 220 224 240 232" fill="none" stroke="#4A2E22" strokeWidth="4.5" strokeLinecap="round" />
        <circle cx="172" cy="260" r="7.6" fill="#6B4A38" />
        <circle cx="220" cy="260" r="7.6" fill="#6B4A38" />
        <path d="M172 298 Q 196 326 220 298 Q 196 312 172 298 Z" fill="#E8788C" />
        <path d="M122 244 C 116 182 152 148 196 148 C 240 148 276 182 270 244 C 250 206 226 192 196 194 C 164 196 146 210 134 240 C 130 230 126 234 122 244 Z" fill="url(#rp-hair)" />
      </svg>
      <div style={SCRIM_TOP} />
      <div style={SCRIM_BOTTOM} />
    </div>
  );
}

const SCENE: CSSProperties = {
  position: 'absolute',
  inset: 0,
  zIndex: 0,
  overflow: 'hidden',
};

const SVG: CSSProperties = {
  position: 'absolute',
  top: 0,
  left: 0,
  width: '100%',
  height: '100%',
  display: 'block',
};

const SCRIM_TOP: CSSProperties = {
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  height: 160,
  background: 'linear-gradient(to bottom, rgba(255, 247, 238, 0.85), transparent)',
  pointerEvents: 'none',
};

const SCRIM_BOTTOM: CSSProperties = {
  position: 'absolute',
  left: 0,
  right: 0,
  bottom: 0,
  height: '62%',
  background:
    'linear-gradient(to top, rgba(255, 247, 239, 0.97) 10%, rgba(255, 247, 239, 0.86) 32%, rgba(255, 247, 239, 0.45) 64%, transparent)',
  pointerEvents: 'none',
};
