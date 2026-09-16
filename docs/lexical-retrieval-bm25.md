# Lexical retrieval with BM25 for agentic search

This document distills implementation guidance from the repository's third source talk ([source notes](source-notes-bm25.md); timestamps refer to the video). Speaker statements are identified as such; the talk's transcript is auto-generated and contains recognition errors, so slide-only details remain unverified. Section 3 documents the BM25 parameters from established information-retrieval literature — the talk names the two parameters but does not define their roles in the captured audio.

## 1. Agentic search: retrieval inside the agent loop

The talk defines agentic search as search inside an agent loop: an agent working on a task (coding, deep research) develops an information need and must resolve it mid-task (1:09–2:15). Building such a system takes three components:

1. A capable model that can use tools and formulate queries.
2. A harness that exposes retrieval to the model — via tool calling or via code execution against the retrieval infrastructure.
3. A retrieval engine that searches efficiently, potentially over billion-scale document sets.

The design consequence for the framework: retrieval quality is part of the agent's control loop, not a preprocessing step. Evaluate it inside the loop, not only as a standalone ranking component.

## 2. What BM25 is

BM25 (Best Match 25 — the name comes from a series of experiments in which number 25 performed best, per the speaker at 2:15–3:21) is a lexical search algorithm used for search retrieval. It is a scoring function that determines how relevant a document is to a search query: query terms and document terms interact to produce a score, and that score serves as a proxy for relevance. Documents are ranked by score, and top-k retrieval returns the highest-scoring k. Scoring every document exhaustively is expensive at scale; decades of information-retrieval work address accelerating top-k retrieval (indexes, early termination), which is orthogonal to the scoring function itself — BM25 has not changed.

Two properties matter for agent systems. First, BM25 is lexical: it matches literal terms and phrases, so it excels at exact strings — names, entities, zip codes, SKUs, identifiers — that embedding models, which encode text into a fixed vocabulary and dense vector, can represent poorly (10:39–11:14). Second, it is explainable: because results come from literal term matches, an agent (or a human) can inspect why a query returned what it did and reformulate accordingly (11:14–11:49).

What changed, the speaker argues, is the user (3:21–3:55): LLMs carry broad parametric knowledge of entities, companies, and dates, and they issue far more queries than humans — longer queries, with search syntax operators learned from web search. Comparing GPT-5 search trajectories with human query logs (the leaked AOL logs; humans still search with a few terms), the agent workload is new, and it plays to lexical search's strengths (8:25–9:31). BM25 is also cheap relative to embedding inference, which requires model infrastructure for every indexed and queried text.

## 3. The k1 and b parameters

BM25 has two hyperparameters that shape the scoring function. The talk references both and reports that a prominent benchmark's weak BM25 baseline traced back to parameter choices unsuited to its documents (9:31–10:39). The parameter semantics below are established information-retrieval knowledge, not a transcript quote.

**k1 — term-frequency saturation.** k1 controls how quickly a document's score increases as a query term appears more often in the document. With k1 = 0, term frequency is ignored entirely: one occurrence scores the same as a hundred. As k1 rises, repeated occurrences add more score, but with diminishing returns — the contribution saturates rather than growing linearly, so a document cannot rank without bound just by repeating a term. A common default is k1 = 1.2.

**b — document-length normalization.** b controls how strongly document length penalizes the score, so that long documents do not overpower shorter documents simply because they contain more words — and therefore more chances to contain a query term by coincidence. With b = 0, length is ignored: long documents keep their raw term-frequency advantage. With b = 1, each document's term frequencies are fully normalized against the average document length. A common default is b = 0.75.

The operational lesson the talk demonstrates: these defaults are not universal. The BrowseComp-Plus benchmark's BM25 baseline used parameters the speaker describes as inadequate for its long documents, making lexical retrieval look weak against embedding-based methods; more recent research cited in the talk shows properly configured parameters change the comparison (10:06–10:39). "Which BM25 do you mean?" — implementations, parameters, and performance differ. Treat k1 and b as configuration to record in the release manifest and to tune against representative queries and the actual document-length distribution, especially when documents are long or heterogeneous in length. Reuse established defaults as a starting point, not as an unexamined given.

