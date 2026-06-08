import type { CSSProperties } from 'react';
import {
  IonContent,
  IonIcon,
  IonPage,
  useIonViewWillEnter,
} from '@ionic/react';
import { chevronBack } from 'ionicons/icons';
import { colors, gradients } from '@/theme/tokens';
import { ErrorView, LoadingView } from '@/components/ui';
import { useOnboarding } from '@/features/onboarding/use_onboarding';
import { TriggerStep } from './steps/trigger_step';
import { TinyPracticeStep } from './steps/tiny_practice_step';
import { VariableRewardStep } from './steps/variable_reward_step';
import { LoginStep } from './steps/login_step';
import { ReminderStep } from './steps/reminder_step';
import { PlanLandingStep } from './steps/plan_landing_step';

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
  const onboarding = useOnboarding();
  const {
    step,
    selectedTrigger,
    firstTaskId,
    isLoading,
    isError,
    isSavingTrigger,
    triggerError,
    progress,
    canGoBack,
  } = onboarding;

  // Re-read onboarding + home each time the page becomes active — this is how the
  // flow resumes at the "first win" after the user returns from the task runtime.
  useIonViewWillEnter(() => {
    onboarding.refresh();
  });

  const showChrome = step !== 'plan_landing';

  let body;
  if (isLoading) {
    body = <LoadingView message="Setting things up…" />;
  } else if (isError && step === 'trigger') {
    body = (
      <ErrorView
        message="We couldn’t get started just now. Give it another try."
        onRetry={onboarding.refresh}
      />
    );
  } else {
    switch (step) {
      case 'trigger':
        body = (
          <TriggerStep
            selectedTrigger={selectedTrigger}
            isSaving={isSavingTrigger}
            error={triggerError}
            onSelect={(value) => void onboarding.selectTrigger(value)}
          />
        );
        break;
      case 'tiny_practice':
        body = (
          <TinyPracticeStep
            trigger={selectedTrigger ?? onboarding.onboarding?.selectedTrigger ?? null}
            ready={!!firstTaskId}
            onStart={onboarding.startFirstTask}
          />
        );
        break;
      case 'variable_reward':
        body = <VariableRewardStep onContinue={onboarding.advance} />;
        break;
      case 'login':
        body = <LoginStep onContinue={onboarding.advance} />;
        break;
      case 'reminder':
        body = <ReminderStep onContinue={onboarding.advance} />;
        break;
      case 'plan_landing':
        body = <PlanLandingStep onEnter={onboarding.completeAndEnter} />;
        break;
      default:
        body = <TriggerStep
          selectedTrigger={selectedTrigger}
          isSaving={isSavingTrigger}
          error={triggerError}
          onSelect={(value) => void onboarding.selectTrigger(value)}
        />;
    }
  }

  return (
    <IonPage>
      <IonContent>
        <div style={SHELL}>
          {showChrome && (
            <div style={TOP_BAR}>
              {canGoBack ? (
                <button
                  type="button"
                  className="witty-pressable"
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
                {Array.from({ length: progress.total }, (_, i) => (
                  <span key={i} style={segmentStyle(i < progress.filled)} />
                ))}
              </div>
              <span style={{ width: 40, height: 40, flex: 'none' }} aria-hidden />
            </div>
          )}
          {body}
        </div>
      </IonContent>
    </IonPage>
  );
}
