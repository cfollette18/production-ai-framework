import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validate_intake', ROOT / 'scripts/validate_intake.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.packet = json.loads((ROOT / 'ingestion/examples/intake.json').read_text())

    def reject(self):
        with self.assertRaises(ValueError):
            module.validate_packet(self.packet)

    def test_synthetic_source_validates_without_promoting_to_verified(self):
        result = module.validate_packet(self.packet)
        self.assertEqual(result['claims'], 4)
        self.assertEqual(result['review_status'], 'needs_review')

    def test_empty_template_is_not_valid_output(self):
        self.packet = json.loads((ROOT / 'ingestion/packet.template.json').read_text())
        self.reject()

    def test_unknown_evidence_is_rejected(self):
        self.packet['claims'][0]['evidence_segment_ids'] = ['invented-segment']
        self.reject()

    def test_omitted_ledger_link_is_rejected(self):
        self.packet['segments'][0]['claim_ids'] = []
        self.reject()

    def test_complete_cannot_hide_unread_segment(self):
        segment = self.packet['segments'][-1]
        segment.update(state='unread', disposition='unprocessed')
        self.packet['coverage'].update(reviewed_segment_count=5, unprocessed_segment_ids=[segment['id']])
        self.packet['resume']['next_segment_ids'] = [segment['id']]
        self.reject()
        self.packet['extraction']['state'] = 'partial'
        self.assertEqual(module.validate_packet(self.packet)['state'], 'partial')

    def test_claim_cannot_reference_unread_segment(self):
        self.packet['segments'][0]['state'] = 'unread'
        self.reject()

    def test_coverage_count_mismatch_is_rejected(self):
        self.packet['coverage']['supplied_segment_count'] = 7
        self.reject()

    def test_invented_review_is_rejected(self):
        self.packet['extraction']['review']['status'] = 'reviewed'
        self.reject()

    def test_contradiction_must_have_conflict_record(self):
        self.packet['conflicts'] = []
        self.reject()

    def test_no_snapshot_cannot_claim_external_comparison(self):
        self.packet['integration']['existing_record_ids'] = ['orchestration']
        self.reject()

    def test_proposal_step_still_needs_known_motivation(self):
        self.packet['procedures'][0]['steps'][1]['supporting_claim_ids'] = ['unsupported']
        self.reject()

    def test_invalid_date_or_pillar_is_rejected(self):
        original = copy.deepcopy(self.packet)
        self.packet['extraction']['run_date'] = '2026-99-99'
        self.reject()
        self.packet = original
        self.packet['claims'][0]['primary_pillar'] = 'random-new-category'
        self.reject()

    def test_duplicate_ids_and_missing_required_fields_rejected(self):
        original = copy.deepcopy(self.packet)
        self.packet['claims'].append(copy.deepcopy(self.packet['claims'][0]))
        self.reject()
        self.packet = original
        del self.packet['claims'][0]['scope']
        self.reject()

    def test_documented_routing_exports_source_intake_and_guide(self):
        knowledge_spec = importlib.util.spec_from_file_location('intake_routing_knowledge', ROOT / 'scripts/knowledge.py')
        knowledge = importlib.util.module_from_spec(knowledge_spec)
        knowledge_spec.loader.exec_module(knowledge)
        with tempfile.TemporaryDirectory() as tmp:
            repository = Path(tmp)
            for folder in ('knowledge', 'docs', 'sources', 'templates'):
                shutil.copytree(ROOT / folder, repository / folder)
            shutil.copy2(ROOT / 'START_HERE.md', repository / 'START_HERE.md')
            destination = repository / 'sources/example-retry-workshop'
            destination.mkdir()
            for name in ('intake.json', 'guide.md', 'handoff.md'):
                shutil.copy2(ROOT / 'ingestion/examples' / name, destination / name)
            manifest_path = repository / 'knowledge/manifest.json'
            manifest = json.loads(manifest_path.read_text())
            for suffix, file_name, origin in [('intake', 'intake.json', 'source_metadata'), ('guide', 'guide.md', 'source_synopsis')]:
                manifest['records'].append({'id': 'source-example-retry-workshop-' + suffix,
                    'path': 'sources/example-retry-workshop/' + file_name, 'heading': None, 'origin': origin})
            manifest_path.write_text(json.dumps(manifest))
            knowledge.ROOT = repository
            knowledge.validate()
            records = {row['id']: row for row in knowledge.bundle()['records']}
            self.assertIn('source-example-retry-workshop-intake', records)
            self.assertIn('retry', records['source-example-retry-workshop-guide']['text'])
            self.assertIn('source-manifest', records)  # Original source remains registered.


if __name__ == '__main__':
    unittest.main()
