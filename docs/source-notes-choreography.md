# Source and interpretation — multi-agent orchestration talk

Source: [From Chaos to Choreography: Multi-Agent Orchestration Patterns That Actually Work](https://ai.engineer/talks/2czYyrTzILg-from-chaos-to-choreography-multi-agent-orchestration-patterns-that-actually-work-sandipan-bhaumi), Sandipan Bhaumik, AI Engineer Europe 2026. Video: https://www.youtube.com/watch?v=2czYyrTzILg.

This is the repository's second source talk; it complements the playbook talk in [source-notes.md](source-notes.md). Where the playbook talk motivates the five pillars, this talk supplies concrete distributed-systems patterns for the orchestration pillar. The distilled implementation guidance lives in [multi-agent-orchestration.md](multi-agent-orchestration.md).

## Source synopsis

The talk argues that scaling from one agent to many is a distributed systems problem, not a model quality problem. A financial-services war story illustrates the failure mode: five credit-decisioning agents shared a cache without coordinated invalidation, so the risk agent read a stale credit score (680 instead of 750) and 20% of decisions carried incorrect risk ratings until a two-day diagnosis found the cause between the agents and the database.

The speaker then presents five mechanisms: a choreography-versus-orchestration decision framework based on workflow complexity and autonomy requirements; immutable state snapshots with versioned handoffs instead of shared mutable records; data contracts validated at each handoff boundary; circuit breakers around every agent call; and Saga compensation (execute/compensate pairs) for undoing partial work. A reference architecture places a workflow engine, an append-only state store, and telemetry inside the orchestrator's responsibility, followed by a Databricks-specific mapping (LangGraph, Unity Catalog, Model Serving/AI Gateway, Delta Lake, MLflow, Agent Bricks).

## Navigation

| Approximate time | Topic |
|---|---|
| 0:00–1:31 | Speaker background and agenda |
| 1:31–2:34 | From one agent to five: coordination becomes the problem |
| 2:34–4:34 | War story: stale cache produces wrong credit decisions |
| 4:34–5:48 | Why coordination complexity grows with agent count |
| 5:48–8:16 | Choreography: event-driven coordination and its debugging burden |
| 8:16–10:12 | Orchestration: central coordinator owns graph, state, retries |
| 10:12–11:28 | Decision matrix; hybrid of choreography with Saga compensation |
| 11:28–14:07 | Shared mutable state, lost updates, immutable versioned snapshots |
| 14:07–15:23 | Handoff code walkthrough and version-history debugging |
| 15:23–16:24 | Data contracts at the handoff boundary |
| 16:24–18:58 | Circuit breaker pattern and graceful degradation |
| 18:58–20:56 | Saga compensation pattern |
| 20:56–22:03 | Combined production architecture |
| 22:03–24:58 | Databricks platform mapping and execution walkthrough |
| 24:58–end | Closing thoughts |

## Review limitations

See the [validation report](../sources/2czYyrTzILg/validation.md) for the independent transcript comparison, evidence locations, corrections, and remaining gaps. This is an AI-assisted repository review, not speaker approval or independent verification of the reported production incidents.

The talk page embeds a 115-segment machine-readable transcript with start and end timestamps. Its upstream review status is `needs_review`, and every segment carries that status. All available segment text was reviewed on 2026-09-16. Audio alignment, slide-only details (including the exact code shown on slides), and QR-linked resources remain unverified. Transcript availability is not the same as complete audiovisual coverage.

The page also includes an editorial article. Its corrections and resource recommendations are not speaker statements and must not be attributed to the speaker. Where the editorial review identifies weaknesses in speaker claims — quadratic rather than exponential connection growth, an unverified transaction-scale claim, Delta Lake mutability, shallow dataclass freezing — the distilled guidance in multi-agent-orchestration.md carries those caveats explicitly.

The operational documents in this repository are an original implementation proposal organized around the talk's themes, not a substitute transcript or a recreation of the speaker's slides or downloads. Numeric values from the talk (five consecutive failures, sixty-second cooldown, 0.7 confidence threshold) are the speaker's examples, not framework defaults.
