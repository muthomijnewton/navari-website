"""The Navari documentation hub, built from verified public guide destinations."""
import html
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOPICS=[('pos','Point of sale'),('payments','Payments'),('compliance','Fiscal compliance'),('biometrics','Biometric integrations'),('farm','Farm operations'),('sourcing','Procurement & sourcing'),('industry','Industry solutions')]


def load_documentation():
    return json.loads((ROOT/'website/documentation.json').read_text())['applications']


def e(value):
    return html.escape(str(value),quote=True)


def render_documentation(icon):
    apps=load_documentation();by_id={app['id']:app for app in apps};counts=Counter(app['topic'] for app in apps)
    guides=[('vunapos','01','Your first sale starts here.','Get to know VunaPOS'),('frappe-mpesa-payments','02','Make the connection.','Explore M-Pesa payments'),('kenya-compliance-via-slade360-advantage','03','Find your compliance path.','Understand Kenya eTIMS')]
    scene=''.join(f'<a class="docs-scene-row" href="{e(by_id[identity]["start_url"])}"><span class="scene-number">{number}</span><span><strong>{e(title)}</strong><small>{e(label)}</small></span><span aria-hidden="true">↗</span></a>' for identity,number,title,label in guides)
    quick=''.join(f'<a href="{e(by_id[identity]["start_url"])}">{label}<span aria-hidden="true">↗</span></a>' for identity,label in [('vunapos','VunaPOS'),('frappe-mpesa-payments','M-Pesa'),('kenya-compliance-via-slade360-advantage','Kenya compliance')])
    topics=''.join(f'<button type="button" data-doc-topic="{topic}" aria-pressed="false" aria-controls="docs-grid"><span>{e(label)}</span><span>{counts[topic]:02}</span></button>' for topic,label in TOPICS)
    cards=''
    for app in apps:
        destination=app['start_url'] if app.get('available',True) else '/contacts'
        link_label='Open the guide' if app.get('available',True) else 'Ask about this guide'
        icon_label='Open '+app['name']+' documentation (opens in a new tab)' if app.get('available',True) else 'Ask Navari about '+app['name']+' documentation'
        unavailable='' if app.get('available',True) else '<span class="docs-unavailable">Guide unavailable</span>'
        search=' '.join([app['name'],app['description'],app['category'],app['topic'],'M-Pesa MPesa' if app['id']=='frappe-mpesa-payments' else ''])
        cards+=(f'<article class="docs-card" data-doc-card data-topic="{app["topic"]}" data-name="{e(app["name"])}" data-search="{e(search)}" style="--doc-tone:{app["tone"]};--doc-color:{app["color"]}">'
                f'<a class="docs-card-icon" href="{e(destination)}" aria-label="{e(icon_label)}">'+icon(app['icon'],app['tone'],app['color'])+'</a>'+unavailable+
                f'<span class="docs-card-topic">{e(app["category"])}</span><h3><a href="{e(destination)}">{e(app["name"])}</a></h3><p>{e(app["description"])}</p>'
                f'<a class="docs-card-link" href="{e(destination)}">{e(link_label)} <span aria-hidden="true">↗</span></a></article>')
    return (
      '<div class="docs-experience" data-docs-hub>'
      '<section class="docs-hero page-hero"><div class="docs-light" aria-hidden="true"></div><div class="wrap docs-hero-inner">'
      '<div class="docs-hero-copy"><p class="eyebrow"><span class="docs-spark" aria-hidden="true">✦</span> The Navari field guide</p>'
      '<h1>A little clarity.<br><span class="serif accent">Big possibilities.</span></h1>'
      '<p class="intro">From “where do I start?” to “look what we built.” Find your way through Navari’s Frappe apps, one good guide at a time.</p>'
      '<div class="docs-hero-search" hidden><label><span class="sr-only">Search documentation</span><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"></circle><path d="m16 16 5 5"></path></svg><input type="search" data-doc-search placeholder="What would you like to figure out?" aria-label="Search documentation" aria-keyshortcuts="/ Control+K Meta+K" maxlength="200" autocomplete="off"><kbd aria-hidden="true">/</kbd></label><p data-doc-hero-status>Try “M-Pesa”, “attendance” or “eTIMS”.</p></div>'
      '<div class="docs-quick"><span>Good places to start</span>'+quick+'</div>'
      '<div class="docs-hero-footer"><span class="docs-live-dot" aria-hidden="true"></span><span>__DOC_TOTAL__ applications. One place to find your next step.</span><button class="docs-calm" type="button" aria-pressed="false" data-doc-calm hidden>Calm mode <span aria-hidden="true">◌</span></button></div></div>'
      '<div class="docs-scene"><div class="docs-orbit" aria-hidden="true"><svg viewBox="0 0 500 420"><path d="M40 240C40 50 460 50 460 240S40 430 40 240Z"></path><circle cx="55" cy="192" r="6"></circle><circle cx="447" cy="285" r="4"></circle></svg></div><span class="docs-floating-star" aria-hidden="true">✦</span>'
      '<div class="docs-scene-card"><div class="docs-scene-top"><span class="docs-scene-dots" aria-hidden="true"><i></i><i></i><i></i></span><span>NAVARI / DOCUMENTATION</span><span aria-hidden="true">↗</span></div>'
      '<p class="docs-scene-kicker">A guide, not a guessing game.</p><h2>Your next step,<br><span class="serif">illuminated.</span></h2><div class="docs-scene-links">'+scene+'</div><div class="docs-scene-foot"><span aria-hidden="true">✧</span> Built for the work behind your business.</div></div>'
      '<span class="docs-scene-note">A little know-how goes a long way.</span></div></div></section>'
      '<section class="docs-wayfinding"><div class="wrap"><span>Find your app.</span><span aria-hidden="true">↗</span><span>Follow the guide.</span><span aria-hidden="true">↗</span><span>Make it yours.</span><a href="#guides">Let’s get into it <span aria-hidden="true">↓</span></a></div></section>'
      '<section class="section docs-library" id="guides"><div class="wrap"><div class="section-top docs-library-heading"><div><p class="eyebrow">A little less searching. A little more doing.</p><h2 id="docs-results-heading" tabindex="-1">There’s a guide<br><span class="serif">for that.</span></h2></div><p>Pick a topic, find your app, and take the next step. The details are right this way.</p></div>'
      '<div class="docs-library-layout"><aside class="docs-topics"><p class="eyebrow">Browse by topic</p><nav aria-label="Documentation categories" hidden><button type="button" data-doc-topic="all" aria-pressed="true" aria-controls="docs-grid"><span>All applications</span><span>__DOC_TOTAL__</span></button>'+topics+'</nav><a class="docs-help-note" href="/contacts"><span aria-hidden="true">✧</span><strong>A little stuck?</strong><span>There’s a real team behind these guides.</span><span class="text-link">Talk to Navari ↗</span></a></aside>'
      '<div class="docs-results"><div class="docs-toolbar" hidden><label class="docs-filter-search"><span class="sr-only">Filter documentation</span><input type="search" data-doc-search placeholder="Find an app or integration…" maxlength="200" autocomplete="off"></label><label class="docs-sort">Sort <select data-doc-sort aria-label="Sort documentation"><option value="featured">Default order</option><option value="az">Name A–Z</option><option value="za">Name Z–A</option></select></label></div>'
      '<p class="docs-count" role="status" aria-live="polite" data-doc-status>__DOC_TOTAL__ applications to explore</p><div class="docs-grid" id="docs-grid">'+cards+'</div>'
      '<div class="docs-empty" hidden><span aria-hidden="true">✧</span><h3>Let’s try a different path.</h3><p>No guides matched that search. Try another word or clear the topic.</p><button class="btn light" type="button" data-doc-reset>Show all guides</button></div></div></div></div></section>'
      '<section class="docs-closing"><div class="wrap docs-closing-inner"><div><p class="eyebrow">Good tools. Good guidance.</p><h2>Knowing is good.<br><span class="serif">Getting going is better.</span></h2><p>Bring your questions. We’ll help you find a practical way forward.</p></div><a class="btn" href="/contacts">Let’s figure it out <span aria-hidden="true">↗</span></a></div></section></div>'
    ).replace('__DOC_TOTAL__',str(len(apps)))
