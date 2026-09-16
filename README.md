# Production AI Framework

An agent-independent framework for planning, reviewing, and operating enterprise AI systems. Any agent that can read text or JSON can use it. No Hermes installation, model provider, vector database, or agent SDK is required.

The framework turns a proposed AI workflow into explicit requirements, evaluation evidence, operational controls, and accountable release decisions. Its procedures are implementation recommendations inspired by Sandipan Bhaumik's talks at AI Engineer Europe 2026 — a production playbook and a multi-agent orchestration patterns talk — and Jo Kristian Bergum's BM25-for-agentic-search talk at AI Engineer World's Fair 2026, not a verbatim transcript or vendor deployment manual. See the [source notes](docs/source-notes.md) for the playbook talk, the [orchestration talk notes](docs/source-notes-choreography.md), and the [BM25 talk notes](docs/source-notes-bm25.md).

## The five pillars

| Pillar | Question it answers | What you produce |
|---|---|---|
| **Evaluation** | How will we know the system works for this business? | Representative cases, rubrics, behavior checks, release criteria |
| **Observability** | Can we explain what happened during a request? | Correlated traces, outcome metrics, alerts, diagnostic evidence |
| **Data foundations** | Is the information current, authorized, usable, and traceable? | Source inventory, versioned snapshots, freshness checks, trace-data policy, retrieval configuration |
| **Orchestration** | How do steps, agents, and people coordinate and recover? | Workflow state, dependencies, retry limits, human handoffs |
| **Governance** | Who owns decisions, permissions, changes, and failures? | Owners, authorization boundaries, change records, rollback plans |

The pillars work together: evaluation detects a problem; traces locate it; data or workflow controls address its cause; governance determines who can change the system and how recovery is verified. [Read the pillar guide](docs/pillars.md) and [detailed operating procedures](docs/operating-framework.md). For coordination, state handoff, and failure-recovery patterns between agents, see [multi-agent orchestration patterns](docs/multi-agent-orchestration.md).

## Give this to any agent

Start with [START_HERE.md](START_HERE.md). It supplies the operating contract, reading order, and expected outputs. An agent does not need to recognize AGENTS.md automatically: explicitly give it the entry point.

> Read START_HERE.md in this repository. Use its framework as the authority for enterprise AI planning. Ask about my use case, then create a project contract and a plan across the five pillars. Cite supporting sections, flag missing decisions, and do not invent deployment details.

| Agent capability | Access method |
|---|---|
| Reads repositories | Clone this repository; start with START_HERE.md |
| Accepts text attachments or context | Supply [dist/agent-context.md](dist/agent-context.md), a complete text pack |
| Accepts structured context | Load [dist/knowledge.json](dist/knowledge.json), with stable IDs, paths, origins, content, and hashes |
| Calls commands | Use the optional get, related, bundle, and search CLI operations |
| Has its own retrieval service | Import the JSON records while preserving IDs and provenance |

URL-based agents can fetch the [raw text pack](https://raw.githubusercontent.com/cfollette18/production-ai-framework/main/dist/agent-context.md) or [raw JSON pack](https://raw.githubusercontent.com/cfollette18/production-ai-framework/main/dist/knowledge.json). Replace `main` with a commit SHA to pin a version. If your agent cannot fetch URLs, download and attach the pack.

## Apply it to a project

1. Define the business outcome, users, allowed actions, owners, and constraints.
2. Draft a contract using [templates/project.json](templates/project.json).
3. Assess all five pillars and identify the evidence missing from each.
4. Build representative evaluations and diagnostic traces before comparing implementations.
5. Plan staged release, recovery, and ownership. Keep unresolved decisions explicit.
6. Use observed outcomes to update evaluations and controls through reviewed changes.

The agent produces plans and draft artifacts. Actual execution requires its host's separately configured tools and authorization. Reading this repository does not authorize deployment.

## Add another transcript or source with any model

Upload [dist/source-ingestion-kit.md](dist/source-ingestion-kit.md) and your new transcript/document to the model. The kit tells it how to inventory the input, extract evidenced claims, preserve numerical context, map material to the five pillars, handle conflicts, and return files ready for review and integration.

Optionally upload the current [dist/knowledge.json](dist/knowledge.json) so the model can compare against existing records. With no snapshot, it must mark comparison as pending. The kit supplies a complete synthetic example, a JSON Schema, continuation rules for long inputs, and exact file destinations.

See [ingestion/README.md](ingestion/README.md) for the copy/paste prompt and validation commands. This is a standalone authoring kit; no Hermes profile or database is required. [Raw upload file](https://raw.githubusercontent.com/cfollette18/production-ai-framework/main/dist/source-ingestion-kit.md).

## Rebuild and query

Reading the files requires no runtime. Optional tools require Python 3.10+; SQLite search additionally requires FTS5.

```bash
git clone https://github.com/cfollette18/production-ai-framework.git
cd production-ai-framework
python3 scripts/knowledge.py validate
python3 scripts/knowledge.py export
python3 scripts/knowledge.py get evaluation
python3 scripts/knowledge.py related pillar-1
python3 scripts/knowledge.py bundle
python3 scripts/knowledge.py build
python3 scripts/knowledge.py search evaluation
python3 -m pip install -r ingestion/requirements.txt  # optional ingestion validation and full contributor tests
python3 scripts/validate_intake.py --all
python3 scripts/build_ingestion_kit.py --check
python3 -m unittest discover -s tests
```

Markdown and templates are authoritative. The reproducible exports in dist/ are the portable knowledge "database"; .local/ contains disposable SQLite indexes. Graph and vector services are optional. [Agent integration guide](docs/agent-integration.md).

## Optional implementations

[Hermes Enterprise Advisor](https://github.com/cfollette18/hermes-enterprise-advisor) is a separate, ready-to-use native Hermes profile that consumes this framework. It is one adapter, not a dependency.

## Scope and rights

Maintained by [cfollette18](https://github.com/cfollette18). Source review limitations and origin are documented. This is not exhaustive audiovisual extraction, regulatory certification, or current vendor documentation. No transcript or slide images are redistributed. No reuse license has yet been selected; public availability alone is not an open-source license.
