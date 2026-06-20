"""Persona + scene meta-generator.

Replaces hand-authored persona folders: every session is ROLLED (combinatorial
sampling of curated lists + behavioral axes) and then EXPANDED by an LLM
synthesizer into the PersonaConfig/SceneConfig the engine consumes. Wide variety
without encoding it explicitly. See rolls.py (pure roll), synthesizer.py (LLM
expansion), session.py (assembly).
"""
