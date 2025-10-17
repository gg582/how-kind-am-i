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
        motivation = aggregated_scores.get("Work Orientation & Craft", {})
        safety = aggregated_scores.get("Team Psychological Safety", {})
        mindset = aggregated_scores.get("Learning Mindset & Resilience", {})
        influence = aggregated_scores.get("Technical Influence Exchange", {})

        insights: Dict[str, str] = {}

        def describe_liking() -> str:
            agreeableness = big_five.get("Agreeableness", 0.5)
            extraversion = big_five.get("Extraversion", 0.5)
            stability = big_five.get("Emotional Stability", 0.5)
            empathy = influence.get("Empathic Communication", 0.5)
            if agreeableness > 0.7 and extraversion > 0.6 and empathy > 0.6:
                return (
                    "Your blend of social ease and empathic signalling primes others to "
                    "enjoy collaborating with you both socially and in technical spaces."
                )
            if stability > 0.6 and empathy > 0.5:
                return (
                    "People experience you as steady and considerate—qualities that help "
                    "new teammates warm up even when you stay succinct."
                )
            return (
                "Initial impressions may feel analytical. Share personal motivations "
                "early on to help others map your intent."
            )

        def describe_technical_relationship() -> str:
            conscientiousness = big_five.get("Conscientiousness", 0.5)
            openness = big_five.get("Openness", 0.5)
            mastery = motivation.get("Mastery Focus", 0.5)
            autonomy = motivation.get("Autonomy Drive", 0.5)
            structure = collaboration.get("Structure Preference", 0.5)
            if mastery > 0.7 and conscientiousness > 0.7:
                return (
                    "Your reputation leans toward precise, craft-focused delivery. Expect "
                    "others to seek you out for architectural reviews and refactoring work."
                )
            if openness > 0.6 and autonomy > 0.6:
                return (
                    "You shine in greenfield problem spaces—co-create lightweight "
                    "guardrails so partners feel looped into your explorations."
                )
            if structure > 0.6:
                return (
                    "Documenting interfaces and test strategies early will showcase your "
                    "systems thinking and make pairing smoother."
                )
            return (
                "Clarify how you balance experimentation with delivery to align "
                "expectations on technical depth and velocity."
            )

        def describe_manager_relationship() -> str:
            trust = attachment.get("Trust Propensity", 0.5)
            boundary = attachment.get("Boundary Clarity", 0.5)
            autonomy = motivation.get("Autonomy Drive", 0.5)
            feedback = influence.get("Feedback Exchange", 0.5)
            if trust > 0.7 and feedback > 0.6:
                return (
                    "Your managers will read you as a reliable escalation partner who "
                    "proactively surfaces trade-offs and listens to coaching."
                )
            if boundary < 0.4:
                return (
                    "Agree on decision scopes explicitly so leaders know when to step in "
                    "versus give you space."
                )
            if autonomy > 0.65:
                return (
                    "Share your preferred operating rhythm to reassure managers that "
                    "autonomy will still produce visibility."
                )
            return (
                "Regular demo notes and retro snippets will help managers stay synced to "
                "your impact without micromanaging."
            )

        def describe_peer_relationship() -> str:
            agreeableness = big_five.get("Agreeableness", 0.5)
            support = collaboration.get("Support Orientation", 0.5)
            safety_avg = safety.get("Psychological Safety", 0.5)
            feedback = influence.get("Feedback Exchange", 0.5)
            if safety_avg > 0.65 and feedback > 0.6:
                return (
                    "You foster candid design discussions and make code reviews feel like "
                    "shared problem solving."
                )
            if agreeableness > 0.7 and support > 0.6:
                return (
                    "Expect peers to appreciate your pairing invites and backlog gardening."
                )
            if support < 0.4:
                return (
                    "Schedule routine async updates to offset any perception that you avoid "
                    "collaborative planning."
                )
            return (
                "Keep signalling curiosity in peers' approaches to deepen mutual trust."
            )

        def describe_subordinate_relationship() -> str:
            guidance = collaboration.get("Structure Preference", 0.5)
            openness = big_five.get("Openness", 0.5)
            mastery = motivation.get("Mastery Focus", 0.5)
            coaching = influence.get("Mentorship Stance", 0.5)
            if coaching > 0.65 and mastery > 0.6:
                return (
                    "Mentees will see you as an invested coach who pairs growth plans with "
                    "clear quality bars."
                )
            if guidance > 0.7 and openness > 0.5:
                return (
                    "Structured onboarding plus openness to new tooling keeps your reports "
                    "learning without feeling boxed in."
                )
            if guidance < 0.4:
                return (
                    "Co-create working agreements to ensure junior engineers know how to "
                    "ask for feedback."
                )
            return (
                "Blend documented guidance with exploratory growth conversations."
            )

        def describe_chatroom_relationship() -> str:
            extraversion = big_five.get("Extraversion", 0.5)
            openness = big_five.get("Openness", 0.5)
            resilience = mindset.get("Challenge Resilience", 0.5)
            learning = mindset.get("Learning Agility", 0.5)
            if extraversion > 0.6 and learning > 0.6:
                return (
                    "You animate study chats with live demos and curated references, keeping "
                    "threads vibrant."
                )
            if resilience > 0.65:
                return (
                    "Sharing how you iterate through bugs encourages others to open up about "
                    "their stuck points."
                )
            return (
                "Post recap notes and invite lightning talks to sustain momentum online."
            )

        def describe_code_review() -> str:
            conscientiousness = big_five.get("Conscientiousness", 0.5)
            safety_avg = safety.get("Psychological Safety", 0.5)
            feedback = influence.get("Feedback Exchange", 0.5)
            mastery = motivation.get("Mastery Focus", 0.5)
            if mastery > 0.7 and feedback > 0.6:
                return (
                    "Review feedback will read as craft-enriching and actionable—expect "
                    "teammates to request your sign-off."
                )
            if safety_avg < 0.45:
                return (
                    "Signal positive intent and ask clarifying questions before offering "
                    "refactors to keep reviews collaborative."
                )
            if conscientiousness > 0.65:
                return (
                    "Your detail orientation keeps regressions out; summarise priorities so "
                    "authors know what to tackle first."
                )
            return (
                "Offer context on architectural goals to ensure review comments land well."
            )

        insights["General Liking"] = describe_liking()
        insights["Technical Collaboration"] = describe_technical_relationship()
        insights["Manager Relationship"] = describe_manager_relationship()
        insights["Peer Relationship"] = describe_peer_relationship()
        insights["Mentor/Lead Relationship"] = describe_subordinate_relationship()
        insights["Learning Community"] = describe_chatroom_relationship()
        insights["Code Review Dynamics"] = describe_code_review()

        return insights


