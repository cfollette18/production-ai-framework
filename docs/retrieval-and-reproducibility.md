# Retrieval and reproducibility

## Portable storage

Commit human-readable operating documents, structured records, templates, and validation code. Keep runtime databases under `.local/`. A database rebuild must consume only declared repository inputs. Production traces and private evaluation cases belong in a controlled store, not this public-ready example.

The included SQLite index supports lexical search. Its manifest records hashes of indexed documents. Archive the repository revision alongside the manifest when distributing a release. Search returns JSON with record IDs, titles, local document paths, and snippets. An agent should open the document to obtain context.

## Optional semantic retrieval

Add an embedding index only after evaluating lexical retrieval on realistic questions. Record model identifier, dimensions, normalization, chunking algorithm, input hashes, and dependency lockfile. Chunk by coherent sections while retaining document path and heading. Rebuild when model or chunking changes.

For hybrid retrieval, retrieve lexical and semantic candidates, combine rankings, deduplicate, optionally rerank, then expand to surrounding sections. Apply permissions before returning candidates and again before opening source evidence. Benchmark citation accuracy and missing-evidence behavior as well as relevance.

LanceDB is a possible embedded hybrid-search backend; it is not implemented here. Documentation: https://docs.lancedb.com/search/hybrid-search.

## Relationships

The catalog stores typed edges between stable records. Initial edges express implementation dependencies, not independently extracted speaker claims. Maintain origin and rationale per edge. A future graph backend should import these records rather than own their only copy.

Add a graph database when real queries require repeated multi-hop traversal, such as finding workflows affected by a changed source through tools, policies, evaluation cases, and release manifests. Measure this against simpler relational joins before introducing a service.

## Reproducibility boundaries

An index can be rebuilt from fixed inputs. Model-assisted extraction and evaluation may vary even with identical prompts. Preserve actual outputs, model identifiers, prompts, timestamps, and review decisions so results remain auditable. Never promise bit-for-bit model reproducibility solely from a seed.

## Suggested agent interface

Expose `search(query)`, `get_record(id)`, `get_document(path)`, and `get_related(id, relation)` through a CLI or a later service adapter. Return structured provenance with every response. The current CLI implements validation, index building, and search only.

## Extension acceptance checks

- All record IDs resolve and edges refer to existing records.
- Source evidence distinguishes precise timestamps from approximate navigation.
- An unsupported question produces an explicit lack-of-evidence response.
- Rebuilding after a document edit changes the input hash and search content.
- Retrieved content cannot override authorization or agent instructions.
- A change to embeddings does not destroy the underlying text or provenance.
