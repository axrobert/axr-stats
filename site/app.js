"use strict";

const ranks = [
  {
    "name": "Iniciante",
    "hours": 0,
    "image": "01-iniciante.png",
    "note": "O começo da jornada."
  },
  {
    "name": "Aprendiz",
    "hours": 50,
    "image": "02-aprendiz.png",
    "note": "Fundamentos em construção."
  },
  {
    "name": "Estudante",
    "hours": 150,
    "image": "03-estudante.png",
    "note": "A prática vira rotina."
  },
  {
    "name": "Desenvolvedor",
    "hours": 300,
    "image": "04-desenvolvedor.png",
    "note": "Projetos e soluções reais."
  },
  {
    "name": "Especialista",
    "hours": 500,
    "image": "05-especialista.png",
    "note": "Profundidade técnica."
  },
  {
    "name": "Avançado",
    "hours": 800,
    "image": "06-avancado.png",
    "note": "Domínio cada vez maior."
  },
  {
    "name": "Elite",
    "hours": 1200,
    "image": "07-elite.png",
    "note": "Consistência de alto nível."
  },
  {
    "name": "Mestre",
    "hours": 1800,
    "image": "08-mestre.png",
    "note": "Experiência e visão."
  },
  {
    "name": "Arquiteto",
    "hours": 2500,
    "image": "09-arquiteto.png",
    "note": "Estruturas e sistemas complexos."
  },
  {
    "name": "Sábio",
    "hours": 3500,
    "image": "10-sabio.png",
    "note": "Conhecimento que orienta."
  },
  {
    "name": "Lendário",
    "hours": 5000,
    "image": "11-lendario.png",
    "note": "Uma trajetória extraordinária."
  },
  {
    "name": "Soberano",
    "hours": 8000,
    "image": "12-soberano.png",
    "note": "O patamar mais alto desta coleção."
  }
];

const assetPath = (name) => "assets/badges/current/" + name;
const byId = (id) => document.getElementById(id);
const rankGrid = byId("rank-grid");
const search = byId("rank-search");
const rankCount = byId("rank-count");
const dialog = byId("rank-dialog");
let previousFocus = null;

function findRank(hours) {
  const safe = Math.max(0, Math.min(100000, Number.isFinite(hours) ? hours : 0));
  let index = 0;
  ranks.forEach((rank, i) => { if (safe >= rank.hours) index = i; });
  const current = ranks[index];
  const next = ranks[index + 1] || null;
  const progress = next ? (safe - current.hours) / (next.hours - current.hours) : 1;
  return { current, next, index, progress: Math.min(1, Math.max(0, progress)) };
}

function showRank(rank, index) {
  if (!dialog || typeof dialog.showModal !== "function") return;
  previousFocus = document.activeElement;
  byId("dialog-tier").textContent = "TIER " + String(index + 1).padStart(2, "0");
  byId("dialog-art").src = assetPath(rank.image);
  byId("dialog-art").alt = "Emblema do rank " + rank.name;
  byId("dialog-title").textContent = rank.name;
  byId("dialog-details").textContent = rank.note + " Disponível a partir de " +
    rank.hours.toLocaleString("pt-BR") + " horas acumuladas de programação.";
  dialog.showModal();
}

function createRankCard(rank, index) {
  const card = document.createElement("button");
  card.type = "button";
  card.className = "rank-card";
  card.dataset.search = rank.name.toLocaleLowerCase("pt-BR");
  card.setAttribute("aria-label", "Ver detalhes do rank " + rank.name);

  const img = document.createElement("img");
  img.src = assetPath(rank.image);
  img.alt = "";
  img.loading = "lazy";
  img.width = 150;
  img.height = 157;

  const tier = document.createElement("span");
  tier.className = "tier";
  tier.textContent = "TIER " + String(index + 1).padStart(2, "0");

  const label = document.createElement("strong");
  label.textContent = rank.name;

  const minimum = document.createElement("small");
  minimum.textContent = rank.hours.toLocaleString("pt-BR") + " horas";

  card.append(img, tier, label, minimum);
  card.addEventListener("click", () => showRank(rank, index));
  return card;
}

if (rankGrid) {
  ranks.forEach((rank, index) => rankGrid.append(createRankCard(rank, index)));
  const empty = document.createElement("p");
  empty.className = "rank-empty";
  empty.textContent = "Nenhum rank corresponde à sua busca.";
  empty.hidden = true;
  rankGrid.append(empty);

  const updateFilter = () => {
    const query = (search?.value || "").trim().toLocaleLowerCase("pt-BR");
    let count = 0;
    rankGrid.querySelectorAll(".rank-card").forEach((card) => {
      const visible = card.dataset.search.includes(query);
      card.dataset.hidden = String(!visible);
      if (visible) count++;
    });
    empty.hidden = count !== 0;
    if (rankCount) rankCount.textContent = count + (count === 1 ? " rank encontrado" : " ranks encontrados");
  };
  search?.addEventListener("input", updateFilter);
}

