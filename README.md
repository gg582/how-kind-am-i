# How Kind Am I

A small CLI survey tool that combines well-known social psychology frameworks to
explore how another person might perceive working and personal relationships.
The inventory uses:

- A short **Big Five** snapshot to approximate traits that affect first
  impressions.
- An **Attachment & Trust** pulse based on adult attachment questionnaires to
  understand how you approach support and boundaries.
- A **Collaboration Style** check adapted from agile team health surveys to
  reflect how you coordinate and guide others.

The tool aggregates your responses and offers narrative insights for different
contexts (manager, peer, mentee, study group, etc.).

## Requirements

- Python 3.10+

## Usage

List the available models and their questions:

```bash
python -m how_kind_am_i.cli models
```

Run the survey interactively:

```bash
python -m how_kind_am_i.cli run
```

Provide responses from a JSON file and export the results:

```bash
python -m how_kind_am_i.cli run \
  --responses-file sample_responses.json \
  --output results.json
```

The JSON file must map each model name to an array of Likert scores (1–5).

## Development

To ensure the project builds, run Python's bytecode compilation check:

```bash
python -m compileall how_kind_am_i
```
