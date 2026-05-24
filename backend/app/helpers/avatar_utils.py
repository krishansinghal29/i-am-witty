from __future__ import annotations

import json
import random
import os
from helpers.logger import logger

AVATARS_JSON = os.path.join(os.path.dirname(__file__), "..", "static", "avatars", "avatars.json")


def get_random_avatar_url() -> str | None:
    try:
        if not os.path.exists(AVATARS_JSON):
            return None
        with open(AVATARS_JSON) as f:
            avatar_urls = json.load(f)
        if not avatar_urls:
            return None
        return random.choice(avatar_urls)
    except Exception as e:
        logger.error(f"Error getting avatar URL: {str(e)}")
        return None
