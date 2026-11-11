"use strict";
/* AXR Stats Phase 2.1 — render real production SVG templates, fictional data.
 * No credentials, no stats API, no injected markup and no third-party service.
 */
(() => {
  const cardTypes = ["lifetime", "languages", "activity", "ranking", "heatmap", "emblem"];
  const tokens = ["background", "surface", "outline", "text", "muted", "accent", "success"];
  // Canonical production defaults (src/axr_stats.py), not browser-invented colors.
  const defaults = Object.freeze({
    background:"#0c1220", surface:"#141e2c", outline:"#2b3a4f",
    text:"#edf3ff", muted:"#a7b6cc", accent:"#5caeff", success:"#54d2a0"
  });
  const files = new Map();
  const image = document.getElementById("theme-preview-image");
  const message = document.getElementById("theme-preview-message");
  const heading = document.getElementById("theme-preview-name");
  const note = document.getElementById("theme-preview-note");
  const download = document.getElementById("download-preview");
  const controls = [...document.querySelectorAll("[data-preview-card]")];
  if (!image || !controls.length) return;
  let selected = "lifetime";
  let languageRows = 10;
  let currentUrl = null;
  let generated = null;
  let frame = 0;
  let palette = {};
  const isHex = value => /^#[0-9a-f]{6}$/i.test(value);
  const labelMap = {
    lifetime:"Tempo total e evolução",
    languages:"Linguagens",
    activity:"Atividade",
    ranking:"Ranking semanal",
    heatmap:"Calendário de atividade",
    emblem:"Emblema de rank"
  };
  const infoMap = {
    lifetime:"Horários e rank de demonstração, não dados de uma conta.",
    languages:"Distribuição histórica fictícia, gerada pelo backend Python.",
    activity:"Indicador diário de demonstração.",
    ranking:"A posição #2841 é fictícia, não uma classificação oficial.",
    heatmap:"Datas e horas de demonstração, não registros de usuários.",
    emblem:"Emblema original embutido pelo gerador, sem recoloração da arte."
  };

  function currentPalette() {
    return Object.fromEntries(tokens.map(key => [
      key, document.querySelector('[data-color="' + key + '"]')?.value || defaults[key]
    ]));
  }

  // Only change valid SVG fill/stroke attributes whose values exactly match
  // declared production theme tokens. Leave rank artwork and extra heatmap
  // intensity stops unchanged, just as the Python config does.
  function themeSvg(svg, colors) {
    const lookup = new Map(tokens.map(key => [defaults[key], colors[key]]));
    return svg.replace(/\b(fill|stroke|stop-color)="(#[0-9a-fA-F]{6})"/g,
      (attribute, name, value) => {
        const replacement = lookup.get(value.toLowerCase());
        return replacement && isHex(replacement)
          ? name + '="' + replacement.toLowerCase() + '"'
          : attribute;
      });
  }

  function activate(name) {
    if (!cardTypes.includes(name)) return;
    selected = name;
    controls.forEach(button => {
      const active = button.dataset.previewCard === selected;
      button.classList.toggle("is-selected", active);
      button.setAttribute("aria-pressed", String(active));
    });
    heading.textContent = labelMap[selected];
    note.textContent = infoMap[selected];
    paint();
  }

  function paint() {
    const key = selected === "languages" && languageRows !== 10
      ? "languages-" + languageRows : selected;
    if (!files.has(key)) return;
    const text = themeSvg(files.get(key), palette);
    generated = text;
    const url = URL.createObjectURL(new Blob([text], {type:"image/svg+xml"}));
    const old = currentUrl;
    currentUrl = url;
    image.onload = () => {
      if (old) URL.revokeObjectURL(old);
      image.removeAttribute("aria-busy");
      message.textContent = "Prévia SVG de " + labelMap[selected] + " pronta.";
    };
    image.onerror = () => {
      if (old) URL.revokeObjectURL(old);
      image.removeAttribute("aria-busy");
      message.textContent = "Não foi possível renderizar este SVG.";
    };
    image.setAttribute("aria-busy", "true");
    image.alt = "Card " + labelMap[selected] + " com dados fictícios";
    image.src = url;
    download.disabled = false;
  }

  controls.forEach(button => button.addEventListener("click", () => activate(button.dataset.previewCard)));
  window.addEventListener("axr:theme-update", event => {
    const colors = event.detail?.colors;
    if (!colors || !tokens.every(key => isHex(colors[key]))) return;
    palette = {...colors};
    if ([5,8,10].includes(event.detail?.language_rows)) {
      languageRows = event.detail.language_rows;
    }
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(paint);
  });

  download.addEventListener("click", () => {
    if (!generated) return;
    const blob = new Blob([generated], {type:"image/svg+xml"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "axr-preview-" + selected + ".svg";
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1500);
    message.textContent = "Prévia fictícia exportada; não use como estatística pessoal.";
  });

  palette = currentPalette();
  const templates = [...cardTypes,"languages-5","languages-8"];
  Promise.all(templates.map(async name => {
    const response = await fetch("previews/" + name + ".svg", {cache:"no-cache"});
    if (!response.ok) throw new Error(name + ": HTTP " + response.status);
    const svg = await response.text();
    const parsed = new DOMParser().parseFromString(svg, "image/svg+xml");
    if (parsed.querySelector("parsererror") ||
        parsed.documentElement.localName !== "svg" ||
        !parsed.documentElement.getAttribute("viewBox")) {
      throw new Error(name + ": SVG malformado");
    }
    files.set(name, svg);
  })).then(() => {
    message.textContent = "Seis cards e duas variações de densidade carregados. Dados demonstrativos.";
    activate(selected);
  }).catch(error => {
    // Don't expose raw error details in the UI; local dev without generated
    // fixtures should see a useful instruction, rather than an empty preview.
    message.textContent = "Prévia indisponível. Gere os exemplos com scripts/generate_preview_cards.py.";
    download.disabled = true;
    console.warn("AXR previews:", error.message);
  });
  window.addEventListener("pagehide", () => {
    cancelAnimationFrame(frame);
    if (currentUrl) URL.revokeObjectURL(currentUrl);
  });
})();
