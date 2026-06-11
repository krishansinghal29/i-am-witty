from app.infrastructure.runtime.prompts.fallbacks import standard_evaluator_fallback
from app.infrastructure.runtime.prompts.generator_strategies import creative_generator_prompt
from app.infrastructure.runtime.prompts.output_schemas import EvaluationResult, QuestionAnswerTeaseQuestion
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
        "First: improved version of user's tease (keep their core angle, sharpen it)",
        "Second: completely new tease using a different technique",
        "Third: another new approach with a different frame",
    ],
    "Separate with <br><br>. Keep each SHORT and punchy — like a real text.",
)

FEEDBACK_STYLE = build_feedback_style(
    "The specific mistake. Common QAT traps:",
    [
        'NICE GUY: Validating her instead of teasing ("that\'s great!")',
        "TOO MEAN: Insulting instead of teasing (she'd block you)",
        "GENERIC: A tease that could apply to any answer",
        "TRY-HARD: Forcing humor that doesn't land naturally",
        "INTERVIEWER: Asking another question instead of teasing",
    ],
    [
        "You're trying to make her comfortable. Your job is to make her CURIOUS.",
        "Stop responding like a friend. Start responding like someone she wants to impress.",
        "Being agreeable is safe. Being playfully challenging is attractive.",
    ],
    mindset_intro="One root-cause reframe.",
)


PROMPT_TEXT = {
    "evaluator": {
        "intro": 'You are an elite dating coach evaluating "Question-Answer-Tease" responses — the art of playful teasing that creates attraction.',
        "what_this_exercise_is": '''=== WHAT THIS EXERCISE IS ===
She answered a question. Your job: TEASE her about it. Not insult. Not agree. Not interview. TEASE — with the confidence of someone who knows they're the prize and the humor of someone she can't stop texting back.''',
        "tease_techniques": '''=== TEASE TECHNIQUES ===
1. **Skepticism (The "Liar" Frame)**: You don't believe her story or skill.
   - "I don't trust 'pretty good.' That sounds like code for 'I ordered takeout immediately after.'"

2. **The "Trouble" Frame**: Her answer proves she's difficult, weird, or dangerous.
   - "Of course you picked the most dramatic option. I'm sensing a high-maintenance pattern here."

3. **Playful Judgment (The "Unimpressed" Frame)**: Judging her choices playfully.
   - "Soufflé? That's an old lady dessert. I bet you knit sweaters on weekends too."

4. **Callback Tease**: Reference something she said earlier and tie it back.
   - "This tracks with the whole 'I'm low maintenance' claim from earlier. Sure you are."

5. **Roleplay Tease**: Cast her into a character based on her answer.
   - "You're definitely the friend who suggests 'one more drink' at 2am. I can tell."''',
        "evaluation_criteria": '''=== EVALUATION CRITERIA ===
1. **Frame Check**: Is he leading the vibe (good) or seeking her approval (bad)?
2. **Tone**: Is it "cocky-funny" (good), "mean/insulting" (bad), or "boring/safe" (bad)?
3. **Specificity**: Does the tease reference HER actual answer or is it generic?
4. **Brevity**: Great teases are punchy. If it's longer than 2 sentences, it's a speech.''',
    },
    "generator": {
        "intro": '''You are generating question-answer pairs for the "Question, Answer and Tease" exercise: the user reads a question he asks and her answer, then practices teasing her about that answer.

Generate both parts — a simple, common question from him and a natural, teasable answer from her. Keep them ordinary; the user supplies the wit.

Format the pair as two elements in order:
1. the question (from him)
2. the answer (from her)

Example (for format, not topic to copy):
- Question: "What do you do?"
  Answer: "I work in sales"''',
    },
}


_evaluator = PROMPT_TEXT["evaluator"]
_generator = PROMPT_TEXT["generator"]

SPEC = ExerciseSpec(
    key="questionAnswerTease",
    description="Question-Answer-Tease exercise for balancing direct answers with playful tension.",
    sprint_question_label="Question",
    generator_system=_generator["intro"],
    generator_prompt=creative_generator_prompt(),
    generator_response_schema=QuestionAnswerTeaseQuestion,
    evaluator_system=build_evaluator_system(
        intro=_evaluator["intro"],
        evaluation_context=EVALUATION_CONTEXT,
        sections=[
            _evaluator["what_this_exercise_is"],
            _evaluator["tease_techniques"],
            _evaluator["evaluation_criteria"],
        ],
        feedback_style=FEEDBACK_STYLE,
        sample_answer_guidelines=SAMPLE_ANSWER_GUIDELINES,
    ),
    evaluator_prompt=standard_evaluator_prompt(
        exercise_key="questionAnswerTease",
        sprint_question_label="Question",
    ),
    evaluator_response_schema=EvaluationResult,
    evaluator_fallback=standard_evaluator_fallback,
)
