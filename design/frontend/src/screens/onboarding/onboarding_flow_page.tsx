import type { CSSProperties } from 'react';
import { IonContent, IonIcon, IonPage } from '@ionic/react';
import { Redirect } from 'react-router-dom';
import { chevronBack } from 'ionicons/icons';
import { colors, gradients } from '@/theme/tokens';
import { useOnboarding } from '@/features/onboarding/use_onboarding';
import { useSession } from '@/features/identity/use_session';
import { TriggerStep } from './steps/trigger_step';
import { LoginStep } from './steps/login_step';

const SHELL: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  minHeight: '100%',
  background: colors.bg,
};

const TOP_BAR: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 12,
  padding: 'calc(env(safe-area-inset-top, 0px) + 10px) 18px 12px',
};

const BACK_BTN: CSSProperties = {
  width: 40,
  height: 40,
  borderRadius: 13,
  flex: 'none',
  display: 'grid',
  placeItems: 'center',
  border: `1px solid ${colors.line}`,
  background: colors.surface,
  color: colors.muted,
  cursor: 'pointer',
};

const PROGRESS: CSSProperties = {
  flex: 1,
  display: 'flex',
  gap: 6,
  padding: '0 2px',
};

const STEPS = ['trigger', 'login'] as const;

function segmentStyle(on: boolean): CSSProperties {
  return {
    flex: 1,
    height: 5,
    borderRadius: 5,
    background: on ? gradients.activeTab : '#E2E7EF',
    boxShadow: on ? '0 0 8px rgba(59, 130, 246, 0.4)' : 'none',
  };
}

export function OnboardingFlowPage() {
  const { session, isLoading } = useSession();
  const onboarding = useOnboarding();
  const { step, selectedTrigger, isCompleting, completingProvider, error } =
    onboarding;

  // A returning (already-onboarded) user has no business re-onboarding.
  if (!isLoading && session !== null) {
    return <Redirect to="/app/home" />;
  }

  const filled = STEPS.indexOf(step) + 1;
  const canGoBack = step === 'login' && !isCompleting;

  const body =
    step === 'login' ? (
      <LoginStep
        onApple={() => onboarding.signInWithApple().catch(() => {})}
        onGoogle={() => onboarding.signInWithGoogle().catch(() => {})}
        completingProvider={completingProvider}
        error={error}
      />
    ) : (
      <TriggerStep
        selectedTrigger={selectedTrigger}
        isSaving={false}
        error={null}
        onSelect={onboarding.selectTrigger}
      />
    );

  return (
    <IonPage>
      <IonContent>
        <div style={SHELL}>
          <div style={TOP_BAR}>
            {canGoBack ? (
              <button
                type="button"
                className="riffy-pressable"
                style={BACK_BTN}
                onClick={onboarding.back}
                aria-label="Back"
              >
                <IonIcon icon={chevronBack} style={{ fontSize: 20 }} aria-hidden />
              </button>
            ) : (
              <span style={{ width: 40, height: 40, flex: 'none' }} aria-hidden />
            )}
            <div style={PROGRESS} aria-hidden>
              {STEPS.map((s, i) => (
                <span key={s} style={segmentStyle(i < filled)} />
              ))}
            </div>
            <span style={{ width: 40, height: 40, flex: 'none' }} aria-hidden />
          </div>
          {body}
        </div>
      </IonContent>
    </IonPage>
  );
}
