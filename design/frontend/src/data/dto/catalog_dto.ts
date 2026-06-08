/** Wire shapes for catalog / task endpoints (snake_case). */

export interface TaskDto {
  id: string;
  slug: string;
  title: string;
  description: string | null;
  task_type_id: string;
  duration_seconds: number | null;
  thumbnail_key: string | null;
  image_key: string | null;
  access_tier: string;
  status: string;
  sort_order: number;
}

export interface CatalogItemDto {
  task: TaskDto;
  requires_premium: boolean;
  is_locked: boolean;
}
