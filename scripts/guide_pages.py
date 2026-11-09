"""Native reading layouts for the captured public application documentation."""
import html
import json
import hashlib
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def e(s):return html.escape(str(s),quote=True)
def load_guides():return json.loads((ROOT/'website/guides.json').read_text())
def guide_label(guide):return 'guide-'+hashlib.sha256(guide['route'].encode()).hexdigest()[:14]
def render_guide(guide,apps,all_guides,icon,captured_on):
 captured_label=date.fromisoformat(captured_on).strftime("%d %b %Y").lstrip("0")
 app=next(a for a in apps if a['id']==guide['app'])
 chapters=[g for g in all_guides if g['app']==app['id']]
 index=chapters.index(guide)
 navigation=''.join(f'<a href="/{e(g["route"])}" data-guide-chapter data-search="{e(g["title"].lower())}"'+(' aria-current="page"' if g is guide else '')+f'><span>{i+1:02}</span>{e(g["title"])}</a>' for i,g in enumerate(chapters))
 toc=''.join(f'<a href="#{e(h["id"])}">{e(h["title"])}</a>' for h in guide.get('headings',[]))
 neighbours=''
 for delta,label in [(-1,'Previous guide'),(1,'Up next')]:
  if 0<=index+delta<len(chapters):
   g=chapters[index+delta];neighbours+=f'<a href="/{e(g["route"])}"><span>{label} {"←" if delta<0 else "→"}</span><strong>{e(g["title"])}</strong></a>'
 if not neighbours:neighbours='<a href="/documentation"><span>Keep exploring →</span><strong>All application guides</strong></a>'
 content=guide.get('html') or '<div class="guide-notice"><h2>Let’s find the right guidance.</h2><p>This guide is currently unavailable on the source documentation service. Navari can help you find the right next step.</p><a class="btn" href="/contacts">Ask Navari about this guide ↗</a></div>'
 source=f'<a href="{e(guide["source"])}" data-guide-source>View source documentation ↗</a>' if guide.get('html') else ''
 return (
 f'<div class="guide-experience" data-guide-reader style="--guide-tone:{app["tone"]};--guide-color:{app["color"]}">'
 '<section class="page-hero guide-hero"><div class="wrap">'
 '<nav class="guide-breadcrumb" aria-label="Breadcrumb"><a href="/documentation">The field guide</a><span aria-hidden="true">/</span>'
 f'<a href="/documentation/{e(app["id"])}">{e(app["name"])}</a></nav>'
 f'<div class="guide-app-mark">{icon(app["icon"],app["tone"],app["color"])}<span>{e(app["category"])}</span></div>'
 f'<h1>{e(guide["title"])}</h1><div class="guide-meta"><span>{e(app["name"])}</span><span>Guide {index+1:02} / {len(chapters):02}</span>'
 f'<span>{guide.get("minutes",1)} min read</span><span>Documentation snapshot · {e(captured_label)}</span></div></div></section>'
 '<div class="wrap guide-layout">'
 f'<aside class="guide-sidebar"><a class="guide-all-apps" href="/documentation">← All applications</a><details data-guide-menu open><summary>{e(app["name"])} <span aria-hidden="true">⌄</span></summary><div class="guide-nav-body">'
 '<label class="guide-search" hidden><span class="sr-only">Find a chapter</span><input type="search" aria-label="Find a chapter" placeholder="Find a chapter…"></label>'
 f'<nav class="guide-chapters" aria-label="{e(app["name"])} chapters">{navigation}</nav><p data-guide-empty hidden>No chapters found. Try another word.</p></div></details>'
 '<div class="guide-sidebar-help"><span>Questions welcome.</span><a href="/contacts">Talk to the Navari team ↗</a></div></aside>'
 '<article class="guide-reading"><div class="guide-reading-tools"><span>A little know-how goes a long way.</span><button type="button" data-guide-copy hidden>Copy link ↗</button><span data-guide-copy-status class="sr-only" role="status"></span></div>'
 f'<div class="guide-prose" id="guide-content">{content}</div>'
 f'<div class="guide-source-note"><span>From the Navari documentation library. Technical instructions and media retain their source content.</span>{source}</div>'
 f'<nav class="guide-neighbours" aria-label="Guide pagination">{neighbours}</nav>'
 '<div class="guide-human"><span aria-hidden="true">✦</span><div><h2>A little stuck?</h2><p>There’s a real team behind these guides.</p></div><a href="/contacts">Let’s figure it out ↗</a></div></article>'
 f'<aside class="guide-toc"><nav aria-label="On this page"><h2>On this page</h2>{toc or "<span>You’re in the right place.</span>"}</nav><a class="guide-toc-top" href="#main">Back to the beginning ↑</a></aside></div></div>'
 )
