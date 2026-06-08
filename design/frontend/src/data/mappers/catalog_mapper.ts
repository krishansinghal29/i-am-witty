/** Maps catalog DTOs → Task / CatalogItem view-models. */

import { CatalogItem, Task } from '@/types/models';
import { CatalogItemDto, TaskDto } from '@/data/dto/catalog_dto';

export function mapTask(dto: TaskDto): Task {
  return {
    id: dto.id,
    slug: dto.slug,
    title: dto.title,
    description: dto.description,
    taskTypeId: dto.task_type_id,
    durationSeconds: dto.duration_seconds,
    thumbnailKey: dto.thumbnail_key,
    imageKey: dto.image_key,
    accessTier: dto.access_tier,
    status: dto.status,
    sortOrder: dto.sort_order,
  };
}

export function mapCatalogItem(dto: CatalogItemDto): CatalogItem {
  return {
    task: mapTask(dto.task),
    requiresPremium: dto.requires_premium,
    isLocked: dto.is_locked,
  };
}
