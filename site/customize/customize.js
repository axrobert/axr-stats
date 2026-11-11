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
  const canvas = $("#theme-card");
  const output = $("#theme-json");
  const status = $("#theme-feedback");

  function redraw() {
    for (const key of keys) {
      canvas.style.setProperty("--preview-" + key, palette[key]);
      const color = document.querySelector('[data-color="' + key + '"]');
      const hex = document.querySelector('[data-hex="' + key + '"]');
      if (color) color.value = palette[key];
      if (hex && document.activeElement !== hex) hex.value = palette[key];
    }
    const cfg = { theme, colors: {...palette} };
    output.textContent = JSON.stringify(cfg, null, 2);
    window.dispatchEvent(new CustomEvent("axr:theme-update", {detail:{theme, colors:{...palette}}}));
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