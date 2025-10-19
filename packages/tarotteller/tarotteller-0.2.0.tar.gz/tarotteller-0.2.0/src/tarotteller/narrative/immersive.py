"""Immersive storytelling helpers for unforgettable tarot sessions."""

from __future__ import annotations

import textwrap
from collections import Counter
from typing import Iterable, Mapping, Sequence

from ..core.context import ContextProfile
from ..core.deck import DrawnCard, TarotCard

_WRAP_WIDTH = 72

_SUIT_TO_ELEMENT: Mapping[str, str] = {
    "wands": "fire",
    "cups": "water",
    "swords": "air",
    "pentacles": "earth",
}

_ELEMENT_TITLES: Mapping[str, str] = {
    "fire": "Fire — creative ignition",
    "water": "Water — emotional tides",
    "air": "Air — crystalline insight",
    "earth": "Earth — rooted devotion",
    "spirit": "Spirit — archetypal resonance",
}

_ELEMENT_RITUALS: Mapping[str, str] = {
    "fire": "Light a candle, whisper your intention into the flame, and let the glow energise your next bold move.",
    "water": "Stir a glass of water or tea clockwise, naming each feeling you are ready to honour before sipping mindfully.",
    "air": "Write a single-line mantra on paper, then stand by an open window and let the breeze carry your words into motion.",
    "earth": "Arrange three grounding objects in a small altar, breathing slowly as you affirm the stability you are cultivating.",
    "spirit": "Sit with palms over heart, visualising starlight threading through your question until gratitude softens your breath.",
}

_ELEMENT_SOUNDTRACKS: Mapping[str, str] = {
    "fire": "Spin cinematic drums or energising synthwave to keep momentum roaring.",
    "water": "Queue lush ambient waves or gentle piano to let emotions ebb and flow with grace.",
    "air": "Choose shimmering strings or choral harmonies that clear mental skies and invite fresh perspective.",
    "earth": "Play earthy instrumentals—handpan, cello, or lo-fi beats—to ground every step you take.",
    "spirit": "Bathed in cosmic soundscapes or singing bowls, let intuition rise and weave the unseen threads together.",
}

_TONE_STYLES: Mapping[str, Mapping[str, str]] = {
    "radiant": {
        "label": "Radiant",
        "journal_intro": "Let this light spill across the page:",
        "ritual_intro": "Kindle an act of devotion:",
        "sound_intro": "Score the moment:",
        "closing": "Carry this golden charge with you and notice what begins to bloom in its wake.",
    },
    "mystic": {
        "label": "Mystic",
        "journal_intro": "Trace the symbols that surface:",
        "ritual_intro": "Weave a pocket ritual:",
        "sound_intro": "Summon an aural veil:",
        "closing": "Let every synchronicity echo back, guiding you deeper into the mystery you are courting.",
    },
    "grounded": {
        "label": "Grounded",
        "journal_intro": "Name the roots you are tending:",
        "ritual_intro": "Anchor the insight in your body:",
        "sound_intro": "Harmonise your space:",
        "closing": "Walk forward deliberately, stacking each small action into the life you trust yourself to build.",
    },
}


def _wrap(text: str) -> str:
    return textwrap.fill(text, width=_WRAP_WIDTH)


def _normalise_cards(cards: Iterable[DrawnCard]) -> Sequence[DrawnCard]:
    return list(cards)


def _element_for_card(card: TarotCard) -> str:
    if card.element:
        return card.element.lower()
    suit = (card.suit or "").lower()
    return _SUIT_TO_ELEMENT.get(suit, "spirit")


def _dominant_element(cards: Sequence[DrawnCard]) -> str:
    if not cards:
        return "spirit"
    counts: Counter[str] = Counter()
    for drawn in cards:
        element = _element_for_card(drawn.card)
        counts[element] += 1
    return counts.most_common(1)[0][0]


