# i-am-witty Task Catalog And Runtime Design

Source: current backend exercise behavior, current sprint frontend behavior, and the new backend design docs.

This document is the canonical design source for task types, task runtime payloads, prompt generation, prompt evaluation, and the current exercise catalog. It is intended to be complete enough that the old backend prompt files do not need to be consulted during the new backend implementation.

## Purpose

The app has a generic task catalog, but not every exercise needs a separate frontend implementation. Exercises should share a task type when they have the same user interaction shape: the same kind of generated input, the same response capture flow, and the same output feedback shape.

This document defines:
- The task types needed for the current voice exercises.
- How `task_types`, `tasks.content`, and `tasks.runtime_config` should be populated.
- The request and response contracts for task generation and completion.
- The prompt behavior and evaluation behavior for each current exercise.
- Seed data examples for task types and tasks.

## Design Decision

Use three task types for the current exercise set:

| Task type id | UI schema key | Runtime engine key | Use case |
| --- | --- | --- | --- |
| `voice_single_prompt` | `voice_single_prompt_v1` | `voice_prompt_v1` | One generated prompt, one spoken answer, one evaluation. |
| `voice_dialogue_prompt` | `voice_dialogue_prompt_v1` | `voice_prompt_v1` | A short generated dialogue or multi-message setup, one spoken answer, one evaluation. |
| `voice_scaffolded_prompt` | `voice_scaffolded_prompt_v1` | `voice_prompt_v1` | One generated prompt plus guided rehearsal stages before the final spoken answer. |

`misinterpretation_techniques` should not be a separate task type. It uses the same single-prompt recording flow as `misinterpretation`; it only adds an assigned technique card. That is task/runtime config, not a new frontend shell.

`push_pull` and `first_unusual_thing` should share `voice_scaffolded_prompt` because both use a multi-stage guided response flow. Their stages differ, but the UI structure is the same.

`question_answer_tease` should use `voice_dialogue_prompt` because the generated input has two ordered speaker messages: the user's question and the other person's answer. This should render like a compact dialogue rather than a single prompt card.

## Core Model

### Task Types

`task_types` define shared frontend and runtime behavior. A task type should answer:
- What screen shell does the client render?
- What generated prompt shape is expected?
- Does the flow include assigned technique instructions?
- Does the flow include scaffold stages?
- Which runtime engine handles generation and completion?

Task types should not contain exercise-specific prompt wording.

### Tasks

`tasks` define individual exercises or catalog items. A task should answer:
- What is this exercise called?
- What task type does it use?
- What copy and labels does the client render?
- Which backend prompt bundle/generator/evaluator should the runtime engine use?
- What generated prompt shape and evaluation contract apply?

### `tasks.content`

`content` is client-renderable task data. It should be safe to send to the app.

Recommended shape:

```json
{
  "exercise_key": "pushPull",
  "display_title": "Push/Pull",
  "short_description": "Balance genuine interest with playful challenge.",
  "prompt_label": "Scenario",
  "response_instruction": "Say a short response for this situation.",
  "prompt_roles": ["She"],
  "recording_limit_seconds": 30,
  "assigned_technique_mode": "none",
  "scaffold_stages": [],
  "feedback_tabs": {
    "feedback_label": "Feedback",
    "sample_answer_label": "Better Way"
  }
}
```

For scaffolded tasks, `scaffold_stages` should be populated. For assigned-technique tasks, `assigned_technique_mode` should be `runtime_generated`.

### `tasks.runtime_config`

`runtime_config` is backend-only runtime data. It can be returned only when the client needs it, and should not expose private model prompts.

Recommended shape:

```json
{
  "backend_key": "pushPull",
  "prompt_bundle_key": "push_pull_v1",
  "generator": {
    "strategy": "weighted_seed",
    "output_shape": "single_message"
  },
  "evaluator": {
    "strategy": "transcript_feedback",
    "output_shape": "feedback_and_sample_answer"
  },
  "tts": {
    "enabled": true,
    "voice_mode": "multi_role"
  },
  "avatar": {
    "enabled": true,
    "selection": "random"
  }
}
```

`backend_key` is the stable compatibility key for the existing exercise behavior. New implementation code can route by this key without inheriting the old file layout.

## Shared Voice Runtime

All current exercises use the same high-level runtime:

1. The client requests task runtime data for a task.
2. The backend checks access and creates or resumes a `task_attempt`.
3. The backend generates the prompt payload using the task's `runtime_config`.
4. The client optionally plays generated TTS and shows the prompt.
5. The client records the user's spoken answer.
6. The client sends transcript and audio metadata to complete the runtime portion.
7. The backend evaluates the transcript and returns feedback.
8. The backend marks the task attempt completed and updates progress, plan item status, usage counters, and streak state.

The voice runtime should be implemented behind `TaskRuntimeEngine` as `VoicePromptTaskEngine` or equivalent. The engine should support all three task types through configuration.

