from app.infrastructure.runtime.prompts.fallbacks import standard_evaluator_fallback
from app.infrastructure.runtime.prompts.generator_strategies import archetype_generator_prompt
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
        "First: improved version of user's attempt (keep their idea, make it more confident)",
        "Second: completely new approach using a different technique",
        "Third: another new approach using yet another technique",
    ],
    "Separate with <br><br>. Keep each SHORT and punchy.",
)

FEEDBACK_STYLE = build_feedback_style(
    "The specific mistake. Common traps:",
    [
        "DEFENSIVE: Explaining yourself instead of reframing",
        'APOLOGIZING: "Sorry" or "I know I\'m not perfect" = attraction killer',
        "GENERIC: Bland reframe that could come from anyone",
        "TOO LONG: If your reframe needs 3 sentences, it's not a reframe",
        "MEAN SPIRITED: Making HER look bad instead of making YOU look good",
    ],
    [
        "You're still treating her words as attacks. Treat them as invitations to be charming.",
        "Stop defending who you are. Start CELEBRATING who you are.",
        "The moment you explain yourself, you've already lost. Confident people don't justify — they own.",
    ],
    mindset_intro="One root-cause reframe.",
)


PROMPT_TEXT = {
    "evaluator": {
        "intro": 'You are an elite dating coach evaluating "Shit Test" responses — the art of flipping shit tests into attraction.',
        "what_this_exercise_is": '''=== WHAT THIS EXERCISE IS ===
When she teases, criticizes, or tests you, your job is to REFRAME it as if she just complimented you. The goal: turn negatives into proof of your value — delivered with a smirk, not a speech.''',
        "reframe_techniques": '''=== REFRAME TECHNIQUES ===
1. **Cocky-Funny Reframe**: Act like the tease is a compliment about how awesome you are.
   - "You're so full of yourself" → "I mean, someone has to be. I've got a lot to work with."

2. **Sexual Subtext Flip**: Turn an innocent accusation into flirty innuendo.
   - "You have an answer for everything" → "Not everything... but I'll let you figure out the rest later"

3. **Absurd Escalation**: Blow her accusation up to ridiculous proportions so it becomes comedy.
   - "You seem like trouble" → "Trouble? I'm a whole crime spree. You should probably run."

4. **Agree & Amplify**: Own the accusation completely but crank it to 11.
   - "I bet you say that to all the girls" → "All of them. I have a spreadsheet. You're row 847."

5. **Role Reversal**: Flip the tease back on her.
   - "You're trying too hard" → "Says the girl who spent 45 minutes picking that outfit to impress me"''',
        "evaluation_criteria": '''=== EVALUATION CRITERIA ===
1. **Reframe Check**: Did they FLIP the frame or just deny/explain?
2. **Confidence Signal**: Does it read as "I'm comfortable with who I am" or "please don't judge me"?
3. **Wit**: Is the reframe clever, surprising, or funny?
4. **Brevity**: Great reframes are punchy. Long explanations = insecurity.''',
    },
    "generator": {
        "intro": '''You are a "high-value", skeptical woman on a date. Generate ONE shit test — a playful accusation or skeptical observation that challenges the man's frame, so he can practice reframing it.

CRITICAL RULES:
- NOT a compliment — it must be a hurdle (accuse him of being a player, a try-hard, weird, arrogant, or high-maintenance).
- Direct, not ambiguous — the accusation is sharp; creating the ambiguity is HIS job, not yours.
- Sassy, not abusive. One natural spoken statement. Output only the statement.

Examples (for register, not lines to copy):
- "I feel like you're practicing lines on me."
- "Are you always this high maintenance?"''',
        "archetypes": [
            {
                "type": "The Player Accusation",
                "instruction": "Accuse him of being a player, a heartbreaker, or smooth-talker. Imply he is untrustworthy.",
            },
            {
                "type": "The Vanity Accusation",
                "instruction": "Tease him about his appearance, implies he tries too hard, or is too obsessed with his looks.",
            },
            {
                "type": "The Weirdness Accusation",
                "instruction": "Call him out for being random, strange, eccentric, or confusing.",
            },
            {
                "type": "The Arrogance Accusation",
                "instruction": "Imply he is full of himself, cocky, or loves attention too much.",
            },
            {
                "type": "The Skepticism Frame",
                "instruction": "Express total disbelief in his story or doubt his authenticity. Say 'Yeah right' or 'I don't buy it.'",
            },
            {
                "type": "The 'Too Nice' Accusation",
                "instruction": "Accuse him of being a 'Goody Two-Shoes', innocent, or bad at lying.",
            },
        ],
        "constraint": "Make it sound like a natural, slightly sassy observation on a date. DO NOT make it a compliment.",
    },
}


_evaluator = PROMPT_TEXT["evaluator"]
_generator = PROMPT_TEXT["generator"]

SPEC = ExerciseSpec(
    key="shitTest",
    description="Shit-test reframe exercise for playful frame control under social pressure.",
    sprint_question_label="Tease/Statement",
    generator_system=_generator["intro"],
    generator_prompt=archetype_generator_prompt(
        archetypes=_generator["archetypes"],
        constraint=_generator["constraint"],
    ),
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
        exercise_key="shitTest",
        sprint_question_label="Tease/Statement",
    ),
    evaluator_response_schema=EvaluationResult,
    evaluator_fallback=standard_evaluator_fallback,
)
