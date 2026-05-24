"""
Shared prompt components used identically across ALL exercises.

Instead of copy-pasting these blocks into every exercise prompt file,
import them here and reference in each exercise's PROMPT_COMPONENTS dict.
"""


def _render_bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _render_quoted_examples(items: list[str]) -> str:
    return "\n".join(f'- "{item}"' for item in items)


def build_feedback_style(
    trap_intro: str,
    common_traps: list[str],
    mindset_examples: list[str],
    *,
    level_up_instruction: str = "One specific technique from the list above. 1-2 sentences max.",
    mindset_intro: str = "One root-cause mental reframe.",
) -> str:
    """Build the shared 4-part HTML feedback instruction block."""
    traps_block = _render_bullets(common_traps)
    mindset_examples_block = _render_quoted_examples(mindset_examples)

    return f'''=== FEEDBACK FORMAT (CRITICAL — FOLLOW THIS STRUCTURE) ===

<b>✅ What Landed</b><br>
What worked. Quote their words if possible. 1-2 sentences max.
<br><br>

<b>⚠️ The Trap</b><br>
{trap_intro}
{traps_block}
1-2 sentences max.
<br><br>

<b>🚀 Level Up</b><br>
{level_up_instruction}
<br><br>

<b>🧠 Mindset Shift</b><br>
{mindset_intro}
Examples:
{mindset_examples_block}
1-2 sentences max.'''


def build_sample_answer_guidelines(
    sample_answer_instructions: list[str],
    closing_instruction: str,
) -> str:
    """Build the sample-answer guidance block shared across prompt types."""
    sample_answer_block = _render_bullets(sample_answer_instructions)

    return f'''=== SAMPLE ANSWER GUIDELINES ===
Generate 3 sample answers:
{sample_answer_block}
{closing_instruction}'''


# ---------------------------------------------------------------------------
# Sprint shared components
# ---------------------------------------------------------------------------

VOICE_DELIVERY_EVALUATION = '''=== VOICE DELIVERY EVALUATION (from audio) ===
Analyse the AUDIO DIRECTLY to evaluate:
    - **Filler Words**: Detect and count fillers ("um", "uh", "like", "you know", "basically", "actually", "so", "right")
    - **Speaking Pace**: Estimate words per minute (ideal: 130-170 WPM)
    - **Confidence**: Assess vocal confidence from tone, volume consistency, hesitation
    - **Fluency**: How smoothly they delivered the response
    - **Tone & Energy**: Emotional quality and engagement level
Do NOT rely solely on the transcript for voice analysis.'''

REFINEMENT_MODE = '''=== REFINEMENT MODE ===
When a previous response is provided, compare both attempts and highlight improvements or regressions.'''

SPRINT_JSON_OUTPUT_FORMAT = '''=== JSON OUTPUT FORMAT (CRITICAL) ===
Respond with ONLY valid JSON, no text before or after, no markdown code blocks.

{
    "text_score": <1-10>,
    "voice_score": <1-10>,
    "overall_score": <1-10>,
    "text_feedback": "<HTML formatted text analysis using the exact 4-section structure above: What Landed, The Trap, Level Up, Mindset Shift>",
    "voice_feedback": "<HTML formatted voice delivery analysis focused only on delivery: filler words, pace, confidence, fluency, tone, and energy>",
    "sample_answer": "<short, punchy alternative>",
    "filler_words_total_count": <number>,
    "filler_words_breakdown": "<JSON string e.g. {\\"um\\": 2}>",
    "filler_words_frequency_per_minute": <number>,
    "improvement_tips": ["<tip1>", "<tip2>", "<tip3>"],
    "pace_wpm": <number>,
    "confidence_level": "<low|medium|high>",
    "refinement_comparison": "<HTML comparison if previous response provided, else 'null'>"
}

Rules:
- text_feedback MUST follow the exact 4-section structure defined above.
- voice_feedback MUST stay separate from text_feedback and focus only on vocal delivery.
- sample_answer should stay short, punchy, and exercise-specific.'''


# ---------------------------------------------------------------------------
# Combined agent shared components
# ---------------------------------------------------------------------------

COMBINED_JSON_FORMAT = '''=== JSON FORMAT (CRITICAL) ===
Respond with ONLY valid JSON, no text before or after, no markdown code blocks.

{
    "evaluation": {
        "feedback": "HTML formatted feedback using the 4-section structure above",
        "sample_answer": "short, punchy alternative response"
    },
    "scoring": {
        "skills": [
            {
                "skillKey": "humor",
                "delta": 2.0,
                "confidenceDelta": 1.0,
                "rationale": "...",
                "difficultyMultiplier": 1.0
            }
        ],
        "overallRationale": "...",
        "timeBasedAdjustment": "..."
    }
}'''


def build_scoring_role(skills: str) -> str:
    """Build the scoring role component with exercise-specific skill keys."""
    return f'''=== SCORING ROLE ===
Assess and update skill scores for ALL skills: {skills}.

Scoring rules:
    1. Return changes for ALL skills listed.
    2. Consider time gaps in recent history.
    3. Factor in user's selected dating focus areas.
    4. Be engaging and game-like but fair.
    5. Consider streaks and recent performance trends.
    6. Encourage learning: small positive deltas for near-misses.
    7. Confidence changes reflect user's self-assessment accuracy.
    8. difficultyMultiplier MUST be inversely related to current skill score:
       * High scores (70-100): use 0.5-0.9 (harder to improve)
       * Medium scores (40-70): use 0.9-1.2 (moderate difficulty)
       * Low scores (0-40): use 1.2-2.0 (easier to improve)'''


def build_sprint_scoring(skill_description: str) -> str:
    """Build the sprint scoring component with an exercise-specific description."""
    return f'''=== SCORING ===
- text_score: 1-10 (content quality — {skill_description})
- voice_score: 1-10 (delivery quality from audio)
- overall_score: 1-10 (weighted: 60% text + 40% voice)'''


SPRINT_CONTEXT = '''=== SPRINT CONTEXT ===
You are evaluating a user's SPOKEN response. You have access to BOTH the raw audio recording and the transcript.
This is a SPRINT exercise — the user records a spoken response within a time limit. Evaluate BOTH the content quality (using normal exercise criteria) AND vocal delivery (from the audio).'''
