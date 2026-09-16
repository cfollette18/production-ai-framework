# Multi-agent orchestration patterns

This document distills implementation guidance from the repository's second source talk ([source notes](source-notes-choreography.md), timestamps below refer to that video). Everything here is implementation recommendation, not a transcript substitute. Speaker statements are identified as such; numeric values from the talk (five failures, sixty seconds, 0.7 confidence) are the speaker's examples, and each project must set its own thresholds through an explicit decision.

## 1. Why added agents become a distributed system

The speaker describes a successful single-agent demo before introducing coordination failures. That example does not establish that model quality alone makes a single-agent production system reliable; all five pillars still apply. Adding agents introduces dependencies: A produces data B needs, C waits on both, D mutates state B is reading, and E can crash mid-workflow. These failure modes can require coordination and consistency fixes beyond prompt or model changes (1:31–2:34).

The talk's war story (2:34–4:34): a credit-decisioning deployment ran one credit-score agent for two weeks without issues, then added income verification, risk assessment, fraud detection, and final approval. Within three days, the speaker reports, 20% of decisions had incorrect risk ratings, and diagnosis took two days. The credit-score agent wrote 750 to PostgreSQL; 500 milliseconds later the risk agent read 680 for the same customer from a shared cache. The database write had succeeded — cache invalidation had not. The defect sat between the agents and the database: several agents shared a cache with no coordinated invalidation. Fixing the prompt could not repair that read path.

Treat this as the canonical failure lesson: when agents misbehave, examine the coordination and consistency architecture before assuming a model or prompt defect.

On growth: the count of potential undirected connections among n agents is n(n−1)/2 — zero for one agent, one for two, ten for five. That is quadratic growth. The speaker describes the increase as exponential and invokes a 25-fold complexity figure; the connection math supports quadratic growth, and no measured multiplier was supplied. Either way, each connection is another place for races, failures, and state synchronization problems (4:34–5:48).

## 2. Choosing choreography or orchestration

The first design decision is who owns coordination (5:48–10:12).

**Choreography** coordinates through events. A research agent publishes a research-completed event to a message bus; an analysis agent subscribes, processes, and publishes analysis-ready; a report agent consumes that. No central component calls participants in sequence. Loose coupling makes adding a subscriber cheap, but the difficulty moves into operations: when a report never appears, did research fail to publish, did analysis fail to consume, or was an event consumed twice? Choreography requires end-to-end event tracing and deliberate delivery guarantees. Choose it for naturally event-driven workflows with independent agents and frequent additions — only when the team can reconstruct event propagation. Choosing it because autonomy "feels more agentic" leaves that operational work undone.

**Orchestration** puts coordination in a central component. It calls A and waits, starts B and C in parallel, waits for both, then calls D with the combined outputs. Agents never call each other; they accept inputs, do work, and return results. The orchestrator owns the execution graph, state, retries, and step logs. Any workflow engine with dependency graphs (DAGs) and retry mechanisms can fill the role. Central control fits complex dependencies, work that needs compensation, and operators who need one view of execution — especially when the graph changes less often than agent internals. The speaker reports using orchestration almost exclusively in financial-services work because a failed credit decision must be reconstructed: which agent acted, in which order, with which data.

Decision framework from the talk (10:12–11:28), using workflow complexity and required autonomy:

| Workflow | Autonomy requirement | Suggested pattern |
|---|---|---|
| Simple | High | Choreography |
| Complex | Low | Orchestration |
| Complex | High | Choreography with Saga compensation (section 6) |

The hybrid keeps independent event-driven agents while adding a way to compensate partially completed work. Choosing a pattern establishes who coordinates; it does not yet establish how agents safely exchange state.

## 3. Immutable state snapshots and versioned handoffs

Two consistency failures motivate this pattern (11:28–14:07). First, the stale read from the war story. Second, the lost update: A and B both read a credit score of 680; A writes 750; B writes 720; under last-write-wins, A's update disappears. Database protections help only when the application actually uses them — explicit transactions, row locks, serializable isolation, SELECT FOR UPDATE are mechanisms to choose and apply, not properties of default settings. Teams that assume defaults ship race conditions.

The working alternative is immutable state snapshots with versioned handoffs:

