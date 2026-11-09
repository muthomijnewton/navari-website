"""Compile editable website sources into native Frappe Builder block exports.

Run before validation/preview after editing website/*. Never run the live export
script afterwards unless intentionally replacing these sources from a Frappe site.
"""
import copy
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from story_archive import render_archive, render_story_cards, load_stories
from article_pages import render_article
from documentation_page import render_documentation

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'website'
APPS = json.loads((SOURCE / 'apps.json').read_text())
ICONS = {
 'sprout':'<path d="M12 21V11M12 14C5 14 3 10 3 5c6 0 9 3 9 7M12 10c0-5 3-8 9-8 0 6-3 10-9 10"/>',
 'fingerprint':'<path d="M4 12a8 8 0 0 1 16 0M7 15v-3a5 5 0 0 1 10 0v3M10 20c2-3 2-5 2-8M4 16v-1M7 20l1-3M16 21c2-3 3-6 3-9"/>',
 'ledger':'<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 7h6M9 11h6M9 15h2M14 15h1M9 18h2M14 18h1"/>',
 'cart':'<path d="M3 4h2l2 12h11l3-8H6M9 20h.01M17 20h.01"/>',
 'people':'<circle cx="9" cy="8" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3M16 5a3 3 0 0 1 0 6M19 21v-3a6 6 0 0 0-2-4"/>',
 'crm':'<path d="M20 11v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h7M16 3h5v5M21 3l-9 9"/>',
 'box':'<path d="m12 3 9 5v9l-9 5-9-5V8l9-5Zm0 10 9-5M12 13 3 8M12 13v9M7.5 5.5l9 5"/>',
 'factory':'<path d="M3 21V9l6 3V6l6 3V3h5v18H3ZM7 16h1m3 0h1m4 0h1"/>',
 'project':'<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M7 2v4M17 2v4M3 10h18M7 14h4M7 17h8"/>',
 'chart':'<path d="M4 3v18h17M8 16v-4M13 16V7M18 16V4"/>',
 'book':'<path d="M12 5c-3-2-7-2-10-1v16c3-1 7-1 10 1 3-2 7-2 10-1V4c-3-1-7-1-10 1Zm0 0v16"/>',
 'phone':'<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M10 18h4M10 6h4M12 9v5M10 12l2 2 2-2"/>',
 'shield':'<path d="m12 2 9 4v6c0 5-6 9-9 10-3-1-9-5-9-10V6l9-4Zm-4 10 3 3 5-6"/>'}

def icon(key, tone='#e5edbb', color='#56704c'):
 return f'<span class="app-icon" style="--tone:{tone};--icon:{color}"><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[key]}</svg></span>'
def btn(text,href,kind=''):
 return f'<a class="btn {kind}" href="{href}">{text}<span aria-hidden="true">↗</span></a>'
def intro(label,title,copy):
 return f'<section class="page-hero"><div class="wrap"><p class="eyebrow">{label}</p><h1>{title}</h1><p class="intro">{copy}</p></div></section>'
