# i-am-witty Trimmed Task Runtime Context

Source: condensed from `design/extra/tasks.md`.

Use this document when an implementation agent needs compact context for the task runtime model. It intentionally includes only one representative task for each current task type. Use `design/extra/tasks.md` when adding or migrating the rest of the exercise catalog.

## Core Decision

Current voice exercises use three runtime task types:

| Task type id | UI schema key | Runtime engine key | Representative task |
| --- | --- | --- | --- |
| `voice_single_prompt` | `voice_single_prompt_v1` | `voice_prompt_v1` | `misinterpretation-techniques` |
| `voice_dialogue_prompt` | `voice_dialogue_prompt_v1` | `voice_prompt_v1` | `question-answer-tease` |
| `voice_scaffolded_prompt` | `voice_scaffolded_prompt_v1` | `voice_prompt_v1` | `push-pull` |

Use task types for frontend/runtime interaction shape, not product categories. Product groupings such as sprint, improv, calm, and story should live in task metadata or a future category table.

## Data Model Split

`task_types` define shared interaction structure:
- `id`
- `ui_schema_key`
- `runtime_engine_key`
- shared type metadata

`tasks.content` is client-renderable config:
- title/description copy
- prompt label
- expected prompt roles
- response instruction
- recording limit
- assigned technique mode
- scaffold stages

`tasks.runtime_config` is backend runtime config:
- stable `backend_key`
- prompt bundle key
- generator strategy
- generated output shape
- evaluator strategy
- optional assigned technique strategy

## Shared Runtime Flow

1. Client requests runtime for a task.
2. Backend checks access and creates or resumes a `task_attempt`.
3. Backend generates prompt data using `tasks.runtime_config`.
4. Client renders the prompt and optional TTS/avatar.
5. Client records the user's spoken response, or accepts a typed response ("one line is plenty").
6. Client submits the transcript and optional audio metadata.
7. Backend evaluates the transcript.
8. Backend completes the attempt and updates progress, daily usage, plan item status, and streak state.

## Runtime Payload Shape

All current voice task types should use one generated runtime payload shape. Optional sections vary by task type.

```json
{
  "attempt_id": "uuid",
  "task": {
    "id": "uuid",
    "slug": "push-pull",
    "title": "Push/Pull",
    "task_type_id": "voice_scaffolded_prompt",
    "ui_schema_key": "voice_scaffolded_prompt_v1",
    "duration_seconds": 30,
    "thumbnail_key": "push-pull",
    "image_key": "push-pull"
  },
  "content": {
    "prompt_label": "Scenario",
    "response_instruction": "Build a push, a pull, then combine them.",
    "recording_limit_seconds": 30,
    "feedback_tabs": {
      "feedback_label": "Feedback",
      "sample_answer_label": "Better Way"
    }
  },
  "prompt": {
    "messages": [
      {
        "role": "She",
        "content": "She laughs at her own joke before anyone else reacts."
      }
    ],
    "speech_text": "She laughs at her own joke before anyone else reacts."
  },
  "assigned_technique": null,
  "scaffold_stages": [],
  "audio": {
    "audio_base64": null,
    "content_type": null
  },
  "avatar": {
    "image_url": null
  }
}
```

## Completion Request Shape

```json
{
  "attempt_id": "uuid",
  "task_id": "uuid",
  "prompt": {
    "messages": [
      {
        "role": "She",
        "content": "She laughs at her own joke before anyone else reacts."
      }
    ]
  },
  "transcript": "You are way too proud of that joke, which is annoying because it was actually funny.",
  "audio_metadata": {
    "audio_base64": "optional-base64",
    "content_type": "audio/webm",
    "duration_seconds": 12,
    "word_count": 17
  },
  "assigned_technique": null,
  "stage_responses": []
}
```

For scaffolded tasks, earlier stage responses may be omitted in the first implementation. Only the final stage must be evaluated.

## Completion Response Shape

```json
{
  "success": true,
  "attempt_id": "uuid",
  "status": "completed",
  "style_label": "Quick Wit",
  "feedback_html": "<b>What Landed</b><br>...",
  "sample_answer_html": "Example 1<br><br>Example 2<br><br>Example 3",
  "completion_metadata": {
    "exercise_key": "pushPull",
    "evaluator_version": "push_pull_v1",
    "assigned_technique_name": null
  },
  "progress_delta": {
    "completed_task_count": 1,
    "free_tasks_completed_today": 1,
    "streak_qualified": true
  }
}
```

## Evaluation Output Contract

Every current voice exercise returns:
- `feedback_html`: four-section HTML feedback with `What Landed`, `The Trap`, `Level Up`, and `Mindset Shift`.
- `sample_answer_html`: three better or alternative responses separated by `<br><br>`.
- `style_label` (optional): a short, playful label for the variable-reward celebration (e.g. `Quick Wit`); may be null for tasks that do not classify style.

