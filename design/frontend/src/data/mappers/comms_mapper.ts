/** Maps comms DTOs → NotificationDevice / SupportMessage view-models. */

import { NotificationDevice, SupportMessage } from '@/types/models';
import { DeviceDto, SupportDto } from '@/data/dto/comms_dto';

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
