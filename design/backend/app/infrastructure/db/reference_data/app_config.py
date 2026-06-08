"""Canonical product config rows."""

APP_CONFIG: list[dict] = [
    {
        "key": "free_task_limit",
        "value": 3,
        "is_public": True,
        "description": "Authoritative daily free-task limit for non-subscribers.",
    },
    {
        "key": "telegram_community_url",
        "value": "https://t.me/iamwitty",
        "is_public": True,
        "description": "Telegram community link (placeholder - update with real URL).",
    },
    {
        "key": "terms_url",
        "value": "https://i-am-witty.app/terms",
        "is_public": True,
        "description": "Terms of Service URL (placeholder).",
    },
    {
        "key": "privacy_url",
        "value": "https://i-am-witty.app/privacy",
        "is_public": True,
        "description": "Privacy Policy URL (placeholder).",
    },
]

FEATURE_GATES: list[dict] = [
    {
        "feature_key": "role_play",
        "default_enabled": False,
        "requires_entitlement": "witty_plus",
        "min_app_version": None,
    },
    {
        "feature_key": "witty_plus",
        "default_enabled": True,
        "requires_entitlement": None,
        "min_app_version": None,
    },
    {
        "feature_key": "premium_task_library",
        "default_enabled": True,
        "requires_entitlement": "witty_plus",
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

