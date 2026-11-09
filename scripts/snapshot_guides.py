"""Refresh public Navari guide content (requires beautifulsoup4).

Run explicitly, never during the offline build. Fetches only documented chapter
routes listed in the application sidebars, then stores sanitized content.
"""
import argparse
import concurrent.futures
import json
import math
import re
import urllib.request
from datetime import date
from pathlib import Path
from urllib.parse import urljoin,urlsplit,unquote
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
ORIGIN='https://docs.navari.co.ke/'
SAFE={'aside','p','div','span','strong','em','b','i','u','s','del','sub','sup','br','hr','h1','h2','h3','h4','h5','h6','ul','ol','li','a','img','video','source','pre','code','blockquote','table','thead','tbody','tfoot','tr','th','td','details','summary','figure','figcaption','kbd'}
def fetch(url):
 for attempt in range(2):
  try:
   with urllib.request.urlopen(url,timeout=30) as response:return response.read().decode()
  except Exception:
   if attempt:raise

def capture(app):
 if app.get('available') is False:return []
 soup=BeautifulSoup(fetch(app['start_url']),'html.parser');links={}
 for a in soup.select('.wiki-sidebar a[data-route]'):links.setdefault(a['data-route'],a.get_text(' ',strip=True))
 if not links:raise ValueError('No chapter links for '+app['id'])
 return [{'app':app['id'],'route':r,'title':t} for r,t in links.items()]
def chapter(record):
 try:
  s=BeautifulSoup(fetch(ORIGIN+record['route']),'html.parser'); c=s.select_one('#wiki-content')
  if c is None:raise ValueError('No wiki-content')
  return {**record,'title':s.select_one('#wiki-page-title').get_text(' ',strip=True),'html':str(c)}
 except Exception as error:return {**record,'error':str(error)}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--captured',type=Path,help='Sanitize an already captured chapter JSON file');args=parser.parse_args()
 apps=json.loads((ROOT/'website/documentation.json').read_text())['applications']
 if args.captured:raw=json.loads(args.captured.read_text())
 else:
  jobs=[]
  for app in apps:jobs.extend(capture(app))
  with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:raw=list(pool.map(chapter,jobs))
 counts={};local={};guides=[]
 for record in raw:
  app=record['app'];first=app not in counts;counts[app]=counts.get(app,0)+1
  suffix=record['route'].split('/',1)[-1]
  record['local_route']='documentation/'+app+('' if first else '/'+suffix)
  local[ORIGIN+record['route']]=record['local_route']
 for app in apps:
  if 'documentation/'+app['id'] not in local.values():continue
  local[app['url'].rstrip('/')]='documentation/'+app['id'];local[app['start_url'].rstrip('/')]='documentation/'+app['id']
 # Prefix source IDs to avoid collisions with the site shell. Resolve headingless
 # anchors too, so source deep links survive inside the reading layout.
 target_ids={}
 for record in raw:
  soup=BeautifulSoup(record.get('html',''),'html.parser');ids={};used=set()
  for node in soup.select('[id]'):
   old=node['id'];new='doc-'+re.sub('[^a-zA-Z0-9_-]','-',old)
   while new in used:new+='-section'
   used.add(new);ids.setdefault(old,new);node['id']=new
  target_ids[record['local_route']]=ids;record['_soup']=soup
 for record in raw:
  soup=record['_soup'];source=ORIGIN+record['route'];headings=[]
  for node in list(soup.find_all(True)):
   if node.parent is None:continue
   if node.name in {'script','style','form','button','input','noscript','svg'}:node.decompose();continue
   if node.name=='iframe':
    src=urljoin(source,node.get('src',''));a=soup.new_tag('a',href=src);a.string='Open embedded media ↗';node.replace_with(a);continue
   if node.name not in SAFE:node.unwrap();continue
   if 'wiki-blank-line' in node.get('class',[]):node.decompose();continue
   attrs={k:v for k,v in node.attrs.items() if k in {'id','href','src','alt','title','colspan','rowspan','start','reversed','type','open','width','height'}}
   callout_classes=[c for c in node.get('class',[]) if c in {'callout','callout-note','callout-tip','callout-important','callout-warning','callout-caution','callout-header','callout-title','callout-content'}]
   if callout_classes:attrs['class']=' '.join(callout_classes)
   if node.name=='h1':node.name='h2'
   if node.name in {'h2','h3','h4'}:
    if 'id' not in attrs:attrs['id']='doc-section-'+str(len(headings)+1)
    headings.append({'id':attrs['id'],'title':node.get_text(' ',strip=True)})
   for attr in ['src','href']:
    if attr not in attrs:continue
    absolute=urljoin(source,str(attrs[attr]));parts=urlsplit(absolute)
    if parts.scheme not in {'http','https','mailto','tel'}:attrs.pop(attr);continue
    if attr=='href' and parts.scheme in {'http','https'}:
     key=parts._replace(query='',fragment='').geturl().rstrip('/');route=local.get(key)
     if route:
      anchor=target_ids.get(route,{}).get(unquote(parts.fragment))
      attrs[attr]='/'+route+('#'+anchor if anchor else '')
     else:attrs[attr]=absolute
    else:attrs[attr]=absolute
   if node.name=='img':attrs.update(loading='lazy',decoding='async');attrs.setdefault('alt','Documentation illustration')
   if node.name=='video':attrs.update(controls='controls',preload='none')
   if node.name=='a' and str(attrs.get('href','')).startswith('http'):attrs.update(target='_blank',rel='noopener noreferrer')
   if node.name=='div' and not node.get_text(strip=True) and not node.find(['img','video','source']):node.decompose();continue
   node.attrs=attrs
  # Scroll tables within the prose instead of forcing the whole page wide.
  for table in soup.find_all('table'):
   wrapper=soup.new_tag('div');wrapper['class']='guide-table-wrap';wrapper['tabindex']='0';wrapper['role']='region';wrapper['aria-label']='Documentation table';table.wrap(wrapper)
  content=str(soup);text=soup.get_text(' ',strip=True)
  guides.append({'app':record['app'],'route':record['local_route'],'source':source,'title':record['title'],'minutes':max(1,math.ceil(len(text.split())/220)),'headings':headings,'html':content if 'error' not in record else '',**({'unavailable_reason':record['error']} if 'error'in record else {})})
 for app in apps:
  if app['id'] not in counts:guides.append({'app':app['id'],'route':'documentation/'+app['id'],'source':app['start_url'],'title':app['name']+' documentation','minutes':1,'headings':[],'html':'','unavailable_reason':'Published guide unavailable at capture time.'})
 (ROOT/'website/guides.json').write_text(json.dumps({'captured_on':str(date.today()),'origin':ORIGIN,'pages':guides},ensure_ascii=False,indent=2)+'\n')
 print('Captured',len(guides),'guide pages;',sum(bool(g['html']) for g in guides),'with source content')
if __name__=='__main__':main()