1. Agent A produces state version 1 and seals it. The orchestrator stores it as a new row in an append-only log — inserts, never updates.
2. Agent B receives that specific version, validates its schema, processes it, and inserts version 2 as a new row rather than updating version 1.
3. Agent C receives version 2. If C fails, the workflow returns to that known input instead of reconstructing a record other agents overwrote.

In the talk's Python illustration, an `AgentState` dataclass carries a version, a payload, and a creator; `frozen=True` blocks attribute reassignment, and the handoff validates the contract, creates the next version, and invokes the next agent with immutable input. Two caveats: `frozen=True` is shallow — it does not recursively freeze a dict or list inside the object, so nested payloads need their own immutability; and persistence of versions belongs to the orchestrator, not the agents.

Snapshots serve as inputs and audit records, never as shared mutable working memory. This eliminates concurrent modification of the same snapshot and removes ambiguous "read the latest value" lookups. It does not, by itself, guarantee that the correct version was selected or that other data sources (such as caches) are consistent — those remain workflow responsibilities.

Version history also narrows debugging: if version 7 contains a bad result, inspect the version-6 input, then earlier versions, to locate where state first diverged. The speaker suggests binary search through history, which helps when a reproducible check can distinguish a good prefix from the bad states after it. The underlying benefit is retained evidence at every handoff (15:01–15:23).

## 4. Data contracts at handoff boundaries

Immutability preserves an input; a data contract decides whether the next agent should accept it (15:23–16:24). Each producer promises an output shape — in the talk's example, findings, a confidence score, sources, and a timestamp — and each consumer declares input requirements and validates them before doing work. The example rejects research with confidence below 0.7. That number is the speaker's example acceptance rule, not evidence that any confidence score is calibrated; each project sets thresholds from domain decisions.

Enforce the contract at the boundary, before the consuming agent runs. A rejected handoff is far easier to diagnose than a bad report three agents downstream. A rejected handoff needs a defined disposition: retry with correction, route to a human, or fail the workflow — silence is not an option.

For larger organizations, the talk suggests registering input/output schemas in a central catalog (the speaker names Unity Catalog) so contracts are versioned and governed in one place. Registration aids discovery and governance; the receiving agent must still enforce the contract at execution time. Use [templates/handoff-contract.json](../templates/handoff-contract.json) to record each contract.

## 5. Circuit breakers around agent calls

Even with explicit coordination and valid inputs, dependencies fail: LLMs time out, APIs rate-limit, agents crash (16:24–18:58). A circuit breaker stops a repeatedly failing dependency from consuming workflow resources on every subsequent call. In the talk's example, five consecutive failures open the circuit; new calls then fail immediately instead of waiting for another timeout.

Recovery is a state machine, not an unlimited retry loop:

| State | Call behavior | Transition |
|---|---|---|
| Closed | Call the dependency normally | Success resets the failure count; reaching the threshold opens the circuit |
| Open | Reject calls immediately (fail fast) | Cooldown expiry permits a probe |
| Half-open | Allow one test request | Success closes; failure reopens and resets the cooldown |

The example waits 60 seconds before permitting the half-open probe. This gives the dependency room to recover instead of being bombarded.

An open circuit still leaves a business decision, which must be designed in advance:

- Reduced functionality: skip an optional agent and continue with a smaller result.
- Cached results: use a previous result where its age and meaning are acceptable.
- Human intervention: alert an operator when continuing automatically would be unsafe.

Wrap every agent call in a breaker, record open/close transitions as operational events (so an investigator can see when a dependency began flaking, alongside the calls that caused it), and enforce the policy at the serving boundary where possible. Note the gap the talk's editorial review flags: vendor gateway configuration for rate limits and per-request fallbacks does not by itself implement the failure counter, cooldown, and half-open probe — that state machine needs an explicit implementation. Use [templates/circuit-breaker-policy.json](../templates/circuit-breaker-policy.json) to record each policy.

## 6. Saga compensation for partial failure

A circuit breaker contains repeated calls; it does not remove side effects from work already completed. For that, the workflow needs Saga compensation (18:58–20:56). Each participating agent exposes two methods: `execute` does the work, `compensate` undoes it. The orchestrator records which steps succeeded; on failure it walks the successful-step list backward:

