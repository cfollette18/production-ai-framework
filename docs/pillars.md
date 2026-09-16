# Understanding the five pillars

This guide explains the repository's implementation design. The pillars organize responsibilities; they do not mandate a software stack or five separate services.

## Evaluation — define and measure success

Evaluation turns business intent into testable expectations. A fluent answer may still be wrong, unauthorized, slow, expensive, or ineffective. Assess both the outcome and how the workflow reached it.

Define representative cases, expected and prohibited behavior, and measurable criteria. Use deterministic checks for objectively checkable constraints, semantic rubrics for evidence-based quality, and behavioral checks for tool use and workflow execution. Calibrate model judges against human-reviewed examples.

Inputs: business goals, user journeys, domain examples, and risk categories. Outputs: versioned cases, rubrics, results, and thresholds. Acceptance evidence: a candidate can be compared with a baseline on identical cases, with failures visible by category. See operating-framework.md section 2 and templates/evaluation-case.json.

## Observability — make behavior explainable

Observability connects individual actions with the user outcome. Operators need to distinguish a source failure from a model, permission, tool, or workflow failure.

Correlate request, retrieval, model, tool, guardrail, and handoff events. Capture versions, durations, errors, and safe evidence references. Record observable actions without requiring hidden model reasoning or indiscriminate logging of sensitive payloads.

Inputs: workflow events and retention/access requirements. Outputs: traces, dashboards, alerts, and diagnostic paths. Acceptance evidence: an operator can reconstruct a failed test request and locate the responsible owner. See section 3 and templates/trace.json.

## Data foundations — manage system inputs and evidence

Answer-serving information and operational trace data serve different purposes and need explicit lifecycle policies. A model cannot reliably compensate for stale policies, missing permissions, or ambiguous data definitions.

Maintain authoritative sources, owners, effective dates, access restrictions, freshness objectives, transformations, and index versions. Publish consistent retrieval snapshots, test updates and deletions, and retain rollback paths. Govern trace storage separately when sensitivity or retention differs.

Inputs: source inventory, changes, and access rules. Outputs: qualified snapshots, retrieval evidence, freshness monitoring, and managed trace storage. Acceptance evidence: an updated policy is retrieved with the correct version, while superseded and restricted content is handled correctly. See section 4 and [lexical-retrieval-bm25.md](lexical-retrieval-bm25.md) for lexical retrieval configuration and agentic search guidance.

## Orchestration — coordinate work and recover

Orchestration specifies work order, dependencies, and human involvement. Multiple agents are justified only when their roles provide enough benefit to offset coordination cost.

Choose explicit coordination for ordered work or independent event-driven workers where appropriate. Define states, deadlines, retries, cancellation, duplicate delivery, and recovery. Human review needs an owner, queue, and timeout outcome. Approval must refer to the actual proposed action.

Inputs: steps, dependencies, side effects, and human responsibilities. Outputs: state model, coordination decisions, recovery policies. Acceptance evidence: restart, timeout, duplicate delivery, and unavailable-reviewer scenarios have known outcomes. See section 5, [multi-agent-orchestration.md](multi-agent-orchestration.md) for coordination, versioned-state, contract, circuit-breaker, and compensation patterns, and templates/handoff-contract.json.

## Governance — assign accountability and control changes

Governance connects ownership and authorization to the evidence supporting a decision, release, or change.

Name owners for business outcomes, sources, evaluations, runtime, and incidents. Version prompts, models, tools, retrieval configuration, and datasets in release manifests. Enforce permissions outside model text. Record why behavior changed, what was tested, and when to roll back.

Inputs: ownership, permission requirements, risks, and change requests. Outputs: manifests, reviewed changes, exceptions, and incident responsibilities. Acceptance evidence: operators can identify the running version, approved evidence, and authorized recovery path. See sections 6–7 and change/incident templates.

## How the pillars reinforce each other

Imagine a proposed support workflow answering an updated internal policy incorrectly. Evaluation detects the regression; traces reveal the retrieved version; data controls check snapshot publication; orchestration supplies a fallback; governance assigns correction and release decisions. A new regression case verifies the fix on future changes.

This is a hypothetical application, not an additional reported case study. It shows why a database or model alone cannot establish readiness. Begin with a project contract and enough of each pillar to test one end-to-end workflow. Expand based on observed gaps. The pillars are responsibilities, not a rigid calendar.
