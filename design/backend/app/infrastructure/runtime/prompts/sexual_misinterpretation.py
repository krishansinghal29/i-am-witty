from app.infrastructure.runtime.prompts.fallbacks import standard_evaluator_fallback
from app.infrastructure.runtime.prompts.generator_strategies import relatable_seed_generator_prompt
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
        "First: improved version of user's attempt (keep their angle — sexual or compliment — and sharpen it; suggestive, not graphic)",
        "Second: a completely new approach grabbing a different handle in the line (a different word, the action, or the whole scenario)",
        "Third: another new approach using a different technique (e.g. flip a sexual read to a flattering one, or vice versa)",
    ],
    "Separate with <br><br>. Keep each SHORT, playful, and suggestive rather than explicit.",
)

FEEDBACK_STYLE = build_feedback_style(
    "The specific mistake. Common traps:",
    [
        "NON-SEQUITUR: Said something charged that didn't spring from the line — it'd fit under almost any sentence",
        "TOO CRUDE: Went graphic instead of suggestive — implication, not a description",
        "CONTINUATION: Took the line at face value and never reframed it",
        "BROKE THE BIT: Added 'haha just kidding' or explained the joke — kills it instantly",
        "TRY-HARD: Forced an angle the line didn't actually support",
    ],
    [
        "The line is innocent — the move is to decide it wasn't, and say so with a straight face.",
        "The best read is one you could deny. Imply it, don't announce it.",
        "Confidence sells the read — the flatter and more certain your delivery, the funnier it lands.",
    ],
    mindset_intro="One root-cause observation.",
)


PROMPT_TEXT = {
    "evaluator": {
        "intro": 'You are a wit coach evaluating "Sexual Misinterpretation" responses — the skill of taking an ordinary, innocent line and choosing to hear it as a flirty advance or a compliment aimed your way, then committing to that read.',
        "what_this_exercise_is": '''=== WHAT THIS EXERCISE IS ===
Given an everyday, innocent sentence containing "I", "you", or "we", the learner responds as if they heard it as a charged advance or a compliment aimed their way. The line itself is plain — usually there is NO pun sitting in it to "find". The skill is to impose a flirty or flattering reading that still plausibly springs from the line, and deliver it with confident, knowing deadpan. The goal is not to be crude — it's to make an innocent line sound like it meant something more, in a way she can't quite deny.''',
        "what_counts": '''=== WHAT COUNTS ===
A valid response re-casts something in the line — a word, the action, the image, or the whole scenario — as a sexual/flirty advance OR a compliment aimed at the speaker, and commits to it. Either target counts. The charged read must plausibly spring from THIS line, not from nowhere.

**The portability test** (use this instead of hunting for a single pun): could the learner's response follow almost ANY sentence? If yes, it's a generic line that didn't come from this one — fail it. If it's specifically keyed to something in this line, it counts — even when no single word has a dictionary double-meaning.

A response is NOT a valid misinterpretation if it:
- Could be pasted under any sentence (a generic charged line that doesn't spring from this one)
- Takes the line at face value and responds normally
- Just escalates enthusiasm about the literal topic

❌ Line: "I need to standardize these forms before we send them out."
❌ Response: "I love someone who's good in bed." → fails the portability test: it fits under any line; nothing here was reframed.
✅ Line (innocent, no pun): "I've been on my feet all day." → "You're welcome to get off them at my place." → works: the advance springs from her line (on her feet → off them, at mine), no double-entendre word needed.
✅ Compliment read: "You always know exactly what I need." → "Careful — talk like that and I'll think you've been studying me." → works: hears her plain line as her being into him, keyed to "know what I need".
✅ Line (easy, lexical anchor): "I finally finished mounting the shelf." → "'Mounting' — bold of you to lead with that on a first date." → works: leans on a real second meaning of a word in the line.''',
        "reframe_techniques": '''=== REFRAME TECHNIQUES ===
1. **Double-Entendre**: Seize a word with an innocent and a charged meaning, and act like you heard the charged one.
   - "You always finish so fast" → "That's not usually the feedback I get."

2. **Charged Reframe**: Treat an innocent action as if it belonged to a far more intimate situation.
   - "We should take this slow" → "Finally, someone who reads the manual."

3. **Into-Me Flip (compliment)**: Hear her plain line as her secretly flirting with or praising you, and accept it.
   - "You're a lot of work" → "And yet here you are, still interested. Telling."

4. **Confident Deadpan**: Deliver the read flat and certain, as if it's obviously what was meant.
   - "I can go all night" → "Big claim. I'll allow it."

5. **Playful Boast / Deflect**: Spin it into a cocky, self-aware brag rather than a leer.
   - "You're a lot to handle" → "So I've been told. Repeatedly."''',
        "evaluation_criteria": '''=== EVALUATION CRITERIA ===
1. **Springs from the line (portability test)**: Name what in the line they grabbed — a word, the action, the image, or the scenario. If their response would fit under almost any sentence, it came from nowhere — fail it.
2. **Suggestive, not graphic**: The read lives in implication — the cleverest version makes her fill in the blank. Spelling it out crudely kills the wit.
3. **Committed**: Did they deliver it with confidence, or hedge / giggle / explain ("haha jk")?
4. **Brevity**: One or two sentences. Longer = explaining the joke.
5. **Charm**: Is it playful and fun, or just horny / try-hard?''',
    },
    "generator": {
        "intro": '''You generate the opening line for a flirting-practice drill.

The learner's job — NOT yours — is to take an ordinary line and playfully reframe it as a sexual advance or a backhanded compliment. Your only job is to hand them a believable, ordinary line to work with.

You are given a random seed word (a verb, adjective, or noun) and a pronoun. Write ONE line that:
- a real person would actually say out loud — relatable and natural, the kind of thing that comes up on a date or while two people are getting to know each other
- uses the given pronoun ("I", "you", or "we") naturally
- draws loosely on the seed word for freshness (use it or just its vibe — never force it)
- sounds completely innocent on its face: do NOT plant innuendo, do NOT make it suggestive, do NOT load it with a double meaning. It should read as plainly ordinary — the learner supplies the twist, not you.

Keep it to ONE short sentence in everyday words, no punctuation theatrics. Output only the sentence, nothing else.''',
    },
}


_evaluator = PROMPT_TEXT["evaluator"]
_generator = PROMPT_TEXT["generator"]

SPEC = ExerciseSpec(
    key="sexualMisinterpretation",
    description="Sexual Misinterpretation — hear the suggestive double-meaning in an everyday sentence and commit.",
    sprint_question_label="Tease/Statement",
    generator_system=_generator["intro"],
    generator_prompt=relatable_seed_generator_prompt,
    generator_response_schema=SingleSheQuestion,
    evaluator_system=build_evaluator_system(
        intro=_evaluator["intro"],
        evaluation_context=EVALUATION_CONTEXT,
        sections=[
            _evaluator["what_this_exercise_is"],
            _evaluator["what_counts"],
            _evaluator["reframe_techniques"],
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
