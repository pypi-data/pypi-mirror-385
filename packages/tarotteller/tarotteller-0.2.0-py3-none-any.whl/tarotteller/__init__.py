"""Public package interface for TarotTeller."""

from .core import (
    ContextProfile,
    DrawnCard,
    InterpretationEngine,
    PersonalizedInsight,
    SPREADS,
    Spread,
    SpreadPlacement,
    SpreadPosition,
    SpreadReading,
    TarotCard,
    TarotDeck,
    TarotKnowledgeBase,
    analyze_question,
    build_prompt_interpretation,
    describe_card_correspondences,
    draw_spread,
    format_card,
)
from .narrative import build_immersive_companion

__all__ = [
    "ContextProfile",
    "DrawnCard",
    "InterpretationEngine",
    "PersonalizedInsight",
    "SPREADS",
    "Spread",
    "SpreadPlacement",
    "SpreadPosition",
    "SpreadReading",
    "TarotCard",
    "TarotDeck",
    "TarotKnowledgeBase",
    "analyze_question",
    "build_immersive_companion",
    "build_prompt_interpretation",
    "describe_card_correspondences",
    "draw_spread",
    "format_card",
]

__version__ = "0.2.0"
