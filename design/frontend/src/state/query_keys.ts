/**
 * Centralised TanStack Query key definitions.
 *
 * NOTE: progress and plan both come from the `home` query (the backend bundles
 * them into a single /v1/home response). There is NO separate progress or plan
 * key. Free-limit data is returned inline by the start/complete mutations and is
 * therefore NOT tracked by a query key.
 *
 * `offerings` is populated client-side via the RevenueCat SDK; no backend
 * endpoint exists for it.
 */
export const queryKeys = {
  session: ['session'] as const,
  config: ['config'] as const,
  home: ['home'] as const,
  catalog: ['practice', 'catalog'] as const,
  lessons: ['lessons', 'catalog'] as const,
  taskRuntime: (taskId: string) => ['task', 'runtime', taskId] as const,
  access: ['entitlement', 'access'] as const,
  offerings: ['subscription', 'offerings'] as const, // RevenueCat SDK, client-side
};
