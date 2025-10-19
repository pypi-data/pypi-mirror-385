"""Core tarot deck logic for TarotTeller."""

from __future__ import annotations

import random
from dataclasses import dataclass
import textwrap
from typing import Iterable, Iterator, List, Optional, Sequence

from . import data


_MEANING_WRAP_WIDTH = 72


def _natural_join(words: Sequence[str]) -> str:
    """Return a human-friendly comma separated list."""

    if not words:
        return ""
    if len(words) == 1:
        return words[0]
    if len(words) == 2:
        return f"{words[0]} and {words[1]}"
    return f"{', '.join(words[:-1])}, and {words[-1]}"


def _wrap_paragraph(text: str) -> str:
    """Wrap ``text`` to the standard meaning width."""

    return textwrap.fill(" ".join(text.split()), width=_MEANING_WRAP_WIDTH)


@dataclass(frozen=True)
class TarotCard:
    """Represents a single tarot card with upright and reversed meanings."""

    name: str
    arcana: str
    number: int
    keywords: Sequence[str]
    reversed_keywords: Sequence[str]
    description: str
    suit: Optional[str] = None
    rank: Optional[str] = None
    element: Optional[str] = None

    @classmethod
    def from_dict(cls, payload: dict) -> "TarotCard":
        """Create a :class:`TarotCard` from a dictionary entry."""

        return cls(
            name=str(payload["name"]),
            arcana=str(payload["arcana"]),
            number=int(payload["number"]),
            keywords=tuple(payload["keywords"]),
            reversed_keywords=tuple(payload["reversed_keywords"]),
            description=str(payload["description"]),
            suit=payload.get("suit"),
            rank=payload.get("rank"),
            element=payload.get("element"),
        )

    def matches(self, query: str) -> bool:
        """Return ``True`` if ``query`` corresponds to this card's name.

        The comparison is case-insensitive and ignores superfluous whitespace.
        """

        normalized = " ".join(query.strip().lower().split())
        return normalized == " ".join(self.name.lower().split())


@dataclass(frozen=True)
class DrawnCard:
    """A tarot card that has been drawn and oriented."""

    card: TarotCard
    is_reversed: bool = False

    @property
    def orientation(self) -> str:
        return "reversed" if self.is_reversed else "upright"

    @property
    def keywords(self) -> Sequence[str]:
        return self.card.reversed_keywords if self.is_reversed else self.card.keywords

    @property
    def meaning(self) -> str:
        keywords = self.keywords
        theme = _natural_join(keywords)
        focus = f"themes of {theme}" if theme else "its central lesson"

        if self.is_reversed:
            opening = (
                f"Reversed, {self.card.name} signals blocks around {focus}."
            )
            closing = (
                "Notice where the energy feels stalled, take stock with honesty, "
                "and restore balance through steady, realistic adjustments."
            )
        else:
            opening = (
                f"Upright, {self.card.name} highlights {focus}."
            )
            closing = (
                "Integrate the lesson with grounded action and keep checking that "
                "your choices align with what matters most."
            )

        paragraphs = [opening, self.card.description, closing]
        wrapped = [_wrap_paragraph(text) for text in paragraphs if text]
        return "\n\n".join(wrapped)


class TarotDeck:
    """A full 78-card tarot deck with helpful drawing helpers."""

    def __init__(self, *, rng: Optional[random.Random] = None) -> None:
        self._rng = rng or random.Random()
        self._cards: List[TarotCard] = [
            TarotCard.from_dict(entry) for entry in data.iter_all_cards()
        ]
        self._stack: List[TarotCard] = []
        self.reset(shuffle=True)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._stack)

    def __iter__(self) -> Iterator[TarotCard]:  # pragma: no cover - simple passthrough
        return iter(self._stack)

    @property
    def all_cards(self) -> Sequence[TarotCard]:
        """All cards in their canonical order (major followed by minor)."""

        return tuple(self._cards)

    def seed(self, seed_value: Optional[int]) -> None:
        """Seed the internal random number generator for deterministic draws."""

        self._rng.seed(seed_value)

    def reset(self, *, shuffle: bool = False) -> None:
        """Restore the deck to its full size, optionally shuffling."""

        self._stack = list(self._cards)
        if shuffle:
            self.shuffle()

    def shuffle(self) -> None:
        """Shuffle the deck in-place using the deck's RNG."""

        self._rng.shuffle(self._stack)

    def draw(
        self,
        count: int = 1,
        *,
        allow_reversed: bool = True,
        rng: Optional[random.Random] = None,
    ) -> List[DrawnCard]:
        """Draw ``count`` cards from the deck.

        :param count: Number of cards to draw.
        :param allow_reversed: Whether cards may appear reversed.
        :param rng: Optional custom RNG for orientation decisions.
        :raises ValueError: If the deck does not contain enough cards.
        """

        if count < 1:
            raise ValueError("count must be at least 1")
        if count > len(self._stack):
            raise ValueError("Not enough cards remaining in the deck")

        orientation_rng = rng or self._rng
        drawn_cards: List[DrawnCard] = []
        for _ in range(count):
            card = self._stack.pop(0)
            is_reversed = allow_reversed and bool(orientation_rng.getrandbits(1))
            drawn_cards.append(DrawnCard(card=card, is_reversed=is_reversed))
        return drawn_cards

    def get_card(self, query: str) -> Optional[TarotCard]:
        """Look up a card by name, returning ``None`` if it is not found."""

        for card in self._cards:
            if card.matches(query):
                return card
        return None

    def list_cards(
        self,
        *,
        arcana: Optional[str] = None,
        suit: Optional[str] = None,
    ) -> Iterable[TarotCard]:
        """Yield cards filtered by arcana and suit criteria."""

        for card in self._cards:
            if arcana and card.arcana.lower() != arcana.lower():
                continue
            if suit and (card.suit or "").lower() != suit.lower():
                continue
            yield card


def format_card(card: TarotCard) -> str:
    """Return a richly formatted multi-line string for ``card``."""

    lines = [card.name]
    lines.append("-" * len(card.name))
    lines.append(f"Arcana : {card.arcana.title()}")
    if card.suit:
        lines.append(f"Suit   : {card.suit} (element of {card.element})")
        lines.append(f"Rank   : {card.rank}")
    lines.append(f"Number : {card.number}")
    lines.append(f"Keywords (upright) : {', '.join(card.keywords)}")
    lines.append(
        f"Keywords (reversed): {', '.join(card.reversed_keywords)}"
    )
    lines.append("")
    lines.append(card.description)
    return "\n".join(lines)
