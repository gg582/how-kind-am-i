"""Survey data structures and scoring utilities."""
from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Dict, Iterable, List, Tuple


@dataclass(frozen=True)
class LikertScaleQuestion:
    """A single Likert-scale question."""

    prompt: str
    dimension: str
    reverse_scored: bool = False
    scale_min: int = 1
    scale_max: int = 5

    def normalise(self, raw_value: int) -> float:
        """Convert a raw Likert response into a normalised value."""
        if raw_value < self.scale_min or raw_value > self.scale_max:
            raise ValueError(
                f"Response {raw_value} is outside the allowed range "
                f"[{self.scale_min}, {self.scale_max}]"
            )
        distance = raw_value - self.scale_min
        scale_range = self.scale_max - self.scale_min
        normalised = distance / scale_range
        if self.reverse_scored:
            return 1.0 - normalised
        return normalised


@dataclass
class SurveyModel:
    """Represents a validated psychological framework expressed as a survey."""

    name: str
    description: str
    questions: List[LikertScaleQuestion]
    dimension_aliases: Dict[str, str] = field(default_factory=dict)

    def aggregate(self, responses: Iterable[int]) -> Dict[str, float]:
        """Aggregate responses into normalised dimension scores."""
        dimension_scores: Dict[str, List[float]] = {}
        for question, response in zip(self.questions, responses):
            dimension_scores.setdefault(question.dimension, []).append(
                question.normalise(response)
            )
        return {dim: mean(values) for dim, values in dimension_scores.items()}


class SurveyEngine:
    """Combines multiple survey models and derives contextual insights."""

    def __init__(self, models: Iterable[SurveyModel]):
        self.models = list(models)

    def run(self, responses: Dict[str, List[int]]) -> Dict[str, Dict[str, float]]:
        """Run the engine using the provided responses for each model."""
        results: Dict[str, Dict[str, float]] = {}
        for model in self.models:
            model_responses = responses.get(model.name, [])
            if len(model_responses) != len(model.questions):
                raise ValueError(
                    f"Expected {len(model.questions)} responses for {model.name}, "
                    f"received {len(model_responses)}"
                )
            results[model.name] = model.aggregate(model_responses)
        return results

    def interpret_relationship_dynamics(
        self, aggregated_scores: Dict[str, Dict[str, float]]
    ) -> Dict[str, str]:
        """Generate qualitative insights for different social contexts."""
        big_five = aggregated_scores.get("Big Five Snapshot", {})
        attachment = aggregated_scores.get("Attachment & Trust", {})
        collaboration = aggregated_scores.get("Collaboration Style", {})

        insights: Dict[str, str] = {}

        def describe_liking() -> str:
            agreeableness = big_five.get("Agreeableness", 0.5)
            extraversion = big_five.get("Extraversion", 0.5)
            neuroticism = big_five.get("Emotional Stability", 0.5)
            if agreeableness > 0.7 and extraversion > 0.6:
                return (
                    "People are likely to perceive you as warm and approachable. "
                    "Expect positive first impressions in casual settings."
                )
            if neuroticism < 0.4:
                return (
                    "Your calm demeanour encourages trust even if you are more reserved."
                )
            return (
                "Mixed signals may arise; focus on active listening to reinforce rapport."
            )

        def describe_technical_relationship() -> str:
            conscientiousness = big_five.get("Conscientiousness", 0.5)
            openness = big_five.get("Openness", 0.5)
            collaboration_style = collaboration.get("Structure Preference", 0.5)
            if conscientiousness > 0.7 and collaboration_style > 0.6:
                return (
                    "As an engineer you project reliability and a preference for well-defined "
                    "processes. Teammates will appreciate clear plans and retrospectives."
                )
            if openness > 0.6:
                return (
                    "You thrive in exploratory technical discussions—lean into design spikes "
                    "and brainstorming sessions."
                )
            return (
                "Balance structure with curiosity to strengthen technical collaborations."
            )

        def describe_manager_relationship() -> str:
            trust = attachment.get("Trust Propensity", 0.5)
            support = collaboration.get("Support Orientation", 0.5)
            if trust > 0.7 and support > 0.6:
                return (
                    "Managers are likely to see you as a dependable partner who escalates "
                    "risks early and seeks joint solutions."
                )
            if trust < 0.4:
                return (
                    "Clarify expectations frequently to avoid misunderstandings with managers."
                )
            return (
                "Share progress rhythms and decision logs to reinforce confidence upward."
            )

        def describe_peer_relationship() -> str:
            agreeableness = big_five.get("Agreeableness", 0.5)
            support = collaboration.get("Support Orientation", 0.5)
            if agreeableness > 0.7 and support > 0.6:
                return (
                    "Peers will value pairing sessions and shared ownership with you."
                )
            if support < 0.4:
                return (
                    "Proactively offer feedback rounds to counter perceptions of distance."
                )
            return (
                "Keep communication cadences steady to deepen peer rapport."
            )

        def describe_subordinate_relationship() -> str:
            guidance = collaboration.get("Structure Preference", 0.5)
            openness = big_five.get("Openness", 0.5)
            if guidance > 0.7 and openness > 0.5:
                return (
                    "Direct reports will benefit from your organised onboarding and "
                    "willingness to adapt to their learning styles."
                )
            if guidance < 0.4:
                return (
                    "Define check-ins and role clarity to avoid ambiguity with mentees."
                )
            return (
                "Blend documented guidance with exploratory growth conversations."
            )

        def describe_chatroom_relationship() -> str:
            extraversion = big_five.get("Extraversion", 0.5)
            openness = big_five.get("Openness", 0.5)
            trust = attachment.get("Trust Propensity", 0.5)
            if extraversion > 0.6 and openness > 0.6:
                return (
                    "In study groups you naturally catalyse discussion and share resources."
                )
            if trust < 0.4:
                return (
                    "Start with asynchronous contributions to build familiarity before "
                    "facilitating live sessions."
                )
            return (
                "Consistent summaries and question prompts will keep chatrooms engaged."
            )

        insights["General Liking"] = describe_liking()
        insights["Technical Collaboration"] = describe_technical_relationship()
        insights["Manager Relationship"] = describe_manager_relationship()
        insights["Peer Relationship"] = describe_peer_relationship()
        insights["Mentor/Lead Relationship"] = describe_subordinate_relationship()
        insights["Learning Community"] = describe_chatroom_relationship()

        return insights


