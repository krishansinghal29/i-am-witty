import type { CSSProperties } from 'react';
import { IonIcon } from '@ionic/react';
import {
  chatbubblesOutline,
  checkmark,
  headsetOutline,
  lockClosed,
  timeOutline,
} from 'ionicons/icons';
import { colors } from '@/theme/tokens';
import { Card } from './card';
import { TintedThumbnail } from './tinted_thumbnail';
import './ui.css';

export type PlanNodeStatus = 'done' | 'current' | 'upcoming';

export interface PlanNode {
  id: string;
  status: PlanNodeStatus;
  /** Lesson vs exercise — drives the eyebrow label and thumbnail icon. */
  kind?: 'lesson' | 'exercise' | null;
  title?: string;
  description?: string | null;
  durationSeconds?: number | null;
  /** Tint/thumbnail lookup keys (thumbnail asset key, then slug). */
  thumbnailKey?: string | null;
  slug?: string | null;
  /** Premium task the caller can't start yet (shows a Riffy+ badge). */
  isLocked?: boolean;
  /** Marks the single "Next up" node (badge + gentle glow). */
  highlighted?: boolean;
}

export interface PlanPathProps {
  nodes: PlanNode[];
  onSelect?: (id: string) => void;
}

const NODE_BASE: CSSProperties = {
  width: 26,
  height: 26,
  borderRadius: '50%',
  flex: 'none',
  display: 'grid',
  placeItems: 'center',
  marginTop: 18,
};

function nodeStyle(status: PlanNodeStatus): CSSProperties {
  switch (status) {
    case 'done':
      return {
        ...NODE_BASE,
        background: 'rgba(22, 163, 74, 0.12)',
        border: '1px solid rgba(22, 163, 74, 0.4)',
      };
    case 'current':
      return {
        ...NODE_BASE,
        background: colors.surface,
        boxShadow: '0 0 0 4px rgba(59, 130, 246, 0.2)',
      };
    case 'upcoming':
    default:
      return {
        ...NODE_BASE,
        background: colors.surface,
        border: `1.5px dashed ${colors.line}`,
      };
  }
}

const CURRENT_DOT: CSSProperties = {
  width: 14,
  height: 14,
  borderRadius: '50%',
  background: `linear-gradient(150deg, ${colors.primary}, ${colors.active})`,
  boxShadow: '0 0 10px rgba(59, 130, 246, 0.6)',
};

const CONNECTOR: CSSProperties = {
  width: 2,
  flex: 1,
  minHeight: 22,
  marginTop: 6,
  background: `repeating-linear-gradient(${colors.line} 0 4px, transparent 4px 9px)`,
};

const BADGE: CSSProperties = {
  display: 'inline-block',
  fontWeight: 800,
  fontSize: 10.5,
  letterSpacing: '1.4px',
  color: colors.active,
  background: 'rgba(59, 130, 246, 0.12)',
  border: '1px solid rgba(59, 130, 246, 0.34)',
  padding: '3px 9px',
  borderRadius: 7,
  marginBottom: 8,
};

const ROW: CSSProperties = {
  position: 'relative',
  display: 'flex',
  gap: 12,
  alignItems: 'flex-start',
};

const COL: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 4,
  minWidth: 0,
  flex: 1,
};

const KICKER: CSSProperties = {
  fontWeight: 800,
  fontSize: 10.5,
  letterSpacing: '1.2px',
  textTransform: 'uppercase',
  color: colors.muted,
};

const TITLE: CSSProperties = {
  fontWeight: 700,
  fontSize: 16,
  letterSpacing: '-0.2px',
  lineHeight: 1.2,
  color: colors.text,
};

const DESC: CSSProperties = {
  fontSize: 12.5,
  color: colors.muted,
  lineHeight: 1.4,
  display: '-webkit-box',
  WebkitLineClamp: 2,
  WebkitBoxOrient: 'vertical',
  overflow: 'hidden',
};

