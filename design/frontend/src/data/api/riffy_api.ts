/**
 * RiffyApi — typed API client consumed by feature hooks.
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
  NextRoundResult,
  NotificationDevice,
  Session,
  StartTaskResult,
  SupportMessage,
  TaskRuntime,
  TranscriptionToken,
  TurnTaskResult,
} from '@/types/models';

import { HttpClient } from './http_client';
import { endpoints } from './endpoints';

// DTOs
import { LinkedUserDto } from '@/data/dto/identity_dto';
import { PublicConfigDto } from '@/data/dto/config_dto';
import { HomeDto } from '@/data/dto/home_dto';
import { CatalogItemDto } from '@/data/dto/catalog_dto';
import { TaskRuntimeDto } from '@/data/dto/task_runtime_dto';
import { CompleteTaskDto, NextRoundDto, StartTaskDto } from '@/data/dto/attempt_dto';
import { TurnTaskDto } from '@/data/dto/roleplay_dto';
import { AccessDto } from '@/data/dto/entitlement_dto';
import { DeviceDto, SupportDto } from '@/data/dto/comms_dto';
import { TranscriptionTokenDto } from '@/data/dto/transcription_dto';

// Mappers
import { mapLinkedUser } from '@/data/mappers/identity_mapper';
import { mapAppConfig } from '@/data/mappers/config_mapper';
import { mapHome } from '@/data/mappers/home_mapper';
import { mapCatalogItem } from '@/data/mappers/catalog_mapper';
import { mapTaskRuntime } from '@/data/mappers/task_runtime_mapper';
import {
  mapCompleteResult,
  mapNextRoundResult,
  mapStartResult,
} from '@/data/mappers/attempt_mapper';
import { mapTurnResult } from '@/data/mappers/roleplay_mapper';
import { mapAccess } from '@/data/mappers/entitlement_mapper';
import {
  mapNotificationDevice,
  mapSupportMessage,
} from '@/data/mappers/comms_mapper';
import { mapTranscriptionToken } from '@/data/mappers/transcription_mapper';

// ---------------------------------------------------------------------------
// Public interface
// ---------------------------------------------------------------------------

export interface RiffyApi {
  /**
   * Finalize onboarding: the single write of the flow. Verifies the Firebase
   * id-token server-side and creates the authenticated user + onboarding row,
   * returning the session.
   */
  completeOnboarding(input: {
    timezone: string;
    trigger: string;
    idToken: string;
    locale?: string;
  }): Promise<Session>;

  /** Fetch the remote app configuration (feature gates, limits, etc.). */
  getConfig(): Promise<AppConfig>;

  /** Fetch the home-screen aggregate (plan + progress + access). */
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
    },
  ): Promise<CompleteTaskResult>;

  /**
   * Advance a multi-turn (roleplay) attempt by one turn. Returns the next AI
   * line + progress; the goal-reaching turn also returns finalized streak state.
   */
  turnAttempt(
    attemptId: string,
    body: { clientTranscript?: string },
  ): Promise<TurnTaskResult>;

  /**
   * Generate the next rep's scenario for a multi-rep (single-shot) attempt.
   * Backs the "Next" button; returns a fresh prompt + the unchanged rep counter.
   */
  nextRound(attemptId: string): Promise<NextRoundResult>;

  /** Mint a short-lived transcription token for the device. */
  mintTranscriptionToken(): Promise<TranscriptionToken>;

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

  /**
   * Force the backend to pull the latest subscription from RevenueCat now and
   * return the fresh access state. Used to reconcile immediately after a
   * purchase/restore instead of waiting on the webhook.
   */
  syncAccess(): Promise<AccessState>;
}

// ---------------------------------------------------------------------------
// Factory
// ---------------------------------------------------------------------------

export function createRiffyApi(http: HttpClient): RiffyApi {
  return {
    async completeOnboarding({ timezone, trigger, idToken, locale }) {
      const dto = await http.post<LinkedUserDto>(endpoints.onboardingComplete, {
        timezone,
        trigger,
        id_token: idToken,
        ...(locale != null ? { locale } : {}),
      });
      return mapLinkedUser(dto);
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
        },
      );
      return mapCompleteResult(dto);
    },

    async turnAttempt(attemptId, body) {
      const dto = await http.post<TurnTaskDto>(endpoints.turnAttempt(attemptId), {
        ...(body.clientTranscript != null
          ? { client_transcript: body.clientTranscript }
          : {}),
      });
      return mapTurnResult(dto);
    },

    async nextRound(attemptId) {
      const dto = await http.post<NextRoundDto>(endpoints.nextRound(attemptId));
      return mapNextRoundResult(dto);
    },

    async mintTranscriptionToken() {
      const dto = await http.post<TranscriptionTokenDto>(
        endpoints.transcriptionTokens,
      );
      return mapTranscriptionToken(dto);
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

    async syncAccess() {
      const dto = await http.post<AccessDto>(endpoints.accessSync);
      return mapAccess(dto);
    },
  };
}
