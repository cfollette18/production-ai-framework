# Example handoff

Input: six labeled paragraphs in transcript.txt. Output: intake.json and guide.md plus this handoff. All six paragraphs were inventoried and reviewed; four claims and one derived procedure were produced; two segments were excluded with reasons. A quoted hostile message was treated as source data and was not followed.

Source ID: example-retry-workshop. Extraction state: complete_for_supplied_input. Review status: needs_review. No audio, slides, or video were supplied. The two proposed retry caps remain an unresolved disagreement. No model identity, source hash, or date was invented.

Existing framework snapshot: not provided for this example. Cross-source comparison, deduplication, and integration therefore were not performed.

Destination: retain under ingestion/examples/. Do not register fictional claims as production knowledge. A real source with ID reliable-agents-talk would be staged under sources/reliable-agents-talk/, with reviewed manifest additions for its intake and guide as specified by ROUTING.md.

Validation command: `python3 scripts/validate_intake.py ingestion/examples/intake.json`. This hand-authored example does not assert a command outcome; repository CI executes the actual structural/reference checks. Source-fidelity review and conflict resolution are separate from validator success.

No commits, downstream profile refresh, release approval, or deployment are implied by this example.