## 4. Why BM25 fits agentic search

The talk's evidence chain runs through BrowseComp-Plus, a deep-research benchmark: 830 riddle-like questions over roughly 100,000 web documents, where a model gets a single search tool (query string in, snippets out) and answers are checked against golden references for end-to-end accuracy (4:30–5:39). Two findings matter for design (6:11–7:52):

- Context is scarce. The speaker compares the usable context window to a floppy disk — on the order of 350,000 tokens before quality degrades (his stated opinion) versus about 1.4 MB on a floppy. Even a perfect reasoner needs retrieval to decide what enters the context window.
- Retrieval, not reasoning, is the bottleneck. When gold evidence documents are stuffed directly into the context, answer accuracy is high — the speaker reports even GPT-4-class models answer well. When the model must find evidence through the retrieval tool, accuracy falls with the harness, the model's query formulation, and retriever quality.

So improving retrieval quality and the retrieval interface directly improves end-to-end task accuracy. Within that picture, the speaker's case for BM25 as a primitive: exact-match strength on entities and identifiers, low cost and mature tooling, and explainability that lets the model debug its own queries — plus natural combination with grep-style literal search over retrieved content (16:55–17:30).

These are speaker assertions from a vendor of retrieval infrastructure; the benchmark structure is checkable in the cited paper, but treat the comparative performance claims as motivation for running your own measurements, not as settled results.

## 5. Evaluation shifts from ranked lists to task success

Classical information-retrieval evaluation assumed one human query and one ranked list: compute nDCG over the top results and compare systems. The speaker argues this no longer fits when the user is an agent that reformulates queries, issues many of them, and expands terms (14:37–15:49). The recommendation: evaluate end-to-end task success — for question answering, whether the final answer is right — rather than only per-query ranking metrics.

This aligns with the framework's evaluation pillar: per-query lexical metrics remain useful diagnostics for the retrieval component, but release decisions should rest on end-to-end evaluation cases that exercise the whole loop — query formulation, retrieval, reading, and answer — since failures can live in any of them. When comparing retrieval configurations (lexical, semantic, hybrid, different k1/b settings), hold the rest of the loop fixed and compare on the same task set.

## 6. Retrieval results as a filesystem workspace

The talk highlights a recent University of Waterloo paper, "Scaling Direct Corpus Interaction via Dynamic Workspace Expansion" (Jimmy Lin's group, per the speaker), as a design direction (12:21–14:37): place retrieved documents into a workspace organized as a filesystem — a search-engine result page for agents. Progressive disclosure shows titles and snippets first; the agent decides what to open in full, using the primitives coding agents already excel at (grep, ripgrep, sed, bash). This combines sandbox infrastructure with retrieval infrastructure and rides the same model-optimization wave: frontier models are trained heavily for coding and tool use, so framing retrieval as file navigation aligns the task with what models do well.

When adopting this pattern, apply the framework's existing controls: workspace contents are retrieved data, not instructions; permission filtering applies before documents enter the workspace and again before evidence is cited; and trace which files the agent opened so retrieval quality remains diagnosable.

## 7. Mapping to the five pillars

- Data foundations: BM25 configuration (k1, b, tokenizer, index version) is retrieval configuration — version it, record it in the release manifest, and requalify when the document corpus or its length distribution changes.
- Evaluation: compare retrieval configurations on end-to-end task success, not only ranked-list metrics; keep per-query diagnostics for locating failures.
- Observability: record the agent's query trajectory — queries issued, results returned, documents opened — so retrieval-caused failures are distinguishable from reasoning failures.
- Orchestration: retrieval inside the agent loop is a dependency call; apply the circuit-breaker and degradation policies from [multi-agent-orchestration.md](multi-agent-orchestration.md) to the retrieval backend.
- Governance: name an owner for the retrieval index, its refresh policy, and its parameter decisions.
