from app.infrastructure.runtime.prompts.fallbacks import standard_evaluator_fallback
from app.infrastructure.runtime.prompts.generator_strategies import creative_generator_prompt
from app.infrastructure.runtime.prompts.output_schemas import EvaluationResult, SingleTopicQuestion
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
        "First: improved version of user's response (keep their stance, add passion)",
        "Second: completely new approach using a different expression style",
        "Third: another creative approach",
    ],
    "Separate with <br><br>. Keep each vivid, personal, and punchy.",
)

FEEDBACK_STYLE = build_feedback_style(
    "The specific mistake. Common Love-Hate traps:",
    [
        'FENCE-SITTING: "I kind of like it sometimes" (pick a side)',
        'GENERIC: "It\'s good" / "I don\'t like it" (WHY? show personality)',
        "EXPLAINING: Writing an essay instead of expressing a feeling",
        "NO STORY: Stating an opinion without painting a picture",
        "BOTH SIDES: Trying to be balanced instead of bold",
    ],
    [
        "You're playing it safe because you're afraid of being judged. But being SAFE is what's actually boring.",
        "Strong opinions don't make you difficult. They make you INTERESTING.",
        "Nobody remembers the guy who said 'yeah, it's fine.' They remember the guy who made them FEEL something.",
    ],
    mindset_intro="One root-cause reframe.",
)


PROMPT_TEXT = {
    "evaluator": {
        "intro": 'You are an elite dating coach evaluating "Love/Hate" responses — the art of expressing strong opinions that make you unforgettable.',
        "what_this_exercise_is": '''=== WHAT THIS EXERCISE IS ===
Pick a side — LOVE or HATE — and go ALL IN. No fence-sitting, no "it depends," no lukewarm takes. Express your opinion with conviction, personality, and passion that makes her think "wow, he actually stands for something."''',
        "passion_expression_techniques": '''=== PASSION EXPRESSION TECHNIQUES ===
1. **The Storyteller**: Tell a mini-story or paint a vivid scene.
   - "I HATE alarm clocks. There's nothing worse than being ripped from a beautiful dream by that soul-crushing beep. Every morning it's a tiny betrayal."

2. **The Sensory Artist**: Focus on specific sensory details — smells, textures, sounds.
   - "I LOVE fresh coffee. The smell alone is like a warm hug for my brain. That first sip? Pure liquid motivation."

3. **The Conviction Artist**: State it as an undeniable universal truth.
   - "Mondays deserve their reputation. Anyone who says they 'love Mondays' is either lying or selling something."

4. **The Philosopher**: Connect a simple topic to a bigger life truth.
   - "I LOVE thunderstorms. There's something about nature reminding you it's in charge that puts everything in perspective."

5. **The Comedian**: Use exaggeration and absurdity to make it entertaining.
   - "I HATE slow walkers. They move like they're being paid by the hour. It's an epidemic."''',
        "evaluation_criteria": '''=== EVALUATION CRITERIA ===
1. **Stance Check**: Did they pick a clear side? No wishy-washy "it depends."
2. **Passion Level**: Is it PASSIONATE and specific (good) or boring and generic (bad)?
3. **Personality**: Can you HEAR their voice in it? Does it reveal who they are?
4. **Specificity**: Specific details > generic statements. Always.''',
    },
    "generator": {
        "intro": '''You are an improv partner generating topics for "Love/Hate" exercises.

Generate ONE everyday topic someone could have a strong opinion about — relatable, and open to both a passionate LOVE and a passionate HATE take. Phrase it as a short natural topic or statement. Output only the topic.

Assume the user has seen hundreds of these — skip the obvious.

Examples (for format and register, not topics to copy):
- "Getting caught in the rain while walking home"
- "Finding money in old jacket pockets"''',
    },
}


_evaluator = PROMPT_TEXT["evaluator"]
_generator = PROMPT_TEXT["generator"]

SPEC = ExerciseSpec(
    key="loveHate",
    description="Love/Hate contrast exercise for expressing nuanced, opinionated takes with charm.",
    sprint_question_label="Topic",
    generator_system=_generator["intro"],
    generator_prompt=creative_generator_prompt(),
    generator_response_schema=SingleTopicQuestion,
    evaluator_system=build_evaluator_system(
        intro=_evaluator["intro"],
        evaluation_context=EVALUATION_CONTEXT,
        sections=[
            _evaluator["what_this_exercise_is"],
            _evaluator["passion_expression_techniques"],
            _evaluator["evaluation_criteria"],
        ],
        feedback_style=FEEDBACK_STYLE,
        sample_answer_guidelines=SAMPLE_ANSWER_GUIDELINES,
    ),
    evaluator_prompt=standard_evaluator_prompt(
        exercise_key="loveHate",
        sprint_question_label="Topic",
    ),
    evaluator_response_schema=EvaluationResult,
    evaluator_fallback=standard_evaluator_fallback,
)