def nav():
 groups=[('Solutions','solutions', '<div class="menu-group"><p class="eyebrow">ERPNext modules</p>'+''.join(f'<a href="{a["url"]}">{a["name"]} <span aria-hidden="true">↗</span></a>' for a in APPS if a['group']=='ERPNext')+'</div><div class="menu-group"><p class="eyebrow">The Frappe suite</p>'+''.join(f'<a href="{a["url"]}">{a["group"]}</a>' for a in APPS if a['group'].startswith('Frappe'))+'</div><div class="menu-note"><p class="eyebrow">Make it yours</p><h3>Global software.<br>Local understanding.</h3><p>Discover Navari apps for payments, compliance and the way your industry works.</p><a class="text-link" href="/services#local">Explore local solutions ↗</a></div>'),
 ('Company','company','<div class="menu-group"><p class="eyebrow">Meet Navari</p><a href="/about">About our company ↗</a><a href="/about#approach">How we work</a><a href="/about#careers">Careers &amp; connections</a></div><div class="menu-group"><p class="eyebrow">Our community</p><a href="/frappe-partner-awards-2026">Frappe partnership</a><a href="/stories">Customer stories</a><a href="https://navari.co.ke/testimonial/">Customer testimonials ↗</a></div><div class="menu-note"><p class="eyebrow">Nairobi. East Africa. Africa.</p><h3>Your next chapter.<br>Our shared ambition.</h3><a class="text-link" href="/contacts">Meet your ERP partner ↗</a></div>'),
 ('Resources','resources','<div class="menu-group"><p class="eyebrow">Read &amp; explore</p><a href="/stories">Stories &amp; insights</a><a href="/stories#customer-stories">Customer experiences</a><a href="/stories#news">News &amp; events</a></div><div class="menu-group"><p class="eyebrow">Build &amp; learn</p><a href="https://docs.navari.co.ke/">Navari documentation ↗</a><a href="https://github.com/navariltd">Open-source projects ↗</a><a href="https://frappe.io/products">Frappe products ↗</a></div><div class="menu-note"><h3>A little context goes a long way.</h3><p>Explore practical ideas and real experiences with open-source business software.</p></div>')]
 menus=''.join(f'<div class="nav-item"><button class="nav-trigger" type="button" aria-expanded="false" aria-controls="menu-{slug}">{label}<span aria-hidden="true">⌄</span></button><div class="menu" id="menu-{slug}" hidden><div class="wrap menu-inner">{content}</div></div></div>' for label,slug,content in groups)
 return '<a class="skip" href="#main">Skip to content</a><div class="announcement"><a href="/frappe-partner-awards-2026">FRAPPE PARTNER AWARD 2026 · AFRICA <span aria-hidden="true">Explore our partnership ↗</span></a></div><header class="header"><div class="wrap nav">'+brand()+f'<nav class="navlinks" id="navigation" aria-label="Main navigation">{menus}<a href="/services#delivery">Our services</a></nav>'+btn('Let’s talk','/contacts')+'<button class="nav-toggle" type="button" aria-label="Open navigation" aria-expanded="false" aria-controls="navigation">☰</button></div><noscript><nav class="wrap noscript-nav" aria-label="Site navigation"><a href="/services">Solutions</a><a href="/about">Company</a><a href="/stories">Resources</a><a href="/contacts">Contact</a></nav></noscript></header>'
def brand():
 return '<a class="brand" href="/" aria-label="Navari Limited home"><img src="/files/navari-logo.png" width="49" height="48" alt=""><span class="brand-word">navari<small>CONNECTED POSSIBILITIES</small></span></a>'
def footer():
 return '<section class="cta"><div class="wrap cta-inner"><div><p class="eyebrow">Your next move</p><h2>Make space for<br><span class="serif">what’s next.</span></h2><p>Let’s find the right starting point for your business.</p></div><div class="actions">'+btn('Talk to an ERP specialist','/contacts')+btn('Explore the apps','/services','light')+'</div></div></section><footer class="footer"><div class="wrap"><div class="footer-grid"><div>'+brand()+'<p>Open-source business systems.<br>Built around your world.</p></div><div><h3>Explore</h3><div class="footer-links"><a href="/services">Solutions &amp; apps</a><a href="/services#delivery">Implementation &amp; support</a><a href="/about">Company</a><a href="/stories">Stories &amp; insights</a></div></div><div><h3>Connect</h3><div class="footer-links"><a href="/contacts">Contact us</a><a href="https://docs.navari.co.ke/">Documentation ↗</a><a href="https://github.com/navariltd">GitHub ↗</a><a href="/about#careers">Careers</a></div></div><div><h3>Find us in Nairobi</h3><p>7th Floor, Block I, Eden Square Complex, Chiromo Road.<br>P.O. Box 56248-00200, Kenya.</p><div class="footer-links"><a href="mailto:solutions@navari.co.ke">solutions@navari.co.ke</a><a href="tel:+254723575670">+254 723 575 670</a></div></div></div><div class="footer-base"><span>© 2026 Navari Limited. All rights reserved.</span><span>Built on open source. Grounded in Africa.</span></div></div></footer>'
