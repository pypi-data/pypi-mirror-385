"""Interpretation engine that ties spreads to contextual insights."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .context import ContextProfile
from .knowledge import TarotKnowledgeBase
from .spreads import SpreadPlacement, SpreadReading


def build_prompt_interpretation(
    placement: SpreadPlacement, knowledge_base: TarotKnowledgeBase
) -> str:
    """Return a narrative interpretation that pairs a prompt with card insight."""

    drawn_card = placement.card
    themes = knowledge_base.themes_for_card(drawn_card.card)
    focus = themes[0] if themes else "spirituality"
    message = knowledge_base.insight_for(drawn_card, focus)

    prompt = placement.position.prompt.strip()
    if prompt and not prompt.endswith((".", "!", "?")):
        prompt += "."
    prompt = f"{prompt} " if prompt else ""

    return (
        f"In the {placement.position.title} position, "
        f"{prompt}{message}"
    )


@dataclass
class PersonalizedInsight:
    """A contextual message generated for a drawn card."""

    placement_index: int
    title: str
    card_name: str
    orientation: str
    prompt: str
    message: str


class InterpretationEngine:
    """Produce contextual readings that blend spreads with question intent."""

    def __init__(self, knowledge_base: TarotKnowledgeBase):
        self._knowledge_base = knowledge_base

    def _format_focuses(self, focuses: Sequence[str]) -> str:
        if not focuses:
            return "your evolving path"
        if len(focuses) == 1:
            return focuses[0].replace("_", " ")
        *rest, last = [focus.replace("_", " ") for focus in focuses]
        return ", ".join(rest) + f" and {last}"

    def _select_focus(self, card_themes: Sequence[str], focuses: Sequence[str]) -> str:
        for focus in focuses:
            if focus in card_themes:
                return focus
        if card_themes:
            return card_themes[0]
        return focuses[0] if focuses else "general"

    def _build_insight(
        self,
        placement: SpreadPlacement,
        profile: ContextProfile,
    ) -> PersonalizedInsight:
        card = placement.card
        themes = self._knowledge_base.themes_for_card(card.card)
        focus = self._select_focus(themes, profile.focuses)
        message = self._knowledge_base.insight_for(card, focus)
        return PersonalizedInsight(
            placement_index=placement.position.index,
            title=placement.position.title,
            card_name=card.card.name,
            orientation=card.orientation,
            prompt=placement.position.prompt,
            message=message,
        )

    def insights_for_reading(
        self, reading: SpreadReading, profile: ContextProfile
    ) -> List[PersonalizedInsight]:
        return [self._build_insight(placement, profile) for placement in reading.placements]

    def _compose_story_arc(
        self, insights: Sequence[PersonalizedInsight], profile: ContextProfile
    ) -> List[str]:
        story_lines: List[str] = []
        focus_text = self._format_focuses(profile.focuses)
        timeframe = profile.timeframe.replace("_", " ")
        mood = profile.sentiment
        highlighted = ", ".join(sorted(profile.highlighted_terms)[:6])

        opener = (
            f"You arrive with a {mood} heart, asking '{profile.question}'. "
            f"This reading frames a {timeframe} journey through {focus_text}."
        )
        if highlighted:
            opener += f" Notable echoes from your question — {highlighted} — set the scene."
        story_lines.append(opener)

        for insight in insights:
            orientation = insight.orientation.lower()
            prompt = insight.prompt.rstrip(".")
            chapter = (
                f"In the chapter of {insight.title}, the {insight.card_name} appears {orientation}. "
                f"It responds to the call to {prompt.lower()} and whispers: {insight.message}"
            )
            story_lines.append(chapter)

        closer = (
            "Together these moments sketch a living story — one you can revisit, annotate, "
            "and reshape as you take your next steps."
        )
        story_lines.append(closer)
        return story_lines

    def render_personalised_summary(
        self,
        reading: SpreadReading,
        profile: ContextProfile,
        insights: Sequence[PersonalizedInsight] | None = None,
    ) -> str:
        """Return a multi-line personalised summary for ``reading``."""

        if insights is None:
            insights = self.insights_for_reading(reading, profile)
        lines: List[str] = []
        lines.append("Personalized Insight")
        lines.append("-------------------")
        lines.append(f"Question : {profile.question}")
        if profile.focuses:
            lines.append(f"Focus    : {', '.join(profile.focuses)}")
        lines.append(f"Timeframe: {profile.timeframe.replace('_', ' ')}")
        lines.append(f"Mood     : {profile.sentiment}")
        if profile.highlighted_terms:
            lines.append(
                "Signals  : " + ", ".join(sorted(profile.highlighted_terms)[:6])
            )
        lines.append("")
        for insight in insights:
            header = (
                f"{insight.placement_index}. {insight.title} — "
                f"{insight.card_name} ({insight.orientation})"
            )
            lines.append(header)
            lines.append("   " + insight.prompt)
            lines.append("   " + insight.message)
            lines.append("")
        lines.append("Story Arc")
        lines.append("---------")
        for paragraph in self._compose_story_arc(insights, profile):
            lines.append(paragraph)
            lines.append("")
        lines.append(
            "Let these highlights guide follow-up actions and keep logging feedback to "
            "train the model on what resonates."
        )
        return "\n".join(lines).strip()

    def render_for_cards(
        self, cards: Iterable[PersonalizedInsight], profile: ContextProfile
    ) -> str:
        lines: List[str] = []
        lines.append("Personalized Insight")
        lines.append("-------------------")
        lines.append(f"Question : {profile.question}")
        if profile.focuses:
            lines.append(f"Focus    : {', '.join(profile.focuses)}")
        lines.append(f"Timeframe: {profile.timeframe.replace('_', ' ')}")
        lines.append(f"Mood     : {profile.sentiment}")
        lines.append("")
        for insight in cards:
            header = f"{insight.card_name} ({insight.orientation})"
            lines.append(header)
            lines.append("   " + insight.message)
            lines.append("")
        return "\n".join(lines).strip()

    def build_card_insight(self, drawn_card, profile: ContextProfile) -> PersonalizedInsight:
        themes = self._knowledge_base.themes_for_card(drawn_card.card)
        focus = self._select_focus(themes, profile.focuses)
        message = self._knowledge_base.insight_for(drawn_card, focus)
        return PersonalizedInsight(
            placement_index=0,
            title="",  # Not used for direct draws
            card_name=drawn_card.card.name,
            orientation=drawn_card.orientation,
            prompt="",
            message=message,
        )

    def render_question_response(
        self,
        insights: Sequence[PersonalizedInsight],
        profile: ContextProfile,
        *,
        spread_title: str | None = None,
    ) -> str:
        """Summarise how the reading answers the querent's question."""

        if not insights:
            return ""

        primary = min(
            insights,
            key=lambda insight: (
                insight.placement_index if insight.placement_index else 0,
                insight.card_name,
            ),
        )
        focus_text = self._format_focuses(profile.focuses)
        timeframe_text = profile.timeframe.replace("_", " ")

        response_lines: List[str] = []
        response_lines.append("Question Response")
        response_lines.append("-----------------")
        response_lines.append(f"You asked: {profile.question}")
        response_lines.append("")

        if spread_title:
            context_line = f"Drawing on the {spread_title} spread, "
        else:
            context_line = "Drawing from the cards, "

        descriptor: List[str] = []
        if primary.title:
            descriptor.append(f"the {primary.title} position")
        if primary.prompt:
            descriptor.append(primary.prompt.lower().rstrip("."))
        descriptor_text = " about ".join(descriptor) if descriptor else "the message"

        orientation = primary.orientation.lower()
        card_name = primary.card_name

        message_sentence = (
            f"{context_line}{descriptor_text} brings the {orientation} {card_name} forward as your clearest answer."
        )

        if primary.prompt:
            prompt_text = primary.prompt.rstrip(".").lower()
            follow_intro = f"It speaks to {prompt_text}. "
        else:
            follow_intro = ""

        follow_up = primary.message
        closing = (
            f"Look for this to unfold over a {timeframe_text} horizon, especially within {focus_text}."
        )

        response_lines.append(
            f"{message_sentence} {follow_intro}{follow_up} {closing}".strip()
        )

        return "\n".join(response_lines).strip()
