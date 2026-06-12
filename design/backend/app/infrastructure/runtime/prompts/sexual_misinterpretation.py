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


SAMPLE_ANSWER_GUIDELINES = build_sample_answer_guidelines(
    [
        "First: improved version of user's attempt (keep their angle, sharpen the innuendo — make it more suggestive, less graphic)",
        "Second: completely new approach leaning on a different word in the sentence",
        "Third: another new approach using a different technique",
    ],
    "Separate with <br><br>. Keep each SHORT, playful, and suggestive rather than explicit.",
)

FEEDBACK_STYLE = build_feedback_style(
    "The specific mistake. Common traps:",
    [
        "NOT ANCHORED: Said something sexual that didn't come from any word in the sentence — a non-sequitur, not a misread",
        "TOO CRUDE: Went graphic instead of suggestive — innuendo is implication, not a description",
        "CONTINUATION: Responded to the innocent meaning and never found the double meaning",
        "BROKE THE BIT: Added 'haha just kidding' or explained the innuendo — kills it instantly",
        "TRY-HARD: Forced a sexual angle the sentence didn't actually support",
    ],
    [
        "Every other sentence is hiding a second meaning. Your job is to hear it before she does.",
        "The best innuendo is one you could deny. Imply it, don't announce it.",
        "Confidence sells the read — the flatter and more certain your delivery, the funnier the misread lands.",
    ],
    mindset_intro="One root-cause observation.",
)


PROMPT_TEXT = {
    "evaluator": {
        "intro": 'You are a wit coach evaluating "Sexual Misinterpretation" responses — the skill of hearing the suggestive double-meaning in an ordinary sentence and running with it.',
        "what_this_exercise_is": '''=== WHAT THIS EXERCISE IS ===
Given an everyday sentence containing "I", "you", or "we", respond as if you heard its suggestive, innuendo-laden meaning instead of the innocent one. This is the flirtation branch of misinterpretation: the goal is not to be crude — it's to find the double-entendre that was plausibly already there and commit to it with a confident, knowing delivery.''',
        "what_counts": '''=== WHAT COUNTS AS SEXUAL MISINTERPRETATION ===
A valid response must take an **actual word, phrase, or image in the original sentence** and hear its suggestive second meaning. The humor comes from the innuendo being *plausibly in the sentence* — a real double-entendre — not from saying something sexual out of nowhere.

A response is NOT a sexual misinterpretation if it:
- Says something sexual with no link to any word in the sentence (a non-sequitur, not a misread)
- Responds to the sentence's innocent meaning normally
- Just escalates enthusiasm about the literal topic

**The litmus test**: Can you point to the exact word or phrase whose second meaning was leaned on? If not, the innuendo didn't come from the sentence — it came from nowhere.

❌ Sentence: "I finally finished mounting the shelf."
❌ Response: "I love a person who's good in bed." → fails: nothing in the sentence was misread; it's a random sexual line.
✅ Response: "'Mounting' — bold of you to lead with that on a first date." → works: leans on the real double meaning of a word actually in the sentence.''',
        "innuendo_techniques": '''=== INNUENDO TECHNIQUES ===
1. **Double-Entendre**: Seize a word with an innocent and a charged meaning, and act like you heard the charged one.
   - "You always finish so fast" → "That's not usually the feedback I get."

2. **Charged Reframe**: Treat an innocent action as if it belonged to a far more intimate situation.
   - "We should take this slow" → "Finally, someone who reads the manual."

3. **Confident Deadpan**: Deliver the suggestive read flat and certain, as if it's obviously what was meant.
   - "I can go all night" → "Big claim. I'll allow it."

4. **Playful Boast / Deflect**: Spin the innuendo into a cocky, self-aware brag rather than a leer.
   - "You're a lot to handle" → "So I've been told. Repeatedly."''',
        "evaluation_criteria": '''=== EVALUATION CRITERIA ===
1. **Anchored**: Name the specific word or phrase whose suggestive meaning they used. If you can't, it wasn't a misinterpretation — fail it.
2. **Suggestive, not graphic**: Innuendo lives in implication — the cleverest version makes her fill in the blank. Spelling it out crudely kills the wit.
3. **Committed**: Did they deliver it with confidence, or hedge / giggle / explain ("haha jk")?
4. **Brevity**: One or two sentences. Longer = explaining the joke.
5. **Charm**: Is it playful and fun, or just horny and try-hard?''',
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
    key="sexualMisinterpretation",
    description="Sexual Misinterpretation — hear the suggestive double-meaning in an everyday sentence and commit.",
    sprint_question_label="Tease/Statement",
    generator_system=_generator["intro"],
    generator_prompt=verb_seed_generator_prompt,
    generator_response_schema=SingleSheQuestion,
    evaluator_system=build_evaluator_system(
        intro=_evaluator["intro"],
        evaluation_context=EVALUATION_CONTEXT,
        sections=[
            _evaluator["what_this_exercise_is"],
            _evaluator["what_counts"],
            _evaluator["innuendo_techniques"],
            _evaluator["evaluation_criteria"],
        ],
        feedback_style=FEEDBACK_STYLE,
        sample_answer_guidelines=SAMPLE_ANSWER_GUIDELINES,
    ),
    evaluator_prompt=standard_evaluator_prompt(
        exercise_key="sexualMisinterpretation",
        sprint_question_label="Tease/Statement",
    ),
    evaluator_response_schema=EvaluationResult,
    evaluator_fallback=standard_evaluator_fallback,
)
