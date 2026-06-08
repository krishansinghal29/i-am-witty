/**
 * Per-route error boundary.
 *
 * Wraps a screen so a render failure degrades to a recoverable {@link ErrorView}
 * inside a full `IonPage` instead of blanking the whole app. "Try again" simply
 * re-mounts the wrapped subtree.
 */

import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { IonContent, IonPage } from '@ionic/react';
import { ErrorView } from '@/components/ui';

interface ErrorBoundaryProps {
  children: ReactNode;
  /** Optional override for the recovery message shown on failure. */
  label?: string;
}

interface ErrorBoundaryState {
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    if (import.meta.env.DEV) {
      console.error('ErrorBoundary caught a render error', error, info);
    }
  }

  private handleRetry = (): void => {
    this.setState({ error: null });
  };

  render(): ReactNode {
    if (this.state.error) {
      return (
        <IonPage>
          <IonContent>
            <ErrorView
              title="Something went sideways"
              message={
                this.props.label ??
                'We hit a snag rendering this screen. Let’s try that again.'
              }
              onRetry={this.handleRetry}
            />
          </IonContent>
        </IonPage>
      );
    }

    return this.props.children;
  }
}
