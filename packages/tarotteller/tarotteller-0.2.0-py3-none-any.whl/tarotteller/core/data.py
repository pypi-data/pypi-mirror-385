"""Static data definitions for tarot cards used by :mod:`tarotteller`.

The module exposes rich metadata for both the major and minor arcana.  The
minor arcana data is generated programmatically from suit and rank descriptors
so that the resulting cards feel cohesive while keeping the definitions easy to
maintain.
"""

from __future__ import annotations

from typing import Dict, Iterable, List


MAJOR_ARCANA: List[Dict[str, object]] = [
    {
        "arcana": "major",
        "number": 0,
        "name": "The Fool",
        "keywords": ["beginnings", "adventure", "innocence"],
        "reversed_keywords": ["hesitation", "risk", "recklessness"],
        "description": "A leap of faith invites new experiences and personal growth when embraced with curiosity.",
    },
    {
        "arcana": "major",
        "number": 1,
        "name": "The Magician",
        "keywords": ["manifestation", "resourcefulness", "power"],
        "reversed_keywords": ["untapped potential", "manipulation", "distraction"],
        "description": "Focused intention turns ideas into reality; align your skills with your will to create change.",
    },
    {
        "arcana": "major",
        "number": 2,
        "name": "The High Priestess",
        "keywords": ["intuition", "mystery", "stillness"],
        "reversed_keywords": ["secrets", "disconnection", "doubt"],
        "description": "Quiet reflection reveals hidden knowledge and invites trust in your inner wisdom.",
    },
    {
        "arcana": "major",
        "number": 3,
        "name": "The Empress",
        "keywords": ["abundance", "nurturing", "fertility"],
        "reversed_keywords": ["creative block", "dependence", "neglect"],
        "description": "A season of growth rewards compassion, creativity, and tending to what you cherish most.",
    },
    {
        "arcana": "major",
        "number": 4,
        "name": "The Emperor",
        "keywords": ["structure", "authority", "stability"],
        "reversed_keywords": ["control", "rigidity", "power struggles"],
        "description": "Clear boundaries and deliberate leadership bring lasting security when used responsibly.",
    },
    {
        "arcana": "major",
        "number": 5,
        "name": "The Hierophant",
        "keywords": ["tradition", "wisdom", "mentorship"],
        "reversed_keywords": ["rebellion", "dogma", "restriction"],
        "description": "Seek guidance in shared knowledge and rituals, while remembering to keep them meaningful to you.",
    },
    {
        "arcana": "major",
        "number": 6,
        "name": "The Lovers",
        "keywords": ["connection", "values", "choice"],
        "reversed_keywords": ["misalignment", "imbalance", "temptation"],
        "description": "Relationships mirror your ideals; choose with integrity and honour your heart's truth.",
    },
    {
        "arcana": "major",
        "number": 7,
        "name": "The Chariot",
        "keywords": ["determination", "willpower", "momentum"],
        "reversed_keywords": ["scattered energy", "aggression", "lack of direction"],
        "description": "Harness discipline to steer conflicting forces toward a shared destination and triumph.",
    },
    {
        "arcana": "major",
        "number": 8,
        "name": "Strength",
        "keywords": ["courage", "compassion", "resilience"],
        "reversed_keywords": ["self-doubt", "fear", "raw emotion"],
        "description": "Gentle persistence and empathy tame fears more effectively than force alone ever could.",
    },
    {
        "arcana": "major",
        "number": 9,
        "name": "The Hermit",
        "keywords": ["introspection", "solitude", "wisdom"],
        "reversed_keywords": ["withdrawal", "loneliness", "isolation"],
        "description": "Retreat to listen to your own voice and carry its lantern back to light the path forward.",
    },
    {
        "arcana": "major",
        "number": 10,
        "name": "Wheel of Fortune",
        "keywords": ["cycles", "destiny", "turning point"],
        "reversed_keywords": ["resistance", "unexpected setbacks", "control"],
        "description": "Life turns in constant motion; adapt with grace and you can ride the wave of change.",
    },
    {
        "arcana": "major",
        "number": 11,
        "name": "Justice",
        "keywords": ["fairness", "truth", "accountability"],
        "reversed_keywords": ["bias", "dishonesty", "avoidance"],
        "description": "Decisions carry consequence—act with honesty and weigh all sides before moving ahead.",
    },
    {
        "arcana": "major",
        "number": 12,
        "name": "The Hanged Man",
        "keywords": ["surrender", "new perspective", "pause"],
        "reversed_keywords": ["stalling", "resistance", "martyrdom"],
        "description": "Letting go of control clears space for insight and transforms limbo into awakening.",
    },
    {
        "arcana": "major",
        "number": 13,
        "name": "Death",
        "keywords": ["transformation", "endings", "renewal"],
        "reversed_keywords": ["stagnation", "fear of change", "clinging"],
        "description": "Release what has reached its conclusion to welcome a revitalising chapter.",
    },
    {
        "arcana": "major",
        "number": 14,
        "name": "Temperance",
        "keywords": ["balance", "moderation", "alchemy"],
        "reversed_keywords": ["excess", "imbalance", "restlessness"],
        "description": "Blend opposing elements thoughtfully to craft a harmonious and sustainable rhythm.",
    },
    {
        "arcana": "major",
        "number": 15,
        "name": "The Devil",
        "keywords": ["shadow", "bondage", "materialism"],
        "reversed_keywords": ["liberation", "awareness", "detachment"],
        "description": "Notice the chains you accept; conscious choice can dissolve limiting patterns.",
    },
    {
        "arcana": "major",
        "number": 16,
        "name": "The Tower",
        "keywords": ["upheaval", "revelation", "breakthrough"],
        "reversed_keywords": ["averted disaster", "denial", "fear of change"],
        "description": "Sudden clarity dismantles unstable foundations so that stronger truth can emerge.",
    },
    {
        "arcana": "major",
        "number": 17,
        "name": "The Star",
        "keywords": ["hope", "healing", "guidance"],
        "reversed_keywords": ["discouragement", "doubt", "over-giving"],
        "description": "A calm beacon reminds you to replenish your spirit and trust that renewal is near.",
    },
    {
        "arcana": "major",
        "number": 18,
        "name": "The Moon",
        "keywords": ["intuition", "dreams", "subconscious"],
        "reversed_keywords": ["confusion", "anxiety", "revelation"],
        "description": "Shadows distort the path—listen to subtle cues and move slowly until truth surfaces.",
    },
    {
        "arcana": "major",
        "number": 19,
        "name": "The Sun",
        "keywords": ["vitality", "success", "joy"],
        "reversed_keywords": ["delayed gratification", "overconfidence", "temporary cloudiness"],
        "description": "Warmth, clarity, and celebration radiate outward when you act from authentic confidence.",
    },
    {
        "arcana": "major",
        "number": 20,
        "name": "Judgement",
        "keywords": ["rebirth", "reckoning", "awakening"],
        "reversed_keywords": ["self-doubt", "avoidance", "stagnation"],
        "description": "Answer the call to evolve; honest reflection frees you to step into purpose.",
    },
    {
        "arcana": "major",
        "number": 21,
        "name": "The World",
        "keywords": ["completion", "integration", "wholeness"],
        "reversed_keywords": ["loose ends", "incompletion", "delays"],
        "description": "Celebrate milestones and recognise the mastery earned through the journey's cycle.",
    },
]


