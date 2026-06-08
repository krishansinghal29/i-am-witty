/**
 * Normalised application error — the single error shape used across the whole app.
 */

export type AppErrorCode =
  | 'network'
  | 'unauthorized'
  | 'forbidden'
  | 'not_found'
  | 'paywall_required'
  | 'conflict'
  | 'validation'
  | 'server'
  | 'unknown';

/** Friendly default messages shown to users, keyed by error code. */
const DEFAULT_USER_MESSAGES: Record<AppErrorCode, string> = {
  network: 'A network error occurred. Please check your connection and try again.',
  unauthorized: 'You need to sign in to continue.',
  forbidden: 'You don\'t have permission to do that.',
  not_found: 'The requested resource could not be found.',
  paywall_required: 'This feature requires a Witty+ subscription.',
  conflict: 'There was a conflict with your request. Please try again.',
  validation: 'Some of the information you provided is invalid.',
  server: 'Something went wrong on our end. Please try again shortly.',
  unknown: 'An unexpected error occurred.',
};

interface AppErrorOptions {
  code: AppErrorCode;
  /** Internal/developer message (passed to Error base). Defaults to userMessage. */
  message?: string;
  /** Safe string to display to the end-user. */
  userMessage?: string;
  /** HTTP status code, if applicable. */
  status?: number;
  /** Machine-readable reason string from backend `{ "error": reason }`. */
  reason?: string;
  /** Original caught value for debugging. */
  cause?: unknown;
}

export class AppError extends Error {
  readonly code: AppErrorCode;
  readonly userMessage: string;
  readonly status?: number;
  readonly reason?: string;
  readonly cause?: unknown;

  constructor(options: AppErrorOptions) {
    const userMessage =
      options.userMessage ?? DEFAULT_USER_MESSAGES[options.code];
    super(options.message ?? userMessage);
    this.name = 'AppError';
    this.code = options.code;
    this.userMessage = userMessage;
    this.status = options.status;
    this.reason = options.reason;
    this.cause = options.cause;

    // Restore prototype chain for instanceof checks in transpiled environments.
    Object.setPrototypeOf(this, new.target.prototype);
  }

  /**
   * Pass through existing `AppError` instances; wrap anything else as `unknown`.
   */
  static from(e: unknown): AppError {
    if (e instanceof AppError) return e;
    const message =
      e instanceof Error ? e.message : typeof e === 'string' ? e : undefined;
    return new AppError({ code: 'unknown', message, cause: e });
  }

  /**
   * Construct an `AppError` from an HTTP status code and parsed response body.
   * Reads `body.error` (string) as the machine reason when available.
   */
  static fromHttp(status: number, body: unknown): AppError {
    let code: AppErrorCode;
    if (status === 401) code = 'unauthorized';
    else if (status === 402) code = 'paywall_required';
    else if (status === 403) code = 'forbidden';
    else if (status === 404) code = 'not_found';
    else if (status === 409) code = 'conflict';
    else if (status === 422) code = 'validation';
    else if (status >= 500) code = 'server';
    else code = 'unknown';

    const reason =
      body !== null &&
      typeof body === 'object' &&
      'error' in body &&
      typeof (body as Record<string, unknown>)['error'] === 'string'
        ? (body as Record<string, string>)['error']
        : undefined;

    return new AppError({ code, status, reason });
  }
}
