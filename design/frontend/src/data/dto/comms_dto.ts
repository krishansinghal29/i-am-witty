/** Wire shapes for notification devices and support (snake_case). */

export interface DeviceDto {
  id: string;
  device_key: string;
  platform: string;
  permission_status: string;
  push_token: string | null;
  disabled_at: string | null;
}

export interface SupportDto {
  id: string;
  status: string;
  created_at: string;
}

// ---------------------------------------------------------------------------
// Request bodies
// ---------------------------------------------------------------------------

export interface RegisterDeviceRequestDto {
  device_key: string;
  platform: string;
  push_token?: string | null;
  permission_status: string;
  app_version?: string | null;
  release_channel?: string | null;
}

export interface SubmitSupportRequestDto {
  message_text: string;
  source_screen?: string | null;
}