1. Execute A; record A as completed.
2. Execute B; record B as completed.
3. Execute C; if C fails, enter recovery.
4. Compensate B, then compensate A.

In the talk's example, analysis deletes its draft recommendation and research clears its cached findings, returning to the initial state. That clean reversal works because those side effects are reversible. In general, compensation is application-specific, not a database rollback spanning arbitrary services: an external action may be irreversible, concurrent changes may need to survive, and compensation itself can fail. Every compensatable workflow therefore needs defined recovery actions per step, and irreversible steps need an explicit decision — human approval gates, reordering so irreversible actions come last, or accepted risk with an owner.

The compensate methods must encode the actual undo operations, not merely mark a step failed. Reverse order describes the talk's sequential example; a branching workflow needs a recovery order that respects its dependencies and business constraints. Compensation may itself need retries, durable progress, and human escalation. These qualifications are implementation guidance, supported by the [compensating transaction reference](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction). The speaker emphasizes planning for partial completion in financial-services workflows.

## 7. Reference architecture and vendor mapping

The combined architecture (20:56–22:03) places three things inside the orchestrator's responsibility: a workflow engine, a state store holding versions 0 through N, and an observability layer recording execution. A returns version 1; the orchestrator gives that same snapshot to B and C in parallel and stores their results as versions 2 and 3 — sibling versions sharing a parent input, not a claim that C consumed B's output — then calls D with the combined results. All coordination passes through the orchestrator, giving operators one place to inspect execution and initiate recovery. The speaker says this architecture runs around the clock across billions of transactions; no workload, measurement period, or reliability metric was supplied for that scale claim, so treat it as an unverified assertion. The durable design point is the ownership boundary: agents perform work; the orchestrator decides when they run, what state they receive, and what happens after failure.

The talk then maps the architecture onto Databricks (22:03–24:58). This is a vendor-specific illustration, not a requirement; verify each capability against current vendor documentation before relying on it:

- Orchestration: LangGraph wired into Mosaic AI Agent Framework manages the graph and call order.
- Agent implementation: Unity Catalog functions (SQL or Python) or registered models, centrally discoverable, governed, and versioned.
- Serving boundary: Model Serving or Function Serving, with retries, timeouts, rate limits, and call protection via AI Gateway configuration — plus an explicitly implemented breaker state machine where needed.
- State and data: Delta Lake holds workflow state history; each agent result becomes a new state row. Append-only state is an application policy — Delta Lake supports updates, deletes, and merges, so the application and its access controls must preserve immutability.
- Observability and governance: the speaker describes MLflow traces and evaluation, Unity Catalog governance, and Agent Bricks packaging. The transcript does not specify an instrumentation command. The website's editorial `mlflow.langchain.autolog()` example is supplementary guidance, not a speaker quotation or a verified deployment recipe; linking state versions and breaker events still requires application instrumentation.

Walkthrough of one execution path: the orchestrator calls A and writes version 1 to the state table; calls B with version 1 and appends version 2; serving-layer protection guards each call while telemetry records it; if C fails, the workflow invokes compensate on previously successful steps in reverse order. Note that checkpoint recovery in a workflow engine does not automatically undo external side effects — the compensation path is application logic.

## 8. Mapping the patterns to the five pillars

The patterns land primarily in the Orchestration pillar but connect across the framework:

- Coordination choice (choreography/orchestration/hybrid): Orchestration. Choreography additionally makes heavy Observability demands — without end-to-end event tracing it is not debuggable.
- Immutable versioned state: Orchestration and Data foundations. The append-only history is a data lifecycle policy with retention, access, and storage owners.
- Handoff contracts: Orchestration and Evaluation. Acceptance thresholds are domain decisions, and contract rejections belong in evaluation evidence.
- Circuit breakers: Orchestration and Observability. Transitions must be logged operational events, and degradation strategies are business decisions recorded in advance.
- Saga compensation: Orchestration and Governance. Compensation for irreversible actions needs authorized owners and explicit risk acceptance.

Applying these patterns is ordinary infrastructure engineering. Its value shows up as the absence of late-night incidents: a system that keeps behaving predictably when its agents do not (25:07–26:20).