def default_models() -> Tuple[SurveyModel, ...]:
    """Factory for the default survey models used by the CLI."""
    big_five_questions = [
        LikertScaleQuestion(
            "I make friends easily.", "Extraversion"
        ),
        LikertScaleQuestion(
            "I feel little concern for others.", "Agreeableness", reverse_scored=True
        ),
        LikertScaleQuestion(
            "I am always prepared.", "Conscientiousness"
        ),
        LikertScaleQuestion(
            "I get stressed out easily.", "Emotional Stability", reverse_scored=True
        ),
        LikertScaleQuestion(
            "I have a rich vocabulary.", "Openness"
        ),
        LikertScaleQuestion(
            "I don't talk a lot.", "Extraversion", reverse_scored=True
        ),
        LikertScaleQuestion(
            "I sympathise with others' feelings.", "Agreeableness"
        ),
        LikertScaleQuestion(
            "I leave my belongings around.", "Conscientiousness", reverse_scored=True
        ),
        LikertScaleQuestion(
            "I change my mood a lot.", "Emotional Stability", reverse_scored=True
        ),
        LikertScaleQuestion(
            "I am quick to understand things.", "Openness"
        ),
    ]

    attachment_questions = [
        LikertScaleQuestion(
            "I find it easy to depend on other people.", "Trust Propensity"
        ),
        LikertScaleQuestion(
            "I worry that others won't support me.", "Trust Propensity", reverse_scored=True
        ),
        LikertScaleQuestion(
            "I communicate boundaries clearly.", "Boundary Clarity"
        ),
        LikertScaleQuestion(
            "I prefer solving problems alone.", "Boundary Clarity", reverse_scored=True
        ),
    ]

    collaboration_questions = [
        LikertScaleQuestion(
            "I enjoy facilitating group retrospectives.", "Support Orientation"
        ),
        LikertScaleQuestion(
            "I prefer to document plans before acting.", "Structure Preference"
        ),
        LikertScaleQuestion(
            "I proactively check in on teammates' progress.", "Support Orientation"
        ),
        LikertScaleQuestion(
            "I am comfortable when requirements remain flexible.", "Structure Preference", reverse_scored=True
        ),
    ]

    return (
        SurveyModel(
            name="Big Five Snapshot",
            description=(
                "A brief inventory inspired by the Big Five model to gauge core "
                "personality traits related to social perception."
            ),
            questions=big_five_questions,
            dimension_aliases={
                "Emotional Stability": "Neuroticism (reversed)",
            },
        ),
        SurveyModel(
            name="Attachment & Trust",
            description=(
                "Questions adapted from adult attachment research highlighting how "
                "you form trust and manage relational boundaries."
            ),
            questions=attachment_questions,
        ),
        SurveyModel(
            name="Collaboration Style",
            description=(
                "A collaboration readiness pulse inspired by agile team health "
                "checks, focusing on support behaviours and structure preferences."
            ),
            questions=collaboration_questions,
        ),
    )
