/* Optional reading tools. Article text, contents and source links work without JS. */
(() => {
  const init = () => {
    const article = document.querySelector('[data-article]');
    if (!article) return;
    const copy = article.querySelector('[data-copy-article]');
    const message = article.querySelector('[data-share-status]');
    if (navigator.clipboard?.writeText) {
      copy.hidden = false;
      copy.addEventListener('click', async () => {
        try {
          const url = new URL(location.href);url.hash='';url.search='';
          await navigator.clipboard.writeText(url.href);
          message.textContent='Article link copied.';
          copy.textContent='Link copied ✓';
        } catch {message.textContent='Could not copy the link. Copy the address from your browser instead.';}
      });
    }
    const body = article.querySelector('[data-article-content]');
    const progress = document.querySelector('[data-reading-progress]');
    let frame;
    const updateProgress = () => {
      frame=null;
      const rect=body.getBoundingClientRect();
      const start=scrollY+rect.top-innerHeight*.25;
      const range=Math.max(1,rect.height-innerHeight*.5);
      const value=Math.max(0,Math.min(1,(scrollY-start)/range));
      progress.style.transform=`scaleX(${value})`;
    };
    window.addEventListener('scroll',()=>{if(!frame)frame=requestAnimationFrame(updateProgress);},{passive:true});
    window.addEventListener('resize',updateProgress);updateProgress();
    if ('IntersectionObserver' in window) {
      const links=[...article.querySelectorAll('.article-sidebar nav a')];
      const observer=new IntersectionObserver(entries=>{
        const visible=entries.filter(entry=>entry.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top);
        if(!visible.length)return;
        links.forEach(link=>{
          if(link.hash==='#'+visible[0].target.id)link.setAttribute('aria-current','location');
          else link.removeAttribute('aria-current');
        });
      },{rootMargin:'-15% 0px -50% 0px',threshold:0});
      article.querySelectorAll('.article-chapter,.article-media').forEach(section=>observer.observe(section));
    }
    article.querySelectorAll('[data-article-media]').forEach(shell=>{
      const button=shell.querySelector('[data-load-media]');
      const mount=shell.querySelector('.media-mount');
      const source=new URL(shell.dataset.src);
      const video=shell.dataset.kind==='video'&&source.origin==='https://www.youtube-nocookie.com'&&/^\/embed\/[A-Za-z0-9_-]{11}$/.test(source.pathname);
      const isDocument=shell.dataset.kind==='document'&&source.origin==='https://navari.co.ke'&&source.pathname.startsWith('/wp-content/uploads/')&&source.pathname.endsWith('.pdf');
      if(!video&&!isDocument)return;
      button.hidden=false;
      button.addEventListener('click',()=>{
        button.disabled=true;
        const iframe=window.document.createElement('iframe');
        iframe.src=source.href;iframe.title=shell.dataset.title;
        iframe.referrerPolicy='strict-origin-when-cross-origin';
        if(video){iframe.allow='encrypted-media; picture-in-picture; fullscreen';iframe.allowFullscreen=true;}
        iframe.addEventListener('error',()=>{shell.parentElement.querySelector('.media-error').hidden=false;});
        mount.replaceChildren(iframe);mount.hidden=false;
        shell.querySelector('.media-cover').hidden=true;
        iframe.setAttribute('tabindex','0');iframe.focus();
      },{once:true});
    });
  };
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
