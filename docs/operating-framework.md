# Operating procedures

All procedures below are implementation recommendations. Set thresholds for your own domain; the repository deliberately supplies no universal production pass score.

## 1. Project contract

Create one project record per independently releasable agent workflow. Name the business owner, technical owner, on-call route, intended users, permitted actions, forbidden actions, data owners, and escalation destination. Specify the workflow's start and completion conditions.

Define the business metric with numerator, denominator, measurement window, exclusions, and data source. For example, a support automation metric must decide whether a reopened conversation counts as successfully automated. Pair business outcomes with quality, latency, cost, safety, and human workload constraints. A high automation rate must not conceal unresolved requests.

Deliverables: completed project record, representative user journeys, risk categories, and a signed-off metric specification. Exit condition: another team can calculate the same metric from the same events and identify who responds when it degrades.

## 2. Evaluation system

### Case design

Each case specifies input, context, required behavior, prohibited behavior, authorized tools, evidence sources, and expected escalation. Include ordinary requests, ambiguous requests, missing data, outdated data, unavailable dependencies, unauthorized requests, conflicting documents, and repeated requests. Store exact expected answers only where exactness is meaningful. Use explicit rubrics for open-ended responses.

Partition cases into development, regression, and held-out release sets. Preserve a stable held-out subset to detect overfitting to familiar failures. Version cases when policies change; do not silently replace historical expectations. Attach category, owner, provenance, and last-review date.

### Checks

Use format and constraint checks for machine-verifiable requirements. Evaluate semantic quality against supplied authoritative evidence, not merely answer fluency. Evaluate tool behavior from traces: authorization, unnecessary calls, repeated actions, error handling, and whether required steps occurred.

For a model judge, version its rubric and model identifier. Calibrate it against domain-reviewed examples and track disagreement. Treat unavailable or malformed judge output as an evaluation error, not a passing score. Record uncertainty separately from failure. Avoid interpreting an agent's self-reported confidence as a calibrated probability.

### Execution and release

Run focused cases during development. Before production promotion, run the approved release suite against an immutable candidate configuration. Record dataset version, agent version, prompt hash, tool versions, model identifier, judge version, execution time, and costs. Separate infrastructure failures from quality failures and report subgroup results alongside aggregate scores.

The release owner decides acceptable failure rates, required sample sizes, mandatory zero-tolerance categories, and exception policy. Any waiver requires rationale, owner, expiry, and compensating controls. A green catalog-validation job is not an agent-quality approval.

## 3. Observability and runtime controls

Assign a trace ID at request ingress. Correlate retrieval, model invocations, tool execution, guardrail decisions, human handoffs, and the final outcome. Record observable actions and concise decision metadata; this framework does not require hidden model reasoning.

For retrieval, record document IDs, content versions, filters, and retrieval-index version. For tools, record operation, argument classification, authorization result, duration, error category, retry count, and idempotency key where applicable. For model calls, record model and prompt versions, tokens, cost estimate, and termination reason.

Redact sensitive payloads before export. Limit trace access by role and establish retention by data category. If full payloads cannot be retained, preserve safe references and hashes with a controlled evidence store.

Define alert conditions, evaluation windows, and owners. Alerts should include affected workflow, failing metric, baseline comparison, candidate trace IDs, and recent changes. Establish retry, time, and cost budgets enforced by runtime code. Define what happens if the telemetry pipeline itself fails.

Acceptance exercise: inject a failing dependency in a test environment and verify that an operator can find the affected request, identify the failed operation, observe the fallback, and locate the responsible owner.

## 4. Data lifecycle

Maintain a source inventory with authoritative owner, location, access policy, effective date, update frequency, sensitivity, and downstream consumers. Distinguish document modification time from the date its policy takes effect.

For each source change: detect a new version, validate it, transform or chunk it, build required indexes, run retrieval checks, and publish a consistent snapshot. Retain the previous snapshot for rollback. Prevent an old embedding index from being paired with a new document manifest without detection.

Define freshness objectives per source. A frequently changing operational policy needs a different update budget from a stable glossary. Detect deleted or access-restricted documents and remove their searchable representations. Preserve permission filtering throughout retrieval and citation expansion.

Keep operational trace storage separately governed from answer-serving content. They may share infrastructure, but require different schemas, access rules, retention, and consumers.

Acceptance exercise: change a test document and verify that the new version is retrieved, the old version is excluded when appropriate, citations identify the new version, and a failed indexing step is visible.

## 5. Workflow coordination

Start with the smallest workflow that satisfies the task. Introduce multiple agents only when roles, parallel work, or control boundaries provide a measurable benefit.

