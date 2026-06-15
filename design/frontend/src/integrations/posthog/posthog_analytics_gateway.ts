import posthog from 'posthog-js';

import type {
  AnalyticsGateway,
  FeatureFlagValue,
} from '@/integrations/ports/analytics_gateway';

/**
 * Real PostHog-backed implementation of {@link AnalyticsGateway}.
 *
 * PostHog is the source of truth for feature flags (e.g. `riffy_plus` gating),
 * consistent with the backend `feature_gate_defaults`.
 * When `VITE_POSTHOG_KEY` is absent the gateway is a safe no-op so dev/web
 * still runs without a configured PostHog project.
 */
export class PostHogAnalyticsGateway implements AnalyticsGateway {
  private enabled = false;

  constructor() {
    const key = import.meta.env.VITE_POSTHOG_KEY;
    const host = import.meta.env.VITE_POSTHOG_HOST;

    if (key) {
      try {
        posthog.init(key, {
          api_host: host || 'https://us.i.posthog.com',
          capture_pageview: false,
          autocapture: false,
          persistence: 'localStorage',
          loaded: () => {},
        });
        this.enabled = true;
      } catch {
        this.enabled = false;
      }
    }
  }

  capture(event: string, props?: Record<string, unknown>): void {
    if (this.enabled) {
      posthog.capture(event, props);
    }
  }

  identify(appUserId: string, traits?: Record<string, unknown>): void {
    if (this.enabled) {
      posthog.identify(appUserId, traits);
    }
  }

  reset(): void {
    if (this.enabled) {
      posthog.reset();
    }
  }

  isFeatureEnabled(flag: string): boolean {
    if (!this.enabled) {
      return false;
    }
    return posthog.isFeatureEnabled(flag) ?? false;
  }

  getFeatureFlag(flag: string): FeatureFlagValue {
    if (!this.enabled) {
      return undefined;
    }
    return posthog.getFeatureFlag(flag) as FeatureFlagValue;
  }

  onFeatureFlags(cb: () => void): () => void {
    if (!this.enabled) {
      return () => {};
    }
    const unsub = posthog.onFeatureFlags(() => cb());
    return typeof unsub === 'function' ? unsub : () => {};
  }
}
