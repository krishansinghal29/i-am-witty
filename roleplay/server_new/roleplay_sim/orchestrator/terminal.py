"""TerminalChecker: ongoing / won / left / locked-out. [P2 -> refined P8]"""
from __future__ import annotations

from roleplay_sim.domain.enums import Consequence, SessionStatus
from roleplay_sim.domain.models import GameState


class TerminalCheckerImpl:
    """Decide whether the session has ended after a turn.

    - WON: she accepted the close.
    - LEFT: she walked off, or engagement bottomed out.
    - LOCKED_OUT: a hard point-of-no-return lockout while disengaged.
    - ONGOING: otherwise.
    """

    def __init__(self, engagement_floor: float = 1.0) -> None:
        self.engagement_floor = engagement_floor

    def status(self, state: GameState, last: list[Consequence]) -> SessionStatus:
        if Consequence.CLOSE_ACCEPTED in last:
            return SessionStatus.WON
        if Consequence.LEAVES in last or state.emotional.engagement <= self.engagement_floor:
            return SessionStatus.LEFT
        if Consequence.LOCKED_OUT in last and state.emotional.engagement < 20.0:
            return SessionStatus.LOCKED_OUT
        return SessionStatus.ONGOING
