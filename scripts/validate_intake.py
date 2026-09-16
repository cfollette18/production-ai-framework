"""Validate source packets structurally and relationally; not a semantic judge."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def validate_packet(packet, schema=None):
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError as error:
        raise ValueError('Install optional intake dependencies: python3 -m pip install -r ingestion/requirements.txt') from error
    if schema is None:
        schema = json.loads((ROOT / 'ingestion/packet.schema.json').read_text(encoding='utf-8'))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(packet), key=lambda e: str(list(e.absolute_path)))
    if errors:
        error = errors[0]
        raise ValueError(f'{list(error.absolute_path)}: {error.message}')

    def require(condition, message):
        if not condition:
            raise ValueError(message)

    def references(values, known, label):
        require(set(values) <= set(known), f'{label}: unknown references {sorted(set(values) - set(known))}')

    source_id = packet['source']['id']
    seen = set()
    maps = {}
    for group in ('segments', 'claims', 'procedures', 'conflicts'):
        maps[group] = {}
        for row in packet[group]:
            rid = row['id']
            require(rid not in seen, 'Duplicate ID: ' + rid)
            if group != 'segments':
                require(rid.startswith(source_id + '-'), 'IDs must be source-scoped: ' + rid)
            seen.add(rid)
            maps[group][rid] = row
    segments, claims = maps['segments'], maps['claims']
    require(bool(packet['source']['title'].strip()), 'Source title is blank')
    for segment in segments.values():
        references(segment['claim_ids'], claims, segment['id'])
        if segment['state'] == 'reviewed':
            require(segment['disposition'] != 'unprocessed', 'Reviewed segment marked unprocessed')
        else:
            require(segment['disposition'] == 'unprocessed' and not segment['claim_ids'], 'Unreviewed segment cannot supply claims')
        if segment['disposition'] == 'extracted':
            require(bool(segment['claim_ids']), 'Extracted segment has no claims')
        if segment['disposition'] == 'no_relevant_content':
            require(not segment['claim_ids'], 'Excluded segment cannot supply claims')
        require(bool(segment['note'].strip()), 'Each segment needs an explanation')

    for claim in claims.values():
        references(claim['evidence_segment_ids'], segments, claim['id'])
        require(bool(claim['statement'].strip()) and bool(claim['scope'].strip()), 'Claim text/scope cannot be blank')
        require(claim['primary_pillar'] not in claim['secondary_pillars'], 'Primary pillar repeated in secondary tags')
        require('unmapped' not in claim['secondary_pillars'], 'Unmapped is not a secondary pillar')
        if claim['primary_pillar'] == 'unmapped':
            require(not claim['secondary_pillars'] and bool(claim['caveats']), 'Unmapped claims need a reason and no mapped secondary tags')
        for sid in claim['evidence_segment_ids']:
            require(segments[sid]['state'] == 'reviewed', 'Claim cites unreviewed evidence')
            require(claim['id'] in segments[sid]['claim_ids'], 'Evidence ledger missing reciprocal claim link')
    for segment in segments.values():
        for cid in segment['claim_ids']:
            require(segment['id'] in claims[cid]['evidence_segment_ids'], 'Claim missing reciprocal segment evidence')

    coverage = packet['coverage']
    pending = {s['id'] for s in segments.values() if s['state'] != 'reviewed'}
    require(coverage['supplied_segment_count'] == len(segments), 'Incorrect supplied segment count')
    require(coverage['reviewed_segment_count'] == len(segments) - len(pending), 'Incorrect reviewed segment count')
    require(set(coverage['unprocessed_segment_ids']) == pending, 'Coverage omits or invents unprocessed segments')
    require(set(packet['resume']['next_segment_ids']) == pending, 'Resume must list all known pending segments')
    complete = packet['extraction']['state'] == 'complete_for_supplied_input'
    if complete:
        require(not pending and not packet['resume']['missing_input'], 'Complete extraction still has pending input')
    else:
        require(bool(pending or packet['resume']['missing_input']), 'Partial extraction needs a resumable gap')

    review = packet['extraction']['review']
    if review['status'] == 'reviewed':
        require(complete and bool(review['reviewer'] and review['reviewer'].strip()) and bool(review['date']) and bool(review['notes'].strip()), 'Reviewed status requires completed extraction and reviewer/date/notes')
    integration = packet['integration']
    external = set(integration['existing_record_ids'])
    require(not (external & seen), 'Existing record IDs collide with new source IDs')
    if integration['comparison_status'] == 'not_provided':
        require(not external and integration['existing_revision'] is None, 'Cannot assert comparisons without an existing snapshot')
    else:
        require(bool(external) and bool(integration['existing_revision'] and integration['existing_revision'].strip()), 'Comparison requires existing records and a revision/hash')
    endpoints = set(claims) | external
    for conflict in packet['conflicts']:
        references(conflict['claim_ids'], claims, conflict['id'])
        references(conflict['existing_record_ids'], external, conflict['id'])
        require(len(conflict['claim_ids']) + len(conflict['existing_record_ids']) >= 2, 'Conflict requires two distinct sides')
    for relation in packet['relationships']:
        references([relation['from'], relation['to']], endpoints, 'Relationship endpoints')
        references(relation['supporting_claim_ids'], claims, 'Relationship evidence')
        require(relation['from'] != relation['to'], 'Relationship cannot point to itself')
        if relation['type'] == 'contradicts':
            require(any({relation['from'], relation['to']} <= set(c['claim_ids'] + c['existing_record_ids']) for c in packet['conflicts']), 'Contradiction requires an unresolved conflict record')
    for procedure in packet['procedures']:
        for step in procedure['steps']:
            references(step['supporting_claim_ids'], claims, 'Procedure evidence')
    return {'source_id': source_id, 'segments': len(segments), 'claims': len(claims),
            'state': packet['extraction']['state'], 'review_status': review['status'],
            'scope': 'structure and references only; source fidelity and inventory completeness require review'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', nargs='?', type=Path)
    parser.add_argument('--all', action='store_true', help='Check the synthetic example and all sources/*/intake.json packets')
    args = parser.parse_args()
    if bool(args.packet) == args.all:
        parser.error('Specify either an intake.json path or --all')
    paths = [ROOT / 'ingestion/examples/intake.json', *sorted((ROOT / 'sources').glob('*/intake.json'))] if args.all else [args.packet]
    for path in paths:
        result = validate_packet(json.loads(path.read_text(encoding='utf-8')))
        print(json.dumps({'file': str(path), **result}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
