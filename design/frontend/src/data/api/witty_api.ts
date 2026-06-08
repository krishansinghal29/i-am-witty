/**
 * WittyApi — typed API client consumed by feature hooks.
 *
 * All methods accept camelCase inputs, call the HTTP client with snake_case
 * request bodies, and return camelCase view-models (mapped from DTOs).
 */

import {
  AccessState,
  AppConfig,
  CatalogItem,
  CompleteTaskResult,
  HomeView,
  NotificationDevice,
  OnboardingState,
  Reminder,
  Session,
  StartTaskResult,
  SupportMessage,
  TaskRuntime,
  TranscriptionToken,
} from '@/types/models';

import { HttpClient } from './http_client';
import { endpoints } from './endpoints';

// DTOs
import { GuestSessionDto, LinkedUserDto } from '@/data/dto/identity_dto';
import { OnboardingStateDto } from '@/data/dto/onboarding_dto';
import { PublicConfigDto } from '@/data/dto/config_dto';
import { HomeDto } from '@/data/dto/home_dto';
import { CatalogItemDto } from '@/data/dto/catalog_dto';
import { TaskRuntimeDto } from '@/data/dto/task_runtime_dto';
import { CompleteTaskDto, StartTaskDto } from '@/data/dto/attempt_dto';
import { AccessDto } from '@/data/dto/entitlement_dto';
import { DeviceDto, ReminderDto, SupportDto } from '@/data/dto/comms_dto';
import { TranscriptionTokenDto } from '@/data/dto/transcription_dto';

// Mappers
import { mapGuestSession, mapLinkedUser } from '@/data/mappers/identity_mapper';
import { mapOnboardingState } from '@/data/mappers/onboarding_mapper';
import { mapAppConfig } from '@/data/mappers/config_mapper';
import { mapHome } from '@/data/mappers/home_mapper';
import { mapCatalogItem } from '@/data/mappers/catalog_mapper';
import { mapTaskRuntime } from '@/data/mappers/task_runtime_mapper';
import { mapCompleteResult, mapStartResult } from '@/data/mappers/attempt_mapper';
import { mapAccess } from '@/data/mappers/entitlement_mapper';
import {
  mapNotificationDevice,
  mapReminder,
  mapSupportMessage,
} from '@/data/mappers/comms_mapper';
import { mapTranscriptionToken } from '@/data/mappers/transcription_mapper';

// ---------------------------------------------------------------------------
// Public interface
// ---------------------------------------------------------------------------

export interface WittyApi {
  /** Create an anonymous guest session. */
  createGuestSession(input: { timezone: string; locale?: string }): Promise<Session>;

  /** Link the current guest session to a Firebase-authenticated account. */
  linkAccount(idToken: string): Promise<Session>;

  /** Fetch the current onboarding state. */
  getOnboarding(): Promise<OnboardingState>;

  /** Save the user's selected trigger and advance onboarding. */
  saveTrigger(trigger: string): Promise<OnboardingState>;

  /** Fetch the remote app configuration (feature gates, limits, etc.). */
  getConfig(): Promise<AppConfig>;

  /** Fetch the home-screen aggregate (plan + progress + access + onboarding). */
  getHome(): Promise<HomeView>;

  /** Fetch the full task catalog. */
  getCatalog(): Promise<CatalogItem[]>;

  /**
   * Fetch the runtime payload needed to play a task.
   * Defaults to source `'practice_library'` when not provided.
   */
  getTaskRuntime(
    taskId: string,
    opts?: { source?: string; dailyPlanItemId?: string },
  ): Promise<TaskRuntime>;

  /** Record that the user has started a task attempt. */
  startTask(
    taskId: string,
    opts?: { source?: string; dailyPlanItemId?: string },
  ): Promise<StartTaskResult>;

  /** Submit the user's completed attempt for evaluation. */
  completeTask(
    attemptId: string,
    body: {
      clientTranscript?: string;
      audioBase64?: string;
      contentType?: string;
      language?: string;
      stageResponses?: { position: number; transcript: string }[];
    },
  ): Promise<CompleteTaskResult>;

  /** Mint a short-lived transcription token for the device. */
  mintTranscriptionToken(): Promise<TranscriptionToken>;

  /** Fetch the user's current reminder preference (null if none set). */
  getReminder(): Promise<Reminder | null>;

  /** Create or replace the user's reminder preference. */
  saveReminder(input: {
    status: string;
    timingKey?: string | null;
    localTime?: string | null;
    timezone: string;
  }): Promise<Reminder>;

  /** Remove the user's reminder preference. */
  clearReminder(): Promise<void>;

  /** Register (or update) a device for push notifications. */
  registerDevice(input: {
    deviceKey: string;
    platform: string;
    pushToken?: string | null;
    permissionStatus: string;
    appVersion?: string | null;
    releaseChannel?: string | null;
  }): Promise<NotificationDevice>;

