"""Editorial article layouts and preserved case-study/webinar access."""
import json
from pathlib import Path
from story_archive import CATEGORIES, article_url, card, e, image, load_stories, story_date

ROOT = Path(__file__).resolve().parents[1]


def article_data():
    return json.loads((ROOT / 'website/articles.json').read_text())



def render_article(story):
    data = article_data()[story['id']]
    records = load_stories()
    current = next(i for i, record in enumerate(records) if record['id'] == story['id'])
    contents = ''.join(f'<a href="#section-{i}">{e(section["heading"])}</a>' for i, section in enumerate(data['sections'], 1))
    sections = ''.join(
        f'<section class="article-chapter" id="section-{i}"><span class="chapter-number">0{i}</span><h2>{e(section["heading"])}</h2>'
        + ''.join(f'<p>{e(paragraph)}</p>' for paragraph in section['paragraphs']) + '</section>'
        for i, section in enumerate(data['sections'], 1)
    )
    media = ''
    if resource := data.get('media'):
        if resource['kind'] == 'video':
            source = 'https://www.youtube-nocookie.com/embed/' + resource['id']
            action = 'Play the webinar'
            descriptor = 'The original session, with Muchai Gateru and Ankita Roychoudhary.'
            external_action = 'Watch on YouTube ↗'
        else:
            source = resource['url']
            action = 'Open the document reader'
            descriptor = 'Explore the customer’s complete original presentation.'
            external_action = 'Open the full PDF ↗'
        media = (
            '<section class="article-media" id="original-material"><p class="eyebrow">The complete source material</p>'
            f'<h2>{"Watch the conversation." if resource["kind"] == "video" else "Read the full case study."}</h2><p>{e(descriptor)}</p>'
            f'<div class="media-shell" data-article-media data-kind="{resource["kind"]}" data-src="{e(source)}" data-title="{e(resource["label"])}">'
            f'<div class="media-cover"><span class="media-symbol" aria-hidden="true">{"▷" if resource["kind"] == "video" else "▤"}</span><p>{e(resource["label"])}</p>'
            f'<button class="btn" type="button" data-load-media hidden>{action}</button></div><div class="media-mount" hidden></div></div>'
            f'<a class="text-link" href="{e(resource["url"])}">{external_action}</a>'
            '<p class="media-error" role="alert" hidden>If the reader does not load, use the link above to open the original material.</p></section>'
        )
        contents += '<a href="#original-material">' + ('Watch the webinar' if resource['kind'] == 'video' else 'Full case study') + '</a>'
    neighbours = ''
    for offset, label in [(-1, 'Newer story'), (1, 'Older story')]:
        position = current + offset
        if 0 <= position < len(records):
            neighbour = records[position]
            neighbours += f'<a class="article-neighbour" href="{article_url(neighbour)}"><span class="eyebrow">{label}</span><h3>{e(neighbour["short_title"])}</h3><span class="text-link">Continue reading <span aria-hidden="true">→</span></span></a>'
    related = sorted((record for record in records if record['id'] != story['id']), key=lambda record: record['category'] != story['category'])[:3]
    return (
        '<div class="reading-progress" aria-hidden="true"><span data-reading-progress></span></div>'
        '<article class="journal-article" data-article>'
        '<header class="page-hero article-hero"><div class="wrap">'
        '<nav class="article-breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/stories">Stories</a><span aria-hidden="true">/</span>'
        f'<a href="/stories?category={e(story["category"])}#archive">{e(CATEGORIES[story["category"]])}</a></nav>'
        f'<p class="eyebrow">{e(data["kind"])}</p><h1>{e(story["title"])}</h1><p class="intro">{e(story["excerpt"])}</p>'
        f'<div class="article-byline"><span class="author-mark" aria-hidden="true">N</span><span>Navari Journal</span><span aria-hidden="true">·</span><time datetime="{story["date"]}">{story_date(story)}</time>'
        '<button class="copy-link" type="button" data-copy-article hidden>Copy link <span aria-hidden="true">↗</span></button><span class="sr-only" role="status" data-share-status></span></div>'
        '</div></header>'
        f'<figure class="article-figure wrap">{image(story, True)}<figcaption>{e(story["short_title"])} · Navari Journal</figcaption></figure>'
        '<div class="wrap article-reading-layout"><aside class="article-sidebar"><nav aria-label="In this story"><p class="eyebrow">In this story</p>' + contents + '</nav>'
        '<a class="text-link" href="/stories#archive">← Back to the archive</a></aside>'
        '<div class="article-prose" data-article-content>'
        f'<div class="article-takeaway"><span class="eyebrow">The thread through this story</span><p>{e(data["takeaway"])}</p></div>'
        + sections + media +
        '<div class="article-source"><p>This is a concise editorial overview of Navari’s published story.</p>'
        f'<a class="text-link" data-original-publication href="{e(story["url"])}">Read the original publication <span aria-hidden="true">↗</span></a></div>'
        '<div class="article-end"><span class="eyebrow">Your next chapter</span><h2>What could work<br><span class="serif">better for you?</span></h2><p>Bring your business questions to a team that understands the work behind them.</p><a class="btn" href="/contacts">Talk to Navari <span aria-hidden="true">↗</span></a></div>'
        f'<nav class="article-neighbours" aria-label="More stories">{neighbours}</nav></div></div></article>'
        '<section class="section article-related"><div class="wrap"><div class="section-top"><div><p class="eyebrow">Keep the conversation going</p><h2>A little more <span class="serif">perspective.</span></h2></div><a class="text-link" href="/stories#archive">Explore all stories →</a></div><div class="story-grid">'
        + ''.join(card(record) for record in related) + '</div></div></section>'
    )
