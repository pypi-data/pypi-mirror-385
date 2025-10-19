from tarotteller import SPREADS, TarotDeck, draw_spread


def test_spread_definitions_have_expected_sizes():
    assert SPREADS["single"].size == 1
    assert SPREADS["three_card"].size == 3
    assert SPREADS["celtic_cross"].size == 10


def test_draw_spread_produces_reading():
    deck = TarotDeck()
    deck.seed(99)
    deck.reset(shuffle=True)
    reading = draw_spread(deck, "three_card", rng=21)
    assert len(reading.placements) == 3
    assert reading.placements[0].position.title == "Past"
    assert reading.placements[-1].position.title == "Future"
    # Orientation seed deterministically sets reversed states
    orientations = [placement.card.orientation for placement in reading.placements]
    assert orientations == ["upright", "upright", "reversed"]
    text = reading.as_text()
    assert "Three Card Story" in text
    assert "Past" in text and "Future" in text
