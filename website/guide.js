/* Reading enhancements; every chapter and instruction remains usable without JS. */
(() => {
 const init=()=>{
  const reader=document.querySelector('[data-guide-reader]');if(!reader)return;
  const menu=reader.querySelector('[data-guide-menu]');
  const compact=matchMedia('(max-width:900px)');
  menu.open=!compact.matches;
  compact.addEventListener('change',()=>{menu.open=!compact.matches;});
  const search=reader.querySelector('.guide-search');search.hidden=false;
  const chapters=[...reader.querySelectorAll('[data-guide-chapter]')];
  search.querySelector('input').addEventListener('input',event=>{
   const query=event.target.value.toLocaleLowerCase().trim();
   chapters.forEach(link=>link.hidden=!link.dataset.search.includes(query));
   reader.querySelector('[data-guide-empty]').hidden=chapters.some(link=>!link.hidden);
  });
  const copy=reader.querySelector('[data-guide-copy]');
  if(navigator.clipboard?.writeText){
   copy.hidden=false;copy.addEventListener('click',async()=>{
    const status=reader.querySelector('[data-guide-copy-status]');
    try{await navigator.clipboard.writeText(location.href);copy.textContent='Link copied ✓';status.textContent='Page link copied.';}
    catch(_){status.textContent='Copy the page address from your browser.';}
   });
  }
  const links=[...reader.querySelectorAll('.guide-toc nav a[href^="#"]')];
  const headings=links.map(link=>document.getElementById(decodeURIComponent(link.hash.slice(1)))).filter(Boolean);
  let frame;
  const update=()=>{
   frame=null;let active=headings[0];
   headings.forEach(heading=>{if(heading.getBoundingClientRect().top<=160)active=heading;});
   links.forEach(link=>{if(link.hash==='#'+active?.id)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');});
  };
  window.addEventListener('scroll',()=>{if(!frame)frame=requestAnimationFrame(update);},{passive:true});update();
 };
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
