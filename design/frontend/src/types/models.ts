/**
 * View-model types for the i-am-witty app.
 *
 * All fields are camelCase, mapped from the backend's snake_case REST contract.
 * Dates/times are kept as ISO strings as returned by JSON serialisation.
 *
 * Domains:
 *   - Session & Auth
 *   - Config & Feature Gates
 *   - Home / Daily Plan
 *   - Catalog & Tasks
 *   - Task Runtime & Execution
 *   - Entitlements & Access
 *   - Notifications
 *   - Support & Utility
 */

// ---------------------------------------------------------------------------
// Session & Auth
// ---------------------------------------------------------------------------

/** The current authenticated app-user session. */
export interface Session {
  appUserId: string;
  status: string;
  firebaseUid: string | null;
  timezone: string;
}

// ---------------------------------------------------------------------------
// Config & Feature Gates
// ---------------------------------------------------------------------------

/** A single feature-flag entry from the remote config. */
export interface FeatureGate {
  featureKey: string;
  defaultEnabled: boolean;
  requiresEntitlement: string | null;
  minAppVersion: string | null;
}

/** Remote app configuration returned by the `/v1/config` endpoint. */
export interface AppConfig {
  values: Record<string, unknown>;
  freeTaskLimit: number;
  featureGates: FeatureGate[];
}

// ---------------------------------------------------------------------------
// Home / Daily Plan
// ---------------------------------------------------------------------------

/** Status of a single item in the user's daily plan. */
export type PlanItemStatus = 'completed' | 'current' | 'missed' | 'upcoming' | string;

/** One task slot inside a daily plan. */
export interface PlanItem {
  id: string;
  taskId: string;
  position: number;
  status: PlanItemStatus;
  currentAttemptId: string | null;
}

/** The user's full daily plan. */
export interface DailyPlan {
  id: string;
  planDate: string;
  status: string;
  items: PlanItem[];
}

/** Aggregated activity progress for the user. */
export interface Progress {
  completedTaskCount: number;
  currentStreakCount: number;
  longestStreakCount: number;
  lastActivityDate: string | null;
}

// ---------------------------------------------------------------------------
// Entitlements & Access
// ---------------------------------------------------------------------------

/** Lifecycle status of a single entitlement. */
export type EntitlementStatus = 'active' | 'expired' | 'in_grace' | string;

/** One entitlement record attached to the user's account. */
export interface Entitlement {
  entitlementKey: string;
  status: EntitlementStatus;
  productId: string | null;
  currentPeriodEndsAt: string | null;
  trialEndsAt: string | null;
}

/** Summary of what the user can access. */
export interface AccessState {
  isRiffyPlus: boolean;
  entitlements?: Entitlement[];
}

// ---------------------------------------------------------------------------
// Home view aggregate
// ---------------------------------------------------------------------------

/** Single response shape returned by the `/v1/home` endpoint. */
export interface HomeView {
  plan: DailyPlan;
  progress: Progress;
  access: AccessState;
  freeLimit: FreeLimit;
}

// ---------------------------------------------------------------------------
// Catalog & Tasks
// ---------------------------------------------------------------------------

/** Whether a task is available on the free tier or requires premium. */
export type TaskAccessTier = 'free' | 'premium' | string;

/** Core task entity. */
export interface Task {
  id: string;
  slug: string;
  title: string;
  description: string | null;
  taskTypeId: string;
  durationSeconds: number | null;
  thumbnailKey: string | null;
  imageKey: string | null;
  accessTier: TaskAccessTier;
  status: string;
  sortOrder: number;
}

/** A task as it appears in the catalog, with access metadata. */
export interface CatalogItem {
  task: Task;
  requiresPremium: boolean;
  isLocked: boolean;
}

/** Describes how a task should be rendered and executed. */
export interface TaskType {
  id: string;
  displayName: string;
  uiSchemaKey: string;
  runtimeEngineKey: string;
}

// ---------------------------------------------------------------------------
// Task Runtime & Execution
// ---------------------------------------------------------------------------

/**
 * The speaker role for a prompt message.
 * Open union — backend may add new roles.
 */
export type PromptRole = 'She' | 'You' | 'Topic' | 'Storyteller' | string;

/** A single message in the task prompt conversation. */
export interface PromptMessage {
  role: PromptRole;
  content: string;
}

/** The full prompt shown/spoken to the user before they start a task. */
export interface Prompt {
  messages: PromptMessage[];
  /** Pre-generated TTS transcript of the prompt, if available. */
  speechText: string | null;
}

