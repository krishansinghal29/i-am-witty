from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.api.deps import ContainerDep, CurrentUser

router = APIRouter(prefix="/v1", tags=["identity"])


class CreateGuestRequest(BaseModel):
    timezone: str
    locale: str | None = None


class GuestSessionResponse(BaseModel):
    app_user_id: UUID
    status: str
    session_token: str
    timezone: str


class LinkAuthRequest(BaseModel):
    id_token: str


class UserResponse(BaseModel):
    app_user_id: UUID
    status: str
    firebase_uid: str | None
    timezone: str


class UpdateOnboardingRequest(BaseModel):
    trigger: str


class OnboardingStateResponse(BaseModel):
    current_step: str
    selected_trigger: str | None
    first_task_id: UUID | None
    first_task_attempt_id: UUID | None
    completed_at: datetime | None


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
    is_witty_plus: bool


class HomeResponse(BaseModel):
    plan: DailyPlanResponse
    progress: ProgressResponse
    access: AccessSummary
    onboarding: OnboardingStateResponse


@router.post(
    "/guest-sessions",
    response_model=GuestSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_guest_session(
    body: CreateGuestRequest, container: ContainerDep
) -> GuestSessionResponse:
    """Create an anonymous guest user and return its session token."""
    gi = await container.identity_service.create_guest(body.timezone, body.locale)
    return GuestSessionResponse(
        app_user_id=gi.user.id,
        status=gi.user.status.value,
        session_token=gi.session_token,
        timezone=gi.user.timezone,
    )


@router.post("/auth/link", response_model=UserResponse)
async def link_account(
    body: LinkAuthRequest, container: ContainerDep, user: CurrentUser
) -> UserResponse:
    """Link the current guest to a verified Firebase identity."""
    linked = await container.identity_service.link_account(user.id, body.id_token)
    return UserResponse(
        app_user_id=linked.id,
        status=linked.status.value,
        firebase_uid=linked.firebase_uid,
        timezone=linked.timezone,
    )


@router.get("/onboarding", response_model=OnboardingStateResponse)
async def get_onboarding(
    container: ContainerDep, user: CurrentUser
) -> OnboardingStateResponse:
    """Return the caller's onboarding state, starting it if absent."""
    state = await container.onboarding_service.get_or_start(user.id)
    return OnboardingStateResponse(
        current_step=state.current_step,
        selected_trigger=state.selected_trigger,
        first_task_id=state.first_task_id,
        first_task_attempt_id=state.first_task_attempt_id,
        completed_at=state.completed_at,
    )


@router.patch("/onboarding", response_model=OnboardingStateResponse)
async def update_onboarding(
    body: UpdateOnboardingRequest, container: ContainerDep, user: CurrentUser
) -> OnboardingStateResponse:
    """Save the chosen trigger and assign the user's first task."""
    view = await container.onboarding_service.save_trigger_and_assign_first_task(
        user.id, body.trigger
    )
    return OnboardingStateResponse(
        current_step=view.state.current_step,
        selected_trigger=view.state.selected_trigger,
        first_task_id=view.first_task_id,
        first_task_attempt_id=view.state.first_task_attempt_id,
        completed_at=view.state.completed_at,
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
    """Compose today's plan, progress, access, and onboarding for the caller."""
    plan = await container.daily_plan_service.get_or_create_today_plan(user.id)
    progress = await container.progress_service.get_progress(user.id)
    access = await container.entitlement_service.get_access_state(user.id)
    onboarding = await container.onboarding_service.get_or_start(user.id)
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
        access=AccessSummary(is_witty_plus=access.is_witty_plus),
        onboarding=OnboardingStateResponse(
            current_step=onboarding.current_step,
            selected_trigger=onboarding.selected_trigger,
            first_task_id=onboarding.first_task_id,
            first_task_attempt_id=onboarding.first_task_attempt_id,
            completed_at=onboarding.completed_at,
        ),
    )
