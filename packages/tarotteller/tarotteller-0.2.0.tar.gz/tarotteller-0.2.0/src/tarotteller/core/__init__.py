"""Core tarot domain logic powering TarotTeller."""

from .context import ContextProfile, analyze_question
from .correspondences import describe_card_correspondences
from .deck import DrawnCard, TarotCard, TarotDeck, format_card
from .engine import (
    InterpretationEngine,
    PersonalizedInsight,
    build_prompt_interpretation,
)
from .knowledge import THEME_KEYWORDS, TarotKnowledgeBase
from .spreads import (
    SPREADS,
    Spread,
    SpreadPlacement,
    SpreadPosition,
    SpreadReading,
    draw_spread,
)

__all__ = [
    "ContextProfile",
    "analyze_question",
    "describe_card_correspondences",
    "DrawnCard",
    "TarotCard",
    "TarotDeck",
    "format_card",
    "InterpretationEngine",
    "PersonalizedInsight",
    "build_prompt_interpretation",
    "THEME_KEYWORDS",
    "TarotKnowledgeBase",
    "SPREADS",
    "Spread",
    "SpreadPlacement",
    "SpreadPosition",
    "SpreadReading",
    "draw_spread",
]
