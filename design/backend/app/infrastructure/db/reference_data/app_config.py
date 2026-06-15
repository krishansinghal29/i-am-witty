"""Canonical product config rows."""

APP_CONFIG: list[dict] = [
    {
        "key": "free_task_limit",
        "value": 10,
        "is_public": True,
        "description": "Authoritative daily free-task limit for non-subscribers.",
    },
    {
        "key": "telegram_community_url",
        "value": "https://t.me/+coeCFQk8Xs9jNmM1",
        "is_public": True,
        "description": "Telegram community group invite link.",
    },
    {
        "key": "terms_url",
        "value": "https://riffy.pro/legal#terms",
        "is_public": True,
        "description": "Canonical Terms of Service URL.",
    },
    {
        "key": "privacy_url",
        "value": "https://riffy.pro/legal#privacy",
        "is_public": True,
        "description": "Canonical Privacy Policy URL.",
    },
    {
        "key": "account_deletion_url",
        "value": "https://riffy.pro/legal#account-deletion",
        "is_public": True,
        "description": "Canonical account deletion request instructions URL.",
    },
    {
        "key": "ios_app_store_url",
        "value": "https://apps.apple.com/app/id000000000",
        "is_public": True,
        "description": "App Store listing URL (placeholder); web paywall 'download the app' CTA.",
    },
    {
        "key": "android_play_store_url",
        "value": "https://play.google.com/store/apps/details?id=com.iamwitty.app",
        "is_public": True,
        "description": "Play Store listing URL (placeholder); web paywall 'download the app' CTA.",
    },
]

FEATURE_GATES: list[dict] = [
    {
        "feature_key": "riffy_plus",
        "default_enabled": True,
        "requires_entitlement": None,
        "min_app_version": None,
    },
    {
        "feature_key": "premium_task_library",
        "default_enabled": True,
        "requires_entitlement": "riffy_plus",
        "min_app_version": None,
    },
]

APP_RELEASE_CHANNELS: list[dict] = [
    {
        "channel_key": "production",
        "min_supported_version": None,
        "latest_version": None,
        "is_active": True,
        "channel_metadata": {},
    },
    {
        "channel_key": "development",
        "min_supported_version": None,
        "latest_version": None,
        "is_active": True,
        "channel_metadata": {},
    },
]