`first-unusual-thing` is the only current special sample-answer format in the full catalog. It breaks each sample answer into `Ordinary detail`, `Unusual thing`, and `Association`.

## Prompt Message Roles

Supported roles:

| Role | Meaning |
| --- | --- |
| `She` | A sentence, statement, premise, scenario, criticism, or conversational prompt from the other person. |
| `You` | The user's prior line in a generated dialogue setup. |
| `Topic` | A topic to take a strong stance on. |
| `Storyteller` | A personal story or anecdote to respond to. |

The client should render roles as speaker labels.

## Task Type 1: `voice_single_prompt`

Use for one generated prompt, one spoken response, and one evaluation.

Representative task: `misinterpretation-techniques`.

Why this representative is useful:
- It uses the same UI shell as plain single-prompt tasks.
- It also demonstrates optional assigned technique data.
- Simpler single-prompt tasks can set `assigned_technique_mode` to `none`.

Task seed:

```json
{
  "slug": "misinterpretation-techniques",
  "title": "Misinterpretation: Techniques",
  "description": "Apply a specific misinterpretation technique to an ordinary sentence.",
  "task_type_id": "voice_single_prompt",
  "duration_seconds": 30,
  "content": {
    "exercise_key": "misinterpretationTechniques",
    "prompt_label": "Tease/Statement",
    "prompt_roles": ["She"],
    "response_instruction": "Use the assigned technique to misread the sentence.",
    "recording_limit_seconds": 30,
    "assigned_technique_mode": "runtime_generated",
    "scaffold_stages": [],
    "feedback_tabs": {
      "feedback_label": "Feedback",
      "sample_answer_label": "Better Way"
    }
  },
  "runtime_config": {
    "backend_key": "misinterpretationTechniques",
    "prompt_bundle_key": "misinterpretation_techniques_v1",
    "generator": {
      "strategy": "verb_seed",
      "output_shape": "single_message",
      "message_role": "She"
    },
    "assigned_technique": {
      "strategy": "random_choice",
      "source": "misinterpretation_techniques"
    },
    "evaluator": {
      "strategy": "transcript_feedback",
      "criteria": ["technique_match", "litmus_test", "commitment", "fit", "brevity"]
    }
  }
}
```

Generated input:
- One message with role `She`.
- One ordinary sentence using a random verb and one pronoun from `I`, `you`, or `we`.
- One assigned technique returned as runtime data.

Assigned technique shape:

```json
{
  "name": "Literal Trap",
  "instruction": "Respond as if it is literally, physically happening.",
  "example": "\"I might die tonight\" -> \"Should I call someone, or are you handling the arrangements?\""
}
```

Expected response:
- Apply the assigned technique.
- Misinterpret the original sentence through that technique.
- Commit without explaining the joke.

Evaluation:
- First check technique match.
- Then apply the misinterpretation litmus test.
- Check commitment, fit, and brevity.

## Task Type 2: `voice_dialogue_prompt`

Use when generated input has multiple speaker messages but still expects one spoken response.

Representative task: `question-answer-tease`.

Task seed:

```json
{
  "slug": "question-answer-tease",
  "title": "Question Answer Tease",
  "description": "Turn a direct answer into a playful tease.",
  "task_type_id": "voice_dialogue_prompt",
  "duration_seconds": 30,
  "content": {
    "exercise_key": "questionAnswerTease",
    "prompt_label": "Question",
    "prompt_roles": ["You", "She"],
    "response_instruction": "Tease her answer playfully without insulting or interviewing.",
    "recording_limit_seconds": 30,
    "assigned_technique_mode": "none",
    "scaffold_stages": [],
    "feedback_tabs": {
      "feedback_label": "Feedback",
      "sample_answer_label": "Better Way"
    }
  },
  "runtime_config": {
    "backend_key": "questionAnswerTease",
    "prompt_bundle_key": "question_answer_tease_v1",
    "generator": {
      "strategy": "creative_prompt",
      "output_shape": "dialogue_two_message",
      "message_roles": ["You", "She"]
    },
    "evaluator": {
      "strategy": "transcript_feedback",
      "criteria": ["frame", "tone", "specificity", "brevity"]
    }
  }
}
```

Generated input:
- Exactly two messages.
- First message role: `You`.
- Second message role: `She`.
- The first message is a simple question from the user.
- The second message is a realistic answer from the other person.

Expected response:
- Tease the answer playfully.
- Reference the specific answer.
- Avoid validating, asking another question, insulting, or trying too hard.

Evaluation:
- Check whether the user leads the vibe.
- Check playful tone without meanness.
- Check specificity and brevity.

## Task Type 3: `voice_scaffolded_prompt`

