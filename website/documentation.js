/* Search, wayfinding and optional light effects for the documentation hub. */
(() => {
  const init = () => {
    const hub = document.querySelector('[data-docs-hub]');
    if (!hub) return;
    const inputs = [...hub.querySelectorAll('[data-doc-search]')];
    const topics = [...hub.querySelectorAll('[data-doc-topic]')];
    const cards = [...hub.querySelectorAll('[data-doc-card]')];
    const grid = hub.querySelector('#docs-grid');
    const sort = hub.querySelector('[data-doc-sort]');
    const status = hub.querySelector('[data-doc-status]');
    const hint = hub.querySelector('[data-doc-hero-status]');
    const empty = hub.querySelector('.docs-empty');
    const root = document.documentElement;
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const categoryIds = new Set(topics.map(button=>button.dataset.docTopic));
    const normalize = value=>value.normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
    const index = new Map(cards.map((card,order)=>[card,{text:normalize(card.dataset.search),order}]));
    let inputTimer;
    const readState = () => {
      const params = new URLSearchParams(location.search);
      return {topic:categoryIds.has(params.get('topic'))?params.get('topic'):'all',query:(params.get('q')||'').slice(0,200),sort:['az','za'].includes(params.get('sort'))?params.get('sort'):'featured'};
    };
    let state = readState();
    const updateURL = method => {
      const url = new URL(location.href);
      ['topic','q','sort'].forEach(key=>url.searchParams.delete(key));
      if(state.topic!=='all')url.searchParams.set('topic',state.topic);
      if(state.query)url.searchParams.set('q',state.query);
      if(state.sort!=='featured')url.searchParams.set('sort',state.sort);
      url.hash='guides';
      if(url.href!==location.href)history[method+'State'](null,'',url);
    };
    const render = () => {
      const terms=normalize(state.query.trim()).split(/\s+/).filter(Boolean);
      const ordered=[...cards].sort((a,b)=>state.sort==='featured'?index.get(a).order-index.get(b).order:state.sort==='za'?b.dataset.name.localeCompare(a.dataset.name):a.dataset.name.localeCompare(b.dataset.name));
      let found=0;
      ordered.forEach(card=>{
        const visible=(state.topic==='all'||card.dataset.topic===state.topic)&&terms.every(term=>index.get(card).text.includes(term));
        card.hidden=!visible;
        if(visible)found++;
        grid.append(card);
      });
      topics.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.docTopic===state.topic)));
      inputs.forEach(input=>{if(input.value!==state.query)input.value=state.query;});
      sort.value=state.sort;
      status.textContent=`${found} application${found===1?'':'s'} found${state.topic==='all'?'':' in this topic'}`;
      if(hint)hint.textContent=state.query?`${found} match${found===1?'':'es'} · Press Enter to explore.`:'Try “M-Pesa”, “attendance” or “eTIMS”.';
      empty.hidden=found>0;
      hub.dispatchEvent(new CustomEvent('navari:filter',{bubbles:true}));
    };
    const goToResults = () => {
      hub.querySelector('#docs-results-heading').focus({preventScroll:true});
      hub.querySelector('#guides').scrollIntoView({block:'start',behavior:reduced.matches||root.classList.contains('calm-mode')?'instant':'smooth'});
    };
    inputs.forEach(input=>{
      input.addEventListener('input',()=>{
        state.query=input.value;
        clearTimeout(inputTimer);
        inputTimer=setTimeout(()=>{state.query=input.value;render();updateURL('replace');},180);
      });
      input.addEventListener('keydown',event=>{
        if(event.key==='Enter'){event.preventDefault();clearTimeout(inputTimer);state.query=input.value;render();updateURL('replace');goToResults();}
      });
    });
    topics.forEach(button=>button.addEventListener('click',()=>{
      clearTimeout(inputTimer);
      state.topic=button.dataset.docTopic;render();updateURL('push');
    }));
    sort.addEventListener('change',()=>{clearTimeout(inputTimer);state.sort=sort.value;render();updateURL('push');});
    hub.querySelector('[data-doc-reset]').addEventListener('click',()=>{
      clearTimeout(inputTimer);state={topic:'all',query:'',sort:'featured'};render();updateURL('push');inputs[1].focus();
    });
    window.addEventListener('popstate',()=>{clearTimeout(inputTimer);state=readState();render();});
    document.addEventListener('keydown',event=>{
      const editing=event.target.closest('input,textarea,select,[contenteditable=true]');
      if(((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k')||(!editing&&!event.ctrlKey&&!event.metaKey&&!event.altKey&&event.key==='/')){
        event.preventDefault();inputs[0].focus({preventScroll:true});
        inputs[0].scrollIntoView({block:'center',behavior:reduced.matches||root.classList.contains('calm-mode')?'instant':'smooth'});
      }
    });
    const calm=hub.querySelector('[data-doc-calm]');
    calm.hidden=false;
    calm.addEventListener('click',()=>{
      const paused=calm.getAttribute('aria-pressed')!=='true';
      calm.setAttribute('aria-pressed',String(paused));
      calm.innerHTML=(paused?'Calm mode on':'Calm mode')+' <span aria-hidden="true">◌</span>';
      root.classList.toggle('calm-mode',paused);
      document.dispatchEvent(new CustomEvent('navari:motion-preference',{detail:{paused}}));
    });
    const hero=hub.querySelector('.docs-hero');
    let lightFrame,lightX=80,lightY=45;
    const paintLight=()=>{lightFrame=null;hero.style.setProperty('--light-x',lightX+'%');hero.style.setProperty('--light-y',lightY+'%');};
    hero.addEventListener('pointermove',event=>{
      if(event.pointerType!=='mouse'||reduced.matches||root.classList.contains('calm-mode'))return;
      const bounds=hero.getBoundingClientRect();lightX=Math.max(0,Math.min(100,(event.clientX-bounds.left)/bounds.width*100));lightY=Math.max(0,Math.min(100,(event.clientY-bounds.top)/bounds.height*100));
      if(!lightFrame)lightFrame=requestAnimationFrame(paintLight);
    },{passive:true});
    hero.addEventListener('pointerleave',()=>{lightX=80;lightY=45;if(!lightFrame)lightFrame=requestAnimationFrame(paintLight);});
    hub.querySelector('.docs-hero-search').hidden=false;
    hub.querySelector('.docs-topics nav').hidden=false;
    hub.querySelector('.docs-toolbar').hidden=false;
    render();
  };
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
