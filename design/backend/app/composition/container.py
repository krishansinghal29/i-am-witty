from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.app_config_service import AppConfigService
from app.application.daily_plan_service import DailyPlanService
from app.application.entitlement_service import EntitlementService
from app.application.identity_service import IdentityService
from app.application.notification_service import NotificationService
from app.application.progress_service import ProgressService
from app.application.support_service import SupportService
from app.application.task_attempt_service import TaskAttemptService
from app.application.task_catalog_service import TaskCatalogService
from app.application.task_runtime_service import TaskRuntimeService
from app.application.transcription_service import TranscriptionService
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.integrations.deepgram_transcription_client import (
    DeepgramTranscriptionProvider,
)
from app.infrastructure.integrations.firebase_auth_verifier import (
    FirebaseAuthTokenVerifier,
)
from app.infrastructure.integrations.litellm_provider import LiteLlmProvider
from app.infrastructure.integrations.openai_tts_client import OpenAiTtsProvider
from app.infrastructure.integrations.posthog_client import PostHogAnalytics
from app.infrastructure.integrations.revenue_cat_client import (
    RevenueCatSubscriptionProvider,
)
from app.infrastructure.repositories.pg_config_repository import PgConfigRepository
from app.infrastructure.repositories.pg_daily_plan_repository import (
    PgDailyPlanRepository,
)
from app.infrastructure.repositories.pg_entitlement_repository import (
    PgEntitlementRepository,
)
from app.infrastructure.repositories.pg_notification_device_repository import (
    PgNotificationDeviceRepository,
)
from app.infrastructure.repositories.pg_onboarding_repository import (
    PgOnboardingRepository,
)
from app.infrastructure.repositories.pg_profile_repository import PgProfileRepository
from app.infrastructure.repositories.pg_progress_repository import PgProgressRepository
from app.infrastructure.repositories.pg_support_repository import PgSupportRepository
from app.infrastructure.repositories.pg_task_attempt_repository import (
    PgTaskAttemptRepository,
)
from app.infrastructure.repositories.pg_task_repository import PgTaskRepository
from app.infrastructure.repositories.pg_usage_repository import PgUsageRepository
from app.infrastructure.repositories.pg_user_repository import PgUserRepository
from app.infrastructure.runtime.engine_resolver import TaskRuntimeEngineResolver
from app.infrastructure.runtime.lesson_engine import LessonTaskEngine
from app.infrastructure.runtime.roleplay_engine import RoleplayTaskEngine
from app.infrastructure.runtime.voice_prompt_engine import VoicePromptTaskEngine
from app.ports.integrations.analytics import Analytics
from app.ports.integrations.auth_token_verifier import AuthTokenVerifier
from app.ports.integrations.subscription_provider import SubscriptionProvider
from app.ports.integrations.transcription_provider import TranscriptionProvider
from app.settings import Settings


@dataclass(frozen=True)
class Integrations:
    """Process-wide, stateless integration clients built once at startup."""

    auth_verifier: AuthTokenVerifier
    subscription_provider: SubscriptionProvider
    analytics: Analytics
    transcription_provider: TranscriptionProvider
    runtime_engines: TaskRuntimeEngineResolver


def build_integrations(settings: Settings) -> Integrations:
    """Build the integration clients from settings.

    Real vendor adapters for auth (Firebase), subscriptions (RevenueCat),
    analytics (PostHog), transcription (Deepgram), and the LLM-backed voice
    prompt engine (litellm generation/evaluation + OpenAI TTS); each lazily
    initializes so this never touches credentials/network at startup.
    """
    llm = LiteLlmProvider(settings)
    tts = OpenAiTtsProvider(settings)
    voice_prompt_engine = VoicePromptTaskEngine(
        llm,
        tts,
        generator_model=settings.llm_generator_model,
        evaluator_model=settings.llm_evaluator_model,
        tts_voice=settings.tts_voice,
    )
    roleplay_engine = RoleplayTaskEngine(
        llm,
        tts,
        generator_model=settings.llm_generator_model,
        tts_voice=settings.tts_voice,
    )
    # Lessons need no LLM/TTS — just the hosted-audio base URL and the committed
    # caption resources read from disk.
    lesson_engine = LessonTaskEngine(audio_base_url=settings.lesson_audio_base_url)
    runtime_engines = TaskRuntimeEngineResolver(
        {
            "voice_prompt_v1": voice_prompt_engine,
            "roleplay_v1": roleplay_engine,
            "lesson_v1": lesson_engine,
        }
    )
    return Integrations(
        auth_verifier=FirebaseAuthTokenVerifier(settings),
        subscription_provider=RevenueCatSubscriptionProvider(settings),
        analytics=PostHogAnalytics(settings),
        transcription_provider=DeepgramTranscriptionProvider(settings),
        runtime_engines=runtime_engines,
    )


class RequestContainer:
    """Request-scoped services bound to one ``AsyncSession``.

    Every repository shares the single session, so all writes in a request go
    through one unit of work and commit atomically.
    """

    def __init__(self, session: AsyncSession, integrations: Integrations) -> None:
        self.integrations = integrations

        uow = SqlAlchemyUnitOfWork(session)

        users = PgUserRepository(session)
        profiles = PgProfileRepository(session)
        onboarding = PgOnboardingRepository(session)
        tasks = PgTaskRepository(session)
        plans = PgDailyPlanRepository(session)
        attempts = PgTaskAttemptRepository(session)
        progress = PgProgressRepository(session)
        usage = PgUsageRepository(session)
        entitlements = PgEntitlementRepository(session)
        devices = PgNotificationDeviceRepository(session)
        support = PgSupportRepository(session)
        config = PgConfigRepository(session)

        self.transcription_service = TranscriptionService(
            integrations.transcription_provider
        )
        self.identity_service = IdentityService(
            users, onboarding, integrations.auth_verifier, uow
        )
        self.task_catalog_service = TaskCatalogService(tasks, entitlements)
        self.daily_plan_service = DailyPlanService(users, plans, tasks, uow)
        self.task_attempt_service = TaskAttemptService(
            users,
            tasks,
            attempts,
            plans,
            progress,
            usage,
            entitlements,
            config,
            self.transcription_service,
            integrations.runtime_engines,
            uow,
        )
        self.task_runtime_service = TaskRuntimeService(
            self.task_attempt_service, integrations.runtime_engines, attempts, uow
        )
        self.progress_service = ProgressService(users, progress)
        self.entitlement_service = EntitlementService(
            entitlements, users, integrations.subscription_provider, uow
        )
        self.notification_service = NotificationService(devices, uow)
        self.support_service = SupportService(support, uow)
        self.app_config_service = AppConfigService(config)
