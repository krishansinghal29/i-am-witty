/** Web-only landing page; the shared content is also rendered at build time. */
import type { MouseEvent } from 'react';
import { IonPage } from '@ionic/react';
import { useHistory } from 'react-router-dom';
import { LandingContent } from './landing_content';

export function LandingPage() {
  const history = useHistory();
  const openApp = (event: MouseEvent<HTMLAnchorElement>) => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    history.push('/app');
  };

  return <IonPage><LandingContent onOpenApp={openApp} /></IonPage>;
}
