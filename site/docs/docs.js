"use strict";
const searchInput = document.querySelector("#docs-search");
const results = document.querySelector("#docs-results");
const pages = [
  {title:"Visão geral",description:"O que é o AXR Stats",href:"docs/"},
  {title:"Instalação",description:"OAuth, secrets, workflow e testes",href:"docs/installation/"},
  {title:"Configuração",description:"Temas, fuso e saída",href:"docs/configuration/"},
  {title:"Cards e métricas",description:"Fonte dos dados e parâmetros",href:"docs/cards/"},
  {title:"Ranks e progressão",description:"Horas acumuladas e emblemas",href:"docs/ranks/"},
  {title:"Segurança",description:"Boas práticas para credenciais",href:"docs/security/"},
  {title:"Perguntas frequentes",description:"Diagnóstico dos erros comuns",href:"docs/faq/"},
  {title:"Roadmap",description:"Etapas e limitações do beta",href:"docs/roadmap/"}
];
const base = document.documentElement.dataset.base || "../../";
function renderResults(value) {
  if (!results) return;
  const term = (value || "").trim().toLocaleLowerCase("pt-BR");
  results.replaceChildren();
  if (!term) { results.classList.remove("open"); return; }
  const matches = pages.filter(p=>(p.title+" "+p.description).toLocaleLowerCase("pt-BR").includes(term));
  if (!matches.length) {
    const item = document.createElement("span");
    item.textContent = "Nenhum resultado encontrado.";
    results.append(item);
  }
  for (const page of matches) {
    const a = document.createElement("a");
    a.href = base+page.href;
    const title = document.createElement("strong");
    title.textContent = page.title;
    const description = document.createElement("span");
    description.textContent = page.description;
    a.append(title,description);
    results.append(a);
  }
  results.classList.add("open");
}
searchInput?.addEventListener("input",()=>renderResults(searchInput.value));
searchInput?.addEventListener("keydown",ev=>{if(ev.key==="Escape"){searchInput.value="";renderResults("");searchInput.blur();}});
document.addEventListener("click",ev=>{if(!ev.target.closest(".docs-searchbox"))results?.classList.remove("open");});
document.querySelectorAll(".copy-code").forEach(btn=>btn.addEventListener("click",async()=>{
  const code=btn.parentElement.querySelector("code");
  if(!code)return;
  const original=btn.textContent;
  try{
    await navigator.clipboard.writeText(code.textContent);
    btn.textContent="Copiado!";
    setTimeout(()=>btn.textContent=original,1200);
  }catch{
    btn.textContent="Selecione o texto";
    setTimeout(()=>btn.textContent=original,1600);
  }
}));
const mobileButton=document.querySelector(".docs-mobile-nav");
const side=document.querySelector(".docs-sidebar");
mobileButton?.addEventListener("click",()=>{
  const active=mobileButton.getAttribute("aria-expanded")!=="true";
  mobileButton.setAttribute("aria-expanded",String(active));
  side?.classList.toggle("open",active);
});
