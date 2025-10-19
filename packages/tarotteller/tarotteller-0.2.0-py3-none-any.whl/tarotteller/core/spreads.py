"""Spread definitions and helper utilities for tarot readings."""

from __future__ import annotations

import random
from dataclasses import dataclass
import textwrap
from typing import Dict, List, Optional

from .deck import DrawnCard, TarotDeck


@dataclass(frozen=True)
class SpreadPosition:
    """Metadata describing a slot within a tarot spread."""

    index: int
    title: str
    prompt: str


@dataclass(frozen=True)
class Spread:
    """A tarot spread describing how many cards to draw and their roles."""

    name: str
    description: str
    positions: List[SpreadPosition]

    @property
    def size(self) -> int:
        return len(self.positions)


@dataclass(frozen=True)
class SpreadPlacement:
    """A drawn card paired with its position in the spread."""

    position: SpreadPosition
    card: DrawnCard


@dataclass(frozen=True)
class SpreadReading:
    """The final result of evaluating a spread with a deck."""

    spread: Spread
    placements: List[SpreadPlacement]

    def as_text(self) -> str:
        """Render the spread in a human-readable block of text."""

        lines = [f"Spread: {self.spread.name}", self.spread.description, ""]
        for placement in self.placements:
            header = f"{placement.position.index}. {placement.position.title}"
            lines.append(header)
            lines.append("-" * len(header))
            prompt = textwrap.fill(placement.position.prompt, width=72)
            card_line = textwrap.fill(
                f"Card: {placement.card.card.name} ({placement.card.orientation})",
                width=72,
            )
            meaning = textwrap.indent(placement.card.meaning, "  ")
            lines.append(prompt)
            lines.append(card_line)
            lines.append(meaning)
            lines.append("")
        return "\n".join(lines).strip()


SPREADS: Dict[str, Spread] = {
    "single": Spread(
        name="Single Card Insight",
        description="A straightforward pull for guidance on the present moment.",
        positions=[
            SpreadPosition(
                index=1,
                title="Message",
                prompt="What energy is most important to understand right now?",
            )
        ],
    ),
    "three_card": Spread(
        name="Three Card Story",
        description="A balanced Past / Present / Future reading.",
        positions=[
            SpreadPosition(
                index=1,
                title="Past",
                prompt="What history is influencing the situation?",
            ),
            SpreadPosition(
                index=2,
                title="Present",
                prompt="Where does the situation currently stand?",
            ),
            SpreadPosition(
                index=3,
                title="Future",
                prompt="What trajectory is developing from current momentum?",
            ),
        ],
    ),
    "celtic_cross": Spread(
        name="Celtic Cross",
        description="A classic ten-card map of challenges, influences, and outcomes.",
        positions=[
            SpreadPosition(1, "Significator", "The heart of the matter at hand."),
            SpreadPosition(2, "Crossing", "The energy currently challenging the significator."),
            SpreadPosition(3, "Foundation", "Deep roots, subconscious drives, or the distant past."),
            SpreadPosition(4, "Recent Past", "Events that have shaped the present."),
            SpreadPosition(5, "Crown", "Conscious focus, goals, or potential."),
            SpreadPosition(6, "Near Future", "What is entering the story soon."),
            SpreadPosition(7, "Self", "How you view yourself or your role."),
            SpreadPosition(8, "Environment", "External influences and relationships."),
            SpreadPosition(9, "Hopes & Fears", "The vulnerabilities colouring perception."),
            SpreadPosition(10, "Outcome", "Likely direction if the current energy continues."),
        ],
    ),
}


def draw_spread(
    deck: TarotDeck,
    spread_name: str,
    *,
    allow_reversed: bool = True,
    rng: Optional[int] = None,
) -> SpreadReading:
    """Draw cards from ``deck`` according to ``spread_name``.

    :param deck: The :class:`~tarotteller.deck.TarotDeck` to draw from.  Cards are
        removed from the deck's current stack.
    :param spread_name: Key in :data:`SPREADS`.  A :class:`KeyError` is raised if
        the spread is unknown.
    :param allow_reversed: Whether reversals are permitted in the draw.
    :param rng: Optional seed for deterministic orientation results.
    """

    spread = SPREADS[spread_name]
    orientation_rng: Optional[random.Random]
    if rng is None:
        orientation_rng = None
    else:
        orientation_rng = random.Random(rng)

    drawn_cards = deck.draw(
        spread.size,
        allow_reversed=allow_reversed,
        rng=orientation_rng,
    )
    placements = [
        SpreadPlacement(position=position, card=card)
        for position, card in zip(spread.positions, drawn_cards)
    ]
    return SpreadReading(spread=spread, placements=placements)
