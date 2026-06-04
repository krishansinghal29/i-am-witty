from prompts.fallbacks import standard_evaluator_fallback
from prompts.generator_strategies import verb_seed_generator_prompt
from prompts.output_schemas import EvaluationResult, SingleSheQuestion
from prompts.prompt_builders import (
    build_feedback_style,
    build_sample_answer_guidelines,
    build_evaluator_system,
    standard_evaluator_prompt,
)
from prompts.prompt_contracts import EVALUATION_CONTEXT
from prompts.spec import ExerciseSpec


# Local override: unlike other exercises, each sample answer is broken into the
# three beats of the move (ordinary detail → unusual thing → association) so the
# learner sees the anatomy, not just a finished one-liner.
FIRST_UNUSUAL_THING_OUTPUT_CONTRACT = '''=== STRUCTURED OUTPUT CONTRACT (CRITICAL) ===
The response schema has exactly these fields:
- feedback: HTML formatted feedback using the exact 4-section structure above: What Landed, The Trap, Level Up, Mindset Shift.
- sample_answer: 3 answers, each broken into 3 labeled lines, formatted exactly as described below.

Rules:
- feedback MUST follow the exact 4-section structure defined above.
- sample_answer must contain exactly 3 answers, separated by <br><br>.
- Each answer begins with its number (<b>1.</b>, <b>2.</b>, <b>3.</b>) followed by <br>, then exactly three lines separated by <br>, in this order:
  <b>Ordinary detail:</b> <the base-reality detail from the scene being tilted>
  <b>Unusual thing:</b> <the single deviation, stated straight as if normal>
  <b>Association:</b> <the "if this is true, what else is true" build, or an exaggeration of the tilt>
- Keep each line short and punchy. No text outside the three labeled lines.

Example of ONE answer's exact formatting:
<b>1.</b><br><b>Ordinary detail:</b> the TV's on in the background<br><b>Unusual thing:</b> I pause it whenever someone on screen stands up, out of respect<br><b>Association:</b> standing ovations are exhausting, but you don't skip them'''


SAMPLE_ANSWER_GUIDELINES = build_sample_answer_guidelines(
    [
        "First: improved version of user's attempt (keep their tilt, anchor it harder or commit more)",
        "Second: completely new approach using a different technique",
        "Third: another new approach using yet another technique",
    ],
    'Break EACH answer into three labeled lines — <b>Ordinary detail</b> (the scene detail being tilted), <b>Unusual thing</b> (the single deviation, stated straight), and <b>Association</b> (the "if this is true, what else is true" build, or an exaggeration of the tilt). Keep each line SHORT and anchored to the scene. See the structured output contract below for the exact <br> structure.',
)

FEEDBACK_STYLE = build_feedback_style(
    "The specific mistake. Common first-unusual-thing traps:",
    [
        "TOO NORMAL: Reacted to the scene without tilting anything — stayed in base reality, the #1 failure",
        "TOO RANDOM: Threw in chaos or a non-sequitur anchored to nothing — unusual but unbuildable",
        "FICTIONAL: Made the world magical — objects with feelings/memory, physics breaking — instead of revealing something odd about a real person. Keep the world real; put the strangeness in the PERSON (a compulsion, superstition, or ritual)",
        "MULTIPLE THINGS: Introduced several weird things at once, so there's no single game",
        "TOO BIG TOO FAST: Started at maximum absurdity with no base reality left to deviate from",
        "EXPLAINED IT: Justified or winked at the bit instead of committing to it",
    ],
    [
        "You don't need a big joke. The funniest move is one small, sincere deviation from normal.",
        "Keep almost everything ordinary — the tilt only reads as unusual against a normal background.",
        "Commit like it's a documentary. State the strange thing as plain fact and let it breathe.",
    ],
    mindset_intro="One root-cause observation.",
)