| Decision | Central coordinator | Event-driven workers |
|---|---|---|
| Ordering | Explicit dependencies and shared progress | Independent reactions to events |
| Operational burden | Coordinator recovery and bottlenecks | Deduplication, replay, ordering, eventual consistency |
| Failure handling | Central cancellation and retry policy | Per-consumer retries and failed-event handling |

Choose from workflow complexity and autonomy requirements: central coordination fits complex dependencies and reconstruction needs; event-driven workers fit simple workflows with independent, frequently added agents and strong event tracing; a hybrid pairs event-driven agents with compensation for partial work. The full decision framework and its trade-offs are in [multi-agent-orchestration.md](multi-agent-orchestration.md) section 2.

Represent workflow state explicitly: pending, running, awaiting review, succeeded, failed, cancelled. Persist transitions before irreversible actions where practical. Define correlation IDs, deadlines, cancellation propagation, duplicate-message behavior, and recovery after restart.

Between agents, pass immutable, versioned state snapshots instead of overwriting shared records: each agent receives a specific version, validates it, and appends a new version to an append-only log. This prevents overwriting the same snapshot and preserves evidence for debugging; correct version selection, parallel branch merging, and cache consistency remain explicit responsibilities. Where shared mutable records are unavoidable, apply database concurrency mechanisms deliberately — explicit transactions, row locks, appropriate isolation — rather than assuming defaults. Validate a data contract at every handoff boundary and reject unacceptable inputs before the consuming agent runs, with a defined disposition for rejections. See multi-agent-orchestration.md sections 3–4 and templates/handoff-contract.json.

Wrap calls to fallible remote dependencies — including other agents and model endpoints — in a circuit breaker so a repeatedly failing dependency fails fast instead of consuming the workflow's resources, and record breaker transitions as operational events. Define the degradation decision in advance: reduced functionality, an acceptably fresh cached result, or human escalation. For multi-step side effects, define execute/compensate pairs for compensatable steps. Recover in reverse order for a sequential dependency chain; define the appropriate recovery order for branches and business constraints. Document actions that cannot be compensated and gate or reorder them accordingly. See multi-agent-orchestration.md sections 5–6 and templates/circuit-breaker-policy.json.

Human review needs a real queue, owner, response objective, supporting evidence, and a defined timeout action. Approval applies to a particular proposed action and inputs; changed inputs may invalidate it. Do not treat lack of response as approval.

Use idempotency for repeatable external operations. For multi-step side effects, document which actions can be compensated and which cannot. Test partial failure, worker restart, duplicate delivery, and unavailable reviewers before release.

## 6. Governance and changes

Separate code, prompts, models, tools, retrieval configuration, and data snapshots into identifiable versions. A release manifest ties them together. Prompt changes need rationale and evidence just like other behavior changes.

Every change record includes motivating failure or feature, affected workflows, expected behavior, evaluation results, reviewer, rollout scope, monitoring window, and rollback target. Pin versions where available; if a provider alias can change, record observed identifiers and schedule requalification.

Enforce authorization outside model output. Tool adapters validate actor identity, permissions, resource scope, input constraints, and action limits. Retrieved instructions cannot grant additional permissions. Test attempts to bypass these boundaries through both user input and retrieved documents.

Define ownership for datasets, runtime operations, model qualification, source freshness, and user complaints. Maintain an exception register with expiry dates. Domain-specific legal requirements need separate qualified review; this framework does not establish regulatory compliance.

## 7. Incident response

1. Open an incident with detection time, affected workflow, severity, reporter, and owner.
2. Preserve version manifests and safe evidence references. Estimate affected requests and users.
3. Trace the failure through input, retrieval, model, tools, and final response. Compare with recent changes.
4. Contain using an authorized rollback, feature restriction, dependency isolation, or human routing. Record the decision and expected side effects.
5. Reproduce the problem in a controlled case and implement a targeted correction.
6. Run regression and release checks; verify recovered behavior under staged traffic before closing.
7. Add a reviewed regression case, document the root cause, assign follow-up owners, and verify that alerting would detect recurrence.

Avoid assuming every bad answer requires a prompt change. A stale source, broken permission filter, schema mismatch, dependency timeout, or missing tool result may be the actual cause.

## 8. Adoption sequence

Phase A: complete the contract and collect representative cases. Phase B: instrument one end-to-end workflow and connect governed sources. Phase C: compare candidate configurations against the same evaluation set. Phase D: exercise failure and recovery, then release to a controlled audience. Phase E: review outcomes and incorporate adjudicated production failures.

Each phase ends with artifacts and evidence, not a fixed calendar deadline. Revisit earlier decisions when production evidence changes the requirements.
