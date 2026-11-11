"use strict";
// Shared UX for static GitHub Pages: no telemetry, no dependencies, no credential collection.
(() => {
  const root=document.documentElement;
  const base=root.dataset.base||"";
  const reduce=window.matchMedia("(prefers-reduced-motion: reduce)");
  const iconHref=base+"icons/lucide.svg#";
  const icon=(name)=>{const svg=document.createElementNS("http://www.w3.org/2000/svg","svg");svg.classList.add("ui-icon");svg.setAttribute("aria-hidden","true");const use=document.createElementNS("http://www.w3.org/2000/svg","use");use.setAttribute("href",iconHref+name);svg.append(use);return svg};
  document.querySelectorAll("[data-icon]").forEach(node=>{const name=node.dataset.icon;if(!name)return;node.replaceChildren(icon(name))});
  const progress=document.createElement("div");progress.className="ui-progress";progress.setAttribute("aria-hidden","true");document.body.append(progress);
  const top=document.createElement("button");top.type="button";top.className="ui-back-top";top.setAttribute("aria-label","Voltar ao topo");top.append(icon("arrow-up"));document.body.append(top);
  top.addEventListener("click",()=>window.scrollTo({top:0,behavior:reduce.matches?"instant":"smooth"}));
  let scrollPending=false;
  function onScroll(){if(scrollPending)return;scrollPending=true;requestAnimationFrame(()=>{const doc=document.documentElement;const max=Math.max(1,doc.scrollHeight-doc.clientHeight);const fraction=Math.min(1,Math.max(0,doc.scrollTop/max));progress.style.width=(fraction*100).toFixed(2)+"%";top.classList.toggle("is-visible",doc.scrollTop>390);document.querySelector(".site-header")?.classList.toggle("is-scrolled",doc.scrollTop>20);scrollPending=false})}
  addEventListener("scroll",onScroll,{passive:true});addEventListener("resize",onScroll,{passive:true});onScroll();
  // Reveals are opt-in, and the page stays fully visible without JS or with reduced motion.
  const revealTargets=document.querySelectorAll("[data-reveal]");
  if(!reduce.matches&&"IntersectionObserver"in window){
    const observer=new IntersectionObserver((entries)=>{for(const e of entries)if(e.isIntersecting){e.target.classList.add("is-revealed");observer.unobserve(e.target)}},{threshold:.07,rootMargin:"0px 0px -22px 0px"});
    revealTargets.forEach(n=>observer.observe(n));root.classList.add("js-motion");
  }else revealTargets.forEach(n=>n.classList.add("is-revealed"));
  // Keep complete, accessible headline text in the DOM except during the short animated transition.
  let typingToken=0;
  function typeHeadline(node,value,{initial=false}={}){
    if(!node)return;
    const token=++typingToken;
    node.dataset.typing="";
    node.setAttribute("aria-label",value);
    if(reduce.matches||document.hidden){node.textContent=value;node.classList.remove("is-typing");return;}
    // Avoid flash of empty text on first load: type only when a carousel slide changes.
    if(initial){node.textContent=value;return;}
    node.classList.add("is-typing");node.textContent="";
    let start=null;
    const tick=(now)=>{if(token!==typingToken)return;if(start===null)start=now;const count=Math.min(value.length,Math.floor((now-start)/34));node.textContent=value.slice(0,count);if(count<value.length)requestAnimationFrame(tick);else node.classList.remove("is-typing")};
    requestAnimationFrame(tick);
  }
  window.AXRUI={icon,typeHeadline,reduceMotion:()=>reduce.matches};
  const toc=[...document.querySelectorAll(".docs-toc a[href^='#']")];
  if(toc.length&&"IntersectionObserver"in window){
    const map=new Map(toc.map(a=>[a.hash, a]));
    const targets=[...map.keys()].map(h=>document.getElementById(h.slice(1))).filter(Boolean);
    const view=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting){toc.forEach(a=>a.removeAttribute("aria-current"));map.get("#"+e.target.id)?.setAttribute("aria-current","location")}}, {rootMargin:"-115px 0px -68% 0px",threshold:0});
    targets.forEach(t=>view.observe(t));
  }
  // Search shortcut is opt-in: only within docs, and never hijacks text inputs.
  document.addEventListener("keydown",e=>{
    if(!document.getElementById("docs-search"))return;
    const active=document.activeElement;
    const typing=active&&(/input|textarea/i.test(active.tagName)||active.isContentEditable);
    if((e.key==="/"&&!typing)||((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==="k")){
      e.preventDefault();document.getElementById("docs-search").focus();
    }
  });
})();
