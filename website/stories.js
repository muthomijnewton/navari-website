/* Searchable, addressable archive. With no JavaScript, every story remains visible. */
(() => {
  const init = () => {
    const archive = document.querySelector('[data-story-archive]');
    if (!archive) return;
    const cards = [...archive.querySelectorAll('[data-story]')];
    const filters = [...archive.querySelectorAll('[data-archive-filter]')];
    const search = archive.querySelector('[name="story-search"]');
    const status = archive.querySelector('[data-archive-status]');
    const empty = archive.querySelector('.archive-empty');
    const pagination = archive.querySelector('.archive-pagination');
    const numbers = archive.querySelector('[data-page-numbers]');
    const previous = archive.querySelector('[data-page-previous]');
    const next = archive.querySelector('[data-page-next]');
    const categories = new Set(filters.map(button => button.dataset.archiveFilter));
    const pageSize = 6;
    const normalized = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
    const indexed = new Map(cards.map(card => [card, normalized(card.dataset.search)]));
    let state;
    let inputTimer;
    const readState = () => {
      const params = new URLSearchParams(location.search);
      const hashCategory = {'#customer-stories':'customer','#news':'company'}[location.hash];
      const category = params.get('category') || hashCategory || 'all';
      return {category:categories.has(category)?category:'all',query:(params.get('q') || '').slice(0,200),page:Math.max(1,parseInt(params.get('page'),10)||1)};
    };
    const updateURL = method => {
      const url = new URL(location.href);
      ['category','q','page'].forEach(key => url.searchParams.delete(key));
      if (state.category !== 'all') url.searchParams.set('category',state.category);
      if (state.query) url.searchParams.set('q',state.query);
      if (state.page > 1) url.searchParams.set('page',String(state.page));
      url.hash = 'archive';
      if (url.href !== location.href) history[method+'State'](null,'',url);
    };
    const render = (focus = false) => {
      const terms = normalized(state.query.trim()).split(/\s+/).filter(Boolean);
      const matching = cards.filter(card => (state.category === 'all' || card.dataset.story === state.category) && terms.every(term => indexed.get(card).includes(term)));
      const pageCount = Math.max(1,Math.ceil(matching.length/pageSize));
      state.page = Math.min(state.page,pageCount);
      const start = (state.page-1)*pageSize;
      const visible = new Set(matching.slice(start,start+pageSize));
      cards.forEach(card => {card.hidden = !visible.has(card);});
      filters.forEach(button => button.setAttribute('aria-pressed',String(button.dataset.archiveFilter === state.category)));
      search.value = state.query;
      status.textContent = matching.length ? `Showing ${start+1}–${Math.min(start+pageSize,matching.length)} of ${matching.length} stories` : 'No stories match your search';
      empty.hidden = matching.length > 0;
      pagination.hidden = pageCount <= 1;
      previous.disabled = state.page <= 1;
      next.disabled = state.page >= pageCount;
      numbers.replaceChildren();
      for (let page=1; page<=pageCount; page++) {
        const button = document.createElement('button');
        button.type = 'button';button.textContent = String(page);button.dataset.page = String(page);
        button.setAttribute('aria-label',`Page ${page}`);
        if (page === state.page) button.setAttribute('aria-current','page');
        numbers.append(button);
      }
      if (focus) {
        archive.querySelector('#archive-heading').focus({preventScroll:true});
        archive.scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
      }
      archive.dispatchEvent(new CustomEvent('navari:filter',{bubbles:true}));
    };
    const navigate = page => {
      clearTimeout(inputTimer);
      state.query = search.value;state.page = page;
      render(true);
      updateURL('push');
    };
    filters.forEach(button => button.addEventListener('click', () => {
      clearTimeout(inputTimer);
      state.query = search.value;state.category = button.dataset.archiveFilter;state.page = 1;
      render();updateURL('push');
    }));
    search.addEventListener('input', () => {
      clearTimeout(inputTimer);
      inputTimer = setTimeout(() => {
        state.query = search.value;state.page = 1;render();updateURL('replace');
      },200);
    });
    search.addEventListener('keydown', event => {
      if (event.key === 'Enter') {
        event.preventDefault();clearTimeout(inputTimer);state.query=search.value;state.page=1;render();updateURL('replace');
      }
    });
    archive.querySelector('[data-reset-archive]').addEventListener('click', () => {
      clearTimeout(inputTimer);state={category:'all',query:'',page:1};render();updateURL('push');search.focus();
    });
    numbers.addEventListener('click', event => {
      const button = event.target.closest('[data-page]');
      if (button) navigate(Number(button.dataset.page));
    });
    previous.addEventListener('click', () => navigate(state.page-1));
    next.addEventListener('click', () => navigate(state.page+1));
    const restore = () => {clearTimeout(inputTimer);state=readState();render();};
    window.addEventListener('popstate',restore);
    window.addEventListener('hashchange',restore);
    state=readState();
    render();
    archive.querySelector('.archive-controls').hidden=false;
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