PROMPT_TEXT = {
    "evaluator": {
        "intro": 'You are a wit coach evaluating "First Unusual Thing" responses — the skill of taking a completely ordinary moment and introducing the ONE unusual thing that breaks its base reality and opens a game.',
        "what_this_exercise_is": '''=== WHAT THIS EXERCISE IS ===
You are given a deliberately mundane scene — a slice of ordinary, everyday reality with nothing funny in it yet. This is the **base reality**. Your job is to introduce the **first unusual thing**: the single small tilt that knocks the scene off-center and makes it interesting.

This is the engine of every funny conversation — the move that takes "how was your weekend" out of small-talk and into something worth playing with. The challenge is precision: NOT random chaos, NOT a big joke, but ONE grounded deviation you could build an entire bit on.''',
        "the_process": '''=== THE PROCESS (BASE REALITY → NOTICE → FRAME → ASSOCIATE) ===
A clean first-unusual-thing move walks through four beats. The scene gives you the first one; you supply the other three:

1. **Base Reality** (given): the ordinary world of the scene. You must keep most of it intact — if everything is weird, nothing is unusual.
2. **Notice**: spot the one ordinary detail you can twist. The best tilts come from a tiny deviation, not a big swing — a strange belief, an odd emotional reaction, an unexpected behavior, or a normal thing taken way too seriously.
3. **Frame / Label**: introduce the unusual thing and commit to it. State it like it's completely normal. Don't explain it, don't wink, don't hedge — one clear deviation, owned.
4. **Associate**: take the first step of "if this is true, what else is true?" — a single line that shows the tilt has a future and isn't a dead-end non-sequitur.

The strongest answers do Frame + Associate together: introduce the unusual thing AND begin building from it.''',
        "what_counts": '''=== WHAT COUNTS AS A FIRST UNUSUAL THING ===
A valid response must introduce **exactly one** deviation from the scene's base reality that is **anchored** to something in the scene and **buildable** into a game.

The tilt must stay **humanly real**: it reveals an odd belief, habit, reaction, compulsion, or ritual that a real PERSON could actually have. The physical world itself stays normal — floors don't have feelings, objects don't have memory, physics doesn't bend. If you catch yourself giving an object a superpower, move the strangeness back into the person (their compulsion about the object, their superstition or ritual around it). The funniest tilts make the listener think "I know someone exactly like that," not "that's fantasy."

A response FAILS if it:
- Stays in base reality — reacts normally, agrees, or continues the scene without tilting anything (TOO NORMAL)
- Throws in chaos or a non-sequitur with no connection to the scene — unusual but ungrounded, nothing to build on (TOO RANDOM)
- Makes the world magical or fictional — objects with feelings or memory, physics breaking, supernatural events — instead of revealing something odd about a real person (FICTIONAL)
- Introduces three weird things at once, so there's no single game (MULTIPLE THINGS)
- Starts at maximum absurdity with no base reality left to deviate from (TOO BIG TOO FAST)
- Explains, justifies, or winks at the bit instead of committing (EXPLAINED IT)

**The litmus test**: Can you point to the one ordinary thing in the scene that was tilted, AND can you imagine the next "if this is true, what else is true?" beat? If you can't name the single tilt, or it leads nowhere — it's not a clean first unusual thing.

❌ Scene: "I'm folding laundry while the TV plays in the background."
❌ Response: "Folding laundry is so boring, I hate it." → TOO NORMAL (stayed in base reality, just reacted).
❌ Response: "Suddenly a dragon made of taxes flew through the window screaming about Tuesdays." → TOO RANDOM (chaos, anchored to nothing, nowhere to build).
✅ Response: "I fold every shirt exactly the same way the store does — if it's off by an inch, it goes back in the basket." → ONE tilt (a strange over-serious ritual), anchored to the folding, and obviously buildable.

❌ Scene: "You scuffle your shoes on the doormat before stepping inside to keep the floor clean."
❌ Response: "The floor remembers who dirtied it and gets colder toward them." → FICTIONAL (gave the floor supernatural memory — the world stopped being real; the tilt should expose something odd about YOU, not magic about the floor).
✅ Response: "One speck gets through and I'm re-mopping the entire entryway — guests call it a quirk, I call it the bare minimum." → ONE tilt (a real, OCD-ish cleaning compulsion), the world stays normal, and it's obviously buildable.''',
        "unusual_thing_techniques": '''=== TECHNIQUES FOR INTRODUCING THE UNUSUAL THING ===
1. **Disproportionate Reaction**: Have a huge emotional reaction to something completely mundane in the scene.
   - "I'm at the laundromat." → "Watching that one sock tumble alone is the most emotional I've been all month. I'm not okay."

2. **Strange Belief**: Reveal an odd, sincere conviction about the ordinary thing.
   - "I'm waiting for my coffee." → "I never thank the barista. You thank them, they remember you, and then they own a piece of you forever."

3. **Oddly Specific Ritual / Rule**: A private rule or ritual that governs the everyday activity.
   - "I'm packing my bag for work." → "Pens go in left to right by how much I trust them. The clicky one hasn't earned a spot yet."

4. **Over-Valued Trifle**: Treat something trivial as enormously important.
   - "I'm picking a parking spot." → "This decision determines the entire moral arc of my day. No pressure."

5. **The Bad Idea** (harmless, self-directed): Voluntarily do the wrong-but-harmless thing, played straight.
   - "I'm making tea." → "I let it steep for exactly 47 minutes. That's how you build a tea with character."

6. **Tilt One Fact**: Keep everything normal except one detail that's just slightly off.
   - "I'm feeding my cat breakfast." → "Same time every day. He files a complaint if I'm late. In writing."''',
        "evaluation_criteria": '''=== EVALUATION CRITERIA ===
1. **Anchored (Notice)**: Name the specific ordinary detail from the scene that was tilted. If you can't point to it, the move was random — fail it.
2. **Singular & Committed (Frame)**: Is there exactly ONE clear deviation, stated straight as if normal? Multiple tilts, hedging, or "haha just kidding" all fail.
3. **Buildable (Associate)**: Could the next "if this is true, what else is true?" line obviously follow? Bonus if they already took that first step. Dead-end non-sequiturs fail.
4. **Grounded, Not Random**: Did they keep most of base reality intact, or blow up the whole scene? If everything is weird, nothing is unusual. The tilt must also be **humanly real** — an odd person, not a magical world. Floors don't have feelings; if an object got superpowers or physics bent, it failed (FICTIONAL). The strangeness belongs in the person's psychology (a belief, compulsion, ritual), not in the world's physics.
5. **Right Size**: A tiny, specific deviation beats a big loud joke. Did they tilt, or did they swing for the fences and miss the base reality?
6. **Brevity**: One or two sentences. Longer = explaining the bit instead of dropping it.
7. **Wit**: Is the tilt surprising and genuinely funny?
8. **History Awareness**: If they keep playing it safe (too normal) or keep going random, name the pattern.''',
    },
    "generator": {
        "intro": '''You generate mundane scenes for a "First Unusual Thing" exercise.

You receive a verb and a pronoun ("I", "you", or "we"). Write ONE short, deliberately ORDINARY scene — a slice of everyday base reality — spoken in the first person as something a person would casually say.

Treat the verb as the everyday ACTIVITY at the center of the scene, and use the given pronoun naturally. If the verb is obscure or awkward, use a simpler everyday action that captures the same idea.

CRITICAL RULES:
- The scene must be completely NORMAL. Do NOT add anything weird, funny, quirky, or unusual — introducing the unusual thing is the user's job, not yours.
- Be concrete and grounded: a real setting + a real ordinary activity + maybe one plain, true detail. This gives the user a surface to tilt.
- Sound like natural spoken language — something said out loud, not narrated prose.
- 1 sentence (2 only if needed), no punctuation theatrics.
- Output only the scene, nothing else.

Examples:
- "I'm folding laundry on the couch while the TV plays in the background."
- "We're sitting at the bus stop waiting for the 7:15."
- "I'm in line at the post office holding a package I need to mail."
- "I'm reheating last night's pasta in the office microwave."
- "We're walking the dog around the block before it gets dark."''',
    },
}


