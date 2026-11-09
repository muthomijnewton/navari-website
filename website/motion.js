/* Native, progressively enhanced motion. Content never depends on animation. */
(() => {
  const init = () => {
    if (!Element.prototype.animate) return;
    const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
    let userPaused=false;
    const shouldReduce=()=>preference.matches||userPaused;
    const active = new Set();
    const current = new WeakMap();
    const seen = new WeakSet();
    const ease = 'cubic-bezier(.22,1,.36,1)';
    const root = document.documentElement;
    const inView = element => {
      const rect = element.getBoundingClientRect();
      return rect.width && rect.height && rect.top < innerHeight && rect.bottom > 0;
    };
    const play = (element, frames, options = {}) => {
      if (shouldReduce() || document.hidden || !element.getClientRects().length) return;
      current.get(element)?.cancel();
      const animation = element.animate(frames, {duration:650, easing:ease, ...options});
      current.set(element, animation);
      active.add(animation);
      const cleanup = () => {
        active.delete(animation);
        if (current.get(element) === animation) current.delete(element);
      };
      animation.onfinish = cleanup;
      animation.oncancel = cleanup;
      return animation;
    };
    const enter = (element, delay = 0) => {
      seen.add(element);
      play(element, [
        {opacity:.15, transform:'translate3d(0,26px,0)'},
        {opacity:1, transform:'translate3d(0,0,0)'}
      ], {delay, fill:'backwards'});
    };
    const delayInGroup = element => {
      const siblings = [...element.parentElement.children].filter(child => child.matches('[data-motion]') && !child.hidden);
      return Math.min(Math.max(siblings.indexOf(element),0),3) * 70;
    };
    const workspace = document.querySelector('.workspace');
    const animateWorkspace = () => {
      if (!workspace || shouldReduce()) return;
      workspace.querySelectorAll('.metric').forEach((metric, index) => {
        play(metric, [{opacity:.3, transform:'translateY(14px)'},{opacity:1, transform:'translateY(0)'}], {delay:150 + index*100,fill:'backwards'});
      });
      workspace.querySelectorAll('.workflow > span').forEach((step, index) => {
        play(step, [
          {backgroundColor:'transparent', color:'#5c6d70', offset:0},
          {backgroundColor:'#e5edbb', color:'#172d32', offset:.35},
          {backgroundColor:'#e5edbb', color:'#172d32', offset:.65},
          {backgroundColor:'transparent', color:'#172d32', offset:1}
        ], {duration:650,delay:350+index*330});
      });
      workspace.querySelectorAll('.workflow > b').forEach((arrow, index) => {
        play(arrow, [{opacity:.25,transform:'translateX(-4px)'},{opacity:1,transform:'translateX(3px)'},{opacity:1,transform:'translateX(0)'}], {duration:450,delay:600+index*330});
      });
    };
    // Observe content itself, never add a global hidden/preload state.
    const selector = [
      '.hero .eyebrow','.hero h1','.hero .intro','.hero .actions',
      '.hero-footnote','.ribbon-item','.workspace',
      '.page-hero .eyebrow','.page-hero h1','.page-hero .intro',
      '.section-top','.section > .wrap > h2','.section > .wrap > .eyebrow',
      '.docs-card','.docs-library-heading','.docs-closing-inner','.featured-story','.archive-top','.app-card','.trust-item','.pillar','.step','.story-card','.feature',
      '.split > div','.contact-info','.consultation','.cta-inner > div','.faq details'
    ].join(',');
    const targets = [...document.querySelectorAll(selector)];
    targets.forEach(element => element.setAttribute('data-motion',''));
    const observer = 'IntersectionObserver' in window ? new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        if (seen.has(entry.target)) return;
        enter(entry.target, delayInGroup(entry.target));
        if (entry.target === workspace) animateWorkspace();
      });
    }, {threshold:0.08, rootMargin:'0px 0px -24px 0px'}) : null;
    const applyPreference = () => {
      root.classList.toggle('motion-ready', !shouldReduce());
      if (shouldReduce()) {
        active.forEach(animation => animation.cancel());
        observer?.disconnect();
      } else {
        targets.forEach(element => {
          if (seen.has(element)) return;
          if (observer) observer.observe(element);
          else if (inView(element)) enter(element);
        });
      }
    };
    document.addEventListener('navari:motion-preference',event=>{
      userPaused=event.detail?.paused===true;
      root.classList.toggle('calm-mode',userPaused);
      applyPreference();
    });
    preference.addEventListener('change', applyPreference);
    applyPreference();
    // Reintroduce matching results when the visitor changes a filter.
    document.addEventListener('navari:filter', event => {
      [...event.target.querySelectorAll('.app-card:not([hidden]),.story-card:not([hidden]),.docs-card:not([hidden])')]
        .filter(inView).forEach((element,index) => {
          observer?.unobserve(element);
          enter(element,Math.min(index,3)*55);
        });
    });
    // Keyboard focus and hidden tabs immediately settle ongoing motion.
    document.addEventListener('focusin', event => {
      // Pointer focus must not move a link between mouse-down and mouse-up.
      if (!event.target.matches(':focus-visible')) return;
      active.forEach(animation => {
        if (animation.effect?.target?.contains(event.target)) animation.cancel();
      });
    });
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) active.forEach(animation => animation.cancel());
    });
    const header = document.querySelector('.header');
    let frame;
    const updateHeader = () => {
      frame = null;
      header?.classList.toggle('is-scrolled', scrollY > 24);
    };
    window.addEventListener('scroll', () => {
      if (!frame) frame = requestAnimationFrame(updateHeader);
    }, {passive:true});
    updateHeader();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
