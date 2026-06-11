import random

from app.infrastructure.runtime.prompts.fallbacks import standard_evaluator_fallback
from app.infrastructure.runtime.prompts.generator_strategies import verb_seed_generator_prompt
from app.infrastructure.runtime.prompts.output_schemas import EvaluationResult, SingleSheQuestion
from app.infrastructure.runtime.prompts.prompt_builders import (
    build_feedback_style,
    build_sample_answer_guidelines,
    build_evaluator_system,
    standard_evaluator_prompt,
)
from app.infrastructure.runtime.prompts.prompt_contracts import EVALUATION_CONTEXT
from app.infrastructure.runtime.prompts.spec import ExerciseSpec


TECHNIQUES = [
    {
        "name": "Literal Trap",
        "instruction": "Respond as if it's literally, physically happening",
        "example": '"I might die tonight" → "Should I call someone, or are you handling the arrangements?"',
    },
    {
        "name": "Context Shift",
        "instruction": "Respond as if this belongs to a completely different situation",
        "example": '"We should probably stop here" → "Already? We\'ve only known each other a week."',
    },
    {
        "name": "Scope Explosion",
        "instruction": "Treat this small thing like it has massive, world-altering implications",
        "example": '"I always lose my keys when you\'re around" → "So I rearrange your entire life just by existing."',
    },
    {
        "name": "Innuendo",
        "instruction": "Find the suggestive reading — respond from there",
        "example": '"You always take so long" → "Worth every second, I\'ve been told."',
    },
    {
        "name": "Absurd Escalation",
        "instruction": "Run with this to a completely ridiculous conclusion",
        "example": '"I can\'t keep up with you" → "Nobody can. Scientists are looking into it."',
    },
    {
        "name": "Pronoun Swap",
        "instruction": "Take a general 'you' as personal, or split a 'we' so it means just them",
        "example": '"We really made a mess of this" → "We? I watched you do all of it."',
    },
    {
        "name": "Domain Confusion",
        "instruction": "Respond as if this is a formal legal, medical, or professional matter",
        "example": '"We need to talk" → "Agreed. My lawyers are available Thursday."',
    },
    {
        "name": "Temporal Shift",
        "instruction": "Respond as if the timeframe is completely different",
        "example": '"I\'ll be ready in a minute" → "See you Thursday then."',
    },
]


def pick_random_technique() -> dict:
    return random.choice(TECHNIQUES)


SAMPLE_ANSWER_GUIDELINES = build_sample_answer_guidelines(
    [
        "First: improved version of user's attempt using the same assigned technique",
        "Second: completely different execution of the same technique",
        "Third: a different technique entirely — to show the contrast",
    ],
    "Separate with <br><br>. Label the third one with its technique name in parentheses. Keep each SHORT.",
)

FEEDBACK_STYLE = build_feedback_style(
    "Whether they hit the technique or missed it:",
    [
        "WRONG TECHNIQUE: Used a different technique than assigned — note which one they actually used",
        "NO TECHNIQUE: Just reacted naturally to the sentence — failed the litmus test entirely",
        "HALF-HIT: Partially got the technique but pulled back or softened the misread",
        "BROKE THE BIT: Added 'haha just kidding' or explained the joke — kills it instantly",
        "TOO LONG: A misinterpretation that needs 3 sentences is a speech, not a wit move",
    ],
    [
        "The technique is a lens — once you pick it, everything you say comes from inside that lens.",
        "Commitment is the whole skill. A half-committed misinterpretation is just a weird comment.",
        "If you can't find the angle for this technique on this sentence, pick any word and start there.",
    ],
    mindset_intro="One observation about their relationship with committing to the bit.",
)


