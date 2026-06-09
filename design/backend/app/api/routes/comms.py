from __future__ import annotations

from datetime import datetime, time
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from app.api.deps import ContainerDep, CurrentUser
from app.ports.repositories.notification_device_repository import RegisterDeviceInput

router = APIRouter(prefix="/v1", tags=["comms"])


class WebhookAck(BaseModel):
    status: str
    event_id: str


class ReminderResponse(BaseModel):
    status: str
    timing_key: str | None
    local_time: time | None
    timezone: str


class SaveReminderRequest(BaseModel):
    status: str
    timing_key: str | None = None
    local_time: time | None = None
    timezone: str


class RegisterDeviceRequest(BaseModel):
    device_key: str
    platform: str
    push_token: str | None = None
    permission_status: str = "unknown"
    app_version: str | None = None
    release_channel: str | None = None


class DeviceResponse(BaseModel):
    id: UUID
    device_key: str
    platform: str
    permission_status: str
    push_token: str | None
    disabled_at: datetime | None


class SubmitSupportRequest(BaseModel):
    message_text: str
    source_screen: str | None = None


class SupportResponse(BaseModel):
    id: UUID
    status: str
    created_at: datetime


class EntitlementResponse(BaseModel):
    entitlement_key: str
    status: str
    product_id: str | None
    current_period_ends_at: datetime | None
    trial_ends_at: datetime | None


class AccessResponse(BaseModel):
    is_riffy_plus: bool
    entitlements: list[EntitlementResponse]


@router.post("/webhooks/revenuecat", response_model=WebhookAck)
async def revenuecat_webhook(
    request: Request, container: ContainerDep
) -> WebhookAck:
    """Verify a RevenueCat webhook and mirror the subscriber's entitlements.

    `parse_webhook` enforces the shared-secret Authorization header. Processing
    re-fetches the subscriber from RevenueCat (authoritative + idempotent), so a
    failed DB/provider call surfaces as a non-2xx and RevenueCat retries.
    """
    body = await request.body()
    try:
        event = container.integrations.subscription_provider.parse_webhook(
            dict(request.headers), body
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail="invalid_webhook_auth") from exc
    await container.entitlement_service.process_webhook(event)
    return WebhookAck(status="accepted", event_id=event.event_id)


@router.get("/reminders", response_model=ReminderResponse | None)
async def get_reminder(
    user: CurrentUser, container: ContainerDep
) -> ReminderResponse | None:
    """Return the caller's reminder preference, or null when unset."""
    pref = await container.reminder_service.get_reminder(user.id)
    if pref is None:
        return None
    return ReminderResponse(
        status=pref.status,
        timing_key=pref.timing_key,
        local_time=pref.local_time,
        timezone=pref.timezone,
    )


@router.put("/reminders", response_model=ReminderResponse)
async def save_reminder(
    body: SaveReminderRequest, user: CurrentUser, container: ContainerDep
) -> ReminderResponse:
    """Create or update the caller's reminder preference."""
    pref = await container.reminder_service.save_reminder(
        user.id,
        body.status,
        body.timing_key,
        body.local_time,
        body.timezone,
    )
    return ReminderResponse(
        status=pref.status,
        timing_key=pref.timing_key,
        local_time=pref.local_time,
        timezone=pref.timezone,
    )


@router.delete("/reminders", status_code=status.HTTP_204_NO_CONTENT)
async def clear_reminder(user: CurrentUser, container: ContainerDep) -> None:
    """Delete the caller's reminder preference."""
    await container.reminder_service.clear_reminder(user.id)


@router.post(
    "/notification-devices",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_device(
    body: RegisterDeviceRequest, user: CurrentUser, container: ContainerDep
) -> DeviceResponse:
    """Register or refresh a push notification device for the caller."""
    rec = await container.notification_service.register_device(
        RegisterDeviceInput(
            app_user_id=user.id,
            device_key=body.device_key,
            platform=body.platform,
            push_token=body.push_token,
            permission_status=body.permission_status,
            app_version=body.app_version,
            release_channel=body.release_channel,
        )
    )
    return DeviceResponse(
        id=rec.id,
        device_key=rec.device_key,
        platform=rec.platform,
        permission_status=rec.permission_status,
        push_token=rec.push_token,
        disabled_at=rec.disabled_at,
    )


@router.post(
    "/support-messages",
    response_model=SupportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_support(
    body: SubmitSupportRequest, user: CurrentUser, container: ContainerDep
) -> SupportResponse:
    """Submit a support message from the caller."""
    rec = await container.support_service.submit_support(
        body.message_text,
        app_user_id=user.id,
        source_screen=body.source_screen,
    )
    return SupportResponse(
        id=rec.id,
        status=rec.status,
        created_at=rec.created_at,
    )


def _to_access_response(access) -> AccessResponse:
    return AccessResponse(
        is_riffy_plus=access.is_riffy_plus,
        entitlements=[
            EntitlementResponse(
                entitlement_key=e.entitlement_key,
                status=e.status.value,
                product_id=e.product_id,
                current_period_ends_at=e.current_period_ends_at,
                trial_ends_at=e.trial_ends_at,
            )
            for e in access.entitlements
        ],
    )


@router.get("/me/access", response_model=AccessResponse)
async def get_access(
    user: CurrentUser, container: ContainerDep
) -> AccessResponse:
    """Return the caller's derived access state and mirrored entitlements."""
    access = await container.entitlement_service.get_access_state(user.id)
    return _to_access_response(access)


@router.post("/me/access/sync", response_model=AccessResponse)
async def sync_access(
    user: CurrentUser, container: ContainerDep
) -> AccessResponse:
    """Pull the caller's subscription from RevenueCat now and return fresh access.

    Lets the client reconcile immediately after a purchase/restore instead of
    waiting on the (eventually-consistent) webhook. Option A: the RevenueCat app
    user id is the caller's ``app_user_id``, so this needs no extra linking.
    """
    access = await container.entitlement_service.sync_from_provider(user.id)
    return _to_access_response(access)
