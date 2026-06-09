import {
  IonTabs,
  IonTabBar,
  IonTabButton,
  IonIcon,
  IonLabel,
  IonRouterOutlet,
  IonBadge,
  IonPage,
  IonContent,
} from '@ionic/react';
import { Route, Redirect } from 'react-router-dom';
import { Capacitor } from '@capacitor/core';
import {
  homeOutline,
  flameOutline,
  chatbubblesOutline,
  personOutline,
} from 'ionicons/icons';
import { OnboardingGuard } from '@/app/guards/onboarding_guard';
import { ErrorBoundary } from '@/app/error_boundary';
import { useIntegrations } from '@/app/providers';
import { TopCluster, EmptyView } from '@/components/ui';
import { HomePage } from '@/screens/home/home_page';
import { PracticePage } from '@/screens/practice/practice_page';
import { ProfilePage } from '@/screens/profile/profile_page';
import { OnboardingFlowPage } from '@/screens/onboarding/onboarding_flow_page';
import { LandingPage } from '@/screens/landing/landing_page';
import { LegalPage } from '@/screens/legal/legal_page';
import { TaskRuntimePage } from '@/screens/task_runtime/task_runtime_page';
import { PaywallSheet } from '@/screens/paywall/paywall_sheet';
import { SupportSheet } from '@/screens/support/support_sheet';

function RolePlayPlaceholder() {
  return (
    <IonPage>
      <IonContent>
        <EmptyView
          title="Role play"
          message="This space is warming up. Check back soon."
          icon={chatbubblesOutline}
        />
      </IonContent>
    </IonPage>
  );
}

export function AppTabs() {
  const { analytics } = useIntegrations();
  const rolePlayEnabled = analytics.isFeatureEnabled('role_play');

  return (
    <>
      <IonTabs>
        <IonRouterOutlet>
          <Route
            exact
            path="/app/home"
            render={() => (
              <ErrorBoundary>
                <HomePage />
              </ErrorBoundary>
            )}
          />
          <Route
            exact
            path="/app/practice"
            render={() => (
              <ErrorBoundary>
                <PracticePage />
              </ErrorBoundary>
            )}
          />
          <Route
            exact
            path="/app/roleplay"
            render={() => (
              <ErrorBoundary>
                <RolePlayPlaceholder />
              </ErrorBoundary>
            )}
          />
          <Route
            exact
            path="/app/profile"
            render={() => (
              <ErrorBoundary>
                <ProfilePage />
              </ErrorBoundary>
            )}
          />
          <Route exact path="/app">
            <Redirect to="/app/home" />
          </Route>
        </IonRouterOutlet>
        <IonTabBar slot="bottom">
          <IonTabButton tab="home" href="/app/home">
            <IonIcon icon={homeOutline} />
            <IonLabel>Home</IonLabel>
          </IonTabButton>
          <IonTabButton tab="practice" href="/app/practice">
            <IonIcon icon={flameOutline} />
            <IonLabel>Practice</IonLabel>
          </IonTabButton>
          <IonTabButton
            tab="roleplay"
            href={rolePlayEnabled ? '/app/roleplay' : undefined}
            disabled={!rolePlayEnabled}
          >
            <IonIcon icon={chatbubblesOutline} />
            <IonLabel>Role play</IonLabel>
            {!rolePlayEnabled && <IonBadge color="medium">Soon</IonBadge>}
          </IonTabButton>
          <IonTabButton tab="profile" href="/app/profile">
            <IonIcon icon={personOutline} />
            <IonLabel>Profile</IonLabel>
          </IonTabButton>
        </IonTabBar>
      </IonTabs>
      <TopCluster />
      <PaywallSheet />
      <SupportSheet />
    </>
  );
}

export function AppRoutes() {
  return (
    <IonRouterOutlet>
      <Route
        exact
        path="/legal"
        render={() => (
          <ErrorBoundary>
            <LegalPage />
          </ErrorBoundary>
        )}
      />
      <Route
        path="/onboarding"
        render={() => (
          <ErrorBoundary>
            <OnboardingFlowPage />
          </ErrorBoundary>
        )}
      />
      <Route
        path="/task/:taskId"
        render={() => (
          <ErrorBoundary>
            <TaskRuntimePage />
          </ErrorBoundary>
        )}
      />
      <Route
        path="/app"
        render={() => (
          <OnboardingGuard>
            <AppTabs />
          </OnboardingGuard>
        )}
      />
      <Route
        exact
        path="/"
        render={() =>
          // Web visitors get the marketing landing page; native apps skip
          // straight into the product.
          Capacitor.isNativePlatform() ? (
            <Redirect to="/app/home" />
          ) : (
            <ErrorBoundary>
              <LandingPage />
            </ErrorBoundary>
          )
        }
      />
    </IonRouterOutlet>
  );
}
