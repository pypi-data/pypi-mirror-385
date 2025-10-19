from tarotteller import (
    InterpretationEngine,
    TarotDeck,
    TarotKnowledgeBase,
    analyze_question,
    build_prompt_interpretation,
    draw_spread,
)


def test_render_personalised_summary_creates_story_arc():
    deck = TarotDeck()
    deck.seed(11)
    deck.reset(shuffle=True)
    reading = draw_spread(deck, "three_card", allow_reversed=False, rng=7)
    profile = analyze_question(
        "How can I nurture my career and creativity this month?"
    )

    engine = InterpretationEngine(TarotKnowledgeBase(deck.all_cards))
    summary = engine.render_personalised_summary(reading, profile)

    assert "Story Arc" in summary
    assert "You arrive with a" in summary
    assert "chapter of" in summary


def test_build_prompt_interpretation_includes_prompt_and_message():
    deck = TarotDeck()
    deck.seed(5)
    deck.reset(shuffle=True)
    reading = draw_spread(deck, "single", allow_reversed=True, rng=3)
    knowledge = TarotKnowledgeBase(deck.all_cards)

    narrative = build_prompt_interpretation(reading.placements[0], knowledge)

    prompt_text = reading.placements[0].position.prompt.split()[0]

    assert reading.placements[0].card.card.name in narrative
    assert prompt_text in narrative
    assert "In " in narrative
