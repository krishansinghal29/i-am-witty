import type { CSSProperties } from 'react';
import { IonIcon } from '@ionic/react';
import { checkmark } from 'ionicons/icons';
import { colors } from '@/theme/tokens';
import { Card } from './card';
import './ui.css';

export type PlanNodeStatus = 'done' | 'current' | 'upcoming';

export interface PlanNode {
  id: string;
  status: PlanNodeStatus;
  title?: string;
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

function PlanCard({ node, onSelect }: { node: PlanNode; onSelect?: (id: string) => void }) {
  const highlighted = node.highlighted === true;
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
      className={highlighted ? 'witty-card-glow' : undefined}
      style={style}
      onClick={onSelect ? () => onSelect(node.id) : undefined}
      ariaLabel={node.title}
    >
      {highlighted && <span style={BADGE}>NEXT UP</span>}
      <div style={{ fontWeight: 700, fontSize: 17, color: colors.text }}>
        {node.title ?? 'Practice'}
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