PROMPT_TEXT = {
    "evaluator": {
        "intro": 'You are a wit coach evaluating "Misinterpretation Techniques" responses — the skill of applying a specific misinterpretation technique to redirect an everyday sentence.',
        "what_this_exercise_is": '''=== WHAT THIS EXERCISE IS ===
The user is given an everyday sentence AND a specific misinterpretation technique to apply. They must respond as if they understood the sentence differently — using exactly that technique. This trains deliberate technique selection, not just general misinterpretation.

The sentence contains "I", "you", or "we". The user's job is to find the alternative reading the technique points to and commit to it.''',
        "techniques_reference": '''=== TECHNIQUE REFERENCE ===
1. **Literal Trap**: Treat figurative or idiomatic language as if it literally, physically happened.
   - "I might die tonight" → "Should I call someone, or are you handling the arrangements yourself?"

2. **Context Shift**: Respond as if the sentence belongs to a completely different setting — romantic, legal, medical, professional.
   - "We should probably stop here" → "Already? We've only known each other a week."

3. **Scope Explosion**: Inflate a minor everyday statement into something cosmic or world-altering.
   - "I always lose my keys when you're around" → "So I rearrange your entire life just by existing. That's a lot of power."

4. **Innuendo**: Respond as if you heard the charged, suggestive meaning of an innocent sentence.
   - "You always take so long" → "Worth every second, I've been told."

5. **Absurd Escalation**: Take the statement to a completely ridiculous extreme — invent a world where this is a famous problem.
   - "I can't keep up with you" → "Nobody can. Scientists are looking into it."

6. **Pronoun Swap**: Misread who a pronoun points to. Take a generic "you" (meaning "anyone") as a personal "you", or split an inclusive "we" so it only refers to them. The ambiguity must be real — the sentence must genuinely allow both readings.
   - "We really made a mess of this" → "We? I watched you do all of it." (splits the inclusive "we")
   - "You never know with these things" → "I do, actually. Try me." (generic "you" read as personal)

7. **Domain Confusion**: Treat casual emotional language as if it belongs to a formal domain — legal, medical, corporate.
   - "We need to talk" → "Agreed. My lawyers are available Thursday."

8. **Temporal Shift**: Misread any time reference as a wildly different duration.
   - "I'll be ready in a minute" → "See you Thursday then."''',
        "evaluation_criteria": '''=== EVALUATION CRITERIA ===
The user was assigned a specific technique. Evaluate in this order:

1. **Technique Match** (primary): Did they actually use the assigned technique? Name the technique and say whether they hit it, missed it, or accidentally used a different one.
2. **Litmus Test**: Does the response still work under the original intended meaning of the sentence? If yes, it's not a misinterpretation at all — fail it immediately regardless of technique.
3. **Commitment**: Did they commit fully, or did they hedge, explain, or soften the misread?
4. **Fit**: Does the misreading plausibly connect to something actually in the sentence?
5. **Brevity**: One or two sentences. Longer = explaining the joke.''',
    },
    "generator": {
        "intro": '''You generate sentences for a misinterpretation exercise.

Given a verb, write ONE short, natural sentence that a person might actually say in everyday life.

Rules:
- The sentence must use the given verb and pronoun ("I", "you", or "we") naturally
- Sound completely ordinary — something real people say
- 1 sentence only, no punctuation theatrics
- Output only the sentence, nothing else''',
    },
}


_evaluator = PROMPT_TEXT["evaluator"]
_generator = PROMPT_TEXT["generator"]

SPEC = ExerciseSpec(
    key="misinterpretationTechniques",
    description="Misinterpretation Techniques — practice applying a specific misinterpretation technique to any everyday sentence.",
    sprint_question_label="Tease/Statement",
    generator_system=_generator["intro"],
    generator_prompt=verb_seed_generator_prompt,
    generator_response_schema=SingleSheQuestion,
    evaluator_system=build_evaluator_system(
        intro=_evaluator["intro"],
        evaluation_context=EVALUATION_CONTEXT,
        sections=[
            _evaluator["what_this_exercise_is"],
            _evaluator["techniques_reference"],
            _evaluator["evaluation_criteria"],
        ],
        feedback_style=FEEDBACK_STYLE,
        sample_answer_guidelines=SAMPLE_ANSWER_GUIDELINES,
    ),
    evaluator_prompt=standard_evaluator_prompt(
        exercise_key="misinterpretationTechniques",
        sprint_question_label="Tease/Statement",
    ),
    evaluator_response_schema=EvaluationResult,
    evaluator_fallback=standard_evaluator_fallback,
    technique_picker=pick_random_technique,
)
