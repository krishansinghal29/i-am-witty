from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class OnboardingStateRecord:
    app_user_id: uuid.UUID
    selected_trigger: str | None
    completed_at: datetime | None


class OnboardingRepository(Protocol):
    async def get_state(
        self, app_user_id: uuid.UUID
    ) -> OnboardingStateRecord | None: ...

    async def create_completed_state(
        self, app_user_id: uuid.UUID, trigger: str
    ) -> OnboardingStateRecord:
        """Write the single onboarding row (selected_trigger + completed_at=now).

        Idempotent: updates the row in place if one already exists.
        """
        ...
