from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class OnboardingStateRecord:
    app_user_id: uuid.UUID
    current_step: str
    selected_trigger: str | None
    first_task_id: uuid.UUID | None
    first_task_attempt_id: uuid.UUID | None
    first_win_at: datetime | None
    account_prompt_seen_at: datetime | None
    reminder_prompt_seen_at: datetime | None
    completed_at: datetime | None


class OnboardingRepository(Protocol):
    async def get_state(
        self, app_user_id: uuid.UUID
    ) -> OnboardingStateRecord | None: ...

    async def create_initial_state(
        self, app_user_id: uuid.UUID
    ) -> OnboardingStateRecord: ...

    async def save_trigger(
        self, app_user_id: uuid.UUID, trigger: str
    ) -> OnboardingStateRecord: ...

    async def set_first_task(
        self,
        app_user_id: uuid.UUID,
        task_id: uuid.UUID,
        attempt_id: uuid.UUID | None = None,
    ) -> None: ...

    async def advance_step(self, app_user_id: uuid.UUID, step: str) -> None: ...

    async def mark_account_prompt_seen(self, app_user_id: uuid.UUID) -> None: ...

    async def mark_reminder_prompt_seen(self, app_user_id: uuid.UUID) -> None: ...

    async def mark_completed(self, app_user_id: uuid.UUID) -> None: ...
