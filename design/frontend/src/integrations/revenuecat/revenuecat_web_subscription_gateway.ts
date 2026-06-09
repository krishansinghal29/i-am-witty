/**
 * Web Billing implementation of the {@link SubscriptionGateway} port.
 *
 * Backed by RevenueCat's Web Billing SDK (`@revenuecat/purchases-js`), which —
 * unlike `@revenuecat/purchases-capacitor` — provides a real purchase path in
 * the browser. It is wired (in the composition root) only on the web target,
 * so screens/hooks keep talking to the same port regardless of platform.
 *
 * The web SDK requires a public Web Billing key (`VITE_REVENUECAT_WEB_KEY`).
 * When that key is absent the gateway degrades gracefully: offerings return
 * empty, entitlement reads return an empty snapshot, and a purchase throws a
 * friendly {@link AppError}. It never crashes app startup.
 */

import {
  PackageType,
  Purchases,
  type CustomerInfo,
  type Package as RcPackage,
} from '@revenuecat/purchases-js';

import { AppError } from '@/data/errors/app_error';
import type {
  EntitlementSnapshot,
  Offering,
  SubscriptionGateway,
  SubscriptionPackage,
} from '@/integrations/ports/subscription_gateway';

/**
 * Identifier of the entitlement that grants Riffy+ access. MUST match the
 * entitlement identifier configured in the RevenueCat dashboard (and the native
 * gateway).
 */
const RIFFY_PLUS_ENTITLEMENT = 'riffy_plus';

export class RevenueCatWebSubscriptionGateway implements SubscriptionGateway {
  private configured = false;

  /** App user id to identify the customer with, when known. */
  private appUserId: string | null = null;

  /**
   * Cache of SDK package objects keyed by identifier. The port's
   * {@link SubscriptionPackage} DTO is not enough to drive a purchase: the SDK
   * needs its own `Package` object handed back to `purchase()`.
   */
  private packageCache = new Map<string, RcPackage>();

  private apiKey(): string | null {
    return import.meta.env.VITE_REVENUECAT_WEB_KEY || null;
  }

  async configure(appUserId: string | null): Promise<void> {
    this.appUserId = appUserId;
    // Eager attempt so the first purchase is snappy; never throws.
    this.ensureConfigured();
  }

  /**
   * Lazily configure the Web Billing SDK. Returns whether the gateway is usable
   * (i.e. a key exists and the SDK is configured). Safe to call repeatedly.
   */
  private ensureConfigured(): boolean {
    if (this.configured && Purchases.isConfigured()) return true;

    if (Purchases.isConfigured()) {
      this.configured = true;
      return true;
    }

    const apiKey = this.apiKey();
    if (apiKey === null) return false; // No web key: stay unavailable.

    try {
      const appUserId =
        this.appUserId ?? Purchases.generateRevenueCatAnonymousAppUserId();
      Purchases.configure({ apiKey, appUserId });
      this.configured = true;
      return true;
    } catch {
      // App must never crash on a misconfigured SDK: stay unavailable.
      this.configured = false;
      return false;
    }
  }

  async getOfferings(): Promise<Offering[]> {
    if (!this.ensureConfigured()) return [];

    const res = await Purchases.getSharedInstance().getOfferings();

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
    if (!this.ensureConfigured()) {
      throw new AppError({
        code: 'unknown',
        userMessage: 'Online checkout isn’t available right now. Please try again later.',
        reason: 'web_billing_unavailable',
      });
    }

    let rcPackage = this.packageCache.get(pkg.identifier);
    if (!rcPackage) {
      // Cache may be cold (e.g. after a reload). Refresh and try once more.
      await this.getOfferings();
      rcPackage = this.packageCache.get(pkg.identifier);
    }
    if (!rcPackage) {
      throw new AppError({
        code: 'unknown',
        userMessage: 'That subscription is no longer available.',
        reason: 'package_not_found',
      });
    }

    const res = await Purchases.getSharedInstance().purchase({ rcPackage });
    return this.toSnapshot(res.customerInfo);
  }

  async restorePurchases(): Promise<EntitlementSnapshot> {
    // Web Billing has no separate "restore": the entitlement is bound to the
    // configured app user id, so re-reading customer info is the restore.
    if (!this.ensureConfigured()) return this.emptySnapshot();

    const info = await Purchases.getSharedInstance().getCustomerInfo();
    return this.toSnapshot(info);
  }

  async getEntitlement(): Promise<EntitlementSnapshot> {
    if (!this.ensureConfigured()) return this.emptySnapshot();

    const info = await Purchases.getSharedInstance().getCustomerInfo();
    return this.toSnapshot(info);
  }

  /** Map an SDK package to our DTO, caching the SDK object for purchase. */
  private toPackage(pkg: RcPackage): SubscriptionPackage {
    this.packageCache.set(pkg.identifier, pkg);

    let period: SubscriptionPackage['period'];
    switch (pkg.packageType) {
      case PackageType.Annual:
        period = 'annual';
        break;
      case PackageType.Monthly:
        period = 'monthly';
        break;
      default:
        period = 'unknown';
    }

    const product = pkg.webBillingProduct;
    return {
      identifier: pkg.identifier,
      productId: product.identifier,
      title: product.title,
      priceString: product.price.formattedPrice,
      period,
    };
  }

  /** Reduce a Web Billing customer info object into our entitlement snapshot. */
  private toSnapshot(info: CustomerInfo): EntitlementSnapshot {
    const ids = Object.keys(info.entitlements.active);
    return {
      isRiffyPlus: ids.includes(RIFFY_PLUS_ENTITLEMENT),
      activeEntitlementIds: ids,
      managementUrl: info.managementURL ?? null,
    };
  }

  /** Snapshot used when the SDK is unavailable (e.g. no web key configured). */
  private emptySnapshot(): EntitlementSnapshot {
    return { isRiffyPlus: false, activeEntitlementIds: [], managementUrl: null };
  }
}
