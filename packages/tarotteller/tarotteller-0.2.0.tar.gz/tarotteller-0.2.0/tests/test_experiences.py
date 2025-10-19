from tarotteller import (
    ContextProfile,
    DrawnCard,
    TarotDeck,
    build_immersive_companion,
)


def test_build_immersive_companion_includes_sections():
    deck = TarotDeck()
    magician = deck.get_card("The Magician")
    high_priestess = deck.get_card("The High Priestess")
    assert magician is not None and high_priestess is not None

    cards = [
        DrawnCard(card=magician, is_reversed=False),
        DrawnCard(card=high_priestess, is_reversed=True),
    ]

    profile = ContextProfile(
        question="How can I shine at work?",
        focuses=("career",),
        timeframe="short_term",
        sentiment="hopeful",
        highlighted_terms=("shine", "work"),
    )

    guidance = build_immersive_companion(cards, tone="mystic", profile=profile)

    assert "Immersive Companion" in guidance
    assert "Tone     : Mystic" in guidance
    assert "Journal Prompt" in guidance
    assert "Micro-Ritual" in guidance
    assert "Soundscape" in guidance
    assert "career" in guidance.lower()