  /** Submit an in-app support message. */
  submitSupport(input: {
    messageText: string;
    sourceScreen?: string | null;
  }): Promise<SupportMessage>;

  /** Fetch the user's current access / entitlement state. */
  getAccess(): Promise<AccessState>;
}

// ---------------------------------------------------------------------------
// Factory
// ---------------------------------------------------------------------------

export function createWittyApi(http: HttpClient): WittyApi {
  return {
    async createGuestSession({ timezone, locale }) {
      const dto = await http.post<GuestSessionDto>(endpoints.guestSessions, {
        timezone,
        ...(locale != null ? { locale } : {}),
      });
      return mapGuestSession(dto);
    },

    async linkAccount(idToken) {
      const dto = await http.post<LinkedUserDto>(endpoints.authLink, {
        id_token: idToken,
      });
      return mapLinkedUser(dto);
    },

    async getOnboarding() {
      const dto = await http.get<OnboardingStateDto>(endpoints.onboarding);
      return mapOnboardingState(dto);
    },

    async saveTrigger(trigger) {
      const dto = await http.patch<OnboardingStateDto>(endpoints.onboarding, {
        trigger,
      });
      return mapOnboardingState(dto);
    },

    async getConfig() {
      const dto = await http.get<PublicConfigDto>(endpoints.config);
      return mapAppConfig(dto);
    },

    async getHome() {
      const dto = await http.get<HomeDto>(endpoints.home);
      return mapHome(dto);
    },

    async getCatalog() {
      const dtos = await http.get<CatalogItemDto[]>(endpoints.catalog);
      return dtos.map(mapCatalogItem);
    },

    async getTaskRuntime(taskId, opts) {
      const source = opts?.source ?? 'practice_library';
      const dto = await http.post<TaskRuntimeDto>(endpoints.taskRuntime(taskId), {
        source,
        ...(opts?.dailyPlanItemId != null
          ? { daily_plan_item_id: opts.dailyPlanItemId }
          : {}),
      });
      return mapTaskRuntime(dto);
    },

    async startTask(taskId, opts) {
      const source = opts?.source ?? 'practice_library';
      const dto = await http.post<StartTaskDto>(endpoints.startTask(taskId), {
        source,
        ...(opts?.dailyPlanItemId != null
          ? { daily_plan_item_id: opts.dailyPlanItemId }
          : {}),
      });
      return mapStartResult(dto);
    },

    async completeTask(attemptId, body) {
      const dto = await http.post<CompleteTaskDto>(
        endpoints.completeTask(attemptId),
        {
          ...(body.clientTranscript != null
            ? { client_transcript: body.clientTranscript }
            : {}),
          ...(body.audioBase64 != null
            ? { audio_base64: body.audioBase64 }
            : {}),
          ...(body.contentType != null
            ? { content_type: body.contentType }
            : {}),
          ...(body.language != null ? { language: body.language } : {}),
          stage_responses: body.stageResponses ?? [],
        },
      );
      return mapCompleteResult(dto);
    },

    async mintTranscriptionToken() {
      const dto = await http.post<TranscriptionTokenDto>(
        endpoints.transcriptionTokens,
      );
      return mapTranscriptionToken(dto);
    },

    async getReminder() {
      try {
        const dto = await http.get<ReminderDto>(endpoints.reminders);
        return mapReminder(dto);
      } catch (e: unknown) {
        // 404 means no reminder configured — return null rather than throw
        if (
          e != null &&
          typeof e === 'object' &&
          'status' in e &&
          (e as { status?: number }).status === 404
        ) {
          return null;
        }
        throw e;
      }
    },

    async saveReminder(input) {
      const dto = await http.put<ReminderDto>(endpoints.reminders, {
        status: input.status,
        ...(input.timingKey != null ? { timing_key: input.timingKey } : {}),
        ...(input.localTime != null ? { local_time: input.localTime } : {}),
        timezone: input.timezone,
      });
      return mapReminder(dto);
    },

    async clearReminder() {
      await http.del(endpoints.reminders);
    },

    async registerDevice(input) {
      const dto = await http.post<DeviceDto>(endpoints.notificationDevices, {
        device_key: input.deviceKey,
        platform: input.platform,
        ...(input.pushToken != null ? { push_token: input.pushToken } : {}),
        permission_status: input.permissionStatus,
        ...(input.appVersion != null ? { app_version: input.appVersion } : {}),
        ...(input.releaseChannel != null
          ? { release_channel: input.releaseChannel }
          : {}),
      });
      return mapNotificationDevice(dto);
    },

    async submitSupport(input) {
      const dto = await http.post<SupportDto>(endpoints.supportMessages, {
        message_text: input.messageText,
        ...(input.sourceScreen != null
          ? { source_screen: input.sourceScreen }
          : {}),
      });
      return mapSupportMessage(dto);
    },

    async getAccess() {
      const dto = await http.get<AccessDto>(endpoints.access);
      return mapAccess(dto);
    },
  };
}
