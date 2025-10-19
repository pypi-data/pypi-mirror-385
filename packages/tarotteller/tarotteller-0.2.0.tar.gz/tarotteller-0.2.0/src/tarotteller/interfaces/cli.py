"""Command line interface for TarotTeller."""

from __future__ import annotations

import argparse
import sys
import textwrap
from typing import Iterable, List, Optional

from ..core.context import analyze_question
from ..core.correspondences import describe_card_correspondences
from ..core.deck import TarotCard, TarotDeck, format_card
from ..core.engine import InterpretationEngine
from ..core.knowledge import TarotKnowledgeBase
from ..core.spreads import SPREADS, SpreadReading, draw_spread
from ..narrative.immersive import build_immersive_companion


def _print_cards(cards: Iterable[TarotCard]) -> None:
    for card in cards:
        suit = f" ({card.suit})" if card.suit else ""
        print(f"- {card.name}{suit}")


def _wrap_prompt(text: str) -> str:
    wrapper = textwrap.TextWrapper(
        width=72, initial_indent="   ", subsequent_indent="   "
    )
    return wrapper.fill(text)


def cmd_list(deck: TarotDeck, args: argparse.Namespace) -> int:
    """List cards matching the provided filters."""

    cards = deck.list_cards(arcana=args.arcana, suit=args.suit)
    filtered = list(cards)
    if not filtered:
        target = args.suit or args.arcana or "deck"
        print(f"No cards found for {target}.")
        return 0
    print(f"Cards in deck ({len(filtered)} results):")
    _print_cards(filtered[: args.limit] if args.limit else filtered)
    return 0


def cmd_info(deck: TarotDeck, args: argparse.Namespace) -> int:
    card = deck.get_card(args.name)
    if card is None:
        print(f"Unknown card: {args.name}", file=sys.stderr)
        return 1
    print(format_card(card))
    return 0


def _format_simple_draw(reading: SpreadReading) -> str:
    lines: List[str] = []
    for placement in reading.placements:
        card = placement.card
        prompt = _wrap_prompt(placement.position.prompt)
        meaning = textwrap.indent(card.meaning, "   ")
        correspondences = textwrap.indent(
            describe_card_correspondences(card), "   "
        )
        sections = [prompt, meaning, correspondences]
        formatted = "\n\n".join(section for section in sections if section)
        lines.append(
            f"{placement.position.index}. {card.card.name} ({card.orientation})\n"
            f"{formatted}"
        )
    return "\n\n".join(lines)


def cmd_draw(deck: TarotDeck, args: argparse.Namespace) -> int:
    profile = None
    engine: InterpretationEngine | None = None
    if args.question:
        profile = analyze_question(args.question)
        engine = InterpretationEngine(TarotKnowledgeBase(deck.all_cards))

    if args.seed is not None:
        deck.seed(args.seed)
        deck.reset(shuffle=True)

    if args.cards:
        try:
            drawn = deck.draw(args.cards, allow_reversed=not args.no_reversed)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        lines = []
        for index, card in enumerate(drawn, start=1):
            meaning = textwrap.indent(card.meaning, "   ")
            correspondences = textwrap.indent(
                describe_card_correspondences(card), "   "
            )
            block = "\n\n".join(
                segment for segment in (meaning, correspondences) if segment
            )
            lines.append(
                f"Card {index}: {card.card.name} ({card.orientation})\n{block}"
            )
        print("\n\n".join(lines))
        if engine and profile:
            insights = [engine.build_card_insight(card, profile) for card in drawn]
            print()
            print(engine.render_for_cards(insights, profile))
        if args.immersive:
            print()
            print(
                build_immersive_companion(
                    drawn,
                    tone=args.tone,
                    profile=profile,
                )
            )
        return 0

    spread_key = args.spread or "single"
    if spread_key not in SPREADS:
        print(
            f"Unknown spread '{spread_key}'. Available spreads: {', '.join(SPREADS)}",
            file=sys.stderr,
        )
        return 1

    try:
        reading = draw_spread(
            deck,
            spread_key,
            allow_reversed=not args.no_reversed,
            rng=args.orientation_seed,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    rendered = reading.as_text() if args.detailed else _format_simple_draw(reading)
    print(rendered)
    if engine and profile:
        print()
        print(engine.render_personalised_summary(reading, profile))
    if args.immersive:
        print()
        print(
            build_immersive_companion(
                [placement.card for placement in reading.placements],
                tone=args.tone,
                profile=profile,
            )
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tarotteller", description="Explore tarot cards and spreads."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list", help="List cards in the deck")
    list_parser.add_argument("--arcana", choices=["major", "minor"], help="Filter by arcana")
    list_parser.add_argument(
        "--suit",
        choices=["Wands", "Cups", "Swords", "Pentacles"],
        help="Filter minor arcana by suit",
    )
    list_parser.add_argument(
        "--limit", type=int, default=0, help="Limit the number of cards shown"
    )
    list_parser.set_defaults(func=cmd_list)

    info_parser = sub.add_parser("info", help="Display detailed information about a card")
    info_parser.add_argument("name", help="Name of the card to display")
    info_parser.set_defaults(func=cmd_info)

    draw_parser = sub.add_parser("draw", help="Draw cards or full spreads")
    draw_parser.add_argument(
        "--spread",
        choices=list(SPREADS.keys()),
        help="Name of the spread to draw",
    )
    draw_parser.add_argument(
        "--cards", type=int, help="Draw a specific number of cards instead of a spread"
    )
    draw_parser.add_argument(
        "--seed", type=int, help="Seed the deck shuffling for reproducible draws"
    )
    draw_parser.add_argument(
        "--orientation-seed", type=int, help="Seed orientation randomisation"
    )
    draw_parser.add_argument(
        "--no-reversed", action="store_true", help="Disable reversed cards"
    )
    draw_parser.add_argument(
        "--detailed", action="store_true", help="Show the full spread text"
    )
    draw_parser.add_argument(
        "--question",
        help="Phrase the querent's question to unlock contextual insights",
    )
    draw_parser.add_argument(
        "--immersive",
        action="store_true",
        help="Add journal prompts, rituals, and soundtrack cues to the reading",
    )
    draw_parser.add_argument(
        "--tone",
        choices=["radiant", "mystic", "grounded"],
        default="radiant",
        help="Stylistic tone for immersive guidance",
    )
    draw_parser.set_defaults(func=cmd_draw)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    deck = TarotDeck()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(deck, args)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
