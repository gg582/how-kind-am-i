# How Kind Am I

A small CLI survey tool that combines well-known social and organisational
psychology frameworks to explore how collaborators might perceive working with a
software engineer. The inventory now layers multiple validated constructs with a
focus on engineering practice:

- A 20-item **Big Five Snapshot** tuned to engineering rituals (stand-ups,
  incidents, experimentation) to approximate first impressions.
- An **Attachment & Trust** pulse based on adult attachment questionnaires to
  understand how you approach support and boundaries.
- A richer **Collaboration Style** check adapted from agile team health surveys
  that probes facilitation, structure, and enablement habits.
- A **Work Orientation & Craft** triad inspired by self-determination theory to
  capture autonomy, mastery, and purpose drivers common to engineering careers.
- A **Team Psychological Safety** scale drawn from Amy Edmondson's validated
  items and rewritten for software squads.
- A **Learning Mindset & Resilience** set informed by Carol Dweck's growth
  mindset research to understand how you metabolise feedback and incidents.
- A **Technical Influence Exchange** composite grounded in leader–member
  exchange and mentorship literature to illuminate feedback and coaching flows.

The tool aggregates your responses and offers narrative insights for contexts
such as manager alignment, peer collaboration, mentorship, code review dynamics,
and online learning communities.

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
