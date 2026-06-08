import type { ReactNode } from 'react';
import { IonModal } from '@ionic/react';
import type { StyleWithVars } from './style';
import './ui.css';

export interface SheetProps {
  isOpen: boolean;
  onDidDismiss: () => void;
  children: ReactNode;
  /** Sheet stop points (0..1). Defaults to a single fully-open stop. */
  breakpoints?: number[];
  initialBreakpoint?: number;
  className?: string;
}

const SHEET_STYLE: StyleWithVars = {
  '--border-radius': '24px',
  '--background': 'var(--app-surface)',
};

/**
 * Bottom-sheet wrapper over `IonModal` with rounded top corners and a drag
 * handle. The reusable shell behind the paywall / support sheets.
 */
export function Sheet({
  isOpen,
  onDidDismiss,
  children,
  breakpoints = [0, 1],
  initialBreakpoint = 1,
  className,
}: SheetProps) {
  return (
    <IonModal
      isOpen={isOpen}
      onDidDismiss={onDidDismiss}
      breakpoints={breakpoints}
      initialBreakpoint={initialBreakpoint}
      handle
      className={['witty-sheet', className].filter(Boolean).join(' ')}
      style={SHEET_STYLE}
    >
      {children}
    </IonModal>
  );
}
