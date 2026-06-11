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
        "First: improved version of user's attempt (keep their core idea, add poetry)",
        "Second: completely new reframe using a different technique",
        "Third: another creative approach",
    ],
    "Separate with <br><br>. Keep each vivid, confident, and compelling.",
)

FEEDBACK_STYLE = build_feedback_style(
    "The specific mistake. Common If-By-X traps:",
    [
        'LITERAL SWAP: Just replacing one word with a synonym ("If by X you mean being independent")',
        "DEFENSIVE: Explaining yourself instead of reframing with flair",
        "FLAT: A correct structure but zero poetry, zero punch",
        "TOO LONG: Great reframes are punchy, not paragraphs",
        "MEAN-SPIRITED: Attacking her instead of elevating yourself",
    ],
    [
        "Don't just SWAP the word. PAINT A PICTURE. Make her SEE the world you're describing.",
        "Your reframe should make her forget what she originally said because YOUR version is so much more interesting.",
        "Think of it like this: she's handing you clay. Don't hand it back — sculpt something beautiful.",
    ],
    mindset_intro="One root-cause reframe.",
)


PROMPT_TEXT = {
    "evaluator": {
        "intro": 'You are an elite dating coach evaluating "If By X You Mean Y" responses — verbal aikido for redirecting criticism into attraction.',
        "what_this_exercise_is": '''=== WHAT THIS EXERCISE IS ===
When she challenges or criticizes you, use the "If by X you mean Y" structure to TRANSFORM the criticism into something compelling. Don't defend. Don't explain. REFRAME — make her criticism sound like it was actually a compliment all along.''',
        "reframe_techniques": '''=== REFRAME TECHNIQUES ===
1. **Status Flip**: Transform criticism into proof of your high value.
   - "If by living in my own world you mean I've built a universe where imagination thrives and possibility has no limits — then yes, I'm proudly the architect of dreams."

2. **Positive Reframe**: Turn the negative into a genuine positive with vivid language.
   - "If by not following rules you mean I write my own playbook while everyone else is busy memorizing someone else's — then I'm the author, editor, AND publisher."

3. **Humorous Escalation**: Take the criticism to an absurd extreme that's obviously playful.
   - "If by always late you mean I operate on island time where stress doesn't exist and happiness is mandatory — then I'm permanently 3 hours behind and loving it."

4. **Sexual/Flirty Redirect**: Turn criticism into flirty innuendo.
   - "If by talking too much you mean my words are a river and you're invited to float — then bring a towel."

5. **Meta-Commentary**: Turn the frame back on HER.
   - "If by too much you mean more than the silence you're used to — then welcome to full surround sound."''',
        "evaluation_criteria": '''=== EVALUATION CRITERIA ===
1. **Structure Check**: Did they use the proper "If by X, you mean Y" format?
2. **Transformation Quality**: Did they TRANSFORM the criticism or just synonym-swap?
3. **Poetry Level**: Is it vivid and compelling, or flat and literal?
4. **Confidence Signal**: Does it read as confident and charming, or defensive?''',
    },
    "generator": {
        "intro": '''You are an improv partner generating prompts for "If by X, you mean Y" exercises.

Generate ONE statement that sounds like a criticism or negative judgment of a person but is ambiguous enough to be cleverly reframed as a positive. Output only the statement — the criticism itself, not the reframe.

Assume the user has practiced hundreds of these — skip the obvious.

Examples (for format and register, not topics to copy):
- "You're always living in your own little world"
- "You avoid confrontation at all costs"''',
    },
}


_evaluator = PROMPT_TEXT["evaluator"]
_generator = PROMPT_TEXT["generator"]

SPEC = ExerciseSpec(
    key="ifByXYouMeanY",
    description="If-by-X-you-mean-Y verbal reframe exercise for redirecting criticism into status.",
    sprint_question_label="Statement",
    generator_system=_generator["intro"],
    generator_prompt=creative_generator_prompt(),
    generator_response_schema=SingleSheQuestion,
    evaluator_system=build_evaluator_system(
        intro=_evaluator["intro"],
        evaluation_context=EVALUATION_CONTEXT,
        sections=[
            _evaluator["what_this_exercise_is"],
            _evaluator["reframe_techniques"],
            _evaluator["evaluation_criteria"],
        ],
        feedback_style=FEEDBACK_STYLE,
        sample_answer_guidelines=SAMPLE_ANSWER_GUIDELINES,
    ),
    evaluator_prompt=standard_evaluator_prompt(
        exercise_key="ifByXYouMeanY",
        sprint_question_label="Statement",
    ),
    evaluator_response_schema=EvaluationResult,
    evaluator_fallback=standard_evaluator_fallback,
)
