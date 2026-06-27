import type { CSSProperties } from 'react';
import { IonContent, IonPage } from '@ionic/react';
import { IonIcon } from '@ionic/react';
import { lockClosed, timeOutline } from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import {
  Card,
  EmptyView,
  ErrorView,
  LoadingView,
  TintedThumbnail,
  TopBar,
} from '@/components/ui';
import { colors, gradients } from '@/theme/tokens';
import { useFreeLimit } from '@/features/entitlement/use_free_limit';
import { useUiStore } from '@/state/stores/ui_store';
import {
  usePracticeCatalog,
  type CatalogFilter,
} from '@/features/practice/use_practice_catalog';
import type { CatalogItem } from '@/types/models';

const HEADER: CSSProperties = {
  padding: 'calc(env(safe-area-inset-top, 0px) + 14px) 20px 0',
};

const TITLE: CSSProperties = {
  fontWeight: 700,
  fontSize: 27,
  letterSpacing: '-0.5px',
  lineHeight: 1.05,
  color: colors.text,
};

const SUBTITLE: CSSProperties = {
  fontSize: 13,
  color: colors.muted,
  lineHeight: 1.45,
  maxWidth: '28ch',
  marginTop: 5,
};

const DIVIDER: CSSProperties = {
  height: 1,
  background: colors.line,
  margin: '14px 20px 0',
};

const BODY: CSSProperties = { padding: '14px 20px 24px' };

const FILTER_ROW: CSSProperties = {
  display: 'flex',
  gap: 8,
  marginBottom: 16,
  flexWrap: 'wrap',
};

const GRID: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
  gap: 12,
};

const TILE_INNER: CSSProperties = {
  position: 'relative',
  display: 'flex',
  flexDirection: 'column',
  gap: 9,
  minHeight: 120,
};

const TILE_TITLE: CSSProperties = {
  fontWeight: 700,
  fontSize: 15.5,
  letterSpacing: '-0.2px',
  color: colors.text,
  lineHeight: 1.2,
};

const TILE_DESC: CSSProperties = {
  fontSize: 12,
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
  marginTop: 'auto',
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

const FILTERS: { key: CatalogFilter; label: string }[] = [
  { key: 'roleplay', label: 'Roleplay' },
  { key: 'normal', label: 'Standard' },
  { key: 'lessons', label: 'Lessons' },
];

/** task_type_id of audio lessons — tapped without the free-limit gate. */
const LESSON_TASK_TYPE_ID = 'lesson';

function chipStyle(active: boolean): CSSProperties {
  return {
    display: 'inline-flex',
    alignItems: 'center',
    fontWeight: active ? 700 : 600,
    fontSize: 13,
    padding: '8px 14px',
    borderRadius: 999,
    cursor: 'pointer',
    color: active ? '#FFFFFF' : colors.muted,
    background: active ? gradients.warmCta : colors.surface,
    border: `1px solid ${active ? 'transparent' : colors.line}`,
  };
}

function durationLabel(seconds: number | null): string | null {
  if (seconds == null || seconds <= 0) return null;
  const minutes = Math.max(1, Math.round(seconds / 60));
  return `${minutes} min`;
}

export function PracticePage() {
  const { items, filter, setFilter, isLoading, isError, refetch } =
    usePracticeCatalog();
  const history = useHistory();
  const openPaywall = useUiStore((state) => state.openPaywall);
  const { gateTaskStart } = useFreeLimit();

  const handleTap = (item: CatalogItem) => {
    if (item.isLocked) {
      openPaywall('catalog_locked');
      return;
    }
    // Lessons are non-metered — skip the free-limit gate. Exercises still gate.
    const isLesson = item.task.taskTypeId === LESSON_TASK_TYPE_ID;
    if (!isLesson && !gateTaskStart()) return;

    const params = new URLSearchParams({ source: 'practice_library' });
    history.push(`/task/${item.task.id}?${params.toString()}`);
  };

  let content;
  if (isLoading) {
    content = <LoadingView message="Loading your practice library…" />;
  } else if (isError) {
    content = (
      <ErrorView
        message="We couldn’t load the library just now. Give it another try."
        onRetry={() => void refetch()}
      />
    );
  } else if (items.length === 0) {
    content = (
      <EmptyView
        title="Nothing to show here"
        message="Try a different filter — your exercises will appear here."
      />
    );
  } else {
    content = (
      <div style={GRID}>
        {items.map((item) => {
          const duration = durationLabel(item.task.durationSeconds);
          return (
            <Card
              key={item.task.id}
              onClick={() => handleTap(item)}
              ariaLabel={item.task.title}
            >
              <div style={TILE_INNER}>
                {item.isLocked && (
                  <span style={LOCK_BADGE}>
                    <IonIcon icon={lockClosed} style={{ fontSize: 11 }} aria-hidden />
                    Riffy+
                  </span>
                )}
                <TintedThumbnail
                  keyName={item.task.thumbnailKey ?? item.task.slug}
                  title={item.task.title}
                  size={46}
                />
                <div style={TILE_TITLE}>{item.task.title}</div>
                {item.task.description && (
                  <div style={TILE_DESC}>{item.task.description}</div>
                )}
                {duration && (
                  <div style={META}>
                    <IonIcon icon={timeOutline} style={{ fontSize: 13 }} aria-hidden />
                    {duration}
                  </div>
                )}
              </div>
            </Card>
          );
        })}
      </div>
    );
  }

  return (
    <IonPage>
      <IonContent>
        <div style={HEADER}>
          <TopBar supportSource="practice" />
          <h1 style={{ ...TITLE, marginTop: 16 }}>Practice</h1>
          <p style={SUBTITLE}>
            Pick anything, any time. No one’s listening — just you warming up.
          </p>
        </div>
        <div style={DIVIDER} />
        <div style={BODY}>
          <div style={FILTER_ROW}>
            {FILTERS.map(({ key, label }) => (
              <button
                key={key}
                type="button"
                className="riffy-pressable"
                style={chipStyle(filter === key)}
                onClick={() => setFilter(key)}
                aria-pressed={filter === key}
              >
                {label}
              </button>
            ))}
          </div>
          {content}
        </div>
      </IonContent>
    </IonPage>
  );
}
