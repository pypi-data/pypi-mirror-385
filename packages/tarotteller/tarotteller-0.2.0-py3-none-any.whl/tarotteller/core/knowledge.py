"""Lightweight tarot knowledge base and reasoning helpers."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable, List, Mapping, Sequence

from .deck import DrawnCard, TarotCard

# Keyword lexicon connecting high level themes to vocabulary that commonly
# appears in tarot interpretations.  The lexicon intentionally overlaps with the
# card metadata so that we can infer relevant themes from card keywords and
# descriptions without an external database.
THEME_KEYWORDS: Mapping[str, Sequence[str]] = {
    "love": (
        "love",
        "relationship",
        "union",
        "romance",
        "heart",
        "emotion",
        "partnership",
        "marriage",
        "affection",
        "fertility",
        "compassion",
    ),
    "career": (
        "career",
        "work",
        "ambition",
        "leadership",
        "enterprise",
        "project",
        "promotion",
        "skill",
        "achievement",
    ),
    "finance": (
        "money",
        "finance",
        "wealth",
        "abundance",
        "material",
        "resources",
        "security",
        "investment",
    ),
    "health": (
        "health",
        "healing",
        "recovery",
        "wellness",
        "stress",
        "balance",
        "vitality",
    ),
    "spirituality": (
        "spirit",
        "intuition",
        "soul",
        "faith",
        "destiny",
        "purpose",
        "guidance",
        "karma",
    ),
    "creativity": (
        "creativity",
        "art",
        "inspiration",
        "imagination",
        "vision",
        "expression",
        "innovation",
    ),
    "change": (
        "change",
        "transition",
        "transformation",
        "rebirth",
        "ending",
        "beginning",
        "shift",
    ),
}


def _natural_join(words: Sequence[str]) -> str:
    """Return a human friendly comma separated list."""

    if not words:
        return ""
    if len(words) == 1:
        return words[0]
    if len(words) == 2:
        return f"{words[0]} and {words[1]}"
    return f"{', '.join(words[:-1])}, and {words[-1]}"


@dataclass(frozen=True)
class ThemeMatch:
    """A theme along with its support score for a specific card."""

    theme: str
    score: int


class TarotKnowledgeBase:
    """Infer tarot themes and generate contextual insights."""

    def __init__(self, cards: Iterable[TarotCard]):
        self._cards = {card.name: card for card in cards}
        self._cache: dict[str, List[ThemeMatch]] = {}

    def _text_snippets(self, card: TarotCard) -> List[str]:
        snippets: List[str] = []
        snippets.extend(card.keywords)
        snippets.extend(card.reversed_keywords)
        snippets.append(card.description)
        if card.suit:
            snippets.append(card.suit)
        if card.element:
            snippets.append(card.element)
        return [snippet.lower() for snippet in snippets]

    def themes_for_card(self, card: TarotCard) -> List[str]:
        """Return ordered themes that resonate with ``card``."""

        if card.name in self._cache:
            return [match.theme for match in self._cache[card.name]]

        snippets = self._text_snippets(card)
        scores: Counter[str] = Counter()
        for theme, lexicon in THEME_KEYWORDS.items():
            lowered = [token.lower() for token in lexicon]
            for snippet in snippets:
                if any(word in snippet for word in lowered):
                    scores[theme] += 1

        # Provide sensible defaults when no keywords matched.
        if not scores:
            if card.arcana.lower() == "major":
                scores["spirituality"] = 1
            elif (card.suit or "").lower() == "cups":
                scores["love"] = 1
            elif (card.suit or "").lower() == "pentacles":
                scores["finance"] = 1
            elif (card.suit or "").lower() == "wands":
                scores["career"] = 1
            elif (card.suit or "").lower() == "swords":
                scores["change"] = 1

        ordered = [ThemeMatch(theme=theme, score=score) for theme, score in scores.most_common()]
        self._cache[card.name] = ordered
        return [match.theme for match in ordered]

    def insight_for(self, drawn_card: DrawnCard, focus: str) -> str:
        """Generate a short recommendation for ``drawn_card`` within ``focus``."""

        theme_keywords = set(word.lower() for word in THEME_KEYWORDS.get(focus, ()))
        overlap = [
            keyword
            for keyword in drawn_card.keywords
            if keyword.lower() in theme_keywords
        ]
        if not overlap:
            # Fall back to the most characteristic keywords of the orientation.
            overlap = list(drawn_card.keywords[:2])

        descriptor = _natural_join(overlap)
        orientation = "reversed" if drawn_card.is_reversed else "upright"
        focus_text = focus.replace("_", " ")
        return (
            f"In {focus_text} matters, the {orientation} {drawn_card.card.name} encourages you to "
            f"lean into {descriptor or 'the lesson it offers'} to stay aligned with your intent."
        )

    def resolve_card(self, name: str) -> TarotCard:
        """Return a card by name, raising ``KeyError`` if unknown."""

        return self._cards[name]
