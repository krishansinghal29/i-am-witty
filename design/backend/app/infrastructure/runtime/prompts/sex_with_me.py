from app.infrastructure.runtime.prompts.fallbacks import standard_evaluator_fallback
from app.infrastructure.runtime.prompts.generator_strategies import archetype_generator_prompt
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
        "First: improved version of the user's best attempt (keep their subject mapping, sharpen the punch)",
        "Second: a completely different angle on the same setup (e.g. self-deprecating vs boastful)",
        "Third: an absurd or unexpected take on the same setup",
    ],
    "Separate with <br><br>. Keep each a tight one-liner — a real trait of the subject mapped onto sex.",
)

FEEDBACK_STYLE = build_feedback_style(
    "The specific mistake. Common traps:",
    [
        "IGNORED THE SUBJECT: A generic sex joke that would work for any X — the comparison has to be ABOUT this subject",
        "NO PARALLEL: The punchline doesn't map a real trait of X onto anything — the link is arbitrary",
        "FLAT: Took the first, most obvious comparison with no twist or surprise",
        "TOO LONG: Explained the joke instead of landing it — punchlines are short",
        "ONE-NOTE: All the attempts were the same joke reworded — no range",
    ],
    [
        "Start from the subject, not from sex. List what's TRUE about X first, then find which trait maps.",
        "The funniest map is the one nobody saw coming but everyone recognizes the second you say it.",
        "Three swings means three different angles — self-deprecating, boastful, absurd — not one joke three times.",
    ],
    mindset_intro="One root-cause observation.",
)


PROMPT_TEXT = {
    "evaluator": {
        "intro": 'You are a comedy coach evaluating "Sex with me is like ___" responses — the skill of landing a punchy analogy that maps a real trait of the subject onto sex.',
        "what_this_exercise_is": '''=== WHAT THIS EXERCISE IS ===
The user is given a setup — "Sex with me is like X" — and must finish it with a punchline: a comparison that takes a real, recognizable trait of X and maps it onto sex, ideally with a self-aware spin (self-deprecating OR boastful). The user gives SEVERAL attempts (at least three) — evaluate the set as a batch.''',
        "how_the_joke_works": '''=== HOW THE JOKE WORKS ===
A great answer has three things:
1. **A real trait of X**: it uses something genuinely true or well-known about the subject — its mechanics, reputation, quirks, or stereotype.
2. **A clean mapping**: that trait maps onto sex (or being with them) in a way the listener instantly recognizes.
3. **A turn**: the funniest versions add a self-aware angle — self-deprecating or boastful — rather than a flat literal comparison.

Example: "Sex with me is like IKEA — hard to assemble, missing parts, and ends in an argument." Each clause is a real IKEA trait mapped onto a relatable sex/relationship truth.''',
        "evaluation_criteria": '''=== EVALUATION CRITERIA ===
Across their attempts:
1. **Uses the subject**: Does the punchline actually play off the given X — or is it a generic sex joke that ignores the subject? Generic = fail.
2. **Real parallel**: Is there a genuine, recognizable trait of X being mapped — or is the connection arbitrary?
3. **Surprise**: Is it unexpected, or the first obvious thing anyone would say?
4. **Punch**: Is it a tight one-liner that lands fast, or does it ramble and explain itself?
5. **Range** (batch): Across the three+ attempts, did they find different angles — or rewrite the same joke three times?''',
    },
    "generator": {
        "intro": '''You generate setup lines for the "Sex with me is like ___" comedy exercise.

The user is given your setup — "Sex with me is like X" — and practices finishing it with a punchline: a witty comparison that maps a real trait of X onto sex.

Your only job is to produce the SETUP — a single subject X to compare to, in the exact form:
"Sex with me is like <X>."

Rules:
- X should have rich comedic potential — something with recognizable traits, quirks, or a reputation a punchline can play off.
- Do NOT write the punchline, the "because...", or any explanation. Just the setup line.
- Output only the line, nothing else.

Examples (for format, not subjects to copy):
- "Sex with me is like a vending machine."
- "Sex with me is like jury duty."''',
        "categories": [
            {
                "type": "Everyday Object",
                "instruction": "Pick a common, concrete everyday object or appliance whose mechanics, quirks, or reputation could map onto sex.",
            },
            {
                "type": "Abstract Concept",
                "instruction": "Pick an abstract concept, ideology, or social topic that people have opinions about.",
            },
            {
                "type": "Activity or Hobby",
                "instruction": "Pick a physical activity, sport, or hobby.",
            },
            {
                "type": "Place or Business",
                "instruction": "Pick a recognizable type of place, store, or business.",
            },
        ],
        "constraint": 'Output ONLY the setup line in the exact form: "Sex with me is like <X>." Pick an X with rich comedic potential. Do NOT write the punchline or any explanation.',
    },
}


_evaluator = PROMPT_TEXT["evaluator"]
_generator = PROMPT_TEXT["generator"]

SPEC = ExerciseSpec(
    key="sexWithMeIsLike",
    description="Sex With Me Is Like — finish the analogy with a punchline that maps a real trait of the subject onto sex.",
    sprint_question_label="Setup",
    generator_system=_generator["intro"],
    generator_prompt=archetype_generator_prompt(
        archetypes=_generator["categories"],
        constraint=_generator["constraint"],
    ),
    generator_response_schema=SingleTopicQuestion,
    evaluator_system=build_evaluator_system(
        intro=_evaluator["intro"],
        evaluation_context=EVALUATION_CONTEXT,
        sections=[
            _evaluator["what_this_exercise_is"],
            _evaluator["how_the_joke_works"],
            _evaluator["evaluation_criteria"],
        ],
        feedback_style=FEEDBACK_STYLE,
        sample_answer_guidelines=SAMPLE_ANSWER_GUIDELINES,
    ),
    evaluator_prompt=standard_evaluator_prompt(
        exercise_key="sexWithMeIsLike",
        sprint_question_label="Setup",
    ),
    evaluator_response_schema=EvaluationResult,
    evaluator_fallback=standard_evaluator_fallback,
)