_evaluator = PROMPT_TEXT["evaluator"]
_generator = PROMPT_TEXT["generator"]

SPEC = ExerciseSpec(
    key="firstUnusualThing",
    description="First Unusual Thing exercise — take a mundane scene and introduce the one grounded tilt that breaks base reality and opens a game.",
    sprint_question_label="Scene",
    generator_system=_generator["intro"],
    generator_prompt=verb_seed_generator_prompt,
    generator_response_schema=SingleSheQuestion,
    evaluator_system=build_evaluator_system(
        intro=_evaluator["intro"],
        evaluation_context=EVALUATION_CONTEXT,
        sections=[
            _evaluator["what_this_exercise_is"],
            _evaluator["the_process"],
            _evaluator["what_counts"],
            _evaluator["unusual_thing_techniques"],
            _evaluator["evaluation_criteria"],
        ],
        feedback_style=FEEDBACK_STYLE,
        sample_answer_guidelines=SAMPLE_ANSWER_GUIDELINES,
        output_contract=FIRST_UNUSUAL_THING_OUTPUT_CONTRACT,
    ),
    evaluator_prompt=standard_evaluator_prompt(
        exercise_key="firstUnusualThing",
        sprint_question_label="Scene",
    ),
    evaluator_response_schema=EvaluationResult,
    evaluator_fallback=standard_evaluator_fallback,
)