/** A CBT / coaching technique assigned for this task attempt. */
export interface AssignedTechnique {
  name: string;
  instruction: string;
  example: string;
}

/**
 * Backend TTS audio played TO the user when the task starts.
 * Corresponds to `audio_base64` / `audio_content_type` flat fields in the
 * backend payload — regrouped here for clarity (mapper handles the conversion).
 */
export interface RuntimeAudio {
  audioBase64: string | null;
  contentType: string | null;
}

/**
 * Opening turn of a multi-turn roleplay attempt. Present only for roleplay
 * task types; `narration` is shown but not spoken, `dialogue` is her first
 * spoken line (also in `prompt`/`audio`), and the counts seed the progress UI.
 */
export interface RolePlayOpening {
  briefHeading: string;
  narration: string;
  dialogue: string;
  targetCount: number;
  landedCount: number;
  appearance: string;
}

/** All data needed to drive a task runtime session in the UI. */
export interface RuntimePayload {
  prompt: Prompt;
  assignedTechnique: AssignedTechnique | null;
  audio: RuntimeAudio;
  avatarImageUrl: string | null;
  roleplay: RolePlayOpening | null;
}

/** Labels for the two feedback tabs shown on the Reflect phase. */
export interface FeedbackTabs {
  feedbackLabel: string;
  sampleAnswerLabel: string;
}

/**
 * Client-renderable labels/limits sourced from the backend `tasks.content`.
 * Drives the runtime shell's prompt label, response instruction, recording
 * limit, and feedback tab copy.
 */
export interface RuntimeContent {
  promptLabel: string;
  responseInstruction: string;
  recordingLimitSeconds: number;
  feedbackTabs: FeedbackTabs;
}

/** Top-level response from the `/v1/tasks/:id/runtime` endpoint. */
export interface TaskRuntime {
  attemptId: string;
  task: Task;
  taskType: TaskType;
  content: RuntimeContent;
  payload: RuntimePayload;
}

/** Free-tier usage gate returned alongside task start/complete responses. */
export interface FreeLimit {
  allowed: boolean;
  shouldPaywall: boolean;
  remaining: number;
  reason: string | null;
}

/** AI evaluation of the user's submitted response. */
export interface EvaluationResult {
  styleLabel: string | null;
  feedbackHtml: string;
  sampleAnswerHtml: string;
  completionMetadata: Record<string, unknown>;
}

/** Current streak data returned after completing a task. */
export interface Streak {
  currentStreak: number;
  longestStreak: number;
  lastQualifiedDate: string;
}

/** Response from the `/v1/tasks/:id/complete` endpoint. */
export interface CompleteTaskResult {
  attemptId: string;
  status: string;
  result: EvaluationResult;
  freeLimit: FreeLimit;
  streak: Streak;
}

/** Response from the `/v1/tasks/:id/start` endpoint. */
export interface StartTaskResult {
  attemptId: string;
  taskId: string;
  status: string;
  freeLimit: FreeLimit;
}

/** One advance of a roleplay conversation (from `/v1/attempts/:id/turn`). */
export interface RolePlayTurn {
  narration: string;
  dialogue: string;
  landed: boolean;
  intensity: string;
  landedCount: number;
  targetCount: number;
  isComplete: boolean;
  /** A model misinterpretation of the line the user just answered (coaching). */
  sampleAnswer: string;
  audio: RuntimeAudio;
}

/** Response from the `/v1/attempts/:id/turn` endpoint. */
export interface TurnTaskResult {
  attemptId: string;
  status: string;
  turn: RolePlayTurn;
  freeLimit: FreeLimit;
  /** Populated only on the goal-reaching turn that finalizes the attempt. */
  streak: Streak | null;
}

// ---------------------------------------------------------------------------
// Notifications
// ---------------------------------------------------------------------------

/** A registered device for push notifications. */
export interface NotificationDevice {
  id: string;
  deviceKey: string;
  platform: string;
  permissionStatus: string;
  pushToken: string | null;
  disabledAt: string | null;
}

// ---------------------------------------------------------------------------
// Support & Utility
// ---------------------------------------------------------------------------

/** A submitted in-app support message. */
export interface SupportMessage {
  id: string;
  status: string;
  createdAt: string;
}

/** Short-lived token for the device transcription provider. */
export interface TranscriptionToken {
  token: string;
  expiresAt: string | null;
  provider: string;
  extra: Record<string, unknown>;
}
