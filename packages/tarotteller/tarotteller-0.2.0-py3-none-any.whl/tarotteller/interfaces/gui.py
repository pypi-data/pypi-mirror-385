"""Graphical interface for TarotTeller using Tkinter."""

from __future__ import annotations

import textwrap
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Iterable, List, Optional

from ..core.context import analyze_question
from ..core.correspondences import describe_card_correspondences
from ..core.deck import DrawnCard, TarotDeck
from ..core.engine import InterpretationEngine, build_prompt_interpretation
from ..core.knowledge import TarotKnowledgeBase
from ..core.spreads import SPREADS, SpreadReading, draw_spread
from ..narrative.immersive import build_immersive_companion


_TEXT_WRAP_WIDTH = 72

HELP_TEXT = """
TarotTeller Help
================

Getting Started
---------------
1. Choose a spread from the drop-down menu. Leave "Cards" blank to use the spread's default count or enter a number to override it.
2. (Optional) Enter your question or intention in the "Question" field so TarotTeller can tailor interpretations.
3. (Optional) Provide a shuffle seed if you want reproducible draws. Leave it blank for a fresh shuffle each time.
4. Toggle options to allow reversed cards, show detailed spread layout, or add an immersive storytelling companion.
5. Pick the tone for immersive guidance from the "Tone" selector.

Settings Glossary
-----------------
* **Cards override** lets you pull a quick custom number of cards without using a spread.
* **Shuffle seed** repeats the same draw sequence—great for study or journaling.
* **Allow reversed** flips cards upside down to surface shadow lessons and integration work.
* **Detailed spread view** prints every positional prompt for note-taking.
* **Immersive companion** unlocks numerology, Western astrology, Chinese zodiac, and Native medicine storytelling in the tone you choose.

Drawing a Reading
-----------------
* Click **Draw Reading** to pull cards for the chosen spread.
* Click **Reset Deck** to reshuffle using the current seed (if any).
* The results panel shows each card with a short interpretation that blends the spread prompt with TarotTeller's knowledge base. When you provide a question, additional personalised insight appears below the reading.

Correspondence Layers
---------------------
Every card now includes:
* **Chaldean numerology** to describe the card's energetic vibration.
* **Western astrology links** that highlight planetary or elemental allies.
* **Chinese zodiac echoes** for yearly archetypes to meditate on.
* **Native medicine allies** offering grounded, nature-based guidance.
These appear under each card's meaning and inside immersive companions.

Tips
----
* Use consistent seeds when you want to revisit the same draw for journaling.
* Questions that include timeframe, mood, and focus keywords help TarotTeller respond more specifically.
* Reset the deck between readings if you want a fresh shuffle.
"""


def _wrap_prompt(text: str) -> str:
    wrapper = textwrap.TextWrapper(
        width=_TEXT_WRAP_WIDTH, initial_indent="   ", subsequent_indent="   "
    )
    return wrapper.fill(text)


def _format_simple_reading(
    reading: SpreadReading, knowledge_base: TarotKnowledgeBase
) -> str:
    lines: List[str] = []
    for placement in reading.placements:
        card = placement.card
        prompt = _wrap_prompt(
            build_prompt_interpretation(placement, knowledge_base)
        )
        meaning = textwrap.indent(card.meaning, "   ")
        correspondences = textwrap.indent(
            describe_card_correspondences(card), "   "
        )
        sections = [prompt, meaning, correspondences]
        formatted_sections = "\n\n".join(
            section for section in sections if section
        )
        lines.append(
            f"{placement.position.index}. {card.card.name} ({card.orientation})\n"
            f"{formatted_sections}"
        )
    return "\n\n".join(lines)


def _format_direct_draw(cards: Iterable[DrawnCard]) -> str:
    formatted: List[str] = []
    for index, card in enumerate(cards, start=1):
        meaning = textwrap.indent(card.meaning, "   ")
        correspondences = textwrap.indent(
            describe_card_correspondences(card), "   "
        )
        segments = "\n\n".join(
            segment
            for segment in (meaning, correspondences)
            if segment
        )
        formatted.append(
            f"Card {index}: {card.card.name} ({card.orientation})\n{segments}"
        )
    return "\n\n".join(formatted)


