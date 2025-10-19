from tarotteller.core.context import analyze_question


def test_analyze_question_detects_focus_and_timeframe():
    profile = analyze_question("Will I find love at work this year?")
    assert profile.primary_focus == "love"
    assert "career" in profile.focuses
    assert profile.timeframe == "long_term"
    assert profile.sentiment in {"hopeful", "curious", "concerned"}
    assert "love" in profile.highlighted_terms
