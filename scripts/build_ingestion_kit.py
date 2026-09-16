"""Build a deterministic, self-contained authoring attachment for any model."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    'ingestion/WORKFLOW.md', 'ingestion/ROUTING.md',
    'ingestion/packet.schema.json', 'ingestion/packet.template.json',
    'ingestion/examples/transcript.txt', 'ingestion/examples/intake.json',
    'ingestion/examples/guide.md', 'ingestion/examples/handoff.md',
]


def render(root=ROOT):
    text = '# Source Ingestion Kit — Production AI Framework\n\n'
    text += 'Upload this file and a new source to any text-capable model. Optionally supply the current framework knowledge.json for comparisons.\n\n'
    text += 'Task: follow WORKFLOW.md and ROUTING.md below; return intake.json, guide.md, and handoff.md. The kit is instructions and examples, not the new source. The fictional example must never become production knowledge.\n\n'
    text += 'No repository access is required for extraction. File writes, integration, or publication must be authorized separately by the task. Missing tools are not grounds to invent checks or claim completed writes.\n'
    for name in FILES:
        body = (root / name).read_text(encoding='utf-8')
        text += '\n---\n\n## Included file: ' + name + '\n\n'
        if name.endswith(('.json', '.txt')):
            text += ('```json\n' if name.endswith('.json') else '```text\n') + body.rstrip() + '\n```\n'
        else:
            text += body.rstrip() + '\n'
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    destination = ROOT / 'dist/source-ingestion-kit.md'
    content = render()
    if args.check:
        if not destination.exists() or destination.read_text(encoding='utf-8') != content:
            raise ValueError('Ingestion kit is stale; run python3 scripts/build_ingestion_kit.py')
    else:
        destination.parent.mkdir(exist_ok=True)
        destination.write_text(content, encoding='utf-8')
    print(('Checked ' if args.check else 'Built ') + str(destination.relative_to(ROOT)))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
