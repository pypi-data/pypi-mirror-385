"""Esoteric correspondence helpers for tarot cards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence, Tuple

from .deck import DrawnCard, TarotCard


@dataclass(frozen=True)
class NumerologyMeaning:
    number: int
    title: str
    summary: str


# Chaldean numerology emphasises the vibration of the reduced number.
# We treat 0 as the liminal void that precedes manifestation.
_CHALDEAN_NUMEROLOGY: Mapping[int, NumerologyMeaning] = {
    0: NumerologyMeaning(
        number=0,
        title="The Sacred Void",
        summary="Pure potential and spiritual reset before a new cycle begins.",
    ),
    1: NumerologyMeaning(
        number=1,
        title="The Originator",
        summary="Leadership, willpower, and the spark that launches fresh ventures.",
    ),
    2: NumerologyMeaning(
        number=2,
        title="The Diplomat",
        summary="Sensitivity, partnership, and balancing complementary forces.",
    ),
    3: NumerologyMeaning(
        number=3,
        title="The Inspirer",
        summary="Creative expression, optimism, and storytelling that connects hearts.",
    ),
    4: NumerologyMeaning(
        number=4,
        title="The Architect",
        summary="Structure, dedication, and building foundations that endure.",
    ),
    5: NumerologyMeaning(
        number=5,
        title="The Catalyst",
        summary="Adventure, adaptability, and embracing transformative change.",
    ),
    6: NumerologyMeaning(
        number=6,
        title="The Nurturer",
        summary="Service, responsibility, and healing through compassionate care.",
    ),
    7: NumerologyMeaning(
        number=7,
        title="The Seeker",
        summary="Inner wisdom, spiritual study, and trust in the unseen pattern.",
    ),
    8: NumerologyMeaning(
        number=8,
        title="The Alchemist",
        summary="Power, mastery, and aligning ambition with soulful integrity.",
    ),
    9: NumerologyMeaning(
        number=9,
        title="The Humanitarian",
        summary="Closure, generosity, and offering hard-won insight to the world.",
    ),
}


_MAJOR_ARCANA_ASTROLOGY: Mapping[str, str] = {
    "The Fool": "Uranus & Air — leaps of faith, open horizons, originality.",
    "The Magician": "Mercury — intellect, communication, skilful manifestation.",
    "The High Priestess": "The Moon — intuition, dreams, tides of inner knowing.",
    "The Empress": "Venus — fertility, artistry, sensory abundance.",
    "The Emperor": "Aries — authority, strategy, courageous leadership.",
    "The Hierophant": "Taurus — tradition, enduring values, sacred teachings.",
    "The Lovers": "Gemini — choice, dialogue, harmonising dual perspectives.",
    "The Chariot": "Cancer — protective drive, tenacity, emotional sovereignty.",
    "Strength": "Leo — heart-led confidence, creative bravery, radiant presence.",
    "The Hermit": "Virgo — reflective mentorship, discernment, mindful practice.",
    "Wheel of Fortune": "Jupiter — expansion, karmic cycles, fortunate pivots.",
    "Justice": "Libra — equilibrium, accountability, relational harmony.",
    "The Hanged Man": "Neptune — surrender, mysticism, altered perspective.",
    "Death": "Scorpio — transmutation, shadow work, regenerative power.",
    "Temperance": "Sagittarius — synthesis, philosophical questing, alchemy.",
    "The Devil": "Capricorn — earthly mastery, boundaries, confronting attachment.",
    "The Tower": "Mars — disruptive revelation, necessary demolition, liberation.",
    "The Star": "Aquarius — visionary hope, collective healing, future focus.",
    "The Moon": "Pisces — psychic tides, imagination, luminous mystery.",    
    "The Sun": "Solar vitality — joy, vitality, clarity, wholehearted expression.",
    "Judgement": "Pluto — resurrection, awakening call, soul-level renewal.",
    "The World": "Saturn — completion, integration, cosmic wholeness.",
}


_SUIT_ASTROLOGY: Mapping[str, str] = {
    "Wands": "Fire signs (Aries, Leo, Sagittarius) — momentum, inspiration, initiative.",
    "Cups": "Water signs (Cancer, Scorpio, Pisces) — feeling, empathy, intuitive flow.",
    "Swords": "Air signs (Gemini, Libra, Aquarius) — clarity, dialogue, mental mastery.",
    "Pentacles": "Earth signs (Taurus, Virgo, Capricorn) — craftsmanship, prosperity, stewardship.",
}


_CHINESE_ZODIAC: Sequence[Tuple[str, str]] = (
    ("Rat", "Strategic problem-solver who spots openings others miss."),
    ("Ox", "Steadfast builder bringing endurance and patient progress."),
    ("Tiger", "Courageous trailblazer willing to take decisive risks."),
    ("Rabbit", "Diplomatic peacemaker cultivating gentle harmony."),
    ("Dragon", "Charismatic innovator conjuring bold, visionary change."),
    ("Snake", "Insightful mystic reading between the lines and sensing timing."),
    ("Horse", "Free-spirited adventurer chasing movement and autonomy."),
    ("Goat", "Artistic nurturer weaving beauty, empathy, and community."),
    ("Monkey", "Inventive strategist experimenting and iterating playfully."),
    ("Rooster", "Vigilant truth-teller focused on integrity and precision."),
    ("Dog", "Loyal guardian devoted to protection, service, and honesty."),
    ("Pig", "Generous host reminding you to savour comfort and shared joy."),
)


_NATIVE_ELEMENT_ANIMALS: Mapping[str, Tuple[str, str]] = {
    "fire": ("Red-tailed Hawk", "See the long view, trust fierce focus, and answer the call to act."),
    "water": ("Salmon", "Swim upstream with heart, honouring feelings as sacred fuel for wisdom."),
    "air": ("Great Horned Owl", "Survey every angle, listen beyond words, and let insight glide in silently."),
    "earth": ("Buffalo", "Move steadily, respect cycles of giving and receiving, and walk prayerfully."),
    "spirit": ("White Raven", "Embrace synchronicity and let mystery stitch together your unfolding story."),
}


def _reduce_to_chaldean(number: int) -> int:
    if number <= 0:
        return 0
    total = number
    while total > 9:
        total = sum(int(digit) for digit in str(total))
    return total if total in _CHALDEAN_NUMEROLOGY else 0


def numerology_for(card: TarotCard) -> NumerologyMeaning:
    reduced = _reduce_to_chaldean(card.number)
    return _CHALDEAN_NUMEROLOGY[reduced]


def astrology_for(card: TarotCard) -> str:
    if card.name in _MAJOR_ARCANA_ASTROLOGY:
        return _MAJOR_ARCANA_ASTROLOGY[card.name]
    if card.suit and card.suit in _SUIT_ASTROLOGY:
        return _SUIT_ASTROLOGY[card.suit]
    return "Celestial rhythm — tune into the sky's subtle timing cues."


def chinese_zodiac_for(card: TarotCard) -> Tuple[str, str]:
    index = card.number % len(_CHINESE_ZODIAC)
    return _CHINESE_ZODIAC[index]


def native_medicine_for(card: TarotCard) -> Tuple[str, str]:
    element = (card.element or "").lower()
    if element in _NATIVE_ELEMENT_ANIMALS:
        return _NATIVE_ELEMENT_ANIMALS[element]
    if card.suit and card.suit.lower() in _NATIVE_ELEMENT_ANIMALS:
        return _NATIVE_ELEMENT_ANIMALS[card.suit.lower()]
    return _NATIVE_ELEMENT_ANIMALS["spirit"]


def describe_card_correspondences(drawn_card: DrawnCard) -> str:
    """Return a formatted block describing layered esoteric correspondences."""

    numerology = numerology_for(drawn_card.card)
    astrology = astrology_for(drawn_card.card)
    zodiac_name, zodiac_summary = chinese_zodiac_for(drawn_card.card)
    medicine_animal, medicine_summary = native_medicine_for(drawn_card.card)

    orientation_note = (
        "Inner reflection"
        if drawn_card.is_reversed
        else "Outward expression"
    )

    lines = [
        f"Chaldean Numerology : {numerology.number} — {numerology.title}. {numerology.summary}",
        f"Astrological Link    : {astrology}",
        f"Chinese Zodiac Echo  : {zodiac_name} — {zodiac_summary}",
        f"Native Medicine Ally : {medicine_animal} — {medicine_summary}",
        f"Orientation Lens     : {orientation_note} guides how you integrate this card's lesson.",
    ]
    return "\n".join(lines)


__all__ = [
    "describe_card_correspondences",
]
