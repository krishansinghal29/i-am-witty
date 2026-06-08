import type { ReactNode } from 'react';
import { IonButton, IonSpinner } from '@ionic/react';
import { colors, gradients, radius, shadows } from '@/theme/tokens';
import type { StyleWithVars } from './style';
import './ui.css';

export type ButtonVariant = 'accent' | 'primary' | 'ghost';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps {
  children: ReactNode;
  /** `accent` = warm-gradient CTA (default), `primary` = blue, `ghost` = quiet. */
  variant?: ButtonVariant;
  size?: ButtonSize;
  /** Full-width button. */
  block?: boolean;
  loading?: boolean;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  onClick?: () => void;
  className?: string;
  ariaLabel?: string;
}

const SIZE_MAP: Record<ButtonSize, 'small' | 'default' | 'large'> = {
  sm: 'small',
  md: 'default',
  lg: 'large',
};

function variantStyle(variant: ButtonVariant): StyleWithVars {
  const base: StyleWithVars = {
    '--border-radius': radius.md,
    textTransform: 'none',
    fontWeight: 700,
    letterSpacing: '0.1px',
  };

  switch (variant) {
    case 'accent':
      return {
        ...base,
        '--background': gradients.warmCta,
        '--background-activated': gradients.warmCta,
        '--background-focused': gradients.warmCta,
        '--background-hover': gradients.warmCta,
        '--color': '#FFFFFF',
        '--box-shadow': shadows.warm,
      };
    case 'primary':
      return {
        ...base,
        '--background': colors.primary,
        '--color': '#FFFFFF',
        '--box-shadow': shadows.soft,
      };
    case 'ghost':
      return {
        ...base,
        '--background': 'transparent',
        '--background-activated': 'rgba(249, 115, 22, 0.10)',
        '--background-hover': 'rgba(249, 115, 22, 0.08)',
        '--color': colors.accent,
        '--box-shadow': 'none',
      };
  }
}

export function Button({
  children,
  variant = 'accent',
  size = 'md',
  block = false,
  loading = false,
  disabled = false,
  type = 'button',
  onClick,
  className,
  ariaLabel,
}: ButtonProps) {
  return (
    <IonButton
      type={type}
      size={SIZE_MAP[size]}
      expand={block ? 'block' : undefined}
      fill={variant === 'ghost' ? 'clear' : 'solid'}
      disabled={disabled || loading}
      onClick={onClick}
      aria-label={ariaLabel}
      aria-busy={loading || undefined}
      className={className}
      style={variantStyle(variant)}
    >
      {loading ? <IonSpinner name="crescent" /> : children}
    </IonButton>
  );
}
