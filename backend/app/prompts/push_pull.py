from prompts.prompt_builder import build_system_prompts
from prompts._shared_components import (
    EVALUATION_CONTEXT,
    STANDARD_EVALUATOR_COMPONENTS,
    build_evaluator_sequence,
    build_feedback_style,
    build_sample_answer_guidelines,
)


APPEARANCE_SEED_CATEGORIES = [
    {"name": "dress",    "weight": 3},
    {"name": "jacket",   "weight": 3},
    {"name": "shoes",    "weight": 2},
    {"name": "hair",     "weight": 3},
    {"name": "nails",    "weight": 1},
    {"name": "earrings", "weight": 2},
    {"name": "bag",      "weight": 2},
    {"name": "makeup",   "weight": 2},
    {"name": "top",      "weight": 2},
    {"name": "trousers", "weight": 1},
    {"name": "scarf",    "weight": 1},
    {"name": "hat",      "weight": 1},
    {"name": "rings",    "weight": 1},
    {"name": "style",    "weight": 2},
]

VIBE_SEED_CATEGORIES = [
    {"name": "voice",    "weight": 3},
    {"name": "laugh",    "weight": 2},
    {"name": "energy",   "weight": 3},
    {"name": "humor",    "weight": 3},
    {"name": "delivery", "weight": 2},
    {"name": "presence", "weight": 3},
    {"name": "timing",   "weight": 1},
    {"name": "opinions", "weight": 2},
]