Use when the user needs guided rehearsal stages before the final evaluated response.

Representative task: `push-pull`.

Task seed:

```json
{
  "slug": "push-pull",
  "title": "Push/Pull",
  "description": "Balance genuine interest with playful challenge.",
  "task_type_id": "voice_scaffolded_prompt",
  "duration_seconds": 30,
  "content": {
    "exercise_key": "pushPull",
    "prompt_label": "Scenario",
    "prompt_roles": ["She"],
    "response_instruction": "Build a push, a pull, then combine them.",
    "recording_limit_seconds": 30,
    "assigned_technique_mode": "none",
    "scaffold_stages": [
      {
        "position": 1,
        "label": "Step 1 of 3",
        "title": "Push",
        "instruction": "Say just the push: one sentence, no softening.",
        "is_final_submission": false
      },
      {
        "position": 2,
        "label": "Step 2 of 3",
        "title": "Pull",
        "instruction": "Say just the genuine compliment: no irony.",
        "is_final_submission": false
      },
      {
        "position": 3,
        "label": "Step 3 of 3",
        "title": "Combine",
        "instruction": "Combine them into one push-pull line.",
        "is_final_submission": true
      }
    ],
    "feedback_tabs": {
      "feedback_label": "Feedback",
      "sample_answer_label": "Better Way"
    }
  },
  "runtime_config": {
    "backend_key": "pushPull",
    "prompt_bundle_key": "push_pull_v1",
    "generator": {
      "strategy": "weighted_seed",
      "output_shape": "single_message",
      "message_role": "She"
    },
    "evaluator": {
      "strategy": "transcript_feedback",
      "evaluate_stage": "final",
      "criteria": ["both_sides_present", "trivial_push", "genuine_pull", "tension", "brevity", "naturalness"]
    }
  }
}
```

Generated input:
- One message with role `She`.
- One observable scenario about a woman: something she is wearing, doing, saying, or how she carries herself.

Expected response:
- Stage 1: say only the push.
- Stage 2: say only the pull.
- Stage 3: combine them into one final push-pull response.
- The final response should contain both a playful challenge and a genuine interest signal.

Evaluation:
- Evaluate only the final submitted stage.
- Apply the cover-half test: each side should still contain meaningful content when the other side is covered.
- Check whether the push is trivial and about her.
- Check whether the pull is genuine.
- Check tension, brevity, and naturalness.

## `task_types` Seed

```json
[
  {
    "id": "voice_single_prompt",
    "display_name": "Voice Single Prompt",
    "description": "One generated prompt, one spoken response, one feedback result.",
    "ui_schema_key": "voice_single_prompt_v1",
    "runtime_engine_key": "voice_prompt_v1",
    "default_duration_seconds": 30,
    "is_active": true,
    "sort_order": 10,
    "metadata": {
      "supports_tts": true,
      "supports_avatar": true,
      "supports_assigned_technique": true,
      "supports_scaffold_stages": false
    }
  },
  {
    "id": "voice_dialogue_prompt",
    "display_name": "Voice Dialogue Prompt",
    "description": "Two or more generated speaker messages, one spoken response, one feedback result.",
    "ui_schema_key": "voice_dialogue_prompt_v1",
    "runtime_engine_key": "voice_prompt_v1",
    "default_duration_seconds": 30,
    "is_active": true,
    "sort_order": 20,
    "metadata": {
      "supports_tts": true,
      "supports_avatar": true,
      "supports_assigned_technique": false,
      "supports_scaffold_stages": false
    }
  },
  {
    "id": "voice_scaffolded_prompt",
    "display_name": "Voice Scaffolded Prompt",
    "description": "One generated prompt with guided rehearsal stages before the final evaluated response.",
    "ui_schema_key": "voice_scaffolded_prompt_v1",
    "runtime_engine_key": "voice_prompt_v1",
    "default_duration_seconds": 30,
    "is_active": true,
    "sort_order": 30,
    "metadata": {
      "supports_tts": true,
      "supports_avatar": true,
      "supports_assigned_technique": false,
      "supports_scaffold_stages": true
    }
  }
]
```

## How To Add The Rest Of The Catalog

Use `design/extra/tasks.md` as the full source for the remaining exercises:
- `yes-and`
- `misinterpretation`
- `love-hate`
- `if-by-x-you-mean-y`
- `vibing`
- `first-unusual-thing`

Mapping rules:
- Add a new `task_type_id` only when the frontend interaction shape changes.
- Use `voice_single_prompt` for one generated prompt and one final response.
- Use `voice_dialogue_prompt` for ordered speaker-message setup plus one final response.
- Use `voice_scaffolded_prompt` for guided stages before the final response.
- Put user-facing labels and stage config in `tasks.content`.
- Put backend prompt/evaluator routing in `tasks.runtime_config`.