def appgrid(full=False):
 items=APPS if full else APPS[:8]
 categories=list(dict.fromkeys(a['category'] for a in items))
 filters='<div class="filter-bar" aria-label="Filter solutions" hidden>'+''.join(f'<button class="filter" type="button" data-app-filter="{x}" aria-pressed="{str(x=="All apps").lower()}">{x}</button>' for x in ['All apps']+categories)+'</div>'
 cards=''
 for a in items:
  cards+=f'<article class="app-card" id="{a["id"]}" data-category="{a["category"]}"><span class="arrow" aria-hidden="true">↗</span><a href="{a["url"]}" aria-label="Open {a["name"]} (opens in a new tab)">'+icon(a['icon'],a['tone'],a['color'])+f'</a><span class="category">{a["group"]}</span><h3><a href="{a["url"]}">{a["name"]}</a></h3><p>{a["copy"]}</p><a class="text-link" href="{a["url"]}">Explore {a["name"]} ↗</a><details class="app-detail"><summary>{a["name"]} details</summary><p>{a["features"]}</p><a class="text-link" href="/contacts?solution={a["id"]}">Discuss {a["name"]} ↗</a></details></article>'
 return '<div data-catalog>'+filters+f'<p class="sr-only" data-app-count role="status">{len(items)} solutions</p><div class="app-grid">{cards}</div></div>'
def trust():
 return '<section class="trust" aria-label="Navari at a glance"><div class="wrap trust-inner"><p class="trust-label">Local experience.<br>Continental perspective.</p><div class="trust-item"><strong>Kenya’s first</strong>ERPNext Frappe Partner</div><div class="trust-item"><strong>100+ clients</strong>running on ERPNext</div><div class="trust-item"><strong>2026 award</strong>Frappe partnerships · Africa</div></div></section>'
def process():
 return '<section class="section process" id="approach"><div class="wrap"><p class="eyebrow">A partnership, from day one</p><h2>Good software starts<br>with <span class="serif">understanding you.</span></h2><div class="steps">'+''.join(f'<article class="step"><span class="number">0{i}</span><h3>{title}</h3><p>{copy}</p></article>' for i,(title,copy) in enumerate([('Understand','Start with your people, your priorities and the work that needs to flow better.'),('Map & configure','Translate real workflows into a practical system and a clear implementation plan.'),('Launch together','Prepare your data and teams, test the details and make the transition with care.'),('Keep improving','Stay supported as your business grows and your requirements evolve.')],1))+'</div></div></section>'
def local():
 local_urls = {key: next(a['url'] for a in APPS if a['id'] == app_id) for key, app_id in [('phone', 'mpesa'), ('shield', 'compliance')]}
 local_urls.update(people='/documentation?topic=biometrics#guides',box='/documentation?topic=industry#guides')
 return '<section class="section" id="local"><div class="wrap split"><div><p class="eyebrow">Global platform. Local connections.</p><h2>Your ERP should<br>speak <span class="serif">your language.</span></h2><p class="intro">Business happens in the details. Navari builds Frappe apps and integrations that connect your systems to the tools and requirements around you.</p><a class="text-link" href="https://docs.navari.co.ke/">Explore Navari documentation ↗</a></div><div class="local-stack">'+''.join(f'<a class="local-row" href="{local_urls.get(key, "https://docs.navari.co.ke/")}">'+icon(key)+f'<div><h3>{title} <span aria-hidden="true">↗</span></h3><p>{copy}</p></div></a>' for key,title,copy in [('phone','M-Pesa payments','Connect payments and disbursements with ERPNext.'),('shield','Kenya compliance','Explore integrations for KRA eTIMS.'),('people','Biometric attendance','Connect supported devices to Frappe HR.'),('box','Industry-specific apps','Explore utility billing, property management and more.')])+'</div></div></section>'
