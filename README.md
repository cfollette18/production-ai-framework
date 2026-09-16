# Production AI framework

A portable operating framework for teams and AI agents building production AI systems. Inspired by Sandipan Bhaumik's talk; the implementation design and templates here are original recommendations, not the speaker's published artifacts.

## Dedicated Hermes advisor

The native CLI profile lives in [hermes-enterprise-advisor](https://github.com/cfollette18/hermes-enterprise-advisor). Select it with `hermes profile use enterprise-advisor`, then run `hermes chat`. This repository contains its authoritative knowledge and rebuildable SQLite search index.

## Start here

1. Read `docs/source-notes.md` for the source and review limitations.
2. Follow `docs/operating-framework.md` to define your project and release process.
3. Copy `templates/project.json` into your own project and replace every null field.
4. Add evaluation cases using `templates/evaluation-case.json`.
5. Run `python3 scripts/knowledge.py validate` and `python3 scripts/knowledge.py build`.
6. Query with `python3 scripts/knowledge.py search evaluation`.

Requires Python 3.10+ with SQLite FTS5. No API key, paid model, external database, or third-party Python dependency is required for the catalog tools. These tools validate and search knowledge; they do not execute your agent or evaluate its answers.

## Architecture

Markdown and JSON are authoritative. SQLite is a disposable local search projection. Typed relationships are stored in JSON so a graph database can be added without rewriting the knowledge. Optional embeddings should also be rebuilt from versioned records. Never use an embedding as the only retained representation of a claim.

The initial catalog contains navigation records for five operating areas. It is not an exhaustive claim extraction or a transcription of the source. The full available transcript was reviewed; slide-only details and the speaker's downloadable artifacts were not inspected.

## Repository map

- `AGENTS.md`: instructions for agents consuming and changing this repository.
- `docs/operating-framework.md`: detailed implementation procedures and release gates.
- `docs/retrieval-and-reproducibility.md`: search, provenance, versions, and extensions.
- `docs/source-notes.md`: concise source synopsis and timestamp navigation.
- `sources/`: source metadata and transcript coverage information, without transcript text.
- `knowledge/`: structured navigation records and relationships.
- `templates/`: project, evaluation, trace, change, and incident records.
- `scripts/knowledge.py`: structural validation, index building, and JSON search.
- `.github/workflows/validate.yml`: validation on pushes and pull requests.

## Publication status

Published under cfollette18 as a separate knowledge repository. Choose a code license before public distribution. Upstream content retains its own rights; the source metadata reports no asserted license. This repository links to the source rather than redistributing its transcript or slide images.
