/** Wire shapes for entitlement / access endpoints (snake_case). */

export interface EntitlementDto {
  entitlement_key: string;
  status: string;
  product_id: string | null;
  current_period_ends_at: string | null;
  trial_ends_at: string | null;
}

export interface AccessDto {
  is_riffy_plus: boolean;
  entitlements: EntitlementDto[];
}