def stories():
 return render_story_cards()
def home():
 ribbon=''.join(f'<a class="ribbon-item" href="{a["url"]}">'+icon(a['icon'],a['tone'],a['color'])+a['name']+'</a>' for a in APPS[:8])
 return '<section class="hero"><div class="wrap"><p class="eyebrow"><span class="status-dot"></span>OPEN SOURCE. CONNECTED BUSINESS.</p><h1>Big possibilities.<br><span class="serif accent">One connected</span> business.</h1><p class="intro">Bring your people, processes and data together with ERPNext and Frappe. Made to work for you, with Navari.</p><div class="actions">'+btn('Find your solutions','#apps')+btn('Meet your ERP partner','/contacts','light')+'</div><p class="hero-footnote">Open-source software. Local expertise. A long-term partnership.</p><div class="app-ribbon">'+ribbon+'</div><div class="workspace" role="img" aria-label="Illustrative ERPNext workspace showing finance, inventory and team workflows. All figures are sample data."><div class="workspace-top"><span class="dots"><i></i><i></i><i></i></span><span>YOUR BUSINESS, WORKING TOGETHER</span><span>ERPNext + Navari</span></div><div class="workspace-body"><div class="workspace-side"><strong>your workspace.</strong><span class="active">◫ &nbsp; Overview</span><span>▤ &nbsp; Accounting</span><span>▦ &nbsp; Inventory</span><span>♧ &nbsp; People</span><span>⌁ &nbsp; Insights</span></div><div class="workspace-main"><div class="workspace-title">A clearer view of the day.<span class="demo-badge">Illustrative data</span></div><div class="metrics"><div class="metric">SALES ORDERS<strong>128</strong><small>One connected pipeline</small></div><div class="metric">INVENTORY ITEMS<strong>2,460</strong><small>Across your warehouses</small></div><div class="metric">TEAM MEMBERS<strong>84</strong><small>Working in sync</small></div></div><div class="workflow"><span>Quotation</span><b>→</b><span>Sales order</span><b>→</b><span>Delivery</span><b>→</b><span>Invoice</span><b>→</b><span>Payment</span></div></div></div></div></div></section>'+trust()+'<section class="section" id="apps"><div class="wrap"><div class="section-top"><div><p class="eyebrow">Find your starting point</p><h2>A better way to work.<br><span class="serif">For every team.</span></h2></div><p>Start with the work you want to improve. Explore the tools, then shape the right solution with us.</p></div>'+appgrid()+'<p class="catalog-note"><a class="text-link" href="/services">Explore the full Frappe &amp; Navari ecosystem <span aria-hidden="true">→</span></a></p></div></section><section class="section pillars"><div class="wrap"><p class="eyebrow">Open by design</p><h2>Your ambition shouldn’t<br>come with <span class="serif">a ceiling.</span></h2><div class="pillar-grid"><article class="pillar"><span class="number">01 / FREEDOM</span><h3>Open source.<br>More possibilities.</h3><p>Build on accessible source code, with the flexibility to extend your system as your needs change.</p></article><article class="pillar"><span class="number">02 / FIT</span><h3>Your business.<br>Your way of working.</h3><p>Configure the workflows that matter to your teams, with tailored development where it adds value.</p></article><article class="pillar"><span class="number">03 / PARTNERSHIP</span><h3>Local understanding.<br>Long-term support.</h3><p>Work with a Nairobi-based partner for implementation, training and the everyday questions after go-live.</p></article></div></div></section>'+local()+process()+'<section class="section"><div class="wrap"><div class="section-top"><div><p class="eyebrow">From the Navari community</p><h2>Real work.<br><span class="serif">Shared experiences.</span></h2></div><a class="text-link" href="/stories">More stories &amp; insights ↗</a></div>'+stories()+'</div></section>'
