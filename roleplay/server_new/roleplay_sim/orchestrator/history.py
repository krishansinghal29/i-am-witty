"""TurnHistory: windowed transcript + running-recap access. [P2]"""
from __future__ import annotations

from dataclasses import dataclass, field

from roleplay_sim.domain.models import ActorTurn, PlayerTurn


@dataclass
class TurnHistoryImpl:
    """Concrete TurnHistory. Holds the full transcript; `recap` is maintained by
    the BriefAuthor each turn so the Actor stays grounded without the whole log."""
    turns: list[tuple[PlayerTurn, ActorTurn]] = field(default_factory=list)
    recap: str = ""

    def window(self, n: int) -> list[tuple[PlayerTurn, ActorTurn]]:
        return self.turns[-n:] if n > 0 else []

    def append(self, player: PlayerTurn, actor: ActorTurn) -> None:
        self.turns.append((player, actor))

    def __len__(self) -> int:
        return len(self.turns)
