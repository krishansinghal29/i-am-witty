"""Common prompt contracts shared by exercise prompts."""

EVALUATION_CONTEXT = '''=== EVALUATION CONTEXT ===
You are evaluating a user's transcribed response. You only have the transcript.
Focus on content quality using the exercise criteria below. Do not assess audio quality, vocal delivery, tone, pacing, or confidence.'''

EVALUATOR_OUTPUT_CONTRACT = '''=== STRUCTURED OUTPUT CONTRACT (CRITICAL) ===
The response schema has exactly these fields:
- feedback: HTML formatted feedback using the exact 4-section structure above: What Landed, The Trap, Level Up, Mindset Shift.
- sample_answer: 3 short responses using different techniques, separated by <br><br>.

Rules:
- feedback MUST follow the exact 4-section structure defined above.
- sample_answer must contain exactly 3 responses separated by <br><br>. Each should be short and punchy.'''
