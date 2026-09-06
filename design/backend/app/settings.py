from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Pooled connection (Neon PgBouncer endpoint), used by the app at runtime.
    # A harmless placeholder keeps imports working before a real `.env` exists;
    # the engine is lazy and never connects on import.
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/placeholder"

    # Direct/non-pooled connection, used by Alembic migrations.
    database_url_direct: str | None = None

    app_env: str = "development"

    # --- Integrations (real vendor adapters; see app/infrastructure/integrations) ---
    # Firebase: verifies client ID tokens via the Admin SDK.
    firebase_credentials_file: str | None = None  # path to service-account JSON
    firebase_project_id: str | None = None

    # Deepgram: speech-to-text. The main key transcribes; project id is needed to
    # mint short-lived scoped client keys for the live path.
    deepgram_api_key: str | None = None
    deepgram_project_id: str | None = None

    # RevenueCat: subscription source of truth. The secret REST key reads
    # subscribers; the webhook auth value is the Authorization header configured
    # in the RevenueCat dashboard and compared on inbound webhooks.
    revenuecat_api_key: str | None = None
    revenuecat_webhook_auth: str | None = None

    # PostHog: product analytics + experimentation flags.
    posthog_api_key: str | None = None
    posthog_host: str = "https://us.i.posthog.com"

    # LLM (litellm): prompt generation + transcript evaluation. Keys are pushed
    # into the environment for litellm; model strings may target any litellm
    # provider (OpenAI today; `gemini/...`, `anthropic/...`, etc. supported).
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    llm_generator_model: str = "gpt-5.6-sol"
    llm_evaluator_model: str = "gpt-5.6-sol"

    # Per-call bounds for the LLM. Without an explicit timeout the OpenAI SDK
    # waits its 600s (10 min) default read timeout on a stalled response, which
    # surfaces as a frontend stuck on "Setting up your practice…". One retry
    # lets a transient stall recover quickly instead of hanging.
    llm_request_timeout_seconds: float = 30.0
    llm_num_retries: int = 1

    # TTS (OpenAI): spoken prompts. Synthesized eagerly at generate time when a
    # key is present; absent key disables TTS gracefully.
    tts_voice: str = "nova"
    tts_request_timeout_seconds: float = 20.0

    # Lessons: pre-recorded audio explainers hosted as static files on the CDN
    # (Firebase Hosting, which honours HTTP range requests so the client streams
    # and seeks). The lesson engine builds each audio URL as
    # `{lesson_audio_base_url}/{audio_key}.mp3`; no key is ever generated.
    lesson_audio_base_url: str = "https://riffy.pro/audio/lessons"

    # Capgo OTA (self-hosted): the app's @capgo/capacitor-updater checks this
    # backend (POST /v1/ota/check) for new web-layer bundles, so we never use
    # (or pay for) Capgo's cloud. `ota_enabled=False` is the instant kill switch
    # for every installed device — no rebuild, no store release. `ota_pointer_url`
    # is the public URL of the `production.json` written by frontend/deploy_ota.sh;
    # when unset the endpoint always reports "no update".
    ota_enabled: bool = True
    ota_pointer_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
