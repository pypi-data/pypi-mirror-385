"""Question analysis helpers for contextualised tarot readings."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Sequence

from .knowledge import THEME_KEYWORDS

_TIMEFRAME_KEYWORDS = {
    "immediate": ("today", "right now", "currently", "in the moment"),
    "short_term": ("soon", "this week", "next week", "this month", "near future"),
    "long_term": (
        "this year",
        "next year",
        "long term",
        "over time",
        "eventually",
        "future",
    ),
}

_POSITIVE_KEYWORDS = {"confident", "ready", "excited", "hope", "optimistic", "eager"}
_NEGATIVE_KEYWORDS = {
    "worried",
    "anxious",
    "afraid",
    "stressed",
    "concerned",
    "stuck",
    "doubt",
}


@dataclass(frozen=True)
class ContextProfile:
    """Structured representation of a querent's question."""

    question: str
    focuses: Sequence[str]
    timeframe: str
    sentiment: str
    highlighted_terms: Sequence[str]

    @property
    def primary_focus(self) -> str | None:
        return self.focuses[0] if self.focuses else None


def _normalise_question(question: str) -> str:
    return " ".join(question.strip().split())


def _extract_terms(question: str) -> List[str]:
    tokens = re.findall(r"[A-Za-z']+", question.lower())
    return sorted(set(tokens))


def _detect_focuses(lower_question: str) -> List[str]:
    focuses: List[str] = []
    for theme, lexicon in THEME_KEYWORDS.items():
        if any(keyword in lower_question for keyword in lexicon):
            focuses.append(theme)
    return focuses


def _detect_timeframe(lower_question: str) -> str:
    for label, lexicon in _TIMEFRAME_KEYWORDS.items():
        if any(keyword in lower_question for keyword in lexicon):
            return label
    return "open"


def _detect_sentiment(terms: Sequence[str]) -> str:
    if any(term in _NEGATIVE_KEYWORDS for term in terms):
        return "concerned"
    if any(term in _POSITIVE_KEYWORDS for term in terms):
        return "hopeful"
    return "curious"


def analyze_question(question: str) -> ContextProfile:
    """Return a :class:`ContextProfile` derived from ``question``."""

    normalised = _normalise_question(question)
    lowered = normalised.lower()
    focuses = _detect_focuses(lowered)
    terms = _extract_terms(lowered)
    timeframe = _detect_timeframe(lowered)
    sentiment = _detect_sentiment(terms)
    if not focuses:
        focuses = ["general"]
    return ContextProfile(
        question=normalised,
        focuses=tuple(focuses),
        timeframe=timeframe,
        sentiment=sentiment,
        highlighted_terms=tuple(term for term in terms if len(term) > 3),
    )
