import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('knowledge', SOURCE / 'scripts/knowledge.py')
knowledge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(knowledge)


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for folder in ('knowledge', 'docs', 'sources', 'templates'):
            shutil.copytree(SOURCE / folder, self.root / folder)
        shutil.copy2(SOURCE / 'START_HERE.md', self.root / 'START_HERE.md')
        knowledge.ROOT = self.root

    def tearDown(self):
        knowledge.ROOT = SOURCE
        self.tmp.cleanup()

    def test_export_is_repeatable_and_has_full_section(self):
        first = knowledge.bundle()
        self.assertEqual(first, knowledge.bundle())
        evaluation = next(r for r in first['records'] if r['id'] == 'evaluation')
        self.assertIn('### Execution and release', evaluation['text'])
        self.assertNotIn('## 3. Observability', evaluation['text'])

    def test_content_change_changes_hash_and_stale_check_fails(self):
        with contextlib.redirect_stdout(io.StringIO()):
            knowledge.export()
            before = knowledge.bundle()['content_sha256']
            path = self.root / 'START_HERE.md'
            path.write_text(path.read_text() + '\nA new instruction.\n')
            self.assertNotEqual(before, knowledge.bundle()['content_sha256'])
            with self.assertRaises(ValueError):
                knowledge.export(check=True)

    def test_unknown_heading_fails(self):
        path = self.root / 'knowledge/manifest.json'
        obj = json.loads(path.read_text())
        obj['records'][0]['heading'] = '## Absent'
        path.write_text(json.dumps(obj))
        with self.assertRaises(ValueError):
            knowledge.bundle()

    def test_path_escape_fails(self):
        path = self.root / 'knowledge/manifest.json'
        obj = json.loads(path.read_text())
        obj['records'][0]['path'] = str(SOURCE / 'README.md')
        path.write_text(json.dumps(obj))
        with self.assertRaises(ValueError):
            knowledge.bundle()

    def test_duplicate_id_fails(self):
        path = self.root / 'knowledge/manifest.json'
        obj = json.loads(path.read_text())
        obj['records'].append(obj['records'][0])
        path.write_text(json.dumps(obj))
        with self.assertRaises(ValueError):
            knowledge.bundle()

    def test_unknown_source_fails(self):
        path = self.root / 'knowledge/records.json'
        rows = json.loads(path.read_text())
        rows[0]['source_id'] = 'no-such-source'
        path.write_text(json.dumps(rows))
        with self.assertRaises(ValueError):
            knowledge.validate()

    def test_additional_source_manifest_is_accepted(self):
        records = knowledge.validate()
        sources = {row['source_id'] for row in records}
        self.assertIn('2czYyrTzILg', sources)
        self.assertIn('fZH97QHHYjY', sources)


if __name__ == '__main__':
    unittest.main()
