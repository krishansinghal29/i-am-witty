/** Maps config DTOs → AppConfig / FeatureGate view-models. */

import { AppConfig, FeatureGate } from '@/types/models';
import { FeatureGateDto, PublicConfigDto } from '@/data/dto/config_dto';

export function mapFeatureGate(dto: FeatureGateDto): FeatureGate {
  return {
    featureKey: dto.feature_key,
    defaultEnabled: dto.default_enabled,
    requiresEntitlement: dto.requires_entitlement,
    minAppVersion: dto.min_app_version,
  };
}

export function mapAppConfig(dto: PublicConfigDto): AppConfig {
  return {
    values: dto.values,
    freeTaskLimit: dto.free_task_limit,
    featureGates: dto.feature_gates.map(mapFeatureGate),
  };
}
