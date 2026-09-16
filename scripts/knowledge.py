"""Portable knowledge catalog. Uses Python's standard library only."""
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / '.local'


def read(path):
    return json.loads((ROOT / path).read_text())


def validate():
    records = read('knowledge/records.json')
    ids = set()
    for row in records:
        for key in ('id', 'title', 'kind', 'origin', 'document', 'source_id'):
            if not isinstance(row.get(key), str) or not row[key]:
                raise ValueError(f'Missing or invalid {key}: {row}')
        if row['id'] in ids:
            raise ValueError('Duplicate ID: ' + row['id'])
        ids.add(row['id'])
        document = (ROOT / row['document']).resolve()
        if not document.is_relative_to(ROOT) or not document.is_file():
            raise ValueError('Invalid document: ' + row['document'])
        if row['source_id'] != read('sources/manifest.json')['id']:
            raise ValueError('Unknown source')
    for edge in read('knowledge/relationships.json'):
        if edge.get('from') not in ids or edge.get('to') not in ids:
            raise ValueError('Dangling relationship')
        if edge.get('relation') not in ('uses', 'depends_on', 'constrained_by'):
            raise ValueError('Unknown relation')
        if not edge.get('origin') or not edge.get('rationale'):
            raise ValueError('Relationship requires origin and rationale')
    for path in (ROOT / 'templates').glob('*.json'):
        obj = json.loads(path.read_text())
        if obj.get('schema_version') != 1:
            raise ValueError('Unsupported template version')
    return records


def build():
    records = validate()
    LOCAL.mkdir(exist_ok=True)
    temporary = LOCAL / 'knowledge.tmp.sqlite'
    temporary.unlink(missing_ok=True)
    hashes = {}
    try:
        with sqlite3.connect(temporary) as db:
            db.execute('CREATE VIRTUAL TABLE docs USING fts5(id UNINDEXED, title, path UNINDEXED, body)')
            for path in sorted((ROOT / 'docs').glob('*.md')):
                relative = str(path.relative_to(ROOT))
                content = path.read_text()
                hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
                matching = [r['id'] for r in records if r['document'] == relative]
                db.execute('INSERT INTO docs VALUES (?,?,?,?)',
                           (','.join(matching) or path.stem, content.splitlines()[0].lstrip('# '), relative, content))
        temporary.replace(LOCAL / 'knowledge.sqlite')
        (LOCAL / 'manifest.json').write_text(json.dumps({'schema_version': 1, 'inputs': hashes}, indent=2) + '\n')
    finally:
        temporary.unlink(missing_ok=True)
    print(json.dumps({'indexed_documents': len(hashes)}))


def search(query):
    target = LOCAL / 'knowledge.sqlite'
    if not target.exists():
        raise ValueError('Run build before search')
    if not query.strip():
        raise ValueError('Search query cannot be empty')
    # Quote user text as a phrase so FTS operators are not interpreted.
    phrase = '"' + query.replace('"', '""') + '"'
    with sqlite3.connect(f'file:{target}?mode=ro', uri=True) as db:
        rows = db.execute("SELECT id,title,path,snippet(docs,3,'[',']','...',28) FROM docs WHERE docs MATCH ? ORDER BY rank LIMIT 10", (phrase,)).fetchall()
    print(json.dumps([dict(zip(('id', 'title', 'path', 'snippet'), row)) for row in rows], indent=2))


if __name__ == '__main__':
    try:
        command = sys.argv[1] if len(sys.argv) > 1 else ''
        if command == 'validate':
            print(json.dumps({'valid_records': len(validate()), 'scope': 'catalog structure; not project readiness'}))
        elif command == 'build':
            build()
        elif command == 'search' and len(sys.argv) > 2:
            search(' '.join(sys.argv[2:]))
        else:
            raise ValueError('Usage: knowledge.py validate | build | search QUERY')
    except (ValueError, KeyError, OSError, sqlite3.Error) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
