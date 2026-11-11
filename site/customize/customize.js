"use strict";
// AXR Stats Theme Workbench — no telemetry, authentication or external dependencies.
(() => {
  const presets = {
    midnight: {background:"#0C1220",surface:"#141E2C",outline:"#2B3A4F",text:"#EDF3FF",muted:"#A7B6CC",accent:"#5CAEFF",success:"#54D2A0"},
    graphite: {background:"#111317",surface:"#1B2027",outline:"#353D48",text:"#F1F5F9",muted:"#A3ADB9",accent:"#C3A7FF",success:"#58D7B0"},
    aurora: {background:"#0A171B",surface:"#10262B",outline:"#275056",text:"#EAFFFB",muted:"#A8CCCB",accent:"#5DE2C5",success:"#C3EF8E"}
  };
  const keys = Object.keys(presets.midnight);
  const $ = sel => document.querySelector(sel);
  let theme = "midnight";
  let palette = {...presets.midnight};
  const valid = value => /^#[a-f\d]{6}$/i.test(value);
  const output = $("#theme-json");
  const status = $("#theme-feedback");
  const cardIds = ["lifetime","languages","activity","ranking","heatmap","emblem"];
  const cardNames = {lifetime:"Tempo total e progressão",languages:"Linguagens",activity:"Atividade diária",ranking:"Ranking público WakaTime",heatmap:"Calendário de atividade",emblem:"Emblema do rank"};
  const widths = {compact:500,standard:700,large:850};
  const pairWidths = {compact:250,standard:350,large:420};
  const checkbox = id => document.querySelector('[data-include-card="' + id + '"]');
  const currentCards = () => cardIds.filter(id => checkbox(id)?.checked);
  const languageRows = () => Number($("#theme-language-rows").value);
  const typography = () => $("#theme-typography").value;
  const showRankStars = () => $("#theme-rank-stars").checked;
  const headerStyle = () => $("#theme-header-style").value;
  const previewFile = card => {
    let name = card;
    if (card === "languages" && languageRows() !== 10) name += "-" + languageRows();
    if (typography() !== "standard") name += "-type-" + typography();
    if ((card === "lifetime" || card === "emblem") && !showRankStars()) name += "-no-stars";
    if (headerStyle() === "minimal") name += "-header-minimal";
    return name + ".svg";
  };
  const selectionFeedback = $("#theme-selection-feedback");
  const readmeCode = $("#theme-readme-code");
  const readmePreview = $("#theme-readme-preview");
  let lastCards = cardIds.slice();
  let lastReadme = "";
  const escapeAttr = text => text.replaceAll("&","&amp;").replaceAll('"',"&quot;").replaceAll("<","&lt;");
  const imageMarkup = (card,width) => '<img src="assets/axr-stats/' + card + '.svg" alt="AXR Stats — ' + escapeAttr(cardNames[card]) + '" width="' + width + '">';
  function snippet(cards,layout,size) {
    const lines = [
      "<!-- AXR Stats: copie este trecho para o README do seu perfil. -->",
      "<!-- Referências relativas à raiz do repositório; nenhum dado é fictício aqui. -->"
    ];
    if (layout === "stacked") cards.forEach(card => lines.push('<p align="center">' + imageMarkup(card,widths[size]) + '</p>'));
    else {
      lines.push("<table>");
      for(let index=0;index<cards.length;index+=2) {
        lines.push("<tr>");
        for(const card of cards.slice(index,index+2)) lines.push('<td align="center">' + imageMarkup(card,pairWidths[size]) + '</td>');
        lines.push("</tr>");
      }
      lines.push("</table>");
    }
    return lines.join("\n") + "\n";
  }
  function redrawReadme(cards,layout,size) {
    lastReadme=snippet(cards,layout,size);
    readmeCode.textContent=lastReadme;
    // Build real DOM nodes, never inject raw string markup into the document.
    readmePreview.replaceChildren();
    readmePreview.classList.toggle("is-paired",layout==="paired");
    cards.forEach(card=>{
      const figure=document.createElement("figure");
      const picture=document.createElement("img");
      picture.src="previews/"+previewFile(card);
      picture.alt=cardNames[card]+" — demonstração fictícia";
      picture.loading="lazy";
      picture.style.maxWidth=(layout==="paired"?pairWidths[size]:widths[size])+"px";
      const caption=document.createElement("figcaption");
      caption.textContent=cardNames[card];
      figure.append(picture,caption);
      readmePreview.append(figure);
    });
  }
  function selectedState() {
    const chosen=currentCards();
    if (!chosen.length) {
      const fallback=lastCards.at(-1)||"lifetime";
      checkbox(fallback).checked=true;
      selectionFeedback.textContent="Selecione pelo menos um card.";
      return lastCards.slice();
    }
    selectionFeedback.textContent=chosen.length+" de 6 cards selecionados para publicação.";
    lastCards=chosen;
    return chosen;
  }

  function redraw() {
    for (const key of keys) {
      const color = document.querySelector('[data-color="' + key + '"]');
      const hex = document.querySelector('[data-hex="' + key + '"]');
      if (color) color.value = palette[key];
      if (hex && document.activeElement !== hex) hex.value = palette[key];
    }
    const selected = selectedState();
    const layout = $("#theme-layout").value;
    const size = $("#theme-size").value;
    const cfg = { theme, colors: {...palette}, cards:selected, layout, size,
      language_rows:languageRows(), typography:typography(), show_rank_stars:showRankStars(),
      header_style:headerStyle() };
    redrawReadme(selected,layout,size);
    output.textContent = JSON.stringify(cfg, null, 2);
    window.dispatchEvent(new CustomEvent("axr:theme-update", {detail:{theme, colors:{...palette}, language_rows:languageRows(),
      typography:typography(), show_rank_stars:showRankStars(), header_style:headerStyle()}}));
  }

  document.querySelectorAll("[data-theme]").forEach(button => button.addEventListener("click", () => {
    theme = button.dataset.theme;
    palette = {...presets[theme]};
    document.querySelectorAll("[data-theme]").forEach(item => {
      const selected = item === button;
      item.classList.toggle("is-selected", selected);
      item.setAttribute("aria-pressed", String(selected));
    });
    redraw();
  }));
  document.querySelectorAll("[data-color]").forEach(input => input.addEventListener("input", () => {
    palette[input.dataset.color] = input.value.toUpperCase();
    redraw();
  }));
  document.querySelectorAll("[data-hex]").forEach(input => {
    input.addEventListener("input", () => {
      if (!valid(input.value)) { input.setAttribute("aria-invalid","true"); return; }
      input.removeAttribute("aria-invalid");
      palette[input.dataset.hex] = input.value.toUpperCase();
      redraw();
    });
    input.addEventListener("blur", () => {
      if (!valid(input.value)) { input.value = palette[input.dataset.hex]; input.removeAttribute("aria-invalid"); }
    });
  });

  document.querySelectorAll("[data-include-card]").forEach(input => input.addEventListener("change", redraw));
  $("#theme-layout").addEventListener("change", redraw);
  $("#theme-size").addEventListener("change", redraw);
  $("#theme-language-rows").addEventListener("change", redraw);
  $("#theme-typography").addEventListener("change", redraw);
  $("#theme-header-style").addEventListener("change", redraw);
  $("#theme-rank-stars").addEventListener("change", redraw);
  $("#copy-readme").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(lastReadme); status.textContent="Snippet do README copiado."; }
    catch { status.textContent="Cópia indisponível. Selecione o snippet acima."; }
  });
  $("#copy-theme").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(output.textContent); status.textContent = "JSON copiado."; }
    catch { status.textContent = "Cópia indisponível. Selecione o JSON acima."; }
  });
  $("#download-theme").addEventListener("click", () => {
    const blob = new Blob([output.textContent + "\n"], {type:"application/json;charset=utf-8"});
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url; link.download = "axr-stats.json"; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1500);
    status.textContent = "Arquivo axr-stats.json preparado.";
  });

  const menu = $(".menu-toggle");
  const nav = $("#main-nav");
  menu?.addEventListener("click", () => {
    const opened = menu.getAttribute("aria-expanded") !== "true";
    menu.setAttribute("aria-expanded", String(opened));
    nav?.classList.toggle("open", opened);
  });
  nav?.querySelectorAll("a").forEach(link => link.addEventListener("click", () => {
    nav.classList.remove("open"); menu?.setAttribute("aria-expanded", "false");
  }));
  redraw();
})();