SUITS: Dict[str, Dict[str, object]] = {
    "Wands": {
        "element": "Fire",
        "keywords": ["creativity", "ambition", "willpower"],
        "reversed_keywords": ["burnout", "impulsiveness", "frustration"],
        "themes": "passion, invention, and the spark that propels ideas into action",
    },
    "Cups": {
        "element": "Water",
        "keywords": ["emotion", "relationships", "intuition"],
        "reversed_keywords": ["emotional drain", "codependence", "suppression"],
        "themes": "feelings, empathy, spiritual connection, and the flow between hearts",
    },
    "Swords": {
        "element": "Air",
        "keywords": ["thought", "communication", "clarity"],
        "reversed_keywords": ["conflict", "overthinking", "anxiety"],
        "themes": "intellect, conflict, analysis, and the pursuit of clear truth",
    },
    "Pentacles": {
        "element": "Earth",
        "keywords": ["stability", "resources", "practicality"],
        "reversed_keywords": ["insecurity", "materialism", "stagnation"],
        "themes": "work, health, and the tangible results of long-term stewardship",
    },
}


RANKS: List[Dict[str, object]] = [
    {
        "name": "Ace",
        "number": 1,
        "keywords": ["beginnings", "potential", "spark"],
        "reversed_keywords": ["blocked start", "misuse", "uncertainty"],
        "description": "A seed of opportunity arrives, eager to grow if nurtured with intention.",
    },
    {
        "name": "Two",
        "number": 2,
        "keywords": ["balance", "duality", "choice"],
        "reversed_keywords": ["imbalance", "indecision", "stalemate"],
        "description": "Two forces seek harmony, calling for cooperation and mindful decision making.",
    },
    {
        "name": "Three",
        "number": 3,
        "keywords": ["expansion", "collaboration", "growth"],
        "reversed_keywords": ["delay", "misalignment", "frustration"],
        "description": "Community and planning turn early efforts into meaningful progress.",
    },
    {
        "name": "Four",
        "number": 4,
        "keywords": ["stability", "foundation", "containment"],
        "reversed_keywords": ["stagnation", "restlessness", "rigidity"],
        "description": "Structures provide security, yet must be refreshed to avoid complacency.",
    },
    {
        "name": "Five",
        "number": 5,
        "keywords": ["challenge", "disruption", "growth"],
        "reversed_keywords": ["avoidance", "lingering conflict", "recovery"],
        "description": "Tension invites adaptation, forging resilience through discomfort.",
    },
    {
        "name": "Six",
        "number": 6,
        "keywords": ["harmony", "support", "reconciliation"],
        "reversed_keywords": ["one-sidedness", "stagnation", "nostalgia"],
        "description": "Cooperation and shared care restore balance and goodwill.",
    },
    {
        "name": "Seven",
        "number": 7,
        "keywords": ["assessment", "faith", "strategy"],
        "reversed_keywords": ["doubt", "impulsiveness", "avoidance"],
        "description": "Patience and evaluation clarify the next stage of effort.",
    },
    {
        "name": "Eight",
        "number": 8,
        "keywords": ["movement", "mastery", "dedication"],
        "reversed_keywords": ["distraction", "perfectionism", "stalling"],
        "description": "Momentum builds through focused commitment and steady practice.",
    },
    {
        "name": "Nine",
        "number": 9,
        "keywords": ["culmination", "self-reliance", "integration"],
        "reversed_keywords": ["overwhelm", "isolation", "impatience"],
        "description": "Self-awareness and discipline prepare you for the final stretch.",
    },
    {
        "name": "Ten",
        "number": 10,
        "keywords": ["completion", "legacy", "transition"],
        "reversed_keywords": ["burden", "instability", "overextension"],
        "description": "A chapter resolves, offering perspective on what was gained and what comes next.",
    },
    {
        "name": "Page",
        "number": 11,
        "keywords": ["curiosity", "study", "playfulness"],
        "reversed_keywords": ["naivety", "inconsistency", "immaturity"],
        "description": "Messenger energy arrives—stay open to learning and exploring without judgment.",
    },
    {
        "name": "Knight",
        "number": 12,
        "keywords": ["pursuit", "momentum", "mission"],
        "reversed_keywords": ["recklessness", "scattered focus", "frustration"],
        "description": "Bold action advances your goals when tempered with awareness of the impact.",
    },
    {
        "name": "Queen",
        "number": 13,
        "keywords": ["maturity", "nurturing", "magnetism"],
        "reversed_keywords": ["smothering", "insecurity", "withdrawal"],
        "description": "Power softens into generosity, tending to others while upholding healthy boundaries.",
    },
    {
        "name": "King",
        "number": 14,
        "keywords": ["command", "responsibility", "vision"],
        "reversed_keywords": ["domination", "rigidity", "overbearing"],
        "description": "Leadership is proven through integrity and consistent stewardship of resources.",
    },
]


