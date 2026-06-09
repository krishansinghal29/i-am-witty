/** Maps identity DTOs → Session view-model. */

import { Session } from '@/types/models';
import { LinkedUserDto } from '@/data/dto/identity_dto';

export function mapLinkedUser(dto: LinkedUserDto): Session {
  return {
    appUserId: dto.app_user_id,
    status: dto.status,
    firebaseUid: dto.firebase_uid,
    timezone: dto.timezone,
  };
}
