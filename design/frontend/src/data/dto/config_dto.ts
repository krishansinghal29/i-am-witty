/** Wire shapes for config / feature-gate endpoints (snake_case). */

export interface FeatureGateDto {
  feature_key: string;
  default_enabled: boolean;
  requires_entitlement: string | null;
  min_app_version: string | null;
}

export interface PublicConfigDto {
  values: Record<string, unknown>;
  free_task_limit: number;
  feature_gates: FeatureGateDto[];
}
