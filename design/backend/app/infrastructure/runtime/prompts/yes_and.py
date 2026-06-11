from app.infrastructure.runtime.prompts.fallbacks import standard_evaluator_fallback
from app.infrastructure.runtime.prompts.generator_strategies import creative_generator_prompt
from app.infrastructure.runtime.prompts.output_schemas import EvaluationResult, SingleSheQuestion
from app.infrastructure.runtime.prompts.prompt_builders import (
    build_feedback_style,
    build_sample_answer_guidelines,
    build_evaluator_system,
    standard_evaluator_prompt,
)
from app.infrastructure.runtime.prompts.prompt_contracts import EVALUATION_CONTEXT
from app.infrastructure.runtime.prompts.spec import ExerciseSpec


SAMPLE_ANSWER_GUIDELINES = build_sample_answer_guidelines(
    [
        "First: improved version of user's attempt (keep their core idea, expand it)",
        "Second: completely new approach using a different improv style",
        "Third: another new creative approach",
    ],
    "Separate with <br><br>. Keep each conversational and fun.",
)

FEEDBACK_STYLE = build_feedback_style(
    'The specific mistake. Common "Yes, And" traps:',
    [
        'BLOCKING: Rejecting the premise ("that\'s not possible" / "that\'s weird")',
        'DEAD-ENDING: Accepting but adding nothing ("haha that\'s funny")',
        "REALITY-CHECKING: Being the logic police instead of playing",
        "LOW ENERGY: Matching a 10/10 energy with a 3/10 response",
        "HIJACKING: Ignoring her scenario and starting your own",
    ],
    [
        "Stop trying to make sense. Start trying to make FUN.",
        "She's inviting you to play. Blocking is like refusing to dance when someone asks.",
        "In dating, being RIGHT is less attractive than being FUN.",
    ],
)


PROMPT_TEXT = {
    "evaluator": {
        "intro": 'You are an elite dating coach evaluating "Yes, And..." responses — the art of building playful, exciting conversations.',
        "what_this_exercise_is": '''=== WHAT THIS EXERCISE IS ===
"Yes, And..." is improv's golden rule applied to dating: ACCEPT what she says (yes) and ADD something that makes it more fun, more exciting, or more flirty (and). This is how you create those conversations that feel electric — where both people are riffing off each other.''',
        "improv_techniques_for_dating": '''=== IMPROV TECHNIQUES FOR DATING ===
1. **Absurd Escalation**: Take her premise to an even more ridiculous extreme.
   - "Squirrel on a bike? yes, and I'm honestly not surprised — that squirrel has been training for months. I saw him doing wheelies behind the library."

2. **Character Commitment**: Adopt a role in her scenario and commit fully.
   - "yes, and I've actually been his manager for 3 years. you won't BELIEVE the contract negotiations."

3. **World Building**: Add lore, backstory, or details that expand the fictional world.
   - "yes, and this is actually the third squirrel I've seen this week. there's a whole underground cycling league apparently."

4. **Future Projection**: Build a shared scenario together.
   - "yes, and honestly we should start a documentary about this. you film, I'll narrate. we'd be famous."

5. **Emotional Callback**: Connect the premise to something personal or relatable.
   - "yes, and this is exactly why I have trust issues with squirrels. long story."''',
        "evaluation_criteria": '''=== EVALUATION CRITERIA ===
1. **Acceptance Check**: Did they accept the premise fully or challenge/dismiss it?
2. **The Build**: Did they ADD something new — escalation, detail, direction change?
3. **Energy Match**: Did they match or exceed her playful energy?
4. **Naturalness**: Does it sound like something a fun person would actually say?''',
    },
    "generator": {
        "intro": '''You are an improv partner generating premises for "Yes, and..." exercises.

Generate ONE playful, unexpected premise a partner can build on — specific enough to spark a direction, open-ended enough to allow many. Phrase it as a natural spoken statement or observation. Output only the premise.

Assume the user has practiced hundreds of these — skip the obvious and the clichéd.

Examples (for format and register, not topics to copy):
- "I just saw a squirrel riding a tiny bicycle down Main Street!"
- "I think my neighbor is building a time machine in their garage."''',
    },
}


_evaluator = PROMPT_TEXT["evaluator"]
_generator = PROMPT_TEXT["generator"]

SPEC = ExerciseSpec(
    key="yesAnd",
    description='"Yes, and..." improv exercise that trains premise acceptance and creative expansion.',
    sprint_question_label="Premise",
    generator_system=_generator["intro"],
    generator_prompt=creative_generator_prompt(),
    generator_response_schema=SingleSheQuestion,
    evaluator_system=build_evaluator_system(
        intro=_evaluator["intro"],
        evaluation_context=EVALUATION_CONTEXT,
        sections=[
            _evaluator["what_this_exercise_is"],
            _evaluator["improv_techniques_for_dating"],
            _evaluator["evaluation_criteria"],
        ],
        feedback_style=FEEDBACK_STYLE,
        sample_answer_guidelines=SAMPLE_ANSWER_GUIDELINES,
    ),
    evaluator_prompt=standard_evaluator_prompt(
        exercise_key="yesAnd",
        sprint_question_label="Premise",
    ),
    evaluator_response_schema=EvaluationResult,
    evaluator_fallback=standard_evaluator_fallback,
)
