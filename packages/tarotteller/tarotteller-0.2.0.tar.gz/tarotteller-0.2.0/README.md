# TarotTeller

TarotTeller is a modern Python toolkit for exploring tarot cards through scripted workflows, a friendly command line interface, and an optional desktop experience. It ships with a complete 78-card deck, positional spreads, contextual storytelling, and immersive journaling prompts so that every reading feels intentional and repeatable.

## Key capabilities
- **Rich tarot data model** – Generate a shuffled 78-card deck with upright and reversed interpretations, orientation-aware text, elemental correspondences, and numerology insights.
- **Spread orchestration** – Work with bundled layouts such as a single-card draw, three-card story, and the ten-card Celtic Cross or specify an ad-hoc card count for quick pulls.
- **Context-aware insights** – Analyse a querent question to identify themes, timeframe, and sentiment, then blend that profile with spread prompts to surface personalised guidance.
- **Immersive companions** – Layer rituals, soundtrack suggestions, and journaling prompts over readings in radiant, mystic, or grounded tones.
- **Multiple interfaces** – Use the `tarotteller` CLI for scripted draws, launch the Tkinter GUI for live sessions, or import the Python API for automation and experimentation.

## Installation
TarotTeller uses a `pyproject.toml`-driven build powered by setuptools and the `src/` layout.

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

Once installed, the `tarotteller` and `tarotteller-gui` console scripts become available.

## Command line quick start
List cards, inspect a profile, or draw readings directly from your shell:

```bash
# Show the first five major arcana cards
$ tarotteller list --arcana major --limit 5

# Print detailed information about The Magician
$ tarotteller info "The Magician"

# Pull a three-card spread with deterministic shuffle and orientation
$ tarotteller draw --spread three_card --seed 11 --orientation-seed 21

# Draw two upright-only cards with immersive storytelling in a grounded tone
$ tarotteller draw --cards 2 --no-reversed --immersive --tone grounded
```

Provide `--question` text to unlock contextual analysis and personalised insight for each draw. Seeds can be supplied to reproduce both card order and orientation.

## Graphical interface
Launch the Tkinter-powered desktop client after installation:

```bash
tarotteller-gui
```

The GUI lets you pick a spread (or override the card count), capture the querent's question, toggle reversed cards, and decide whether to show positional prompts or immersive extras. Results combine spread prompts, card meanings, correspondence layers, and optional personalised summaries generated from the question profile. A dedicated help dialog summarises controls and reading tips.

## Python API
Interact with the deck and spreads from your own scripts:

```python
from tarotteller import (
    TarotDeck,
    draw_spread,
    build_immersive_companion,
    analyze_question,
    InterpretationEngine,
    TarotKnowledgeBase,
)

# Prepare the deck and spread
deck = TarotDeck()
deck.seed(42)
deck.reset(shuffle=True)
reading = draw_spread(deck, "three_card", rng=13)

# Build contextual insights
profile = analyze_question("What career move should I pursue next quarter?")
engine = InterpretationEngine(TarotKnowledgeBase(deck.all_cards))
insights = engine.insights_for_reading(reading, profile)

for placement, insight in zip(reading.placements, insights):
    print(f"{placement.position.title}: {insight.card_name} ({insight.orientation})")
    print(f"   {insight.message}")

# Optional immersive companion text
print()
print(build_immersive_companion([p.card for p in reading.placements], tone="mystic", profile=profile))
```

## Project structure
TarotTeller follows the canonical packaging layout so it can be published to PyPI without adjustments:

```
src/tarotteller/
├── __init__.py              # Public package surface and version metadata
├── core/                    # Deck, spread, context analysis, and knowledge base logic
├── interfaces/              # CLI and GUI entry points with console script bindings
└── narrative/               # Immersive storytelling helpers
```

Tests live under `tests/` and target the public API, CLI, and GUI helpers.

## Development workflow
1. Create and activate a virtual environment (see Installation above).
2. Install development dependencies if needed (for example `pip install -e .[dev]` when extra requirements are added).
3. Run the automated test suite:
   ```bash
   pytest
   ```
4. Use `python -m tarotteller.interfaces.cli ...` or `python -m tarotteller.interfaces.gui` for module-based debugging.

## Version history
| Version | Date       | Highlights |
|---------|------------|------------|
| 0.2.0   | Unreleased | Reorganised the package into `core`, `interfaces`, and `narrative` modules, introduced consolidated public exports, and refreshed documentation for distribution readiness. |
| 0.1.0   | 2024-03    | Initial release with deck generation, spreads, CLI, GUI, contextual insights, and immersive companion stories. |

Dates will be finalised when publishing tagged releases. Follow semantic versioning as future features land.