## Generated Runtime Payload

The backend should return one payload shape for all voice prompt tasks. Task type fields determine which optional sections are populated.

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
    "response_instruction": "Say a short response for this situation.",
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
  "audio": {
    "audio_base64": null,
    "content_type": null
  },
  "avatar": {
    "image_url": null
  }
}
```

### Prompt Message Roles

Supported prompt message roles:

| Role | Meaning | Typical task type |
| --- | --- | --- |
| `She` | A sentence, statement, premise, scenario, criticism, or conversational prompt from the other person. | `voice_single_prompt`, `voice_scaffolded_prompt` |
| `You` | The user's prior question or line in a generated setup. | `voice_dialogue_prompt` |
| `Topic` | A topic to take a strong stance on. | `voice_single_prompt` |
| `Storyteller` | A personal story or anecdote to respond to. | `voice_single_prompt` |

The client should render roles as speaker labels, not as hardcoded exercise-specific UI.

## Completion Request

The client should submit the final response for evaluation.

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
  "transcript": "You are very proud of that joke, and annoyingly, it did earn the confidence.",
  "audio_metadata": {
    "audio_base64": "optional-base64",
    "content_type": "audio/webm",
    "duration_seconds": 12,
    "word_count": 17
  },
  "assigned_technique": null,
  "stage_responses": [
    {
      "position": 1,
      "transcript": "You are way too proud of that joke."
    },
    {
      "position": 2,
      "transcript": "It was actually funny."
    },
    {
      "position": 3,
      "transcript": "You are way too proud of that joke, which is annoying because it was actually funny."
    }
  ]
}
```

For the first implementation, only the final stage must be evaluated for scaffolded tasks. Earlier `stage_responses` can be omitted or stored as attempt events later.

## Completion Response

