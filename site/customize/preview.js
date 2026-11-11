"use strict";
/* AXR Stats: static production SVG fixtures, fetched lazily from same-origin.
 * Only fictional test metrics. No OAuth, arbitrary SVG injection or telemetry.
 */
(() => {
  const cards = ["lifetime", "languages", "activity", "ranking", "heatmap", "emblem"];
  const tokens = ["background","surface","outline","text","muted","accent","success"];
  const defaults = Object.freeze({
    background:"#0c1220",surface:"#141e2c",outline:"#2b3a4f",text:"#edf3ff",
    muted:"#a7b6cc",accent:"#5caeff",success:"#54d2a0"
  });
  const image = document.getElementById("theme-preview-image");
  const message = document.getElementById("theme-preview-message");
  const heading = document.getElementById("theme-preview-name");
  const note = document.getElementById("theme-preview-note");
  const download = document.getElementById("download-preview");
  const controls = [...document.querySelectorAll("[data-preview-card]")];
  if (!image || !controls.length) return;
  const labels = {
    lifetime:"Tempo total e evolução", languages:"Linguagens", activity:"Atividade",
    ranking:"Ranking semanal",heatmap:"Calendário de atividade",emblem:"Emblema de rank"
  };
  const descriptions = {
    lifetime:"Horas e progressão fictícias, não dados de uma conta.",
    languages:"Distribuição histórica fictícia gerada pelo Python.",
    activity:"Atividade diária de demonstração.",
    ranking:"A posição #2841 é fictícia, não uma classificação oficial.",
    heatmap:"Horas e datas fictícias, não registros reais.",
    emblem:"Emblema original preservado; estrelas configuráveis."
  };
  const cache = new Map();
  let selected = "lifetime", languageRows = 10, typography = "standard", showStars = true;
  let palette = Object.fromEntries(tokens.map(k => [
    k,document.querySelector('[data-color="' + k + '"]')?.value || defaults[k]
  ]));
  let currentUrl = null, generated = null, requestSerial = 0;
  const isHex = value => /^#[0-9a-f]{6}$/i.test(value);
  function pathFor(card) {
    let stem = card;
    if (card === "languages" && languageRows !== 10) stem += "-" + languageRows;
    if (typography !== "standard") stem += "-type-" + typography;
    if ((card === "lifetime" || card === "emblem") && !showStars) stem += "-no-stars";
    return stem;
  }
  function applyTheme(svg) {
    const lookup = new Map(tokens.map(key => [defaults[key],palette[key]]));
    return svg.replace(/\b(fill|stroke|stop-color)="(#[0-9a-fA-F]{6})"/g,(match,key,value) => {
      const color = lookup.get(value.toLowerCase());
      return color && isHex(color) ? key + '="' + color.toLowerCase() + '"' : match;
    });
  }
  async function loadSVG(stem) {
    if (cache.has(stem)) return cache.get(stem);
    const response = await fetch("previews/" + stem + ".svg",{cache:"force-cache"});
    if (!response.ok) throw Error("HTTP " + response.status);
    const svg = await response.text();
    if (svg.length > 750000) throw Error("SVG exceeds fixture size limit");
    const documentSVG = new DOMParser().parseFromString(svg,"image/svg+xml");
    if (documentSVG.querySelector("parsererror") ||
        documentSVG.documentElement.localName !== "svg" ||
        !documentSVG.documentElement.getAttribute("viewBox")) throw Error("Invalid SVG fixture");
    cache.set(stem,svg);
    return svg;
  }
  async function paint() {
    const serial = ++requestSerial;
    const card = selected;
    const stem = pathFor(card);
    image.setAttribute("aria-busy","true");
    download.disabled = true;
    try {
      const source = await loadSVG(stem);
      if (serial !== requestSerial) return; // stale response after rapid option changes
      const svg = applyTheme(source);
      const nextURL = URL.createObjectURL(new Blob([svg],{type:"image/svg+xml"}));
      const previousURL = currentUrl;
      currentUrl = nextURL;
      generated = svg;
      image.onload = () => {
        if (previousURL) URL.revokeObjectURL(previousURL);
        image.removeAttribute("aria-busy");
        download.disabled = false;
        message.textContent = "Prévia SVG de " + labels[card] + " pronta.";
      };
      image.onerror = () => {
        if (previousURL) URL.revokeObjectURL(previousURL);
        image.removeAttribute("aria-busy");
        message.textContent = "A imagem não pôde ser renderizada.";
      };
      image.alt = labels[card] + " com dados fictícios";
      image.src = nextURL;
    } catch (error) {
      if (serial !== requestSerial) return;
      image.removeAttribute("aria-busy");
      generated = null;
      message.textContent = "Prévia indisponível. Confira o build das amostras SVG.";
      console.warn("AXR preview",error.message);
    }
  }
  function activate(card) {
    if (!cards.includes(card)) return;
    selected = card;
    controls.forEach(button => {
      const active = button.dataset.previewCard === card;
      button.classList.toggle("is-selected",active);
      button.setAttribute("aria-pressed",String(active));
    });
    heading.textContent = labels[card];
    note.textContent = descriptions[card];
    void paint();
  }
  controls.forEach(button => button.addEventListener("click",() => activate(button.dataset.previewCard)));
  window.addEventListener("axr:theme-update",event => {
    const detail = event.detail || {};
    if (!detail.colors || !tokens.every(k => isHex(detail.colors[k]))) return;
    palette = {...detail.colors};
    if ([5,8,10].includes(detail.language_rows)) languageRows = detail.language_rows;
    if (["compact","standard","large"].includes(detail.typography)) typography = detail.typography;
    if (typeof detail.show_rank_stars === "boolean") showStars = detail.show_rank_stars;
    void paint();
  });
  download.addEventListener("click",() => {
    if (!generated) return;
    const url = URL.createObjectURL(new Blob([generated],{type:"image/svg+xml"}));
    const link = document.createElement("a");
    link.href = url;
    link.download = "axr-preview-" + selected + ".svg";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url),1500);
    message.textContent = "Prévia fictícia exportada; não use como estatística pessoal.";
  });
  window.addEventListener("pagehide",() => {
    ++requestSerial;
    if (currentUrl) URL.revokeObjectURL(currentUrl);
  });
  // Workbench's first event fires before this file executes; infer defaults
  // directly from its controls and load just one sample at startup.
  languageRows = Number(document.getElementById("theme-language-rows")?.value || 10);
  typography = document.getElementById("theme-typography")?.value || "standard";
  showStars = document.getElementById("theme-rank-stars")?.checked ?? true;
  activate(selected);
})();
