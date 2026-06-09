  RevenueCat dashboard:
  1. Create the project; add an iOS app and an Android app.
  2. Create one entitlement with identifier exactly riffy_plus (both gateways and the backend hardcode this string).
  3. Create products in Play Console for Riffy+ monthly ($9.99) and annual ($59.99), import them into
  RevenueCat, and attach both to the riffy_plus entitlement.
  4. Create an Offering (the code reads the current/first offering) containing the Monthly and Annual packages — the paywall maps
  PACKAGE_TYPE.MONTHLY/ANNUAL (/mo, /yr).
  5. Copy the public SDK keys: Apple key → VITE_REVENUECAT_IOS_KEY, Google key → VITE_REVENUECAT_ANDROID_KEY.
  6. Copy the secret v1 REST key → backend REVENUECAT_API_KEY (this is what get_entitlements uses).
  7. Configure a webhook: URL https://<your-backend>/v1/webhooks/revenuecat, and set the Authorization header value → backend
  REVENUECAT_WEBHOOK_AUTH (the code compares it with hmac.compare_digest).
  8. Skip Web Billing / Stripe setup for now, since web = "download the app."

  Google Play Console (Android): create the subscription products, create a service account, grant it the needed Play permissions, and upload
  its credentials JSON to RevenueCat's Android app config.