```json
{
  "success": true,
  "attempt_id": "uuid",
  "status": "completed",
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

Every current exercise returns:

- `feedback_html`: HTML feedback using four sections:
  - `What Landed`
  - `The Trap`
  - `Level Up`
  - `Mindset Shift`
- `sample_answer_html`: three improved or alternative responses separated by `<br><br>`.

`first_unusual_thing` has a specialized sample answer format. Each of its three sample answers should be broken into:
- `Ordinary detail`
- `Unusual thing`
- `Association`

## Prompt System Fit

The prompt system is an implementation detail behind the voice runtime engine, but the task catalog must define the contract for each exercise.

Each task needs:

- A `backend_key` that selects the prompt behavior.
- A generator strategy.
- A generated output shape.
- An optional assigned-technique strategy.
- An evaluator strategy.
- A feedback/sample-answer output contract.

The backend may implement prompt bundles as code, database rows, or files, but the behavior must match this document.

### Generator Strategies

| Strategy | Behavior | Used by |
| --- | --- | --- |
| `creative_prompt` | Build a varied natural-language generation request from prompt styles, context suggestions, topic suggestions, and creativity boosters. | `yesAnd`, `loveHate`, `ifByXYouMeanY`, `questionAnswerTease`, `vibing`, `heightening` |
| `verb_seed` | Pick a random verb and a pronoun from `I`, `you`, `we`, then ask the generator to produce one natural sentence using them. | `misinterpretation`, `misinterpretationTechniques`, `firstUnusualThing` |
| `weighted_seed` | Pick from weighted seed categories such as verb, adjective, verb+adverb, vibe, and appearance; generate one observable scenario. | `pushPull` |
| `archetype_prompt` | Pick from named prompt archetypes, then ask the generator for one statement that matches the selected archetype and constraint. | inactive `shitTest` candidate |

### Generated Output Shapes

| Output shape | JSON shape | Used by |
| --- | --- | --- |
| `single_message` | Exactly one message with role `She`, `Topic`, or `Storyteller`. | Most single-prompt tasks |
| `dialogue_two_message` | Exactly two messages in order: role `You`, then role `She`. | `questionAnswerTease` |

### Assigned Technique

Assigned technique is optional generated runtime data. It should be returned as:

```json
{
  "name": "Literal Trap",
  "instruction": "Respond as if it is literally, physically happening.",
  "example": "\"I might die tonight\" -> \"Should I call someone, or are you handling the arrangements?\""
}
```

Only `misinterpretationTechniques` currently uses assigned techniques.

### Technique List For `misinterpretationTechniques`

| Name | Instruction | Example |
| --- | --- | --- |
| `Literal Trap` | Respond as if it is literally, physically happening. | `"I might die tonight" -> "Should I call someone, or are you handling the arrangements?"` |
| `Context Shift` | Respond as if this belongs to a completely different situation. | `"We should probably stop here" -> "Already? We have only known each other a week."` |
| `Scope Explosion` | Treat this small thing like it has massive, world-altering implications. | `"I always lose my keys when you are around" -> "So I rearrange your entire life just by existing."` |
| `Innuendo` | Find the suggestive reading and respond from there. | `"You always take so long" -> "Worth every second, I have been told."` |
| `Absurd Escalation` | Run with this to a completely ridiculous conclusion. | `"I cannot keep up with you" -> "Nobody can. Scientists are looking into it."` |
| `Pronoun Swap` | Take a general `you` as personal, or split a `we` so it means just them. | `"We really made a mess of this" -> "We? I watched you do all of it."` |
| `Domain Confusion` | Respond as if this is a formal legal, medical, or professional matter. | `"We need to talk" -> "Agreed. My lawyers are available Thursday."` |
| `Temporal Shift` | Respond as if the timeframe is completely different. | `"I will be ready in a minute" -> "See you Thursday then."` |

## Task Type Details

### `voice_single_prompt`

Use this for exercises that show one generated prompt and record one response.

Frontend behavior:
- Show intro copy from `tasks.content`.
- Generate and show one prompt message.
- If `assigned_technique` is present, show a compact technique instruction card above the prompt.
- Record one spoken response with a 30 second default timer.
- Show feedback and sample answers in two tabs or equivalent sections.

Required `content` fields:

```json
{
  "prompt_label": "Premise",
  "response_instruction": "What would you say in this situation?",
  "prompt_roles": ["She"],
  "recording_limit_seconds": 30,
  "assigned_technique_mode": "none",
  "scaffold_stages": []
}
```

Required `runtime_config` fields:

```json
{
  "backend_key": "yesAnd",
  "prompt_bundle_key": "yes_and_v1",
  "generator": {
    "strategy": "creative_prompt",
    "output_shape": "single_message"
  },
  "evaluator": {
    "strategy": "transcript_feedback",
    "output_shape": "feedback_and_sample_answer"
  }
}
```

Supported current exercises:
- `yesAnd`
- `misinterpretation`
- `misinterpretationTechniques`
- `loveHate`
- `ifByXYouMeanY`
- `vibing`
- `heightening`

### `voice_dialogue_prompt`

Use this when the generated setup has multiple speaker messages but still expects one spoken response.

Frontend behavior:
- Render prompt messages as a compact dialogue.
- Preserve message order.
- Record one spoken response.
- Evaluate against the full dialogue context.

Required `content` fields:

```json
{
  "prompt_label": "Question",
  "response_instruction": "Tease the answer without insulting or interviewing.",
  "prompt_roles": ["You", "She"],
  "recording_limit_seconds": 30,
  "assigned_technique_mode": "none",
  "scaffold_stages": []
}
```

Required `runtime_config` fields:

```json
{
  "backend_key": "questionAnswerTease",
  "prompt_bundle_key": "question_answer_tease_v1",
  "generator": {
    "strategy": "creative_prompt",
    "output_shape": "dialogue_two_message"
  },
  "evaluator": {
    "strategy": "transcript_feedback",
    "output_shape": "feedback_and_sample_answer"
  }
}
```

Supported current exercises:
- `questionAnswerTease`

### `voice_scaffolded_prompt`

Use this when the user needs guided rehearsal stages before the final evaluated response.

Frontend behavior:
- Show one generated prompt.
- Walk the user through ordered scaffold stages.
- Earlier stages are practice and can be discarded or stored as events.
- The final stage is submitted for evaluation.
- Show feedback and sample answers for the final response.

Required `content` fields:

```json
{
  "prompt_label": "Scenario",
  "response_instruction": "Follow each stage, then combine the final response.",
  "prompt_roles": ["She"],
  "recording_limit_seconds": 30,
  "assigned_technique_mode": "none",
  "scaffold_stages": [
    {
      "position": 1,
      "label": "Step 1 of 3",
      "title": "Push",
      "instruction": "Say just the push: one sentence, no softening.",
      "is_final_submission": false
    }
  ]
}
```

Required `runtime_config` fields:

```json
{
  "backend_key": "pushPull",
  "prompt_bundle_key": "push_pull_v1",
  "generator": {
    "strategy": "weighted_seed",
    "output_shape": "single_message"
  },
  "evaluator": {
    "strategy": "transcript_feedback",
    "output_shape": "feedback_and_sample_answer",
    "evaluate_stage": "final"
  }
}
```

Supported current exercises:
- `pushPull`
- `firstUnusualThing`

## Current Exercise Catalog

The current active catalog contains ten exercises.

### `yesAnd`

Catalog:

```json
{
  "slug": "yes-and",
  "title": "Yes, And...",
  "task_type_id": "voice_single_prompt",
  "prompt_label": "Premise",
  "backend_key": "yesAnd"
}
```

Generated input:
- Shape: one message.
- Role: `She`.
- Content: a playful, imaginative premise or observation that invites the user to build on it.
- Examples of premise domains: animals, technology, everyday objects, supernatural, historical, futuristic, nature, urban life.

Expected user response:
- Accept the premise.
- Add a new detail, escalation, role, world-building beat, or future projection.
- Match or exceed the playful energy.
- Avoid blocking, reality-checking, dead-ending, or hijacking the premise.

Evaluation summary:
- Check whether the user accepted the premise.
- Check whether the user added something new.
- Check energy match and conversational naturalness.

Sample answer behavior:
- Return three conversational, fun alternatives.
- First improves the user's core idea.
- Second and third show different improv styles.

Runtime config:

```json
{
  "backend_key": "yesAnd",
  "prompt_bundle_key": "yes_and_v1",
  "generator": {
    "strategy": "creative_prompt",
    "output_shape": "single_message",
    "message_role": "She"
  },
  "evaluator": {
    "strategy": "transcript_feedback",
    "criteria": ["acceptance", "build", "energy_match", "naturalness"]
  }
}
```

### `misinterpretation`

Catalog:

```json
{
  "slug": "misinterpretation",
  "title": "Misinterpretation",
  "task_type_id": "voice_single_prompt",
  "prompt_label": "Tease/Statement",
  "backend_key": "misinterpretation"
}
```

Generated input:
- Shape: one message.
- Role: `She`.
- Content: one short, ordinary sentence using a randomly selected verb and one pronoun from `I`, `you`, or `we`.
- The sentence should sound like something a real person would say.

Expected user response:
- Respond as if the sentence was understood differently.
- Misread a word, modifier, pronoun, ambiguity, phrase, or scope.
- Commit to the alternative reading.
- Keep the response brief.

Evaluation summary:
- Apply the litmus test: if the response still works under the intended meaning, it is not a misinterpretation.
- Identify what was misread.
- Check fit, wit, and brevity.
- Reject normal continuation, emotional reaction, agreement, or random non-sequitur.

Sample answer behavior:
- Return three short punchy responses.
- First sharpens the user's angle.
- Second and third use different approaches.

Runtime config:

```json
{
  "backend_key": "misinterpretation",
  "prompt_bundle_key": "misinterpretation_v1",
  "generator": {
    "strategy": "verb_seed",
    "output_shape": "single_message",
    "message_role": "She"
  },
  "evaluator": {
    "strategy": "transcript_feedback",
    "criteria": ["litmus_test", "misread_target", "fit", "wit", "brevity"]
  }
}
```

### `misinterpretationTechniques`

Catalog:

```json
{
  "slug": "misinterpretation-techniques",
  "title": "Misinterpretation: Techniques",
  "task_type_id": "voice_single_prompt",
  "prompt_label": "Tease/Statement",
  "backend_key": "misinterpretationTechniques"
}
```

Generated input:
- Shape: one message.
- Role: `She`.
- Content: one short, ordinary sentence using a randomly selected verb and one pronoun from `I`, `you`, or `we`.
- Plus one assigned technique from the technique list in this document.

Expected user response:
- Apply the assigned technique specifically.
- Misinterpret the original sentence through that technique.
- Commit without explaining the joke.

Evaluation summary:
- First check technique match.
- Then apply the misinterpretation litmus test.
- Check commitment, fit, and brevity.
- If the user used a different technique, identify that.

Sample answer behavior:
- Return three short responses.
- First improves the user's attempt using the assigned technique.
- Second gives a different execution of the same technique.
- Third uses a different technique and labels it.

Runtime config:

```json
{
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
```

### `loveHate`

Catalog:

```json
{
  "slug": "love-hate",
  "title": "Love/Hate",
  "task_type_id": "voice_single_prompt",
  "prompt_label": "Topic",
  "backend_key": "loveHate"
}
```

Generated input:
- Shape: one message.
- Role: `Topic`.
- Content: a relatable topic or situation that can evoke a strong opinion.
- Examples of domains: food, weather, technology, social situations, daily activities, cultural trends, pet peeves.

Expected user response:
- Pick a clear side: love or hate.
- Express the stance with conviction, personality, and specific details.
- Avoid fence-sitting, generic takes, over-explaining, or trying to be balanced.

Evaluation summary:
- Check for a clear stance.
- Check passion and specificity.
- Check whether the answer reveals personality.

Sample answer behavior:
- Return three vivid, personal, punchy options.
- First improves the user's stance.
- Second and third use different expression styles.

Runtime config:

```json
{
  "backend_key": "loveHate",
  "prompt_bundle_key": "love_hate_v1",
  "generator": {
    "strategy": "creative_prompt",
    "output_shape": "single_message",
    "message_role": "Topic"
  },
  "evaluator": {
    "strategy": "transcript_feedback",
    "criteria": ["stance", "passion", "personality", "specificity"]
  }
}
```

### `ifByXYouMeanY`

Catalog:

```json
{
  "slug": "if-by-x-you-mean-y",
  "title": "If by X you mean Y...",
  "task_type_id": "voice_single_prompt",
  "prompt_label": "Statement",
  "backend_key": "ifByXYouMeanY"
}
```

Generated input:
- Shape: one message.
- Role: `She`.
- Content: a negative or critical statement that can be reframed into a positive.
- Examples of topics: work habits, personality traits, social behavior, lifestyle choices, communication style, decision-making.

Expected user response:
- Use the `If by X you mean Y` structure.
- Transform the criticism into something compelling or status-building.
- Avoid defensiveness, literal synonym swaps, flat phrasing, or mean-spirited attacks.

Evaluation summary:
- Check whether the structure was used.
- Check whether the criticism was transformed rather than merely renamed.
- Check vividness, confidence, and brevity.

Sample answer behavior:
- Return three vivid reframes.
- First improves the user's idea.
- Second and third use different reframe styles.

Runtime config:

```json
{
  "backend_key": "ifByXYouMeanY",
  "prompt_bundle_key": "if_by_x_you_mean_y_v1",
  "generator": {
    "strategy": "creative_prompt",
    "output_shape": "single_message",
    "message_role": "She"
  },
  "evaluator": {
    "strategy": "transcript_feedback",
    "criteria": ["structure", "transformation_quality", "vividness", "confidence"]
  }
}
```

### `questionAnswerTease`

Catalog:

```json
{
  "slug": "question-answer-tease",
  "title": "Question Answer Tease",
  "task_type_id": "voice_dialogue_prompt",
  "prompt_label": "Question",
  "backend_key": "questionAnswerTease"
}
```

Generated input:
- Shape: exactly two messages.
- First message role: `You`.
- Second message role: `She`.
- Content: a simple question from the user and a realistic answer from the other person.
- Examples of topic domains: work, hobbies, food, travel, music, pets, sports, movies, fashion, technology.

Expected user response:
- Tease the answer playfully.
- Reference the specific answer rather than using a generic line.
- Avoid validating, asking another question, insulting, or trying too hard.

Evaluation summary:
- Check whether the user leads the vibe.
- Check cocky-funny tone without meanness.
- Check specificity to her answer.
- Check brevity.

Sample answer behavior:
- Return three short teases.
- First improves the user's tease.
- Second and third use different teasing frames.

Runtime config:

```json
{
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
```

### `vibing`

Catalog:

```json
{
  "slug": "vibing",
  "title": "Vibing",
  "task_type_id": "voice_single_prompt",
  "prompt_label": "Story",
  "backend_key": "vibing"
}
```

Generated input:
- Shape: one message.
- Role: `Storyteller`.
- Content: a personal story or anecdote.
- Examples of domains: childhood, relationships, work, travel, family, friends, hobbies, life lessons, funny moments, challenges.

Expected user response:
- Match the speaker's emotional tone.
- Validate the feeling and build conversational momentum.
- Add curiosity, warmth, or a brief shared bridge.
- Avoid hijacking, fixing, therapy mode, or rapid-fire interviewing.

Evaluation summary:
- Check energy match.
- Check whether the user built on the story.
- Check whether the spotlight stayed on the storyteller.
- Check naturalness.

Sample answer behavior:
- Return three warm, natural, energetic responses.
- First improves the user's response.
- Second and third use different vibing styles.

Runtime config:

```json
{
  "backend_key": "vibing",
  "prompt_bundle_key": "vibing_v1",
  "generator": {
    "strategy": "creative_prompt",
    "output_shape": "single_message",
    "message_role": "Storyteller"
  },
  "evaluator": {
    "strategy": "transcript_feedback",
    "criteria": ["energy_match", "build", "spotlight", "naturalness"]
  }
}
```

### `pushPull`

Catalog:

```json
{
  "slug": "push-pull",
  "title": "Push/Pull",
  "task_type_id": "voice_scaffolded_prompt",
  "prompt_label": "Scenario",
  "backend_key": "pushPull"
}
```

Generated input:
- Shape: one message.
- Role: `She`.
- Content: one specific observable scenario about a woman: something she is wearing, doing, saying, or how she carries herself.
- Seed categories include:
  - appearance: dress, jacket, shoes, hair, nails, earrings, bag, makeup, top, trousers, scarf, hat, rings, style.
  - vibe: voice, laugh, energy, humor, delivery, presence, timing, opinions.
  - general seeds: verb, adjective, verb+adverb.

Scaffold stages:

```json
[
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
]
```

Expected user response:
- Create a one or two sentence response with both a push and a pull.
- Push: a trivial, observable, playful challenge.
- Pull: a genuine specific interest signal or compliment.
- Avoid all-push, all-pull, fake push, accusation push, meanness, hollow compliments, generic phrasing, or long explanations.

Evaluation summary:
- Apply the cover-half test: each side should still contain meaningful content when the other side is covered.
- Check whether the push is trivial and about her.
- Check whether the pull is genuine.
- Check tension, brevity, and naturalness.

Sample answer behavior:
- Return three short responses.
- Each must contain both a push and a pull.
- First improves the user's balance.
- Second and third use different techniques.

Runtime config:

```json
{
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
```

### `heightening`

Catalog:

```json
{
  "slug": "heightening",
  "title": "Heightening",
  "task_type_id": "voice_single_prompt",
  "prompt_label": "Premise",
  "backend_key": "heightening"
}
```

Generated input:
- Shape: one message.
- Role: `She`.
- Content: one grounded statement with a single clear unusual detail that can be escalated.
- It should be mundane enough to feel real, but contain one specific hook.

Expected user response:
- Find the unusual detail.
- Escalate the same idea along scale, frequency, stakes, authority, world-logic, or emotional stakes.
- Avoid switching to a new joke, flat reaction, same-size restatement, winking, randomness, or overlong narration.

Evaluation summary:
- Check whether the user found a detail that was actually in the statement.
- Check whether the response stayed on the same thread.
- Check whether it went bigger.
- Check commitment, brevity, and wit.

Sample answer behavior:
- Return three short heightens.
- First improves the user's detail.
- Second and third use different heightening techniques.

Runtime config:

```json
{
  "backend_key": "heightening",
  "prompt_bundle_key": "heightening_v1",
  "generator": {
    "strategy": "creative_prompt",
    "output_shape": "single_message",
    "message_role": "She"
  },
  "evaluator": {
    "strategy": "transcript_feedback",
    "criteria": ["found_unusual_thing", "same_thread", "went_bigger", "commitment", "brevity", "wit"]
  }
}
```

### `firstUnusualThing`

Catalog:

```json
{
  "slug": "first-unusual-thing",
  "title": "First Unusual Thing",
  "task_type_id": "voice_scaffolded_prompt",
  "prompt_label": "Scene",
  "backend_key": "firstUnusualThing"
}
```

Generated input:
- Shape: one message.
- Role: `She`.
- Content: one short, deliberately ordinary scene using a randomly selected verb and one pronoun from `I`, `you`, or `we`.
- The scene must be normal. The user's job is to introduce the unusual thing.

Scaffold stages:

```json
[
  {
    "position": 1,
    "label": "Step 1 of 3",
    "title": "Notice",
    "instruction": "Say the one most ordinary detail in this scene.",
    "is_final_submission": false
  },
  {
    "position": 2,
    "label": "Step 2 of 3",
    "title": "Frame",
    "instruction": "Introduce one unusual thing about it. State it straight, like it is normal.",
    "is_final_submission": false
  },
  {
    "position": 3,
    "label": "Step 3 of 3",
    "title": "Associate",
    "instruction": "Now say the full move: your unusual thing plus what else is true if that is true.",
    "is_final_submission": true
  }
]
```

Expected user response:
- Introduce exactly one grounded deviation from the scene's base reality.
- Anchor it to a specific ordinary detail.
- Keep the world real; make the strangeness about a person's belief, habit, rule, reaction, or ritual.
- Take at least one buildable association step.
- Avoid staying normal, going random, making the world magical, adding multiple weird things, going too big too fast, or explaining the bit.

Evaluation summary:
- Identify the ordinary detail that was tilted.
- Check singularity and commitment.
- Check buildability.
- Check groundedness.
- Check right size, brevity, and wit.

Sample answer behavior:
- Return three answers.
- Each answer must be broken into:
  - `Ordinary detail`
  - `Unusual thing`
  - `Association`

Runtime config:

```json
{
  "backend_key": "firstUnusualThing",
  "prompt_bundle_key": "first_unusual_thing_v1",
  "generator": {
    "strategy": "verb_seed",
    "output_shape": "single_message",
    "message_role": "She"
  },
  "evaluator": {
    "strategy": "transcript_feedback",
    "evaluate_stage": "final",
    "criteria": ["anchored", "singular_committed", "buildable", "grounded", "right_size", "brevity", "wit"],
    "sample_answer_format": "ordinary_detail_unusual_thing_association"
  }
}
```

## Inactive Legacy Candidate

The current active catalog should seed the ten exercises above. One additional legacy prompt bundle exists conceptually and can be revived later if product wants it.

### `shitTest`

Status:
- Not part of the current active task catalog.
- Do not seed it as active unless product explicitly reintroduces it.
- If revived, it should use `voice_single_prompt`.

Catalog if revived:

```json
{
  "slug": "shit-test",
  "title": "Shit Test",
  "task_type_id": "voice_single_prompt",
  "prompt_label": "Tease/Statement",
  "backend_key": "shitTest"
}
```

Generated input:
- Shape: one message.
- Role: `She`.
- Content: a playful but skeptical or slightly negative dating statement, such as a challenge, accusation, or test of frame.
- Archetype domains: player accusation, vanity accusation, weirdness accusation, arrogance accusation, skepticism frame, too-nice accusation.

Expected user response:
- Reframe the statement as if it were a compliment, flirtation, or proof of value.
- Stay playful and confident.
- Avoid defensiveness, apologizing, generic lines, long explanations, or mean-spirited attacks.

Evaluation summary:
- Check whether the user flipped the frame instead of denying or explaining.
- Check confidence signal.
- Check wit and brevity.

Runtime config if revived:

```json
{
  "backend_key": "shitTest",
  "prompt_bundle_key": "shit_test_v1",
  "generator": {
    "strategy": "archetype_prompt",
    "output_shape": "single_message",
    "message_role": "She"
  },
  "evaluator": {
    "strategy": "transcript_feedback",
    "criteria": ["reframe", "confidence", "wit", "brevity"]
  }
}
```

## Seed Data Examples

### `task_types`

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

### `tasks`

The examples below omit UUIDs, timestamps, thumbnails, and images. Production seed data should add them.

```json
[
  {
    "slug": "yes-and",
    "title": "Yes, And...",
    "description": "Accept a playful premise and build it into something more fun.",
    "task_type_id": "voice_single_prompt",
    "duration_seconds": 30,
    "content": {
      "exercise_key": "yesAnd",
      "prompt_label": "Premise",
      "prompt_roles": ["She"],
      "response_instruction": "Accept the premise and add something that makes it more fun.",
      "assigned_technique_mode": "none",
      "scaffold_stages": []
    },
    "runtime_config": {
      "backend_key": "yesAnd",
      "prompt_bundle_key": "yes_and_v1",
      "generator": {"strategy": "creative_prompt", "output_shape": "single_message", "message_role": "She"},
      "evaluator": {"strategy": "transcript_feedback"}
    }
  },
  {
    "slug": "misinterpretation",
    "title": "Misinterpretation",
    "description": "Find an unexpected reading in an ordinary sentence.",
    "task_type_id": "voice_single_prompt",
    "duration_seconds": 30,
    "content": {
      "exercise_key": "misinterpretation",
      "prompt_label": "Tease/Statement",
      "prompt_roles": ["She"],
      "response_instruction": "Misread the sentence and commit to that alternative meaning.",
      "assigned_technique_mode": "none",
      "scaffold_stages": []
    },
    "runtime_config": {
      "backend_key": "misinterpretation",
      "prompt_bundle_key": "misinterpretation_v1",
      "generator": {"strategy": "verb_seed", "output_shape": "single_message", "message_role": "She"},
      "evaluator": {"strategy": "transcript_feedback"}
    }
  },
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
      "assigned_technique_mode": "runtime_generated",
      "scaffold_stages": []
    },
    "runtime_config": {
      "backend_key": "misinterpretationTechniques",
      "prompt_bundle_key": "misinterpretation_techniques_v1",
      "generator": {"strategy": "verb_seed", "output_shape": "single_message", "message_role": "She"},
      "assigned_technique": {"strategy": "random_choice", "source": "misinterpretation_techniques"},
      "evaluator": {"strategy": "transcript_feedback"}
    }
  },
  {
    "slug": "love-hate",
    "title": "Love/Hate",
    "description": "Pick a side and express a strong opinion with personality.",
    "task_type_id": "voice_single_prompt",
    "duration_seconds": 30,
    "content": {
      "exercise_key": "loveHate",
      "prompt_label": "Topic",
      "prompt_roles": ["Topic"],
      "response_instruction": "Choose love or hate and make the stance vivid.",
      "assigned_technique_mode": "none",
      "scaffold_stages": []
    },
    "runtime_config": {
      "backend_key": "loveHate",
      "prompt_bundle_key": "love_hate_v1",
      "generator": {"strategy": "creative_prompt", "output_shape": "single_message", "message_role": "Topic"},
      "evaluator": {"strategy": "transcript_feedback"}
    }
  },
  {
    "slug": "if-by-x-you-mean-y",
    "title": "If by X you mean Y...",
    "description": "Reframe criticism into something confident and compelling.",
    "task_type_id": "voice_single_prompt",
    "duration_seconds": 30,
    "content": {
      "exercise_key": "ifByXYouMeanY",
      "prompt_label": "Statement",
      "prompt_roles": ["She"],
      "response_instruction": "Use the If by X you mean Y structure to transform the criticism.",
      "assigned_technique_mode": "none",
      "scaffold_stages": []
    },
    "runtime_config": {
      "backend_key": "ifByXYouMeanY",
      "prompt_bundle_key": "if_by_x_you_mean_y_v1",
      "generator": {"strategy": "creative_prompt", "output_shape": "single_message", "message_role": "She"},
      "evaluator": {"strategy": "transcript_feedback"}
    }
  },
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
      "assigned_technique_mode": "none",
      "scaffold_stages": []
    },
    "runtime_config": {
      "backend_key": "questionAnswerTease",
      "prompt_bundle_key": "question_answer_tease_v1",
      "generator": {"strategy": "creative_prompt", "output_shape": "dialogue_two_message", "message_roles": ["You", "She"]},
      "evaluator": {"strategy": "transcript_feedback"}
    }
  },
  {
    "slug": "vibing",
    "title": "Vibing",
    "description": "Match emotion, validate the feeling, and build conversational momentum.",
    "task_type_id": "voice_single_prompt",
    "duration_seconds": 30,
    "content": {
      "exercise_key": "vibing",
      "prompt_label": "Story",
      "prompt_roles": ["Storyteller"],
      "response_instruction": "Respond with warmth, curiosity, and matching energy.",
      "assigned_technique_mode": "none",
      "scaffold_stages": []
    },
    "runtime_config": {
      "backend_key": "vibing",
      "prompt_bundle_key": "vibing_v1",
      "generator": {"strategy": "creative_prompt", "output_shape": "single_message", "message_role": "Storyteller"},
      "evaluator": {"strategy": "transcript_feedback"}
    }
  },
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
      "assigned_technique_mode": "none",
      "scaffold_stages": [
        {"position": 1, "label": "Step 1 of 3", "title": "Push", "instruction": "Say just the push: one sentence, no softening.", "is_final_submission": false},
        {"position": 2, "label": "Step 2 of 3", "title": "Pull", "instruction": "Say just the genuine compliment: no irony.", "is_final_submission": false},
        {"position": 3, "label": "Step 3 of 3", "title": "Combine", "instruction": "Combine them into one push-pull line.", "is_final_submission": true}
      ]
    },
    "runtime_config": {
      "backend_key": "pushPull",
      "prompt_bundle_key": "push_pull_v1",
      "generator": {"strategy": "weighted_seed", "output_shape": "single_message", "message_role": "She"},
      "evaluator": {"strategy": "transcript_feedback", "evaluate_stage": "final"}
    }
  },
  {
    "slug": "heightening",
    "title": "Heightening",
    "description": "Take one unusual detail and escalate it on the same thread.",
    "task_type_id": "voice_single_prompt",
    "duration_seconds": 30,
    "content": {
      "exercise_key": "heightening",
      "prompt_label": "Premise",
      "prompt_roles": ["She"],
      "response_instruction": "Find the unusual detail and make the same idea bigger.",
      "assigned_technique_mode": "none",
      "scaffold_stages": []
    },
    "runtime_config": {
      "backend_key": "heightening",
      "prompt_bundle_key": "heightening_v1",
      "generator": {"strategy": "creative_prompt", "output_shape": "single_message", "message_role": "She"},
      "evaluator": {"strategy": "transcript_feedback"}
    }
  },
  {
    "slug": "first-unusual-thing",
    "title": "First Unusual Thing",
    "description": "Introduce one grounded tilt into an ordinary scene.",
    "task_type_id": "voice_scaffolded_prompt",
    "duration_seconds": 30,
    "content": {
      "exercise_key": "firstUnusualThing",
      "prompt_label": "Scene",
      "prompt_roles": ["She"],
      "response_instruction": "Notice the ordinary detail, frame one unusual thing, then associate.",
      "assigned_technique_mode": "none",
      "scaffold_stages": [
        {"position": 1, "label": "Step 1 of 3", "title": "Notice", "instruction": "Say the one most ordinary detail in this scene.", "is_final_submission": false},
        {"position": 2, "label": "Step 2 of 3", "title": "Frame", "instruction": "Introduce one unusual thing about it. State it straight, like it is normal.", "is_final_submission": false},
        {"position": 3, "label": "Step 3 of 3", "title": "Associate", "instruction": "Now say the full move: your unusual thing plus what else is true if that is true.", "is_final_submission": true}
      ]
    },
    "runtime_config": {
      "backend_key": "firstUnusualThing",
      "prompt_bundle_key": "first_unusual_thing_v1",
      "generator": {"strategy": "verb_seed", "output_shape": "single_message", "message_role": "She"},
      "evaluator": {"strategy": "transcript_feedback", "evaluate_stage": "final", "sample_answer_format": "ordinary_detail_unusual_thing_association"}
    }
  }
]
```

## Product Categories Versus Runtime Types

Product categories such as sprint, improv, calm, and story can still exist as user-facing grouping metadata, filters, or curriculum labels. They should not be used as `task_type_id` when the actual frontend/runtime behavior differs.

Recommended placement:

```json
{
  "metadata": {
    "product_category": "sprint",
    "primary_skill": "improv",
    "difficulty": "beginner"
  }
}
```

## Future Extensions

Add a new task type only when the frontend interaction shape changes materially. Examples:
- Text-only task with no voice recording.
- Multi-turn roleplay with live back-and-forth state.
- Calm/breathing timer with no generated prompt.
- Story-building task with multiple submitted turns.
- Image/video prompt task.

Do not add a task type merely because the evaluation prompt, prompt label, or exercise name changes.