const META: CSSProperties = {
  fontSize: 11.5,
  color: colors.muted,
  fontWeight: 500,
  display: 'flex',
  alignItems: 'center',
  gap: 5,
  marginTop: 2,
};

const LOCK_BADGE: CSSProperties = {
  position: 'absolute',
  top: 0,
  right: 0,
  display: 'inline-flex',
  alignItems: 'center',
  gap: 4,
  fontSize: 10,
  fontWeight: 800,
  letterSpacing: '0.4px',
  color: colors.accent,
  background: 'rgba(249, 115, 22, 0.12)',
  border: '1px solid rgba(249, 115, 22, 0.4)',
  borderRadius: 7,
  padding: '3px 7px',
  textTransform: 'uppercase',
};

function durationLabel(seconds: number | null | undefined): string | null {
  if (seconds == null || seconds <= 0) return null;
  const minutes = Math.max(1, Math.round(seconds / 60));
  return `${minutes} min`;
}

/** Eyebrow label + thumbnail icon per task kind ("Listen" lesson / "Practice" exercise). */
function typeMetaFor(kind: PlanNode['kind']): { label: string; icon: string } | null {
  if (kind === 'lesson') return { label: 'Listen', icon: headsetOutline };
  if (kind === 'exercise') return { label: 'Practice', icon: chatbubblesOutline };
  return null;
}

function PlanCard({ node, onSelect }: { node: PlanNode; onSelect?: (id: string) => void }) {
  const highlighted = node.highlighted === true;
  const duration = durationLabel(node.durationSeconds);
  const typeMeta = typeMetaFor(node.kind);
  const style: CSSProperties = highlighted
    ? {
        margin: '10px 0 4px',
        background: 'linear-gradient(150deg, rgba(59, 130, 246, 0.12), #FFFFFF 58%)',
        border: '1px solid rgba(59, 130, 246, 0.45)',
        boxShadow: '0 14px 30px rgba(59, 130, 246, 0.18)',
      }
    : { margin: '10px 0 4px' };

  return (
    <Card
      className={highlighted ? 'riffy-card-glow' : undefined}
      style={style}
      onClick={onSelect ? () => onSelect(node.id) : undefined}
      ariaLabel={node.title}
    >
      {highlighted && <span style={BADGE}>NEXT UP</span>}
      <div style={ROW}>
        <TintedThumbnail
          keyName={node.thumbnailKey ?? node.slug ?? node.id}
          title={node.title}
          size={46}
          icon={typeMeta?.icon}
        />
        <div style={COL}>
          {typeMeta && <span style={KICKER}>{typeMeta.label}</span>}
          <div style={TITLE}>{node.title ?? 'Practice'}</div>
          {node.description && <div style={DESC}>{node.description}</div>}
          {duration && (
            <div style={META}>
              <IonIcon icon={timeOutline} style={{ fontSize: 13 }} aria-hidden />
              {duration}
            </div>
          )}
        </div>
        {node.isLocked && (
          <span style={LOCK_BADGE}>
            <IonIcon icon={lockClosed} style={{ fontSize: 11 }} aria-hidden />
            Riffy+
          </span>
        )}
      </div>
    </Card>
  );
}

/** Vertical rail of plan nodes with connectors; one node can be "Next up". */
export function PlanPath({ nodes, onSelect }: PlanPathProps) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {nodes.map((node, index) => {
        const isLast = index === nodes.length - 1;
        return (
          <div key={node.id} style={{ display: 'grid', gridTemplateColumns: '30px 1fr', gap: 14 }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span style={nodeStyle(node.status)}>
                {node.status === 'done' && (
                  <IonIcon icon={checkmark} style={{ fontSize: 14, color: colors.green }} aria-hidden />
                )}
                {node.status === 'current' && <span style={CURRENT_DOT} />}
              </span>
              {!isLast && <span style={CONNECTOR} />}
            </div>
            <PlanCard node={node} onSelect={onSelect} />
          </div>
        );
      })}
    </div>
  );
}
