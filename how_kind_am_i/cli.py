"""Command line interface for running social perception surveys."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, List

from .survey import SurveyEngine, default_models

LIKERT_LABEL = "Respond on a scale from 1 (strongly disagree) to 5 (strongly agree)."


def prompt_for_responses(questions: Iterable[str]) -> List[int]:
    """Interactively prompt the user for responses."""
    responses: List[int] = []
    for index, prompt in enumerate(questions, start=1):
        while True:
            try:
                value = int(input(f"Q{index}: {prompt}\n> "))
            except ValueError:
                print("Please provide an integer response.")
                continue
            if value < 1 or value > 5:
                print("Responses must be between 1 and 5.")
                continue
            responses.append(value)
            break
    return responses


def load_responses_from_file(path: Path) -> Dict[str, List[int]]:
    """Load pre-filled responses from a JSON file."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Response file must contain a JSON object.")
    typed_payload: Dict[str, List[int]] = {}
    for model_name, values in payload.items():
        if not isinstance(values, list) or not all(
            isinstance(item, int) for item in values
        ):
            raise ValueError(
                "Every model entry must be an array of integers representing Likert scores."
            )
        typed_payload[model_name] = values
    return typed_payload


def run_cli(args: argparse.Namespace) -> None:
    engine = SurveyEngine(default_models())

    if args.command == "models":
        for model in engine.models:
            print(f"\n=== {model.name} ===")
            print(model.description)
            for idx, question in enumerate(model.questions, start=1):
                note = " (reverse scored)" if question.reverse_scored else ""
                print(f"  {idx}. {question.prompt}{note}")
        return

    if args.command == "run":
        if args.responses_file:
            responses = load_responses_from_file(Path(args.responses_file))
        else:
            responses: Dict[str, List[int]] = {}
            print("\nStarting interactive survey.\n")
            for model in engine.models:
                print(f"\n-- {model.name} --")
                print(model.description)
                print(LIKERT_LABEL)
                prompts = [question.prompt for question in model.questions]
                responses[model.name] = prompt_for_responses(prompts)
        aggregated = engine.run(responses)
        insights = engine.interpret_relationship_dynamics(aggregated)

        print("\nSurvey summary:\n")
        for model_name, dimensions in aggregated.items():
            print(f"{model_name}:")
            for dimension, score in dimensions.items():
                print(f"  {dimension}: {score:.2f}")
        print("\nRelationship insights:\n")
        for context, narrative in insights.items():
            print(f"{context}: {narrative}")

        if args.output:
            output_path = Path(args.output)
            payload = {
                "aggregated_scores": aggregated,
                "relationship_insights": insights,
            }
            output_path.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            print(f"\nSaved results to {output_path}")
        return

    raise ValueError(f"Unhandled command: {args.command}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a CLI survey grounded in validated social psychology models to "
            "understand interpersonal dynamics."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    models_parser = subparsers.add_parser(
        "models", help="List available survey models and their questions."
    )
    models_parser.set_defaults(func=run_cli)

    run_parser = subparsers.add_parser(
        "run", help="Execute the survey interactively or from a JSON file."
    )
    run_parser.add_argument(
        "--responses-file",
        help="Optional path to a JSON file containing pre-filled Likert responses.",
    )
    run_parser.add_argument(
        "--output",
        help="Optional path to store the aggregated results as JSON.",
    )
    run_parser.set_defaults(func=run_cli)

    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
