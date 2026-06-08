/** Maps identity DTOs → Session view-model. */

import { Session } from '@/types/models';
import { GuestSessionDto, LinkedUserDto } from '@/data/dto/identity_dto';

export function mapGuestSession(dto: GuestSessionDto): Session {
  return {
    appUserId: dto.app_user_id,
    status: dto.status,
    sessionToken: dto.session_token,
    firebaseUid: null,
    timezone: dto.timezone,
  };
}

export function mapLinkedUser(dto: LinkedUserDto): Session {
  return {
    appUserId: dto.app_user_id,
    status: dto.status,
    sessionToken: null,
    firebaseUid: dto.firebase_uid,
    timezone: dto.timezone,
  };
}
