/** Maps entitlement DTOs → Entitlement / AccessState view-models. */

import { AccessState, Entitlement } from '@/types/models';
import { AccessDto, EntitlementDto } from '@/data/dto/entitlement_dto';

export function mapEntitlement(dto: EntitlementDto): Entitlement {
  return {
    entitlementKey: dto.entitlement_key,
    status: dto.status,
    productId: dto.product_id,
    currentPeriodEndsAt: dto.current_period_ends_at,
    trialEndsAt: dto.trial_ends_at,
  };
}

export function mapAccess(dto: AccessDto): AccessState {
  return {
    isRiffyPlus: dto.is_riffy_plus,
    entitlements: dto.entitlements.map(mapEntitlement),
  };
}
