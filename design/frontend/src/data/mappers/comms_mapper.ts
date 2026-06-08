/** Maps comms DTOs → Reminder / NotificationDevice / SupportMessage view-models. */

import { NotificationDevice, Reminder, SupportMessage } from '@/types/models';
import { DeviceDto, ReminderDto, SupportDto } from '@/data/dto/comms_dto';

export function mapReminder(dto: ReminderDto): Reminder {
  return {
    status: dto.status,
    timingKey: dto.timing_key,
    localTime: dto.local_time,
    timezone: dto.timezone,
  };
}

export function mapNotificationDevice(dto: DeviceDto): NotificationDevice {
  return {
    id: dto.id,
    deviceKey: dto.device_key,
    platform: dto.platform,
    permissionStatus: dto.permission_status,
    pushToken: dto.push_token,
    disabledAt: dto.disabled_at,
  };
}

export function mapSupportMessage(dto: SupportDto): SupportMessage {
  return {
    id: dto.id,
    status: dto.status,
    createdAt: dto.created_at,
  };
}