def services():
 return intro('Solutions & apps','Start with a need.<br><span class="serif accent">Build what’s next.</span>','Explore ERPNext modules, the Frappe suite and Navari integrations. Find the right tools for your teams, with implementation and support around them.')+'<section class="section" id="apps"><div class="wrap">'+appgrid(True)+'</div></section>'+local()+'<section class="section process" id="delivery"><div class="wrap"><div class="section-top"><div><p class="eyebrow">From selection to everyday use</p><h2>The right software.<br><span class="serif">The right partner.</span></h2></div><p>A successful system connects technology with the realities of your business.</p></div><div class="feature-grid">'+''.join(f'<article class="feature"><p class="eyebrow">0{i}</p><h3>{title}</h3><p>{copy}</p><a class="text-link" href="/contacts">Talk to Navari ↗</a></article>' for i,(title,copy) in enumerate([('Consultancy & mapping','Understand where work gets stuck and turn your requirements into a practical ERP roadmap.'),('Implementation & training','Configure, migrate, test and prepare your teams for a confident transition.'),('Customization & support','Extend workflows, connect systems and keep improving your platform after launch.')],1))+'</div></div></section><section class="section"><div class="wrap"><p class="eyebrow">A few useful answers</p><h2>Before your <span class="serif">next move.</span></h2><div class="faq"><details><summary>Where should we start?</summary><p>Start with the business process you want to improve. Navari can help map requirements and choose the right ERPNext modules or Frappe applications.</p></details><details><summary>Is implementation included with the software?</summary><p>Software, implementation, hosting, training and ongoing support are distinct parts of your solution. Contact Navari for a proposal based on your scope. We do not publish a single price for every business.</p></details><details><summary>Can we improve an existing ERPNext system?</summary><p>Yes. Discuss your existing setup, pain points and priorities with the team to identify a suitable customization or support approach.</p></details><details><summary>Do all Frappe apps share data automatically?</summary><p>Integration needs depend on the applications, versions and workflows involved. Navari will assess those requirements with you instead of assuming every app is connected out of the box.</p></details></div></div></section>'
def about():
 return intro('Company / About Navari','Business is personal.<br><span class="serif accent">Your systems should fit.</span>','We help organisations in Kenya and across Africa put open-source business software to work, with ERP consultancy, implementation and customization.')+trust()+'<section class="section"><div class="wrap split"><div><p class="eyebrow">Built around your world</p><h2>Technology with<br><span class="serif">business understanding.</span></h2></div><div><p class="intro">The work behind a business is rarely simple. Finance needs context. Operations need visibility. People need tools they can rely on.</p><p class="intro">Navari brings those needs into the same conversation, translating real processes into practical ERPNext and Frappe implementations.</p><a class="text-link" href="/services#delivery">Explore how we can help ↗</a></div></div></section>'+process()+'<section class="section pillars" id="partnership"><div class="wrap split"><div><p class="eyebrow">Our Frappe partnership</p><h2>A shared foundation.<br><span class="serif">A wider possibility.</span></h2></div><div><h3>Kenya’s first ERPNext Frappe Partner.</h3><p class="intro" style="color:#cbd7d0">Navari received the Frappe Partner Award 2026 for partnerships in the Africa region.</p><div class="actions">'+btn('Read the award announcement','https://navari.co.ke/frappe-partner-awards-2026/','white')+'</div></div></div></section><section class="section" id="careers"><div class="wrap split"><div><p class="eyebrow">Careers & connections</p><h2>Curious minds.<br><span class="serif">Meaningful work.</span></h2></div><div><p class="intro">Interested in the people and work behind Navari? Get in touch to ask about current opportunities.</p><p class="form-note">This page does not list or imply any open positions.</p><a class="text-link" href="mailto:solutions@navari.co.ke?subject=Careers%20enquiry">Start a careers conversation ↗</a></div></div></section>'
def resources():
 return render_archive()
