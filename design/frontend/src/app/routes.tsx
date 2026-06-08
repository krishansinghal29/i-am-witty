import {
  IonTabs,
  IonTabBar,
  IonTabButton,
  IonIcon,
  IonLabel,
  IonRouterOutlet,
  IonBadge,
} from '@ionic/react';
import { Route, Redirect } from 'react-router-dom';
import {
  homeOutline,
  flameOutline,
  chatbubblesOutline,
  personOutline,
} from 'ionicons/icons';
import { OnboardingGuard } from '@/app/guards/onboarding_guard';
import { HomePage } from '@/screens/home/home_page';
import { PracticePage } from '@/screens/practice/practice_page';
import { ProfilePage } from '@/screens/profile/profile_page';
import { OnboardingFlowPage } from '@/screens/onboarding/onboarding_flow_page';
import { TaskRuntimePage } from '@/screens/task_runtime/task_runtime_page';

export function AppTabs() {
  return (
    <IonTabs>
      <IonRouterOutlet>
        <Route exact path="/app/home" component={HomePage} />
        <Route exact path="/app/practice" component={PracticePage} />
        <Route exact path="/app/profile" component={ProfilePage} />
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
        {/* TODO: gate Role play via AnalyticsGateway.isFeatureEnabled('role_play') */}
        <IonTabButton tab="roleplay" disabled>
          <IonIcon icon={chatbubblesOutline} />
          <IonLabel>Role play</IonLabel>
          <IonBadge color="medium">Soon</IonBadge>
        </IonTabButton>
        <IonTabButton tab="profile" href="/app/profile">
          <IonIcon icon={personOutline} />
          <IonLabel>Profile</IonLabel>
        </IonTabButton>
      </IonTabBar>
    </IonTabs>
  );
}

export function AppRoutes() {
  return (
    <IonRouterOutlet>
      <Route path="/onboarding" component={OnboardingFlowPage} />
      <Route path="/task/:taskId" component={TaskRuntimePage} />
      <Route
        path="/app"
        render={() => (
          <OnboardingGuard>
            <AppTabs />
          </OnboardingGuard>
        )}
      />
      <Route exact path="/">
        <Redirect to="/app/home" />
      </Route>
    </IonRouterOutlet>
  );
}
