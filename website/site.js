/* Progressive enhancement: links, app details and all content work without JS. */
(() => {
  const init = () => {
    const toggle = document.querySelector('.nav-toggle');
    const navigation = document.querySelector('#navigation');
    const triggers = [...document.querySelectorAll('.nav-trigger')];
    const closeMenus = (except) => triggers.forEach(button => {
      if (button === except) return;
      button.setAttribute('aria-expanded', 'false');
      document.getElementById(button.getAttribute('aria-controls')).hidden = true;
    });
    const closeDrawer = (focus = false) => {
      if (!toggle || !navigation) return;
      navigation.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', 'Open navigation');
      closeMenus();
      if (focus) toggle.focus();
    };
    triggers.forEach(button => {
      button.addEventListener('click', () => {
        const open = button.getAttribute('aria-expanded') !== 'true';
        closeMenus(button);
        button.setAttribute('aria-expanded', String(open));
        document.getElementById(button.getAttribute('aria-controls')).hidden = !open;
      });
      button.addEventListener('keydown', event => {
        if (event.key === 'ArrowDown') {
          event.preventDefault();
          if (button.getAttribute('aria-expanded') !== 'true') button.click();
          document.getElementById(button.getAttribute('aria-controls')).querySelector('a')?.focus();
        }
      });
    });
    toggle?.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      navigation.classList.toggle('open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
      if (!open) closeMenus();
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') {
        const open = triggers.find(button => button.getAttribute('aria-expanded') === 'true');
        if (open) { closeMenus(); open.focus(); }
        else if (toggle?.getAttribute('aria-expanded') === 'true') closeDrawer(true);
      }
      if (event.key === 'Tab' && toggle?.getAttribute('aria-expanded') === 'true') {
        const elements = [toggle, ...navigation.querySelectorAll('a, button')].filter(el => el.getClientRects().length);
        const current = elements.indexOf(document.activeElement);
        const next = (current + (event.shiftKey ? -1 : 1) + elements.length) % elements.length;
        event.preventDefault();
        elements[next].focus();
      }
    });
    document.addEventListener('click', event => {
      if (!event.target.closest('.header')) closeDrawer();
    });
    document.addEventListener('focusin', event => {
      if (!event.target.closest('.header')) closeMenus();
    });
    navigation?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => closeDrawer()));
    window.matchMedia('(min-width:901px)').addEventListener('change', () => closeDrawer());
    const path = location.pathname.replace(/\/$/, '') || '/';
    document.querySelectorAll('a[href]').forEach(link => {
      if (new URL(link.href, location.href).origin === location.origin && link.getAttribute('href') === path) link.setAttribute('aria-current', 'page');
    });
    document.querySelectorAll('[data-catalog]').forEach(catalog => {
      const bar = catalog.querySelector('.filter-bar');
      bar.hidden = false;
      const cards = [...catalog.querySelectorAll('[data-category]')];
      const setFilter = category => {
        bar.querySelectorAll('[data-app-filter]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.appFilter === category)));
        cards.forEach(card => {card.hidden = category !== 'All apps' && card.dataset.category !== category;});
        catalog.querySelector('[data-app-count]').textContent = `${cards.filter(card => !card.hidden).length} solutions shown`;
      };
      bar.querySelectorAll('[data-app-filter]').forEach(button => button.addEventListener('click', () => setFilter(button.dataset.appFilter)));
      const revealHash = () => {
        const card = cards.find(card => '#'+card.id === location.hash);
        if (card) {
          setFilter('All apps');
          card.querySelector('details').open = true;
          card.scrollIntoView({block:'start'});
        }
      };
      window.addEventListener('hashchange', revealHash);
      revealHash();
    });
    const stories = document.querySelector('.resource-filters');
    if (stories) {
      stories.hidden = false;
      stories.querySelectorAll('[data-story-filter]').forEach(button => button.addEventListener('click', () => {
        stories.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
        document.querySelectorAll('[data-story]').forEach(card => {card.hidden = button.dataset.storyFilter !== 'all' && card.dataset.story !== button.dataset.storyFilter;});
      }));
    }
    const form = document.querySelector('[data-consultation]');
    if (!form) return;
    const solution = new URLSearchParams(location.search).get('solution');
    if ([...form.elements.solution.options].some(o => o.value === solution)) form.elements.solution.value = solution;
    const date = form.elements.preferred_date;
    // Local Nairobi date avoids a UTC boundary changing the earliest request day.
    const today = new Intl.DateTimeFormat('en-CA', {timeZone:'Africa/Nairobi',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
    date.min = today;
    let busy = false;
    form.addEventListener('submit', async event => {
      event.preventDefault();
      if (busy || !form.reportValidity()) return;
      const values = new FormData(form);
      const value = key => String(values.get(key) || '').trim();
      if (!value('name') || value('message').length < 10) {
        const input = !value('name') ? form.elements.name : form.elements.message;
        input.setCustomValidity('Please provide a name and a message of at least 10 characters.');
        input.reportValidity();
        input.addEventListener('input', () => input.setCustomValidity(''), {once:true});
        return;
      }
      const selected = form.elements.solution.selectedOptions[0].textContent;
      const preference = value('preferred_date') || value('preferred_time') ? `\nPreferred consultation: ${value('preferred_date') || 'Date flexible'} ${value('preferred_time') || 'Time flexible'} EAT (UTC+3). Request only; availability to be confirmed.` : '';
      const data = {name_field:value('name'),email:value('email'),company:value('company'),phone:value('phone'),help_type:value('help_type'),message:`${value('message')}\n\nSolution: ${selected}${preference}`};
      const button = form.querySelector('[type="submit"]');
      const success = form.querySelector('[data-form-success]');
      const failure = form.querySelector('[data-form-error]');
      busy = true;button.disabled = true;form.setAttribute('aria-busy','true');
      const original = button.innerHTML;button.textContent = 'Sending request…';
      success.hidden = true;failure.hidden = true;
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 20000);
      try {
        const headers = {'Content-Type':'application/json'};
        if (window.frappe?.csrf_token) headers['X-Frappe-CSRF-Token'] = window.frappe.csrf_token;
        const response = await fetch('/api/method/frappe.website.doctype.web_form.web_form.accept', {method:'POST',headers,body:JSON.stringify({web_form:'navari-contact-submission',data}),signal:controller.signal});
        if (!response.ok) throw new Error('Request failed');
        const result = await response.json();
        if (result.exc || result.exception || !result.message) throw new Error('Request rejected');
        form.reset();success.hidden = false;success.setAttribute('tabindex','-1');success.focus();
      } catch {
        failure.hidden = false;failure.setAttribute('tabindex','-1');failure.focus();
      } finally {
        clearTimeout(timeout);busy = false;button.disabled = false;button.innerHTML = original;form.removeAttribute('aria-busy');
      }
    });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once:true});
  else init();
})();