const hoursInput = byId("hours-input");
function renderSimulation() {
  if (!hoursInput) return;
  const numeric = Number(hoursInput.value);
  const hours = Number.isFinite(numeric) ? Math.max(0, Math.min(100000, numeric)) : 0;
  const state = findRank(hours);
  const percent = Math.floor(state.progress * 100);

  byId("sim-rank-image").src = assetPath(state.current.image);
  byId("sim-rank-name").textContent = state.current.name;
  byId("sim-next").textContent = state.next
    ? "Próximo: " + state.next.name + " · " + state.next.hours.toLocaleString("pt-BR") + "h"
    : "Patamar máximo desta coleção";
  byId("sim-progress-label").textContent = state.next ? "Progresso até o próximo rank" : "Rank máximo";
  byId("sim-percent").textContent = percent + "%";
  byId("sim-bar").style.width = percent + "%";
  byId("sim-progress").setAttribute("aria-valuenow", String(percent));
}
hoursInput?.addEventListener("input", renderSimulation);
renderSimulation();

byId("close-dialog")?.addEventListener("click", () => dialog?.close());
dialog?.addEventListener("click", (event) => {
  if (event.target === dialog) dialog.close();
});
dialog?.addEventListener("close", () => previousFocus?.focus?.());
byId("dialog-link")?.addEventListener("click", () => dialog?.close());

const menu = document.querySelector(".menu-toggle");
const nav = byId("main-nav");
menu?.addEventListener("click", () => {
  const open = menu.getAttribute("aria-expanded") !== "true";
  menu.setAttribute("aria-expanded", String(open));
  menu.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
  nav?.classList.toggle("open", open);
});
nav?.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => {
  nav.classList.remove("open");
  menu?.setAttribute("aria-expanded", "false");
  menu?.setAttribute("aria-label", "Abrir menu");
}));

const slides = [
  {
    headline: ["Seu código merece", "reconhecimento."],
    description: "Transforme suas horas de programação em uma jornada visual com estatísticas, emblemas e níveis próprios.",
    action: "Conheça os ranks",
    target: "#ranks",
    image: "08-mestre.png"
  },
  {
    headline: ["Seus dados contam", "uma história."],
    description: "Linguagens, atividade e progresso registrados pelo WakaTime, com visual personalizado e sem pontuações inventadas.",
    action: "Explorar os cards",
    target: "#cards",
    image: "03-estudante.png"
  },
  {
    headline: ["Um perfil único.", "Do seu jeito."],
    description: "Projeto aberto para aprender, experimentar, colaborar e construir uma identidade visual para desenvolvedores.",
    action: "Ver o guia",
    target: "docs/installation/",
    image: "12-soberano.png"
  },
];
let slideIndex = 0;

function selectSlide(index) {
  slideIndex = (index + slides.length) % slides.length;
  const slide = slides[slideIndex];
  const title = byId("hero-title");
  const typed=document.createElement("span");
  typed.textContent=slide.headline[1];
  title.replaceChildren(
    document.createTextNode(slide.headline[0]),
    document.createElement("br"),
    typed
  );
  window.AXRUI?.typeHeadline?.(typed,slide.headline[1]);
  byId("hero-description").textContent = slide.description;
  const action = byId("hero-action");
  action.href = slide.target;
  action.replaceChildren(
    document.createTextNode(slide.action + " "),
    Object.assign(document.createElement("span"), { textContent: "↗" })
  );
  const medal=byId("hero-medal");
  medal.classList.add("is-changing");
  const settle=()=>medal.classList.remove("is-changing");
  medal.addEventListener("load",settle,{once:true});
  medal.addEventListener("error",settle,{once:true});
  medal.src=assetPath(slide.image);
  if(medal.complete)settle();
  byId("hero-counter").textContent = String(slideIndex + 1).padStart(2, "0") + " / " + String(slides.length).padStart(2, "0");
  document.querySelectorAll(".slide-dot").forEach((dot, idx) => {
    dot.classList.toggle("selected", idx === slideIndex);
    if (idx === slideIndex) dot.setAttribute("aria-current", "true");
    else dot.removeAttribute("aria-current");
  });
}
byId("prev-slide")?.addEventListener("click", () => selectSlide(slideIndex - 1));
byId("next-slide")?.addEventListener("click", () => selectSlide(slideIndex + 1));
document.querySelectorAll(".slide-dot").forEach((dot) => {
  dot.addEventListener("click", () => selectSlide(Number(dot.dataset.slide)));
});

// One deliberate typing moment on entry; the carousel keeps the same animation.
window.addEventListener("DOMContentLoaded",()=>{
  const span=document.querySelector("#hero-title span");
  if(span)window.AXRUI?.typeHeadline?.(span,span.textContent);
},{once:true});
