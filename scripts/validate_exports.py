"""Check portable Builder exports and the references used during migration."""
import json
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def walk(blocks):
    for block in blocks:
        yield block
        yield from walk(block.get('children', []))


def main():
    manifest = json.loads((ROOT / 'migration/manifest.json').read_text())
    scripts = json.loads((ROOT / 'migration/scripts/client_scripts.json').read_text())
    names = {s['name'] for s in scripts}
    assert len(names) == len(scripts), 'Duplicate script names'
    assert names == set(manifest['scripts']), 'Manifest script list differs'
    for script in scripts:
        if script['script_type'] == 'JavaScript':
            subprocess.run(['node', '--check'], input=script['script'], text=True, check=True, capture_output=True)
    count = 0
    for path in [* (ROOT / 'migration/pages').glob('*.json'), * (ROOT / 'builder').glob('*.json')]:
        page = json.loads(path.read_text())
        blocks = json.loads(page['blocks'])
        ids = [b['blockId'] for b in walk(blocks)]
        assert len(ids) == len(set(ids)), f'{path}: duplicate block IDs'
        for row in page['client_scripts']:
            assert row['builder_script'] in names, f'{path}: missing script'
        if page.get('draft_blocks'):
            assert json.loads(page['draft_blocks']) == blocks, f'{path}: stale draft'
        assert 'hello@navari.co.ke' not in page['blocks'], f'{path}: stale email'
        for block in walk(blocks):
            for key in ['attributes', 'customAttributes']:
                attrs = block.get(key, {})
                for value in attrs.values():
                    if isinstance(value, str):
                        assert 'navari.localhost' not in value, f'{path}: local URL'
                        assert '/private/files/ai-attachment' not in value, f'{path}: private logo'
        count += 1
    for name, info in manifest['pages'].items():
        page = json.loads((ROOT / f'migration/pages/{name}.json').read_text())
        assert info['scripts'] == [s['builder_script'] for s in page['client_scripts']]
    pages = {name: json.loads((ROOT / f'migration/pages/{name}.json').read_text()) for name in manifest['pages']}
    routes = {'/': 'home', **{'/' + page['route'].strip('/'): name for name, page in pages.items()}}
    for name, page in pages.items():
        blocks = list(walk(json.loads(page['blocks'])))
        dom_ids = [b['attributes']['id'] for b in blocks if b.get('attributes', {}).get('id')]
        assert len(dom_ids) == len(set(dom_ids)), f'{name}: duplicate HTML ids'
        assert sum(b.get('element') == 'h1' for b in blocks) == 1, f'{name}: expected one h1'
        for block in blocks:
            href = block.get('attributes', {}).get('href', '')
            if not href or not href.startswith(('/', '#')):
                continue
            link = urlsplit(href)
            target = routes.get(link.path.rstrip('/') or '/') if link.path else name
            assert target, f'{name}: missing route {href}'
            if link.fragment:
                ids = {b.get('attributes', {}).get('id') for b in walk(json.loads(pages[target]['blocks']))}
                assert link.fragment in ids, f'{name}: missing anchor {href}'
    print(f'Validated {count} page exports and {len(scripts)} client scripts; JavaScript syntax passed.')


if __name__ == '__main__':
    main()
