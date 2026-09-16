# Routing new knowledge into the framework

## Canonical pillar map

| Order | ID | Meaning | Existing procedure record |
|---|---|---|---|
| 1 | evaluation | Define success, datasets, scoring, semantic and behavioral tests | evaluation |
| 2 | observability | Traces, operational metrics, diagnostics, alert evidence | observability |
| 3 | data-foundations | Source quality, ownership, freshness, transformations, retrieval lifecycle, trace storage | data-foundations |
| 4 | orchestration | Workflow state, coordination, tool execution, retries, compensation, human handoffs | orchestration |
| 5 | governance | Accountability, permissions, change control, release approval, exceptions | governance |
| — | unmapped | Relevant material that does not fit the above; explain it | none |

Assign one primary pillar and zero or more distinct secondary pillars per claim. Preserve a claim once and use secondary tags rather than duplicating its text into multiple places. Incident handling may touch all five; classify the actual assertion, not the surrounding chapter title.

## File destinations

The authoritative source packet and source-specific guide live together. For source ID `reliable-agents-talk`, propose:

```text
sources/reliable-agents-talk/
  intake.json       # source identity, segments, claims, relationships, procedures, coverage
  guide.md          # human/agent-readable source-specific synthesis, with claim citations
  handoff.md        # extraction/review/integration state and remaining decisions
```

This directory is the candidate addition, not a replacement of the framework's existing sources. Do not overwrite `sources/manifest.json` or `sources/coverage.json`; those describe the original talk. Keep the new source's metadata in its own intake packet. Do not add claims directly to knowledge/records.json: that file is a navigation catalog, not the general claim store. New claim relationships belong in the new intake packet, not the catalog's relationship list. If a separate catalog entry is needed, inspect the current source-registration contract first; the portable bundle registration below is the standard path for this kit.

Never put raw private transcripts, tokens, logs, or customer documents into these public paths. A local original can be retained outside Git with an accurately computed checksum/reference. Respect the source's actual rights when preparing shareable extraction text; unknown rights are not permission to republish raw material.

## Register a reviewed addition for agent consumption

After authorized source review, append these entries to the existing records array in `knowledge/manifest.json` without replacing current entries. Substitute the actual source ID:

```json
[
  {
    "id": "source-reliable-agents-talk-intake",
    "path": "sources/reliable-agents-talk/intake.json",
    "heading": null,
    "origin": "source_metadata"
  },
  {
    "id": "source-reliable-agents-talk-guide",
    "path": "sources/reliable-agents-talk/guide.md",
    "heading": null,
    "origin": "source_synopsis"
  }
]
```

`source_metadata` is the bundle-container label; each claim/step's own origin remains authoritative. `source_synopsis` identifies a source-specific guide; label any proposed implementation material inside that guide explicitly. Unreviewed packets can remain staged but should not be registered as approved authority. The current bundle format has no automatic review gate: this is an explicit reviewer decision. Preserve handoff.md for review, but omit it from default agent context unless it contains necessary unresolved-use constraints; those constraints should also appear in the guide.

If a source adds a general principle, propose a cited patch to the relevant section of docs/operating-framework.md. Do not automatically overwrite that section or remove qualifications from older guidance. If sources conflict, retain both versions and state applicability/uncertainty until a reviewer resolves them. Claim IDs stay stable across revisions unless the assertion's identity changes; new IDs are never reused for different claims.

The portable JSON/text export includes every registered source. The existing SQLite search currently scans docs/ only, so a newly registered source is available through `get` and `bundle` but is not automatically searchable via SQLite. State this accurately in the handoff. Adapters can ingest the portable bundle directly; improving SQLite coverage is separate work.

## Integration checks

From the framework repository:

```bash
python3 scripts/validate_intake.py sources/reliable-agents-talk/intake.json
python3 scripts/knowledge.py validate
python3 scripts/knowledge.py export
python3 scripts/knowledge.py check-export
python3 scripts/knowledge.py get source-reliable-agents-talk-guide
python3 -m unittest discover -s tests
```

Record actual outcomes. Validation confirms structure and references, not semantic fidelity. Before publication, review evidence, scope, contradictions, and public-sharing suitability. The synthetic example is not a source to register in production knowledge.

## Downstream adapters

The framework is independent of every agent runtime. Once integrated, tell consumers the new framework revision and bundle hash. Consumers choose when to update their pinned snapshots. A source-ingestion run does not modify Hermes config, user credentials, tools, or profiles. The separate Hermes repository has its own refresh/publication process; do not claim it was updated just because the framework export changed.
