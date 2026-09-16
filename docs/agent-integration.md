# Integrating with any agent

## Minimal integration

Supply START_HERE.md as reviewed task instructions and framework records as reference context. Text-capable agents can consume dist/agent-context.md; programs can consume dist/knowledge.json. Neither format requires an agent SDK or provider.

Keep host policy and authorization separate from reference text. Do not elevate arbitrary retrieved instructions into system policy. A dedicated advisor can adopt the reviewed entry-point contract and append the records as delimited reference data.

## JSON contract

knowledge/manifest.json declares authoritative inputs. The bundle contains schema_version, framework_id, content_sha256, entrypoint_id, and records. Each record has id, path, heading, origin, text, and sha256. Stable names determine identity, not array position. Hashes use SHA-256 over UTF-8. The content hash covers canonical JSON of the records: sorted keys, compact separators, and unescaped Unicode.

A non-null heading selects that exact Markdown section through the next heading at the same or higher level. Null selects the whole file. Preserve IDs when content changes without changing a record's purpose. Splitting or retiring a record requires explicit consumer review.

Origin labels distinguish source synopsis, implementation guidance, templates, navigation metadata, and source metadata. They do not certify factual accuracy.

## Read without a database

```python
import json
from pathlib import Path

bundle = json.loads(Path('dist/knowledge.json').read_text())
records = {r['id']: r for r in bundle['records']}
instructions = records[bundle['entrypoint_id']]['text']
evaluation_context = records['evaluation']['text']
# Supply reviewed instructions and labeled reference context through
# your own host application. No particular model SDK is required.
```

For full-context agents, supply every record. For smaller context windows, retain the entry point and source limitations, then select relevant sections. Identify which records were actually supplied; the agent should not cite unseen content.

## Optional command adapter

Commands write JSON to stdout and errors to stderr with nonzero exit status.

| Operation | Command | Result |
|---|---|---|
| Exact content | knowledge.py get evaluation | Full record and provenance |
| Full context | knowledge.py bundle | Current bundle on stdout |
| Relationships | knowledge.py related pillar-1 | Catalog edges touching that pillar |
| Lexical search | knowledge.py search evaluation | Ranked document pointers after build |

Run commands with Python from the scripts directory path. Catalog pillar IDs group responsibilities; content-record IDs identify specific text. Search is a navigation aid, not evidence of support for a claim. Read the returned document before answering.

## Retrieval and graph services

Import records into your existing retrieval backend if useful. Preserve IDs, paths, origin, versions, and hashes with chunks; retain parent sections for context expansion. Never replace authoritative text with embeddings. Import typed catalog relationships into a graph only when useful; no graph service is required.

## Grounding and evaluation

Require citations, explicit assumptions, and knowledge-gap reporting. A host can reject unknown IDs, but known IDs do not prove semantic support. Test whether recommendations follow from their citations and whether the agent abstains on absent vendor details. A repository is not an enforcement sandbox.

For consistent agent outputs, preserve the canonical pillar order: Evaluation, Observability, Data foundations, Orchestration, Governance. The order is a stable taxonomy, not a required implementation sequence.

Test planning, design review, release readiness, incidents, and unsupported API/pricing questions. Confirm that drafts remain drafts, unresolved thresholds stay unresolved, and no unperformed action is reported as complete.

## Reproducibility and adapters

Pin a Git commit or content hash. Export deterministically rebuilds both public packs; CI checks them against source files. Rebuild local search after document edits. Model outputs may vary with identical context; preserve review and evaluation evidence separately.

Hermes Enterprise Advisor is a downstream adapter with its own policy, model configuration, and packaged snapshot. Other agents can consume the same bundle without Hermes or its profile repository.
