/** Maps Recall DTOs → RecallSession / RecallOutlook view-models. */

import type {
  RecallCard,
  RecallCheckin,
  RecallCheckinResult,
  RecallOutlook,
  RecallSeenResult,
  RecallSession,
} from '@/types/models';
import type {
  RecallCardDto,
  RecallCheckinDto,
  RecallCheckinResultDto,
  RecallOutlookDto,
  RecallSeenDto,
  RecallSessionDto,
} from '@/data/dto/recall_dto';

export function mapRecallCheckin(dto: RecallCheckinDto): RecallCheckin {
  return {
    itemId: dto.item_id,
    title: dto.title,
    question: dto.question,
    why: dto.why,
    today: dto.today,
    streak: dto.streak,
    last7: dto.last7.map((day) => ({ date: day.date, done: day.done })),
  };
}

/**
 * Returns null for a kind this build doesn't know (or a card missing its
 * payload), so an older app bundle skips new card kinds instead of crashing.
 */
export function mapRecallCard(dto: RecallCardDto): RecallCard | null {
  const base = { itemId: dto.item_id, isNew: dto.is_new };
  if (dto.kind === 'line' && dto.line) {
    return {
      ...base,
      kind: 'line',
      line: {
        cueText: dto.line.cue_text,
        cueType: dto.line.cue_type,
        hint: dto.line.hint,
        text: dto.line.text,
        deliveryNote: dto.line.delivery_note,
        position: dto.line.position,
        cueLineCount: dto.line.cue_line_count,
      },
    };
  }
  if (dto.kind === 'concept' && dto.concept) {
    return {
      ...base,
      kind: 'concept',
      concept: {
        name: dto.concept.name,
        definition: dto.concept.definition,
        scenario: dto.concept.scenario,
        scenarioNumber: dto.concept.scenario_number,
        scenarioCount: dto.concept.scenario_count,
      },
    };
  }
  if (dto.kind === 'routine' && dto.routine) {
    return {
      ...base,
      kind: 'routine',
      routine: { name: dto.routine.name, steps: dto.routine.steps },
    };
  }
  return null;
}

export function mapRecallSession(dto: RecallSessionDto): RecallSession {
  return {
    localDate: dto.local_date,
    checkins: dto.checkins.map(mapRecallCheckin),
    cards: dto.cards
      .map(mapRecallCard)
      .filter((card): card is RecallCard => card !== null),
    counts: {
      due: dto.counts.due,
      new: dto.counts.new,
      line: dto.counts.line,
      concept: dto.counts.concept,
      routine: dto.counts.routine,
    },
  };
}

export function mapRecallOutlook(dto: RecallOutlookDto): RecallOutlook {
  return { dueTomorrow: dto.due_tomorrow, newWaiting: dto.new_waiting };
}

export function mapRecallSeen(dto: RecallSeenDto): RecallSeenResult {
  return { itemId: dto.item_id, seenCount: dto.seen_count, dueOn: dto.due_on };
}

export function mapRecallCheckinResult(
  dto: RecallCheckinResultDto,
): RecallCheckinResult {
  return { itemId: dto.item_id, done: dto.done, streak: dto.streak };
}
