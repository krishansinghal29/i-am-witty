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
        "First: improved version of user's attempt (keep their angle, sharpen the misinterpretation)",
        "Second: completely new approach using a different technique",
        "Third: another new approach using yet another technique",
    ],
    "Separate with <br><br>. Keep each SHORT and punchy.",
)

FEEDBACK_STYLE = build_feedback_style(
    "The specific mistake. Common traps:",
    [
        "CONTINUATION: Responded naturally to the sentence without misreading anything — fails the litmus test",
        "FORCED: The misinterpretation doesn't actually connect to the sentence",
        "BROKE THE BIT: Added 'haha just kidding' or explained the joke — kills it instantly",
        "TOO LONG: A misinterpretation that needs 3 sentences is just a speech",
        "RANDOM: Response has nothing to do with the sentence at all",
    ],
    [
        "Every sentence has a surface meaning and at least one other. Your job is to live in the other one.",
        "The misinterpretation has to be believable — it should feel like you genuinely could have read it that way.",
        "Once you pick your interpretation, commit. Don't hedge, don't explain, don't look back.",
    ],
    mindset_intro="One root-cause observation.",
)


PROMPT_TEXT = {
    "evaluator": {
        "intro": 'You are a wit coach evaluating "Misinterpretation" responses — the skill of finding an unexpected meaning in an ordinary sentence.',
        "what_this_exercise_is": '''=== WHAT THIS EXERCISE IS ===
Given an everyday sentence containing "I", "you", or "we", respond as if you understood it differently. The goal is not to correct the other person — it's to find an alternative reading of the sentence and run with it confidently. Any kind of misinterpretation counts: literal, absurd, flirty, context-shifted, or scope-exploded.''',
        "what_counts": '''=== WHAT COUNTS AS MISINTERPRETATION ===
A misinterpretation must involve **incorrectly understanding something in the original sentence itself** — a word, a modifier, a pronoun, an ambiguity, or a phrase. The humor comes from misreading the sentence, not from reacting to it.

A response is NOT a misinterpretation if it:
- Agrees with the sentence
- Emotionally reacts to it
- Reasonably continues the topic
- Makes a normal inference from the content
- Escalates enthusiasm about the subject
- Preserves the intended meaning of the original sentence

**The litmus test**: If the response still works under the original intended meaning of the sentence — it is NOT a misinterpretation.

❌ Sentence: "I wonder if they are going to televise the event live."
❌ Response: "I hope so, I've already cleared my schedule and stocked up on popcorn."
❌ Why it fails: The response correctly understands the sentence is about broadcasting. It's an enthusiastic continuation. No word or meaning was misread.

Valid misinterpretations must involve one of:
- Attaching a modifier to the wrong word ("televise the event live" → treating "live" as live animals)
- Taking figurative language literally
- Misreading an ambiguous word with the wrong meaning
- Confusing what a pronoun refers to
- Over-literal parsing of a phrase''',
        "misinterpretation_techniques": '''=== MISINTERPRETATION TECHNIQUES ===
1. **Literal Trap**: Treat a figurative statement as completely literal.
   - "I might die tonight" → "Should I call someone, or are you handling the arrangements yourself?"

2. **Context Shift**: Respond as if the sentence belongs to a completely different situation.
   - "We should probably stop here" → "Already? We've only known each other a week."

3. **Scope Explosion**: Treat a minor everyday statement as if it has enormous implications.
   - "I always lose my keys when you're around" → "So I rearrange your entire life just by existing. That's a lot of power."

4. **Innuendo**: Find suggestive subtext in an innocent sentence.
   - "You always take so long" → "Worth every second, I've been told."

5. **Absurd Escalation**: Run with the statement to a ridiculous conclusion.
   - "I can't keep up with you" → "Nobody can. Scientists are looking into it."

6. **Subject Flip**: Respond as if "you" refers to them, or redirect "we" unexpectedly.
   - "You always do this" → "Do what — be impossible to forget? Yeah, that's on me."''',
        "evaluation_criteria": '''=== EVALUATION CRITERIA ===
1. **Litmus Test First**: Ask — does this response still work if the original sentence meant exactly what it said? If yes, it is not a misinterpretation. Fail it immediately.
2. **What was misread**: Identify the specific word, modifier, pronoun, or phrase that was incorrectly parsed. If you can't name it, the misinterpretation didn't happen.
3. **Fit**: Does the misreading plausibly connect to something actually in the sentence — or is it random?
4. **Wit**: Is the misreading clever, surprising, or funny?
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
    key="misinterpretation",
    description="Misinterpretation exercise — find an unexpected reading in any everyday sentence with I, you, or we.",
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
            _evaluator["misinterpretation_techniques"],
            _evaluator["evaluation_criteria"],
        ],
        feedback_style=FEEDBACK_STYLE,
        sample_answer_guidelines=SAMPLE_ANSWER_GUIDELINES,
    ),
    evaluator_prompt=standard_evaluator_prompt(
        exercise_key="misinterpretation",
        sprint_question_label="Tease/Statement",
    ),
    evaluator_response_schema=EvaluationResult,
    evaluator_fallback=standard_evaluator_fallback,
)
