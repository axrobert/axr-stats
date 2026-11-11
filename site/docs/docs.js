"use strict";

/* Search indexes only public static documentation text; no network credentials or telemetry. */
const searchInput = document.querySelector("#docs-search");
const results = document.querySelector("#docs-results");
const base = document.documentElement.dataset.base || "../../";
const fallback = [
  {title:"Visão geral",href:"docs/",description:"O que é o AXR Stats"},
  {title:"Instalação",href:"docs/installation/",description:"OAuth, secrets e workflow"},
  {title:"Configuração",href:"docs/configuration/",description:"Temas, fuso e saída"},
  {title:"Cards e métricas",href:"docs/cards/",description:"Fontes dos dados"},
  {title:"Ranks e progressão",href:"docs/ranks/",description:"Horas e emblemas"},
  {title:"Segurança",href:"docs/security/",description:"Privacidade e credenciais"},
  {title:"Perguntas frequentes",href:"docs/faq/",description:"Dúvidas e diagnósticos"},
  {title:"Roadmap",href:"docs/roadmap/",description:"Etapas de desenvolvimento"}
];
let pages = fallback;
let activeResult = -1;
let links = [];
const normalize = text => String(text||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLocaleLowerCase("pt-BR");
const escapeWhitespace = text => String(text||"").replace(/\s+/g," ").trim();

async function loadIndex() {
  if (!searchInput) return;
  const script = document.querySelector('script[src$="docs.js"]');
  if (!script) return;
  const url = new URL("search-index.json", script.src);
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error("Static search index unavailable");
    const data = await response.json();
    if (data?.version !== 1 || !Array.isArray(data.pages)) throw new Error("Invalid documentation index");
    pages = data.pages.filter(p => typeof p.href === "string" && p.href.startsWith("docs/"));
    if (!pages.length) pages = fallback;
  } catch {
    pages = fallback;
  }
  if (searchInput.value) renderResults(searchInput.value);
}

function excerpt(text, tokens) {
  const value = escapeWhitespace(text);
  const folded = normalize(value);
  const pos = Math.max(0, folded.indexOf(tokens[0] || ""));
  const start = Math.max(0, pos - 58);
  const out = value.slice(start, start + 155);
  return (start ? "…" : "") + out + (start + 155 < value.length ? "…" : "");
}

function matchPage(page, tokens) {
  const title = page.title || "";
  const description = page.description || "";
  const sections = Array.isArray(page.sections) ? page.sections : [];
  const haystack = normalize([title,description,...sections.map(s=>s.title+" "+s.text)].join(" "));
  if (!tokens.every(token => haystack.includes(token))) return null;
  const best = sections.find(s=>tokens.some(token=>normalize(s.title+" "+s.text).includes(token)));
  return {
    title,
    detail: best?.title || description,
    description: excerpt(best?.text || description, tokens),
    href: page.href + (best?.id ? "#"+encodeURIComponent(best.id) : ""),
    score: tokens.reduce((total,t)=>total+(normalize(title).includes(t)?5:0)+(normalize(best?.title).includes(t)?3:0),0)
  };
}

function setActive(index) {
  activeResult = index;
  links.forEach((link,i)=>{
    link.classList.toggle("is-active",i===index);
    link.setAttribute("aria-selected", String(i===index));
  });
  if (index>=0) {
    searchInput?.setAttribute("aria-activedescendant", links[index].id);
    links[index]?.scrollIntoView({block:"nearest"});
  } else searchInput?.removeAttribute("aria-activedescendant");
}

function renderResults(value) {
  if (!results) return;
  const tokens=normalize(value).trim().split(/\s+/).filter(Boolean);
  results.replaceChildren();
  links=[];
  activeResult=-1;
  searchInput?.removeAttribute("aria-activedescendant");
  if (!tokens.length) {
    results.classList.remove("open");
    searchInput?.setAttribute("aria-expanded","false");
    return;
  }

  const matches=pages.map(p=>matchPage(p,tokens)).filter(Boolean)
    .sort((a,b)=>b.score-a.score).slice(0,8);
  if (!matches.length) {
    const empty=document.createElement("p");
    empty.className="docs-search-empty";
    empty.textContent="Nenhum resultado. Tente outra palavra-chave.";
    results.append(empty);
  }
  matches.forEach((hit,i)=>{
    const link=document.createElement("a");
    link.id="docs-result-"+i;
    link.href=base+hit.href;
    link.setAttribute("role","option");
    link.setAttribute("aria-selected","false");
    const heading=document.createElement("strong");
    heading.textContent=hit.title;
    const meta=document.createElement("span");
    meta.textContent=hit.detail;
    const body=document.createElement("small");
    body.textContent=hit.description;
    link.append(heading,meta,body);
    results.append(link);
    links.push(link);
  });
  results.classList.add("open");
  searchInput?.setAttribute("aria-expanded","true");
}

searchInput?.addEventListener("input",()=>renderResults(searchInput.value));
searchInput?.addEventListener("keydown",event=>{
  if (event.key==="Escape") {
    searchInput.value="";
    renderResults("");
    searchInput.blur();
  }
  if (event.key==="ArrowDown"||event.key==="ArrowUp") {
    if (!links.length) return;
    event.preventDefault();
    setActive((activeResult+(event.key==="ArrowDown"?1:-1)+links.length)%links.length);
  }
  if (event.key==="Enter"&&activeResult>=0&&links[activeResult]) {
    event.preventDefault();
    links[activeResult].click();
  }
});
document.addEventListener("click",event=>{
  if(!event.target.closest(".docs-searchbox")){
    results?.classList.remove("open");
    searchInput?.setAttribute("aria-expanded","false");
  }
});

document.querySelectorAll(".copy-code").forEach(btn=>btn.addEventListener("click",async()=>{
  const code=btn.parentElement.querySelector("code");
  if(!code) return;
  const original=btn.textContent;
  try {
    await navigator.clipboard.writeText(code.textContent);
    btn.textContent="Copiado!";
  } catch {
    btn.textContent="Selecione o texto";
  }
  window.setTimeout(()=>btn.textContent=original,1300);
}));

const mobileButton=document.querySelector(".docs-mobile-nav");
const side=document.querySelector(".docs-sidebar");
mobileButton?.addEventListener("click",()=>{
  const open=mobileButton.getAttribute("aria-expanded")!=="true";
  mobileButton.setAttribute("aria-expanded",String(open));
  side?.classList.toggle("open",open);
});
side?.querySelectorAll("a").forEach(a=>a.addEventListener("click",()=>{
  side.classList.remove("open");
  mobileButton?.setAttribute("aria-expanded","false");
}));
loadIndex();
