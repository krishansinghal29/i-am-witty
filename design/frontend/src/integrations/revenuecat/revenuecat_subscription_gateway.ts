/**
 * Real RevenueCat implementation of the {@link SubscriptionGateway} port.
 *
 * Backed by `@revenuecat/purchases-capacitor`, which is a native-only plugin:
 * on the web there is no RevenueCat SDK, so every method degrades gracefully
 * (offerings return empty, entitlement reads return an empty snapshot, and
 * purchases throw a user-friendly {@link AppError}). Configuration never throws
 * so that app startup can call {@link RevenueCatSubscriptionGateway.configure}
 * unconditionally without risk of crashing.
 */

import { Capacitor } from '@capacitor/core';
import {
  PACKAGE_TYPE,
  Purchases,
  type CustomerInfo,
  type PurchasesPackage,
} from '@revenuecat/purchases-capacitor';

import { AppError } from '@/data/errors/app_error';
import type {
  EntitlementSnapshot,
  Offering,
  SubscriptionGateway,
  SubscriptionPackage,
} from '@/integrations/ports/subscription_gateway';

/**
 * Identifier of the entitlement that grants Witty+ access. This MUST match the
 * entitlement identifier configured in the RevenueCat dashboard.
 */
const WITTY_PLUS_ENTITLEMENT = 'witty_plus';

export class RevenueCatSubscriptionGateway implements SubscriptionGateway {
  private configured = false;

  /**
   * Cache of native package objects keyed by their identifier. We need to keep
   * the original SDK objects around because `purchasePackage` must hand the
   * native package back to the SDK (our plain {@link SubscriptionPackage} DTO
   * is not enough).
   */
  private packageCache = new Map<string, PurchasesPackage>();

  /** Resolve the RevenueCat API key for the current platform, or null. */
  private platformApiKey(): string | null {
    switch (Capacitor.getPlatform()) {
      case 'ios':
        return import.meta.env.VITE_REVENUECAT_IOS_KEY || null;
      case 'android':
        return import.meta.env.VITE_REVENUECAT_ANDROID_KEY || null;
      default:
        return import.meta.env.VITE_REVENUECAT_WEB_KEY || null;
    }
  }

  /**
   * Whether the SDK is usable right now. RevenueCat purchases-capacitor is
   * native-only, so on web (or before a successful configure) we treat the
   * gateway as unavailable and degrade gracefully.
   */
  private available(): boolean {
    return Capacitor.isNativePlatform() && this.configured;
  }

  async configure(appUserId: string | null): Promise<void> {
    // Native-only plugin: no-op on web, leaving the gateway unconfigured.
    if (!Capacitor.isNativePlatform()) return;

    const apiKey = this.platformApiKey();
    if (apiKey === null) return; // No key for this platform: stay unconfigured.

    try {
      await Purchases.configure({
        apiKey,
        appUserID: appUserId ?? undefined,
      });
      this.configured = true;
    } catch {
      // Startup must never crash on a misconfigured SDK: stay unconfigured.
      this.configured = false;
    }
  }

  async getOfferings(): Promise<Offering[]> {
    if (!this.available()) return [];

    const res = await Purchases.getOfferings();

    // Prefer the full map of offerings; fall back to the current offering.
    const offerings = Object.values(res.all);
    if (offerings.length === 0 && res.current) {
      offerings.push(res.current);
    }

    return offerings.map((offering) => ({
      identifier: offering.identifier,
      packages: offering.availablePackages.map((pkg) => this.toPackage(pkg)),
    }));
  }

  async purchasePackage(pkg: SubscriptionPackage): Promise<EntitlementSnapshot> {
    if (!this.available()) {
      throw new AppError({
        code: 'unknown',
        userMessage: 'Purchases are only available in the mobile app.',
        reason: 'iap_unavailable',
      });
    }

    let native = this.packageCache.get(pkg.identifier);
    if (!native) {
      // Cache may be cold (e.g. after a reload). Refresh and try once more.
      await this.getOfferings();
      native = this.packageCache.get(pkg.identifier);
    }
    if (!native) {
      throw new AppError({
        code: 'unknown',
        userMessage: 'That subscription is no longer available.',
        reason: 'package_not_found',
      });
    }

    const res = await Purchases.purchasePackage({ aPackage: native });
    return this.toSnapshot(res.customerInfo);
  }

  async restorePurchases(): Promise<EntitlementSnapshot> {
    if (!this.available()) return this.emptySnapshot();

    const res = await Purchases.restorePurchases();
    return this.toSnapshot(res.customerInfo);
  }

  async getEntitlement(): Promise<EntitlementSnapshot> {
    if (!this.available()) return this.emptySnapshot();

    const res = await Purchases.getCustomerInfo();
    return this.toSnapshot(res.customerInfo);
  }

  /** Map a native package to our DTO, caching the native object for purchase. */
  private toPackage(pkg: PurchasesPackage): SubscriptionPackage {
    this.packageCache.set(pkg.identifier, pkg);

    let period: SubscriptionPackage['period'];
    switch (pkg.packageType) {
      case PACKAGE_TYPE.ANNUAL:
        period = 'annual';
        break;
      case PACKAGE_TYPE.MONTHLY:
        period = 'monthly';
        break;
      default:
        period = 'unknown';
    }

    return {
      identifier: pkg.identifier,
      productId: pkg.product.identifier,
      title: pkg.product.title,
      priceString: pkg.product.priceString,
      period,
    };
  }

  /** Reduce a RevenueCat customer info object into our entitlement snapshot. */
  private toSnapshot(customerInfo: CustomerInfo): EntitlementSnapshot {
    const active = customerInfo.entitlements.active;
    const ids = Object.keys(active);
    const isWittyPlus = ids.includes(WITTY_PLUS_ENTITLEMENT);
    const managementUrl = customerInfo.managementURL ?? null;
    return { isWittyPlus, activeEntitlementIds: ids, managementUrl };
  }

  /** Snapshot used when the SDK is unavailable (e.g. on web). */
  private emptySnapshot(): EntitlementSnapshot {
    return { isWittyPlus: false, activeEntitlementIds: [], managementUrl: null };
  }
}
