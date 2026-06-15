"""Prompt package for multi-turn roleplay task types.

Each roleplay is a multi-turn, in-character conversation in which the user
practices a single wit skill against an AI woman's lines. The model plays BOTH
the in-character woman (generator) and the wit coach (evaluator) in one combined
call per turn, returning a structured turn payload.
"""