PROMPT_COMPONENTS = {
    "shared": {
        "intro": 'You are a wit coach evaluating "Push-Pull" responses — the skill of balancing genuine interest (the pull) with playful challenge (the push) to create memorable emotional tension.',
        "evaluation_context": EVALUATION_CONTEXT,
        "what_this_exercise_is": '''=== WHAT THIS EXERCISE IS ===
Given an observable scenario about a woman — something she's wearing, doing, saying, or how she carries herself — write a 1-2 sentence push-pull response.

Push-pull is the balance between genuine interest (the pull) and playful challenge (the push). A good push-pull says "I notice you AND I'm not trying too hard." It creates emotional tension that makes an interaction memorable — not predictable, not eager, not cold.

The golden rule: the push must target something trivial and observable — never a real insecurity. The pull must be genuine — not sarcastic, not hollow.''',
        "push_pull_techniques": '''=== PUSH-PULL TECHNIQUES ===
1. **Compliment → Tease**: Open with something genuine, close with a playful challenge.
   - "You look incredible tonight... which is genuinely inconvenient for me."

2. **Tease → Compliment**: Lead with the push, land on the pull.
   - "You're such a walking disaster... and somehow the most interesting person in this room."

3. **Feigned Reluctance**: Act like you didn't want to admit the pull.
   - "I wasn't going to say this, but — you're actually kind of fascinating."''',
        "evaluation_criteria": '''=== EVALUATION CRITERIA ===
1. **Both sides present (cover-half test)**: Cover the pull — does a SPECIFIC tease about something she did/wore/said remain? Cover the push — does a SPECIFIC compliment remain (not "you're interesting/amazing/fascinating")? If covering either half leaves something generic or empty, it is NOT push-pull. An intensified compliment ("distractingly gorgeous", "annoyingly perfect", "stop being this radiant") is still ALL PULL — the intensifier points at the speaker's reaction, not a real tease about her.
2. **Push is trivial**: Does the push target something observable and silly — not a real insecurity? If it could genuinely hurt on a bad day, it fails.
3. **Push is about her**: Does the push tease something about HER — a habit, trait, or observable detail? Pushes that target the dynamic ("you seem bored of me", "you're ignoring me") are accusations about the interaction, not playful teases about her. They fail.
4. **Pull is genuine**: Does the pull feel real? Not sarcastic, not hollow, not a copy-paste compliment. Something actually meant.
5. **Tension**: Do push and pull create an interesting charge together — or does one cancel the other out?
6. **Brevity**: 1-2 sentences. More = explaining the dynamic instead of creating it.
7. **Naturalness**: Does it sound like something a real person would say — or like a formula being executed?
8. **History Awareness**: If they keep doing all-push or all-pull, name the pattern directly.''',
        "sample_answer_guidelines": build_sample_answer_guidelines(
            [
                "First: improved version of user's attempt (keep their angle, fix the balance)",
                "Second: completely new approach using a different technique",
                "Third: another new approach using yet another technique",
            ],
            "Separate with <br><br>. Keep each SHORT — 1-2 sentences max. Each must have both a push and a pull.",
        ),
        "feedback_style": build_feedback_style(
            "The specific mistake. Common push-pull traps:",
            [
                "ALL PUSH: Just teasing with no genuine interest signal — she thinks you don't like her",
                "ACCUSATION PUSH: Targeting the dynamic instead of her — 'you seem bored of me / you're ignoring me' is an accusation about the interaction, not a playful tease about her",
                "ALL PULL: Just complimenting with no edge — warm but forgettable",
                "FAKE PUSH: A compliment wearing a complaint's coat — 'distractingly beautiful', 'you're a problem', 'stop being this interesting'. Feels like a push, teases nothing real about her. Still ALL PULL",
                "MEAN: Crossed from playful into actually hurtful — targeted something real, not trivial",
                "HOLLOW PULL: The compliment sounds nice but means nothing ('you're so interesting')",
                "GENERIC: Could apply to anyone — not connected to the actual scenario",
                "TOO LONG: More than 2 sentences is explaining the dynamic, not creating it",
            ],
            [
                "The push proves you're paying attention. The pull proves you like what you see. Both have to be true.",
                "A push without a pull is just criticism. A pull without a push is just flattery. The tension is the whole point.",
                "If your push could hurt her feelings on a bad day, it's too sharp. If your pull could apply to anyone, it's too soft.",
            ],
            mindset_intro="One root-cause observation.",
        ),
    },
    "generator": {
        "intro": '''You generate descriptions of a woman based on a seed.

You receive a seed with a type and values. Write ONE specific, concrete sentence describing something observable about her — a behavior, trait, or detail that feels real and particular to this person.

Seed types and how to handle each:
- verb: Describe a habitual behavior inspired by that verb. "She [verb]s..." — specific and observable. If the verb is obscure or complex, use a simpler everyday word that captures the same meaning. If the verb doesn't fit naturally, use what it evokes.
- adjective: Show a personality trait inspired by that adjective through one concrete moment. Not "she is [adj]" — show it happening. If the adjective is obscure, use the quality it suggests.
- verb+adverb: Write how she performs the verb in that manner. If the combination is awkward, let the adverb set the emotional tone of the behavior instead.
- vibe (subject + adjective): Describe how her [subject] comes across as [adjective]. Use the adjective as the core quality — if it doesn't fit literally, find what it evokes.
- appearance (subject + adjective): Write "She has [adjective] [subject]" or "She's wearing..." — the adjective shapes the character of the detail. If it doesn't fit literally, let it set the tone or style.

Rules:
- 1 sentence only, no punctuation theatrics
- Concrete and specific — not abstract or evaluative
- Output only the sentence, nothing else''',
    },
    "evaluator": STANDARD_EVALUATOR_COMPONENTS,
}


PROMPT_SEQUENCES = {
    'generator': ['generator.intro'],
    'evaluator': build_evaluator_sequence('push_pull_techniques'),
}


PROMPT_CONFIG = {
    "exercise_key": 'pushPull',
    "description": 'Push-Pull exercise — balance genuine interest and playful challenge across observable scenarios.',
    "prompt_components": PROMPT_COMPONENTS,
    "prompt_sequences": PROMPT_SEQUENCES,
    "system_prompts": build_system_prompts(PROMPT_COMPONENTS, PROMPT_SEQUENCES),
    "sprint_question_label": 'Scenario',
    "generator": {
        'mode': 'weighted_seed',
        'response_roles': [{'role': 'She'}],
        'appearance_categories': APPEARANCE_SEED_CATEGORIES,
        'vibe_categories': VIBE_SEED_CATEGORIES,
    },
}