def field(label,name,typ='text',required=False,full=False):
 return f'<label class="field {"full" if full else ""}">{label}{" *" if required else ""}<input name="{name}" type="{typ}" {"required" if required else ""} autocomplete="{dict(name="name",email="email",company="organization",phone="tel").get(name,"off")}"></label>'
def contacts():
 return intro('Let’s talk','Your next chapter.<br><span class="serif accent">Let’s plan it together.</span>','Tell us what you would like to improve. We’ll help you explore a practical starting point for your ERP journey.')+'<section class="section"><div class="wrap contact-layout"><div class="contact-info"><p class="eyebrow">A conversation, not a commitment</p><h2>Talk to someone<br>who gets the work.</h2><p>Evaluating ERPNext? Planning an implementation? Making an existing system work better? Start here.</p><dl><dt>Email</dt><dd><a href="mailto:solutions@navari.co.ke">solutions@navari.co.ke</a></dd><dt>Call us</dt><dd><a href="tel:+254723575670">+254 723 575 670</a></dd><dt>Visit us</dt><dd>7th Floor, Block I, Eden Square Complex,<br>Chiromo Road, Nairobi, Kenya.<br>P.O. Box 56248-00200.</dd></dl><a class="text-link" href="https://www.google.com/maps/search/?api=1&amp;query=Eden+Square+Chiromo+Road+Nairobi">Find us on Google Maps ↗</a></div><form class="consultation" data-consultation><h2 class="form-heading">Let’s find your starting point.</h2><div class="form-grid">'+field('Your name','name',required=True)+field('Work email','email','email',True)+field('Company','company')+field('Phone','phone','tel')+'<label class="field full">What would you like to explore?<select name="solution"><option value="">Help me choose</option>'+''.join(f'<option value="{a["id"]}">{a["name"]}</option>' for a in APPS)+'</select></label><label class="field full">How can we help?<select name="help_type"><option>ERPNext implementation</option><option>ERPNext customization</option><option>Business process mapping</option><option>Integrations</option><option>Support</option><option>General enquiry</option></select></label>'+field('Preferred consultation date (optional)','preferred_date','date')+field('Preferred time (EAT / UTC+3)','preferred_time','time')+'<label class="field full">Tell us about your business *<textarea name="message" rows="4" required minlength="10" maxlength="5000" placeholder="What is working well? What would you like to improve?"></textarea></label></div><p class="form-note">We use these details to respond to your enquiry. A preferred time is a request; Navari will confirm availability directly. Fields marked * are required.</p><button class="btn" type="submit">Request a conversation <span aria-hidden="true">↗</span></button><p class="form-status" role="status" data-form-success hidden>Thank you. Your request has been received. The team will contact you to confirm the next step.</p><p class="form-status error" role="alert" data-form-error hidden>We couldn’t send your request. Please try again or email <a href="mailto:solutions@navari.co.ke">solutions@navari.co.ke</a>.</p><noscript><p class="form-note">To send an enquiry without JavaScript, email solutions@navari.co.ke or call +254 723 575 670.</p></noscript></form></div></section>'

class Blocks(HTMLParser):
 """Convert semantic HTML into individual, editable native Builder blocks."""
 def __init__(self):
  super().__init__(convert_charrefs=True);self.root={'children':[]};self.stack=[self.root];self.counter=0
 def handle_starttag(self,tag,attrs):
  self.counter+=1;attrs=dict(attrs);classes=attrs.pop('class','').split();style=attrs.pop('style',None)
  b={'blockId':f'navari-v2-{self.counter}','element':tag,'blockName':attrs.get('id',tag),'baseStyles':{},'children':[]}
  if tag == 'p':classes.append('copy')
  if classes:b['classes']=classes
  if style:attrs['style']=style
  # Empty HTML boolean attributes must remain true through Builder rendering.
  b['attributes']={k:(k if v is None else v) for k,v in attrs.items()}
  self.stack[-1]['children'].append(b)
  if tag not in {'img','input','br','hr','meta','link'}:self.stack.append(b)
 def handle_endtag(self,tag):
  if len(self.stack)>1 and self.stack[-1]['element']==tag:self.stack.pop()
 def handle_data(self,data):
  if data.strip():
   if self.stack[-1].get('element') in {'option','textarea','title'}:
    self.stack[-1]['innerHTML']=self.stack[-1].get('innerHTML','')+html.escape(data)
    return
   # Text spans preserve mixed-content order alongside inline children.
   self.counter+=1;self.stack[-1]['children'].append({'blockId':f'navari-v2-{self.counter}','element':'span','blockName':'text','baseStyles':{},'innerHTML':html.escape(data)})
 def handle_entityref(self,name):self.handle_data(html.unescape('&'+name+';'))