def build_minor_arcana() -> List[Dict[str, object]]:
    """Create the 56 cards that make up the minor arcana.

    The returned dictionaries mirror the structure used for the major arcana,
    but also include ``suit`` and ``rank`` metadata so that callers can filter
    or present the cards as needed.
    """

    cards: List[Dict[str, object]] = []
    for suit_name, suit in SUITS.items():
        suit_keywords = list(suit["keywords"])
        suit_reversed = list(suit["reversed_keywords"])
        for rank in RANKS:
            name = f"{rank['name']} of {suit_name}"
            keywords = sorted(set(rank["keywords"] + suit_keywords))
            reversed_keywords = sorted(set(rank["reversed_keywords"] + suit_reversed))
            description = (
                f"{rank['description']} Expressed through the realm of {suit_name.lower()}, "
                f"it highlights {suit['themes']}.")
            cards.append(
                {
                    "arcana": "minor",
                    "number": rank["number"],
                    "name": name,
                    "suit": suit_name,
                    "rank": rank["name"],
                    "keywords": keywords,
                    "reversed_keywords": reversed_keywords,
                    "description": description,
                    "element": suit["element"],
                }
            )
    return cards


MINOR_ARCANA: List[Dict[str, object]] = build_minor_arcana()


def iter_all_cards() -> Iterable[Dict[str, object]]:
    """Yield dictionaries for each of the 78 tarot cards."""

    yield from MAJOR_ARCANA
    yield from MINOR_ARCANA
