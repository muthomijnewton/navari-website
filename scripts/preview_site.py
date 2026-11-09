"""Render Builder exports for offline review; no Frappe installation required.

This preview supports static blocks and responsive styles. Dynamic page-data bindings
and the contact API still require Frappe; it is not a production replacement.
"""
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'


def css_name(name):
    return re.sub(r'[A-Z]', lambda m: '-' + m[0].lower(), name)


def declarations(styles):
    return ';'.join(f'{css_name(k)}:{v}' for k, v in styles.items() if ':' not in k)


def render(block, rules):
    tag = block.get('element', 'div')
    identity = 'b-' + block['blockId']
    for key, media in [('baseStyles', None), ('tabletStyles', '(max-width: 1024px)'), ('mobileStyles', '(max-width: 767px)')]:
        styles = block.get(key, {})
        rule = f'.{identity}{{{declarations(styles)}}}'
        for k, v in styles.items():
            if ':' in k:
                pseudo, prop = k.split(':', 1)
                rule += f'.{identity}:{pseudo}{{{css_name(prop)}:{v}}}'
        rules.append(f'@media {media}{{{rule}}}' if media else rule)
    attrs = {**block.get('attributes', {}), **block.get('customAttributes', {})}
    attrs['class'] = ' '.join([identity] + block.get('classes', []))
    attributes = ' '.join(f'{html.escape(k)}="{html.escape(str(v), quote=True)}"' for k, v in attrs.items() if v is not None)
    content = block.get('innerHTML', '')
    # Older Builder exports escaped quotes inside inline SVG markup.
    if tag == 'svg' and '<svg' in content:
        tag = 'span'
        content = content.replace('\\"', '"')
    content += ''.join(render(c, rules) for c in block.get('children', []))
    if tag in {'img', 'input', 'br', 'hr', 'meta', 'link'}:
        return f'<{tag} {attributes}>'
    return f'<{tag} {attributes}>{content}</{tag}>'


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / 'files').mkdir(exist_ok=True)
    shutil.copyfile(ROOT / 'migration/assets/navari-logo.png', OUT / 'files/navari-logo.png')
    for image in (ROOT / 'migration/assets/stories').glob('*'):
        if image.is_file():
            shutil.copyfile(image, OUT / 'files' / image.name)
    scripts = {s['name']: s for s in json.loads((ROOT / 'migration/scripts/client_scripts.json').read_text())}
    manifest = json.loads((ROOT / 'migration/manifest.json').read_text())
    for name in manifest['pages']:
        page = json.loads((ROOT / f'migration/pages/{name}.json').read_text())
        rules = []
        body = ''.join(render(b, rules) for b in json.loads(page['blocks']))
        selected = [scripts[row['builder_script']] for row in page['client_scripts']]
        css = '\n'.join(rules + [s['script'] for s in selected if s['script_type'] == 'CSS'])
        js = ''.join('<script>' + s['script'] + '</script>' for s in selected if s['script_type'] == 'JavaScript')
        doc = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(page["page_title"])}</title><meta name="description" content="{html.escape(page.get('meta_description', ''), quote=True)}">{page.get("head_html", "")}<style>{css}</style></head><body>{body}{js}</body></html>'
        folder = OUT / page['route'].strip('/')
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'index.html').write_text(doc)
        if name == 'home':
            (OUT / 'index.html').write_text(doc)
    print(f'Preview built: {OUT}\nRun: python -m http.server 4173 --directory dist')


if __name__ == '__main__':
    main()