def _energy_statement(cards: Sequence[DrawnCard]) -> str:
    if not cards:
        return "The spread hums with potential waiting to be defined."
    reversals = sum(1 for card in cards if card.is_reversed)
    uprights = len(cards) - reversals
    if reversals and reversals > uprights:
        return "The energy leans inward, asking for integration before outward motion."
    if uprights and uprights > reversals:
        return "Momentum surges outward—action wants a tangible next step."
    return "A balanced dialogue between inner reflection and outer expression steadies the path."


def _format_focuses(profile: ContextProfile | None) -> str | None:
    if not profile or not profile.focuses:
        return None
    focuses = [focus.replace("_", " ") for focus in profile.focuses]
    if len(focuses) == 1:
        return focuses[0]
    return ", ".join(focuses[:-1]) + f" and {focuses[-1]}"


def _journal_prompt(anchor: DrawnCard, profile: ContextProfile | None) -> str:
    keyword = anchor.keywords[0] if anchor.keywords else "the lesson at hand"
    orientation = "release" if anchor.is_reversed else "invite"
    focus_text = None
    if profile:
        focus_text = profile.primary_focus or (profile.focuses[0] if profile.focuses else None)
    if focus_text and focus_text != "general":
        focus_text = focus_text.replace("_", " ")
    if focus_text:
        return (
            f"Where does the {anchor.card.name} ask me to {orientation} {keyword} in my {focus_text} story, "
            "and what support would feel brave and true right now?"
        )
    return (
        f"How is the {anchor.card.name} encouraging me to {orientation} {keyword}, and what promise will I make to honour it today?"
    )


def _story_signature(cards: Sequence[DrawnCard]) -> str:
    names = ", ".join(card.card.name for card in cards[:3])
    if len(cards) > 3:
        names += ", …"
    return names or "the unfolding narrative"


def build_immersive_companion(
    cards: Iterable[DrawnCard], *, tone: str = "radiant", profile: ContextProfile | None = None
) -> str:
    """Return an immersive companion script for the provided cards."""

    drawn_cards = _normalise_cards(cards)
    if tone not in _TONE_STYLES:
        tone = "radiant"
    tone_style = _TONE_STYLES[tone]

    lines: list[str] = []
    lines.append("Immersive Companion")
    lines.append("-------------------")
    lines.append(f"Tone     : {tone_style['label']}")
    if profile:
        lines.append(f"Question : {profile.question}")
        focus_text = _format_focuses(profile)
        if focus_text:
            lines.append(f"Focus    : {focus_text}")
        lines.append(f"Timeframe: {profile.timeframe.replace('_', ' ')}")
        lines.append(f"Mood     : {profile.sentiment}")
    dominant = _dominant_element(drawn_cards)
    lines.append(f"Element  : {_ELEMENT_TITLES[dominant]}")
    lines.append(f"Energy   : {_energy_statement(drawn_cards)}")
    lines.append("")

    if drawn_cards:
        anchor = drawn_cards[0]
    else:
        # Fabricate a neutral anchor to keep copy graceful
        placeholder = TarotCard(
            name="the moment", arcana="major", number=0, keywords=(), reversed_keywords=(), description=""
        )
        anchor = DrawnCard(card=placeholder, is_reversed=False)

    lines.append("Journal Prompt")
    lines.append("--------------")
    lines.append(_wrap(f"{tone_style['journal_intro']} {_journal_prompt(anchor, profile)}"))
    lines.append("")

    lines.append("Micro-Ritual")
    lines.append("------------")
    ritual = _ELEMENT_RITUALS[dominant]
    lines.append(_wrap(f"{tone_style['ritual_intro']} {ritual}"))
    lines.append("")

    lines.append("Soundscape")
    lines.append("----------")
    soundtrack = _ELEMENT_SOUNDTRACKS[dominant]
    lines.append(_wrap(f"{tone_style['sound_intro']} {soundtrack}"))
    lines.append("")

    lines.append(
        _wrap(
            f"{tone_style['closing']} Honour the arc painted by {_story_signature(drawn_cards)} as you move forward."
        )
    )

    return "\n".join(lines).strip()
