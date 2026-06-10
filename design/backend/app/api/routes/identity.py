from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.api.deps import ContainerDep, CurrentUser
from app.api.routes.tasks import FreeLimitResponse

router = APIRouter(prefix="/v1", tags=["identity"])


class UserResponse(BaseModel):
    app_user_id: UUID
    status: str
    firebase_uid: str | None
    timezone: str


class CompleteOnboardingRequest(BaseModel):
    timezone: str
    trigger: str
    id_token: str
    locale: str | None = None


class FeatureGateResponse(BaseModel):
    feature_key: str
    default_enabled: bool
    requires_entitlement: str | None
    min_app_version: str | None


class PublicConfigResponse(BaseModel):
    values: dict
    free_task_limit: int
    feature_gates: list[FeatureGateResponse]


class PlanItemResponse(BaseModel):
    id: UUID
    task_id: UUID
    position: int
    status: str
    current_attempt_id: UUID | None


class DailyPlanResponse(BaseModel):
    id: UUID
    plan_date: date
    status: str
    items: list[PlanItemResponse]


class ProgressResponse(BaseModel):
    completed_task_count: int
    current_streak_count: int
    longest_streak_count: int
    last_activity_date: date | None


class AccessSummary(BaseModel):
    is_riffy_plus: bool


class HomeResponse(BaseModel):
    plan: DailyPlanResponse
    progress: ProgressResponse
    access: AccessSummary
    free_limit: FreeLimitResponse


@router.post(
    "/onboarding/complete",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def complete_onboarding(
    body: CompleteOnboardingRequest, container: ContainerDep
) -> UserResponse:
    """Finalize onboarding: verify the Firebase token, then create the user +
    onboarding row in one transaction. This is the first and only write of the
    flow (everything before it runs client-side)."""
    user = await container.identity_service.complete_onboarding(
        timezone=body.timezone,
        trigger=body.trigger,
        id_token=body.id_token,
        locale=body.locale,
    )
    return UserResponse(
        app_user_id=user.id,
        status=user.status.value,
        firebase_uid=user.firebase_uid,
        timezone=user.timezone,
    )


@router.get("/config", response_model=PublicConfigResponse)
async def get_config(container: ContainerDep) -> PublicConfigResponse:
    """Return the client-facing public configuration and feature gates."""
    cfg = await container.app_config_service.get_public_config()
    return PublicConfigResponse(
        values=cfg.values,
        free_task_limit=cfg.free_task_limit,
        feature_gates=[
            FeatureGateResponse(
                feature_key=gate.feature_key,
                default_enabled=gate.default_enabled,
                requires_entitlement=gate.requires_entitlement,
                min_app_version=gate.min_app_version,
            )
            for gate in cfg.feature_gates
        ],
    )


@router.get("/home", response_model=HomeResponse)
async def get_home(container: ContainerDep, user: CurrentUser) -> HomeResponse:
    """Compose today's plan, progress, and access for the caller."""
    plan = await container.daily_plan_service.get_or_create_today_plan(user.id)
    progress = await container.progress_service.get_progress(user.id)
    access = await container.entitlement_service.get_access_state(user.id)
    free_limit = await container.task_attempt_service.get_free_limit(user.id)
    return HomeResponse(
        plan=DailyPlanResponse(
            id=plan.id,
            plan_date=plan.plan_date,
            status=plan.status.value,
            items=[
                PlanItemResponse(
                    id=item.id,
                    task_id=item.task_id,
                    position=item.position,
                    status=item.status.value,
                    current_attempt_id=item.current_attempt_id,
                )
                for item in plan.items
            ],
        ),
        progress=ProgressResponse(
            completed_task_count=progress.completed_task_count,
            current_streak_count=progress.current_streak_count,
            longest_streak_count=progress.longest_streak_count,
            last_activity_date=progress.last_activity_date,
        ),
        access=AccessSummary(is_riffy_plus=access.is_riffy_plus),
        free_limit=FreeLimitResponse.from_decision(free_limit),
    )