def write(path,data):path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')

def page_blocks(content):
 content += '<button class="back-to-top" type="button" data-back-to-top aria-label="Back to top" title="Back to top" hidden><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5m-6 6 6-6 6 6"/></svg></button>'
 records = {record['url'].rstrip('/'): '/' + record['slug'] for record in load_stories()}
 def links(match):
  attrs = match.group(1)
  href = re.search(r'href="([^"]+)"', attrs).group(1)
  if href.rstrip('/')=='https://docs.navari.co.ke':
   return '<a'+attrs.replace('href="'+href+'"','href="/documentation"')+'>'
  if 'data-original-publication' not in attrs and href.rstrip('/') in records:
   attrs = attrs.replace('href="'+href+'"', 'href="'+records[href.rstrip('/')]+'"')
   return '<a'+attrs+'>'
  return '<a'+attrs+' target="_blank" rel="noopener noreferrer" title="Opens in a new tab">'
 content=re.sub(r'<a\b([^>]*\bhref="https?://[^"]+"[^>]*)>', links, content)
 parser=Blocks();parser.feed('<div class="navari-site">'+content+'</div>')
 return content, json.dumps(parser.root['children'],separators=(',',':'),ensure_ascii=False)

def main():
 manifest=json.loads((ROOT/'migration/manifest.json').read_text())
 scripts=[{'name':'Navari Website v2 Styles','script_type':'CSS','script':(SOURCE/'site.css').read_text()},{'name':'Navari Website v2 Interactions','script_type':'JavaScript','script':(SOURCE/'site.js').read_text()},{'name':'Navari Website Motion','script_type':'JavaScript','script':(SOURCE/'motion.js').read_text()},{'name':'Navari Stories Archive','script_type':'JavaScript','script':(SOURCE/'stories.js').read_text()},{'name':'Navari Article Reading','script_type':'JavaScript','script':(SOURCE/'article.js').read_text()},{'name':'Navari Documentation Discovery','script_type':'JavaScript','script':(SOURCE/'documentation.js').read_text()}]
 write(ROOT/'migration/scripts/client_scripts.json',scripts)
 metadata={'documentation':('Documentation & Guides | Navari Limited','Find documentation for Navari apps, payments, compliance and integrations. Search the application guides and discover your next step.'),'home':('ERPNext & Frappe Solutions in Kenya | Navari Limited','Open-source business software with local expertise. Explore ERPNext, Frappe and Navari integrations for your business in Kenya and Africa.'),'services':('ERPNext Modules & Frappe Apps | Navari Solutions','Explore business software for finance, HR, CRM, manufacturing and more. Discover ERPNext modules, Frappe apps and local Navari integrations.'),'about':('About Navari | Your ERPNext Partner in Africa','Meet Navari Limited, Kenya’s first ERPNext Frappe Partner. ERP consultancy, implementation, customization and support from Nairobi.'),'stories':('Stories, Experiences & Insights | Navari Limited','Explore the Navari story archive: customer journeys, open-source perspectives and company news. Search articles and discover stories from across Africa.'),'contacts':('Talk to an ERP Specialist | Navari Limited','Discuss ERPNext, Frappe and your business requirements with Navari in Nairobi. Request a consultation or contact the team directly.')}
 for label,render in [('home',home),('services',services),('about',about),('stories',resources),('contacts',contacts),('documentation',lambda:render_documentation(icon))]:
  page_scripts=scripts[:3]+[scripts[5]] if label=='documentation' else scripts[:4] if label=='stories' else scripts[:3]
  page_path=ROOT/f'migration/pages/{label}.json';page=json.loads(page_path.read_text()) if page_path.exists() else {'doctype':'Builder Page','name':'navari-documentation','page_name':'navari-documentation','route':'documentation','published':1,'staging':0,'is_standard':0,'is_template':0,'dynamic_route':0,'authenticated_access':0,'disable_indexing':0}
  content=nav()+'<main id="main" tabindex="-1">'+render()+'</main>'+footer()
  content, blocks=page_blocks(content)
  page.update(blocks=blocks,head_html='',page_data_script='',page_title=metadata[label][0],meta_description=metadata[label][1],language='en',client_scripts=[{'builder_script':s['name']} for s in page_scripts])
  page['draft_blocks']=page['blocks'];write(page_path,page)
  # Source HTML is an inspectable design artefact; JSON stays the deployment format.
  (SOURCE/f'{label}.html').write_text(content+'\n')
  for variant in (ROOT/'migration/pages').glob(label+'-cloud-*.json'):
   data=json.loads(variant.read_text())
   for key in ['blocks','head_html','page_data_script','page_title','meta_description','client_scripts']:data[key]=page[key]
   if 'draft_blocks' in data:data['draft_blocks']=page['blocks']
   write(variant,data)
  if label=='home':
   for variant in (ROOT/'builder').glob('*.json'):
    data=json.loads(variant.read_text())
    for key in ['blocks','draft_blocks','head_html','page_data_script','page_title','meta_description','client_scripts']:data[key]=page[key]
    write(variant,data)
  manifest['pages'].setdefault(label,{'name':page['name'],'route':page['route']})
  manifest['pages'][label]['scripts']=[s['name'] for s in page_scripts]
  if label=='documentation':
   write(ROOT/'migration/pages/documentation-cloud-create.json',{key:value for key,value in page.items() if key not in {'name','draft_blocks'}})
 # Article routes retain the original published slugs for link compatibility.
 article_scripts=scripts[:3]+[scripts[4]]
 (SOURCE/'articles').mkdir(exist_ok=True)
 for story in load_stories():
  label='article-'+story['id']
  page_path=ROOT/f'migration/pages/{label}.json'
  page=json.loads(page_path.read_text()) if page_path.exists() else {'doctype':'Builder Page','name':'navari-story-'+story['id'],'page_name':'navari-story-'+story['id'],'published':1,'staging':0,'is_standard':0,'is_template':0,'dynamic_route':0,'authenticated_access':0,'disable_indexing':0}
  content=nav()+'<main id="main" tabindex="-1">'+render_article(story)+'</main>'+footer()
  content,blocks=page_blocks(content)
  page.update(route=story['slug'],blocks=blocks,draft_blocks=blocks,head_html='',body_html='',page_data_script='',page_title=story['title']+' | Navari Journal',meta_description=story['excerpt'],canonical_url=story['url'],language='en',client_scripts=[{'builder_script':s['name']} for s in article_scripts])
  write(page_path,page)
  create={key:value for key,value in page.items() if key not in {'name','draft_blocks'}}
  write(ROOT/f'migration/pages/{label}-cloud-create.json',create)
  (SOURCE/'articles'/f"{story['slug']}.html").write_text(content+'\n')
  manifest['pages'][label]={'name':page['name'],'route':page['route'],'scripts':[s['name'] for s in article_scripts]}
 manifest['scripts']=[s['name'] for s in scripts];write(ROOT/'migration/manifest.json',manifest)
 print(f"Built {len(manifest['pages'])} Builder pages, synchronized cloud payloads and homepage exports.")

if __name__=='__main__':main()
