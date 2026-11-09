"""Shared story cards and the complete editorial archive."""
import html
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {'customer': 'Customer stories', 'insights': 'Perspectives', 'company': 'Company & news'}


def load_stories():
    return json.loads((ROOT / 'website/stories.json').read_text())


def e(value):
    return html.escape(str(value), quote=True)


def story_date(story):
    return date.fromisoformat(story['date']).strftime('%d %b %Y').lstrip('0')


def image(story, featured=False):
    priority = 'loading="eager" fetchpriority="high"' if featured else 'loading="lazy"'
    return f'<img src="{e(story["image"])}" alt="{e(story["image_alt"])}" width="{story["image_width"]}" height="{story["image_height"]}" {priority} decoding="async">'


def card(story):
    search = ' '.join([story['title'], story['short_title'], story['excerpt'], CATEGORIES[story['category']]])
    return (
        f'<article class="story-card archive-card" data-story="{e(story["category"])}" data-search="{e(search)}" id="story-{story["id"]}">'
        f'<a class="story-image" href="{e(story["url"])}" aria-label="Read {e(story["title"])} (opens in a new tab)">{image(story)}</a>'
        '<div class="story-content">'
        f'<div class="story-meta"><span class="story-category">{e(CATEGORIES[story["category"]])}</span><time datetime="{story["date"]}">{story_date(story)}</time></div>'
        f'<h3><a href="{e(story["url"])}">{e(story["title"])}</a></h3>'
        f'<p>{e(story["excerpt"])}</p><a class="text-link" href="{e(story["url"])}">Read the story <span aria-hidden="true">↗</span></a>'
        '</div></article>'
    )


def render_story_cards():
    records = {story['id']: story for story in load_stories()}
    return '<div class="story-grid">' + ''.join(card(records[identity]) for identity in ['2275', '2257', '2992']) + '</div>'


def render_archive():
    records = load_stories()
    featured = records[0]
    counts = Counter(story['category'] for story in records)
    filters = ''.join(
        f'<button class="filter" type="button" data-archive-filter="{key}" aria-pressed="{str(key == "all").lower()}" aria-controls="archive-grid">{e(label)} <span class="filter-count">{count}</span></button>'
        for key, label, count in [('all', 'All stories', len(records))] + [(key, label, counts[key]) for key, label in CATEGORIES.items()]
    )
    return (
        '<section class="page-hero journal-hero"><div class="wrap"><p class="eyebrow">THE NAVARI JOURNAL</p>'
        '<div class="journal-intro"><h1>Ideas. Experiences.<br><span class="serif accent">Stories worth sharing.</span></h1>'
        '<div><p class="intro">The people, partnerships and practical ideas behind better business systems. A collection from Navari, across Africa.</p>'
        '<a class="text-link" href="#archive">Browse the full Navari archive <span aria-hidden="true">↓</span></a></div></div></div></section>'
        '<section class="section featured-section"><div class="wrap">'
        '<article class="featured-story">'
        f'<a class="featured-image" href="{e(featured["url"])}" aria-label="Read {e(featured["title"])} (opens in a new tab)">{image(featured, True)}<span class="featured-label">Featured story</span></a>'
        '<div class="featured-content"><p class="eyebrow">A shared milestone</p>'
        f'<div class="story-meta"><span class="story-category">{e(CATEGORIES[featured["category"]])}</span><time datetime="{featured["date"]}">{story_date(featured)}</time></div>'
        '<h2>Frappe Partner<br><span class="serif">Awards 2026.</span></h2>'
        '<p>Recognition for partnerships in Africa. A moment to celebrate the clients, team and community behind the work.</p>'
        f'<a class="btn" href="{e(featured["url"])}">Read the story <span aria-hidden="true">↗</span></a>'
        '</div></article></div></section>'
        '<section class="section archive-section" id="archive" data-story-archive>'
        '<div class="wrap"><div class="archive-top"><div><p class="eyebrow">Explore the collection</p><h2 id="archive-heading" tabindex="-1">The full <span class="serif">archive.</span></h2></div>'
        '<p>Customer journeys. Open-source perspectives.<br>Stories from the people behind Navari.</p></div>'
        '<span id="customer-stories" class="archive-anchor" aria-hidden="true"></span><span id="news" class="archive-anchor" aria-hidden="true"></span>'
        '<div class="archive-controls" hidden><div class="filter-bar archive-filters" aria-label="Filter stories by category">' + filters + '</div>'
        '<label class="archive-search"><span class="sr-only">Search stories</span><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"></circle><path d="m16 16 5 5"></path></svg><input type="search" name="story-search" placeholder="Find a story…" maxlength="200" aria-controls="archive-grid" autocomplete="off"></label></div>'
        f'<p class="archive-count" data-archive-status role="status" aria-live="polite">{len(records)} stories · latest first</p>'
        '<div class="story-grid archive-grid" id="archive-grid">' + ''.join(card(story) for story in records) + '</div>'
        '<div class="archive-empty" hidden><span class="eyebrow">A different starting point?</span><h3>No stories found.</h3><p>Try another word or explore a different category.</p><button class="btn light" type="button" data-reset-archive>Show all stories</button></div>'
        '<nav class="archive-pagination" aria-label="Story archive pages" hidden><button class="pagination-arrow" type="button" data-page-previous>← Previous</button><div class="pagination-pages" data-page-numbers></div><button class="pagination-arrow" type="button" data-page-next>Next →</button></nav>'
        '</div></section>'
        '<section class="section journal-resources"><div class="wrap split"><div><p class="eyebrow">Keep exploring</p><h2>From a good idea<br>to <span class="serif">your next step.</span></h2></div>'
        '<div><p class="intro">Ready to put open-source software to work? Explore our solutions, or dig into the documentation behind Navari’s apps.</p>'
        '<div class="actions"><a class="btn" href="/services">Explore solutions <span aria-hidden="true">↗</span></a><a class="btn light" href="https://docs.navari.co.ke/">Read the documentation <span aria-hidden="true">↗</span></a></div></div></div></section>'
    )
