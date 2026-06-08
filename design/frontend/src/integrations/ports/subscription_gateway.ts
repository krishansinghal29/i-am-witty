export interface SubscriptionPackage {
  identifier: string;
  productId: string;
  title: string;
  priceString: string;
  period: 'monthly' | 'annual' | 'unknown';
}

export interface Offering {
  identifier: string;
  packages: SubscriptionPackage[];
}

export interface EntitlementSnapshot {
  isWittyPlus: boolean;
  activeEntitlementIds: string[];
  managementUrl: string | null;
}

export interface SubscriptionGateway {
  configure(appUserId: string | null): Promise<void>;
  getOfferings(): Promise<Offering[]>;
  purchasePackage(pkg: SubscriptionPackage): Promise<EntitlementSnapshot>;
  restorePurchases(): Promise<EntitlementSnapshot>;
  getEntitlement(): Promise<EntitlementSnapshot>;
}
