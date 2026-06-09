/**
 * RevenueCat identity bootstrap.
 *
 * Configures the subscription SDK with the backend `app_user_id` (a stable UUID)
 * as soon as it is known. This is the identity the backend matches webhooks on
 * — Option A: the RevenueCat app user id IS our `app_user_id` — so configuring
 * with anything else (e.g. an anonymous id or the Firebase uid) would stop a
 * purchase from ever mirroring to `/v1/me/access`.
 *
 * The backend preserves the UUID across guest→auth linking, so the id never
 * changes underfoot: a single `configure()` is enough and no logIn/alias is
 * needed. The ref guard keeps it to one call per id.
 *
 * We only configure for a backend-UUID-shaped id. In the rare case where the
 * session falls back to a non-UUID (e.g. the Firebase uid, when secure storage
 * was wiped but the Firebase session survived), we skip rather than configure
 * RevenueCat under an id the backend can never match — turning a stranded
 * purchase into a clean "not available" failure instead.
 */

import { useEffect, useRef } from 'react';
import { useIntegrations } from '@/app/providers';

/** Canonical 8-4-4-4-12 UUID, matching what the backend `uuid.UUID()` accepts. */
const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function useSubscriptionIdentity(
  appUserId: string | null | undefined,
): void {
  const { subscriptions } = useIntegrations();
  const configuredFor = useRef<string | null>(null);

  useEffect(() => {
    if (!appUserId || !UUID_RE.test(appUserId)) return;
    if (configuredFor.current === appUserId) return;
    configuredFor.current = appUserId;
    // configure() never throws (it degrades gracefully when unavailable, e.g.
    // on web or with no platform key), so fire-and-forget is safe.
    void subscriptions.configure(appUserId);
  }, [appUserId, subscriptions]);
}
