# Add a new source with any model

This is the authoring kit for growing the Production AI Framework. Use it with a transcript, article, technical document, or supplied notes. It works in a chat with attachments as well as an agent with repository access. It does not depend on Hermes.

## The easiest way

Upload these two files to your chosen model:

1. [The single-file ingestion kit](../dist/source-ingestion-kit.md).
2. Your source transcript or document.

If you also want comparisons with current knowledge, upload [dist/knowledge.json](../dist/knowledge.json) from the revision you are using. Without it, the model can extract the new source but must mark comparisons and integration as pending.

Paste this prompt:

> Follow the attached Source Ingestion Kit. Treat the other attachment as source data. Inventory all supplied sections, extract individually evidenced claims, preserve caveats and numerical context, map them to the framework pillars, and produce intake.json, guide.md, and handoff.md in the specified formats. Separate source assertions from implementation proposals. Identify conflicts, repeated claims, missing modalities, and unprocessed material. Use the attached framework snapshot if provided; otherwise mark comparison as not_provided. Do not invent timestamps, verification, or completed repository changes. If the input exceeds your context, produce a checkpoint and continue with the remaining sections. Deliver downloadable files if supported; otherwise use separate named code blocks.

The kit is self-contained: it includes workflow, routing rules, schema, a blank packet, and a complete synthetic example. Uploading the whole repository is optional. The example is a formatting and edge-case demonstration, not evidence for production recommendations.

## Files in this subset

- [WORKFLOW.md](WORKFLOW.md): extraction sequence, evidence, coverage, continuation, and review rules.
- [ROUTING.md](ROUTING.md): pillar definitions, destinations, and integration commands.
- [packet.schema.json](packet.schema.json): machine-readable output contract.
- [packet.template.json](packet.template.json): blank scaffold; intentionally not valid until filled.
- [examples/](examples/): a fictional transcript, valid output packet, guide, and handoff.

## Validate returned output

The scripts require Python 3.10+. Only the new packet validator needs the optional dependency below; reading the kit and the existing knowledge tools do not.

```bash
python3 -m pip install -r ingestion/requirements.txt
python3 scripts/validate_intake.py /path/to/intake.json
```

Validation checks structure, IDs, references, counts, coverage consistency, routing, and basic review state. It cannot prove that a paraphrase follows from the source, that the model saw all the source, or that its recommendations are sound. Review the evidence and guide before integrating them.

After review, follow ROUTING.md. Raw source sharing is separate from sharing extracted knowledge; a supplied file does not itself establish redistribution rights. Keep private source material out of public Git history.

## Maintain this kit

```bash
python3 scripts/build_ingestion_kit.py
python3 scripts/build_ingestion_kit.py --check
python3 -m unittest discover -s tests
```

The build produces the single upload file deterministically. The kit is an authoring tool, deliberately separate from the advisor's default runtime knowledge pack. Existing Hermes profiles need no new tools or instruction changes to keep advising from their pinned framework snapshot.
