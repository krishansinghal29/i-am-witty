import {
  IonTabs,
  IonTabBar,
  IonTabButton,
  IonIcon,
  IonLabel,
  IonRouterOutlet,
} from '@ionic/react';
import { Route, Redirect } from 'react-router-dom';
import { Capacitor } from '@capacitor/core';
import {
  homeOutline,
  flameOutline,
  chatbubbleEllipsesOutline,
  personOutline,
} from 'ionicons/icons';
import { OnboardingGuard } from '@/app/guards/onboarding_guard';
import { ErrorBoundary } from '@/app/error_boundary';
import { HomePage } from '@/screens/home/home_page';
import { PracticePage } from '@/screens/practice/practice_page';
import { RoleplayPage } from '@/screens/roleplay/roleplay_page';
import { ProfilePage } from '@/screens/profile/profile_page';
import { OnboardingFlowPage } from '@/screens/onboarding/onboarding_flow_page';
import { LandingPage } from '@/screens/landing/landing_page';
import { LegalPage } from '@/screens/legal/legal_page';
import { TaskRuntimePage } from '@/screens/task_runtime/task_runtime_page';
import { PaywallSheet } from '@/screens/paywall/paywall_sheet';
import { SupportSheet } from '@/screens/support/support_sheet';

export function AppTabs() {
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
                <RoleplayPage />
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
          <IonTabButton tab="roleplay" href="/app/roleplay">
            <IonIcon icon={chatbubbleEllipsesOutline} />
            <IonLabel>Role play</IonLabel>
          </IonTabButton>
          <IonTabButton tab="profile" href="/app/profile">
            <IonIcon icon={personOutline} />
            <IonLabel>Profile</IonLabel>
          </IonTabButton>
        </IonTabBar>
      </IonTabs>
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
