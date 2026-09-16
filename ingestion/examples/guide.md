# Fictional retry workshop — example guide

This is a synthetic extraction example, not production advice or an independently verified report. Evidence locators refer to paragraph labels in transcript.txt; no audiovisual material was reviewed.

## Claims by pillar

- **Evaluation:** document criteria before approving a release; the speaker supplies no sample size or accuracy threshold. [example-retry-workshop-c004; P004]
- **Observability:** capture the retrieved document's version in the request trace. [example-retry-workshop-c002; P002]
- **Data foundations:** secondary relevance only: the trace recommendation assumes a document version can be identified. It does not establish a complete source-data strategy. [example-retry-workshop-c002; P002]
- **Orchestration:** one facilitator proposes two retry attempts and another proposes four for the same trial. Preserve both as alternatives; neither is a validated default. [example-retry-workshop-c001; P001] [example-retry-workshop-c003; P003]
- **Governance:** release approval is mentioned as the context for evaluation criteria; no full approval workflow is supplied. [example-retry-workshop-c004; P004]

## Procedure and proposed check

Source guidance: record the retrieved version in the request trace. Proposed implementation check: compare a test trace's version with the document actually retrieved. This verification method is our proposal; it was not described or executed in the source. [example-retry-workshop-c002]

## Conflicts and gaps

The retry cap is unresolved and excludes long-running migrations in the first proposal. No tracing vendor, exact schema, fallback for missing identifiers, evaluation sample size, or passing score is supplied. Do not invent these details.

Suggested agent evaluation: ask which retry cap is mandatory. The expected response should describe the disagreement and limited trial scope, rather than selecting a universal number. This is a proposed test, not an executed result. [example-retry-workshop-c001] [example-retry-workshop-c003]
