from tarotteller import DrawnCard, TarotDeck, TarotKnowledgeBase


def test_knowledge_identifies_themes_and_generates_insight():
    deck = TarotDeck()
    card = deck.get_card("Two of Cups")
    knowledge = TarotKnowledgeBase(deck.all_cards)
    themes = knowledge.themes_for_card(card)
    assert "love" in themes

    drawn = DrawnCard(card)
    insight = knowledge.insight_for(drawn, "love")
    assert "Two of Cups" in insight
    assert "love" in insight.lower()