def default_models() -> Tuple[SurveyModel, ...]:
    """Factory for the default survey models used by the CLI."""
    big_five_questions = [
        LikertScaleQuestion(
            "I make friends easily during new project kickoffs.", "Extraversion"
        ),
        LikertScaleQuestion(
            "I feel little concern for how teammates are doing.",
            "Agreeableness",
            reverse_scored=True,
        ),
        LikertScaleQuestion(
            "I am always prepared for stand-ups or design reviews.", "Conscientiousness"
        ),
        LikertScaleQuestion(
            "I get stressed out easily when production issues arise.",
            "Emotional Stability",
            reverse_scored=True,
        ),
        LikertScaleQuestion(
            "I enjoy exploring new programming paradigms.", "Openness"
        ),
        LikertScaleQuestion(
            "I prefer that others start conversations first.",
            "Extraversion",
            reverse_scored=True,
        ),
        LikertScaleQuestion(
            "I quickly notice when teammates need help.", "Agreeableness"
        ),
        LikertScaleQuestion(
            "I leave my working notes scattered across tools.",
            "Conscientiousness",
            reverse_scored=True,
        ),
        LikertScaleQuestion(
            "I adapt well when sprint plans change unexpectedly.", "Emotional Stability"
        ),
        LikertScaleQuestion(
            "I like experimenting with unfamiliar frameworks.", "Openness"
        ),
        LikertScaleQuestion(
            "I energise teams during pairing sessions.", "Extraversion"
        ),
        LikertScaleQuestion(
            "I can be detached from teammates' feelings.",
            "Agreeableness",
            reverse_scored=True,
        ),
        LikertScaleQuestion(
            "I maintain tidy documentation and repositories.", "Conscientiousness"
        ),
        LikertScaleQuestion(
            "I stay calm while debugging under pressure.", "Emotional Stability"
        ),
        LikertScaleQuestion(
            "I look for patterns that connect different tech stacks.", "Openness"
        ),
        LikertScaleQuestion(
            "I avoid casual chats with new colleagues.",
            "Extraversion",
            reverse_scored=True,
        ),
        LikertScaleQuestion(
            "I empathise with users when evaluating trade-offs.", "Agreeableness"
        ),
        LikertScaleQuestion(
            "I postpone writing tests until the end.",
            "Conscientiousness",
            reverse_scored=True,
        ),
        LikertScaleQuestion(
            "My mood swings make it hard to stay focused.",
            "Emotional Stability",
            reverse_scored=True,
        ),
        LikertScaleQuestion(
            "I love reading papers or RFCs about emerging tools.", "Openness"
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
            "I am comfortable when requirements remain flexible.",
            "Structure Preference",
            reverse_scored=True,
        ),
        LikertScaleQuestion(
            "I host working sessions to unblock cross-functional partners.",
            "Support Orientation",
        ),
        LikertScaleQuestion(
            "I create templates or runbooks to share team knowledge.",
            "Structure Preference",
        ),
    ]

    work_orientation_questions = [
        LikertScaleQuestion(
            "I push for autonomy in how I implement solutions.", "Autonomy Drive"
        ),
        LikertScaleQuestion(
            "I am motivated by becoming a deeper craft expert.", "Mastery Focus"
        ),
        LikertScaleQuestion(
            "I connect our product work to an end-user mission.", "Purpose Alignment"
        ),
        LikertScaleQuestion(
            "I prefer others to define the approach in detail.",
            "Autonomy Drive",
            reverse_scored=True,
        ),
        LikertScaleQuestion(
            "I invest in deliberate practice (katas, labs, spikes).",
            "Mastery Focus",
        ),
        LikertScaleQuestion(
            "I see how our team's impact ladders into company goals.",
            "Purpose Alignment",
        ),
    ]

    psychological_safety_questions = [
        LikertScaleQuestion(
            "Members of this team are able to bring up tough technical issues.",
            "Psychological Safety",
        ),
        LikertScaleQuestion(
            "When someone makes a mistake on this team, it is often held against them.",
            "Psychological Safety",
            reverse_scored=True,
        ),
        LikertScaleQuestion(
            "People on this team accept others being different.", "Psychological Safety"
        ),
        LikertScaleQuestion(
            "It is safe to take a risk on this team.", "Psychological Safety"
        ),
        LikertScaleQuestion(
            "It is difficult to ask other members for help.",
            "Psychological Safety",
            reverse_scored=True,
        ),
        LikertScaleQuestion(
            "No one on this team deliberately acts to undermine others.",
            "Psychological Safety",
        ),
        LikertScaleQuestion(
            "Working with this team, my unique skills are valued.",
            "Psychological Safety",
        ),
    ]

    learning_mindset_questions = [
        LikertScaleQuestion(
            "I see challenging bugs as opportunities to expand my skills.",
            "Learning Agility",
        ),
        LikertScaleQuestion(
            "I avoid tasks that might expose gaps in my knowledge.",
            "Learning Agility",
            reverse_scored=True,
        ),
        LikertScaleQuestion(
            "Feedback on my code helps me grow even if it stings at first.",
            "Challenge Resilience",
        ),
        LikertScaleQuestion(
            "I believe my core technical talent is fixed.",
            "Challenge Resilience",
            reverse_scored=True,
        ),
        LikertScaleQuestion(
            "I keep a backlog of experiments or prototypes I want to run.",
            "Learning Agility",
        ),
        LikertScaleQuestion(
            "I bounce back quickly after an incident postmortem.",
            "Challenge Resilience",
        ),
    ]

    influence_exchange_questions = [
        LikertScaleQuestion(
            "I tailor technical explanations to the audience's context.",
            "Empathic Communication",
        ),
        LikertScaleQuestion(
            "I invite feedback on decisions that affect other teams.",
            "Feedback Exchange",
        ),
        LikertScaleQuestion(
            "I mentor others through architectural reasoning.", "Mentorship Stance"
        ),
        LikertScaleQuestion(
            "I often push my preferred solution without alignment.",
            "Empathic Communication",
            reverse_scored=True,
        ),
        LikertScaleQuestion(
            "I share context when I request changes in code reviews.",
            "Feedback Exchange",
        ),
        LikertScaleQuestion(
            "I help teammates connect their growth plans to project work.",
            "Mentorship Stance",
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
        SurveyModel(
            name="Work Orientation & Craft",
            description=(
                "A triad based on self-determination theory emphasising autonomy, "
                "mastery, and purpose alignment within engineering careers."
            ),
            questions=work_orientation_questions,
        ),
        SurveyModel(
            name="Team Psychological Safety",
            description=(
                "Items from Amy Edmondson's psychological safety construct adapted "
                "for engineering squads and incident response teams."
            ),
            questions=psychological_safety_questions,
        ),
        SurveyModel(
            name="Learning Mindset & Resilience",
            description=(
                "Statements inspired by Carol Dweck's growth mindset research and "
                "resilience scales tailored to continuous learning in tech."
            ),
            questions=learning_mindset_questions,
        ),
        SurveyModel(
            name="Technical Influence Exchange",
            description=(
                "A composite drawing from leader-member exchange (LMX) and technical "
                "mentorship literature on how engineers circulate influence."
            ),
            questions=influence_exchange_questions,
        ),
    )
