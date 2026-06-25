"""TurnHistory: windowed transcript + running-recap access. [P2]"""
from __future__ import annotations

from dataclasses import dataclass, field

from roleplay_sim.domain.models import ActorTurn, PlayerTurn


@dataclass
class TurnHistoryImpl:
    """Concrete TurnHistory. Holds the full transcript; `recap` is maintained by
    the BriefAuthor each turn so the Actor stays grounded without the whole log.

    `pending` is the current player line awaiting her reply. The history stores
    completed (player, actor) PAIRS, so the line she's replying to has no pair yet
    and would otherwise be invisible at render time — `pending` carries it so the
    BriefAuthor and Actor both see what he just said. It's set at the top of a turn
    and cleared when the pair is appended."""
    turns: list[tuple[PlayerTurn, ActorTurn]] = field(default_factory=list)
    recap: str = ""
    pending: PlayerTurn | None = None

    def window(self, n: int) -> list[tuple[PlayerTurn, ActorTurn]]:
        return self.turns[-n:] if n > 0 else []

    def transcript(self, n: int) -> str:
        """Recent transcript as HIM/HER lines, with the in-flight `pending` line (the
        one she's about to answer) as a trailing HIM. Single source of truth so callers
        don't each re-handle pairs + pending."""
        lines: list[str] = []
        for player, her in self.window(n):
            lines.append(f"HIM: {player.text}")
            lines.append(f"HER: {her.text}")
        if self.pending is not None:
            lines.append(f"HIM: {self.pending.text}")
        return "\n".join(lines)

    def append(self, player: PlayerTurn, actor: ActorTurn) -> None:
        self.turns.append((player, actor))
        self.pending = None   # the pair is complete; the line is now in `turns`

    def __len__(self) -> int:
        return len(self.turns)
