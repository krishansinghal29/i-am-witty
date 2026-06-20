"""Director.step(): orchestrates StateEngine + TestTrigger + BeatPolicy + BriefAuthor. [P2 glue]

This is real orchestration logic (stable across phases); its sub-components are
swapped from stubs to real implementations in P3–P6.
"""
from __future__ import annotations

from dataclasses import dataclass

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.enums import Consequence
from roleplay_sim.domain.interfaces import (
    BeatPolicy,
    BriefAuthor,
    Classifier,  # noqa: F401  (kept for symmetry/readability)
    StateEngine,
    TestTrigger,
    TurnHistory,
)
from roleplay_sim.domain.models import BehavioralBrief, Classification, DirectorStep, GameState


@dataclass
class DirectorImpl:
    state_engine: StateEngine
    beat_policy: BeatPolicy
    brief_author: BriefAuthor
    test_trigger: TestTrigger

    async def step(
        self, cls: Classification, state: GameState, persona: PersonaConfig,
        history: TurnHistory,
    ) -> DirectorStep:
        update = self.state_engine.apply(cls, state, persona)
        new_state = update.new_state
        consequences = list(update.consequences)

        # She may decide to test him (sets pending_test BEFORE beat selection so
        # the BeatPolicy can route to SHIT_TEST).
        theme = self.test_trigger.maybe_test(new_state, persona)
        if theme:
            new_state.flags.pending_test = theme
            consequences.append(Consequence.TEST_TRIGGERED)

        beat, secondary, dials = self.beat_policy.select(new_state, consequences, persona)
        note, recap = await self.brief_author.author(
            new_state, beat, dials, consequences, history, persona
        )
        brief = BehavioralBrief(
            beat=beat, secondary_beat=secondary, dials=dials, note=note, recap=recap
        )
        return DirectorStep(
            state=new_state, brief=brief, consequences=consequences, events=update.events
        )
