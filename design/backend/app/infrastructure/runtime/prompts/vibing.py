from app.infrastructure.runtime.prompts.fallbacks import standard_evaluator_fallback
from app.infrastructure.runtime.prompts.generator_strategies import creative_generator_prompt
from app.infrastructure.runtime.prompts.output_schemas import EvaluationResult, SingleStorytellerQuestion
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
        "First: improved version of user's attempt (anchor to their thread, add a real story or take)",
        "Second: picks a completely different thread from the vignette and asserts a story",
        "Third: same thread as the first, but a different angle (opinion vs. story vs. absurdity)",
    ],
    "Separate with <br><br>. Keep each confident, specific, and natural.",
)

FEEDBACK_STYLE = build_feedback_style(
    "The specific mistake. Common vibing traps:",
    [
        "GENERIC AGREE: 'Yeah totally / that's so relatable' — no specific thread picked, nothing added",
        "SUMMARIZER: Restated their story back to them instead of contributing something of your own",
        "QUESTIONER: Asked a question without first sharing your own perspective or story",
        "VALIDATOR: Praised or empathized without adding any content of your own",
        "TOPIC-HOPPER: Jumped to something unrelated to anything in the vignette",
    ],
    [
        "You're not there to be a mirror. You're there to be a person — someone with stories and takes of your own.",
        "The spark is when something they said hits you and you just go with it. Trust that hit.",
        "Confidence isn't about being loud. It's about saying your thing without asking permission first.",
    ],
    mindset_intro="One root-cause reframe.",
)


PROMPT_TEXT = {
    "evaluator": {
        "intro": 'You are a conversation coach evaluating "Vibing" responses — the skill of picking a thread from what someone says and jumping in with your own story, memory, or take.',
        "what_this_exercise_is": '''=== WHAT THIS EXERCISE IS ===
Vibing is thread-assertion: when someone shares a story, there are many topics in what they say. PICK one that sparks something in you and JUMP IN with your own story, memory, opinion, or take on it. This is how conversations gain momentum — not by mirroring, but by contributing.''',
        "vibing_techniques": '''=== VIBING TECHNIQUES ===
1. **Thread Anchor**: Name the specific thread you're jumping on, then go.
   - Vignette has a bus/school/independence thread → "The bus thing is real — I actually rode one for the first time in college and it was genuinely surreal."

2. **Personal Bridge**: Lead straight into your own memory or story on the thread.
   - Vignette mentions parents being protective → "My parents were exactly the same — I wasn't allowed to walk anywhere until I was 16, which made the day I finally could feel enormous."

3. **Opinionated Take**: Jump in with a clear, strong POV on the topic.
   - Vignette touches on specializing vs. variety → "I actually think doing one thing deeply is underrated — people who try everything rarely get good enough at anything to feel it."

4. **Shared Absurdity**: Riff on something funny or ironic in the thread.
   - Vignette has an unexpected irony → "The fact that you got more independent and less independent at the exact same time is kind of perfect — growing up is a scam."

5. **Contrast Story**: Your experience was the opposite — that contrast is interesting.
   - Vignette mentions rarely riding the bus → "Wait, I'm the reverse — I took the bus every single day and actually loved it. It was the only quiet time in my day."''',
        "evaluation_criteria": '''=== EVALUATION CRITERIA ===
1. **Thread Clarity**: Did they pick a specific, identifiable thread from the vignette — not just respond generically?
2. **Own Contribution**: Did they share their own story, memory, or opinion — not just validate or agree?
3. **Confidence**: Did they assert it without hedging, softening it excessively, or asking permission?
4. **Specificity**: Is it grounded in specific detail, not a generic "yeah I get that"?''',
    },
    "generator": {
        "intro": '''You generate short personal stories for a "Vibing" exercise — the user practices connecting with whoever shared it.

Generate ONE story told in the first person, the way someone would actually recount it out loud: a real, relatable everyday experience with a little emotional texture or a small reflection at the end. A few sentences — natural and specific, not a polished essay. Output only the story.

Assume the user has heard hundreds of these — skip the generic.

Example (for register and length, not topic to copy):
- "My first job was at a movie theater in high school. The free movies were great, but the popcorn-butter smell got into everything — even after I quit, my car smelled like a theater for months. My friends loved it; they said it was like having a portable cinema. I couldn't eat popcorn for two years after that."''',
    },
}


_evaluator = PROMPT_TEXT["evaluator"]
_generator = PROMPT_TEXT["generator"]

SPEC = ExerciseSpec(
    key="vibing",
    description="Vibing exercise — pick a thread from the vignette and jump in with your own story, take, or memory.",
    sprint_question_label="Vignette",
    generator_system=_generator["intro"],
    generator_prompt=creative_generator_prompt(
        # vibing collapses onto one favourite anecdote (the windowsill-plant story)
        # when a single spark word lands on a theme; two words force odd pairings
        # that break the attractor.
        spark_count=2,
    ),
    generator_response_schema=SingleStorytellerQuestion,
    evaluator_system=build_evaluator_system(
        intro=_evaluator["intro"],
        evaluation_context=EVALUATION_CONTEXT,
        sections=[
            _evaluator["what_this_exercise_is"],
            _evaluator["vibing_techniques"],
            _evaluator["evaluation_criteria"],
        ],
        feedback_style=FEEDBACK_STYLE,
        sample_answer_guidelines=SAMPLE_ANSWER_GUIDELINES,
    ),
    evaluator_prompt=standard_evaluator_prompt(
        exercise_key="vibing",
        sprint_question_label="Vignette",
    ),
    evaluator_response_schema=EvaluationResult,
    evaluator_fallback=standard_evaluator_fallback,
)