class TarotTellerApp:
    """Tkinter application shell for the TarotTeller GUI."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("TarotTeller")
        self.deck = TarotDeck()
        self._help_window: Optional[tk.Toplevel] = None
        self._build_layout()

    def _build_layout(self) -> None:
        self.root.geometry("880x640")
        self.root.minsize(720, 520)

        style = ttk.Style(self.root)
        style.configure("Hint.TLabel", foreground="#444444")

        container = ttk.Frame(self.root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        controls = ttk.Frame(container)
        controls.pack(side=tk.TOP, fill=tk.X, pady=(0, 12))

        # Spread selection
        ttk.Label(controls, text="Spread:").grid(row=0, column=0, sticky=tk.W)
        self.spread_var = tk.StringVar(value="single")
        spread_choices = sorted(SPREADS.keys())
        self.spread_box = ttk.Combobox(
            controls,
            textvariable=self.spread_var,
            values=spread_choices,
            state="readonly",
            width=18,
        )
        self.spread_box.grid(row=0, column=1, sticky=tk.W, padx=(4, 16))

        # Card count override
        ttk.Label(controls, text="Cards:").grid(row=0, column=2, sticky=tk.W)
        self.card_count = tk.StringVar(value="")
        self.card_entry = ttk.Entry(controls, textvariable=self.card_count, width=6)
        self.card_entry.grid(row=0, column=3, sticky=tk.W, padx=(4, 16))
        ttk.Label(controls, text="(leave blank to use spread)").grid(
            row=0, column=4, sticky=tk.W
        )

        # Question input
        ttk.Label(controls, text="Question:").grid(
            row=1, column=0, sticky=tk.NW, pady=(12, 0)
        )
        self.question = tk.Text(controls, height=3, width=60)
        self.question.grid(row=1, column=1, columnspan=4, sticky=tk.W, pady=(12, 0))

        ttk.Label(
            controls,
            text="Tip: Share who or what you're reading for, any timeframe (for example 'next month'), and how you feel so TarotTeller can tailor the insights.",
            style="Hint.TLabel",
            wraplength=520,
            justify=tk.LEFT,
        ).grid(row=2, column=1, columnspan=4, sticky=tk.W, pady=(4, 0))

        # Seed entry
        ttk.Label(controls, text="Shuffle Seed:").grid(row=3, column=0, sticky=tk.W)
        self.seed_var = tk.StringVar(value="")
        self.seed_entry = ttk.Entry(controls, textvariable=self.seed_var, width=10)
        self.seed_entry.grid(row=3, column=1, sticky=tk.W, padx=(4, 16))

        # Options row
        options = ttk.Frame(controls)
        options.grid(row=3, column=2, columnspan=3, sticky=tk.W)

        self.allow_reversed = tk.BooleanVar(value=True)
        ttk.Checkbutton(options, text="Allow reversed", variable=self.allow_reversed).pack(
            side=tk.LEFT
        )

        self.detailed = tk.BooleanVar(value=False)
        ttk.Checkbutton(options, text="Detailed spread view", variable=self.detailed).pack(
            side=tk.LEFT, padx=(12, 0)
        )

        self.immersive = tk.BooleanVar(value=False)
        ttk.Checkbutton(options, text="Immersive companion", variable=self.immersive).pack(
            side=tk.LEFT, padx=(12, 0)
        )

        ttk.Label(options, text="Tone:").pack(side=tk.LEFT, padx=(16, 4))
        self.tone = tk.StringVar(value="radiant")
        tone_menu = ttk.Combobox(
            options,
            textvariable=self.tone,
            values=["radiant", "mystic", "grounded"],
            state="readonly",
            width=10,
        )
        tone_menu.pack(side=tk.LEFT)

        ttk.Label(
            controls,
            text=(
                "Settings guide: 'Allow reversed' invites upside-down cards for shadow work. "
                "'Detailed spread view' prints every positional prompt. "
                "'Immersive companion' adds numerology, Western astrology, Chinese zodiac, and Native medicine layers in the voice you pick. "
                "Use 'Shuffle Seed' for repeatable draws and the 'Cards' override when you want a quick custom pull."
            ),
            style="Hint.TLabel",
            wraplength=760,
            justify=tk.LEFT,
        ).grid(row=4, column=0, columnspan=5, sticky=tk.W, pady=(12, 0))

        # Action buttons
        actions = ttk.Frame(container)
        actions.pack(fill=tk.X)
        draw_button = ttk.Button(actions, text="Draw Reading", command=self.draw_reading)
        draw_button.pack(side=tk.LEFT)

        reset_button = ttk.Button(actions, text="Reset Deck", command=self.reset_deck)
        reset_button.pack(side=tk.LEFT, padx=(12, 0))

        help_button = ttk.Button(actions, text="Help", command=self._show_help)
        help_button.pack(side=tk.LEFT, padx=(12, 0))

        # Output area
        output_frame = ttk.Frame(container)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        self.output = tk.Text(output_frame, wrap=tk.WORD, font=("TkDefaultFont", 11))
        self.output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(output_frame, command=self.output.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output.configure(yscrollcommand=scrollbar.set)

    def run(self) -> None:
        self.root.mainloop()

    def reset_deck(self) -> None:
        seed_text = self.seed_var.get().strip()
        try:
            seed_value = int(seed_text) if seed_text else None
        except ValueError:
            messagebox.showerror("Invalid seed", "Seed must be an integer value.")
            return
        self.deck = TarotDeck()
        if seed_value is not None:
            self.deck.seed(seed_value)
        self.deck.reset(shuffle=True)
        messagebox.showinfo("Deck reset", "Deck reshuffled and ready for a new reading.")

    def draw_reading(self) -> None:
        try:
            seed_value = self._parse_optional_int(self.seed_var.get())
        except ValueError:
            messagebox.showerror("Invalid seed", "Seed must be an integer value.")
            return

        try:
            card_count = self._parse_optional_int(self.card_count.get())
        except ValueError:
            messagebox.showerror("Invalid cards", "Cards must be left blank or an integer.")
            return

        deck = TarotDeck()
        knowledge_base = TarotKnowledgeBase(deck.all_cards)
        if seed_value is not None:
            deck.seed(seed_value)
        deck.reset(shuffle=True)

        question = self.question.get("1.0", tk.END).strip()
        profile = None
        engine: Optional[InterpretationEngine] = None
        if question:
            profile = analyze_question(question)
            engine = InterpretationEngine(knowledge_base)

        allow_reversed = self.allow_reversed.get()

        try:
            if card_count:
                drawn = deck.draw(card_count, allow_reversed=allow_reversed)
                rendered = _format_direct_draw(drawn)
                sections: List[str] = [rendered]
                if engine and profile:
                    insights = [engine.build_card_insight(card, profile) for card in drawn]
                    response = engine.render_question_response(insights, profile)
                    if response:
                        sections.insert(0, response)
                    sections.append(engine.render_for_cards(insights, profile))
                if self.immersive.get():
                    sections.append(
                        build_immersive_companion(
                            drawn, tone=self.tone.get(), profile=profile
                        )
                    )
                self._render_output("\n\n".join(section.strip() for section in sections if section))
                return

            spread_key = self.spread_var.get() or "single"
            if spread_key not in SPREADS:
                raise KeyError(spread_key)
            reading = draw_spread(
                deck,
                spread_key,
                allow_reversed=allow_reversed,
            )
        except (ValueError, KeyError) as exc:
            messagebox.showerror("Unable to draw", str(exc))
            return

        rendered = (
            reading.as_text()
            if self.detailed.get()
            else _format_simple_reading(reading, knowledge_base)
        )
        sections = [rendered]
        if engine and profile:
            insights = engine.insights_for_reading(reading, profile)
            response = engine.render_question_response(
                insights, profile, spread_title=reading.spread.name
            )
            if response:
                sections.insert(0, response)
            sections.append(
                engine.render_personalised_summary(
                    reading, profile, insights=insights
                )
            )

        if self.immersive.get():
            sections.append(
                build_immersive_companion(
                    [placement.card for placement in reading.placements],
                    tone=self.tone.get(),
                    profile=profile,
                )
            )

        self._render_output("\n\n".join(section.strip() for section in sections if section))

    def _render_output(self, text: str) -> None:
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text.strip())
        self.output.see("1.0")

    def _show_help(self) -> None:
        if self._help_window and self._help_window.winfo_exists():
            self._help_window.lift()
            self._help_window.focus_set()
            return

        window = tk.Toplevel(self.root)
        window.title("TarotTeller Help")
        window.geometry("560x480")
        window.transient(self.root)

        frame = ttk.Frame(window, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(frame, wrap=tk.WORD, font=("TkDefaultFont", 11))
        text_widget.insert(tk.END, HELP_TEXT.strip())
        text_widget.configure(state=tk.DISABLED)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.configure(yscrollcommand=scrollbar.set)

        window.protocol("WM_DELETE_WINDOW", self._close_help)
        self._help_window = window

    def _close_help(self) -> None:
        if self._help_window and self._help_window.winfo_exists():
            self._help_window.destroy()
        self._help_window = None

    @staticmethod
    def _parse_optional_int(value: str) -> Optional[int]:
        value = value.strip()
        if not value:
            return None
        return int(value)


def launch() -> None:
    """Convenience entry point for running the GUI."""

    app = TarotTellerApp()
    app.run()


__all__ = ["TarotTellerApp", "launch"]
