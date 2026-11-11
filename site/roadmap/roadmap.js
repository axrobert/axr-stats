"use strict";

// AXR Stats: bespoke roadmap interactions. The markup works without JavaScript.
(() => {
  const buttons = [...document.querySelectorAll("[data-rm-filter]")];
  const items = [...document.querySelectorAll("[data-rm-status]")];
  const notice = document.getElementById("rm-filter-feedback");
  const menu = document.querySelector(".menu-toggle");
  const nav = document.getElementById("main-nav");

  function setFilter(value, { announce = true } = {}) {
    const filter = ["all", "done", "active", "planned"].includes(value) ? value : "all";
    let count = 0;
    for (const item of items) {
      const visible = filter === "all" || item.dataset.rmStatus === filter;
      item.hidden = !visible;
      if (visible) count++;
    }
    buttons.forEach(button => {
      const selected = button.dataset.rmFilter === filter;
      button.classList.toggle("is-selected", selected);
      button.setAttribute("aria-pressed", String(selected));
    });
    if (notice && announce) {
      const label = count === 1 ? "fase" : "fases";
      notice.textContent = "Exibindo " + count + " " + label + ".";
    }
  }

  buttons.forEach(button => button.addEventListener("click", () => setFilter(button.dataset.rmFilter)));

  // Following a path node always reveals its matching phase, regardless of filter.
  document.querySelectorAll('.rm-map-stage a[href^="#fase-"]').forEach(link => {
    link.addEventListener("click", () => setFilter("all", { announce: true }));
  });

  // Native anchors + a tiny entrance animation, not a scroll-jacking timeline.
  const reduce = matchMedia("(prefers-reduced-motion: reduce)");
  const map = document.querySelector(".rm-map");
  if (map && !reduce.matches && "IntersectionObserver" in window) {
    map.classList.add("rm-map--ready");
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          map.classList.add("rm-map--visible");
          observer.disconnect();
        }
      }
    }, { threshold: 0.12 });
    observer.observe(map);
  }

  menu?.addEventListener("click", () => {
    const expanded = menu.getAttribute("aria-expanded") !== "true";
    menu.setAttribute("aria-expanded", String(expanded));
    menu.setAttribute("aria-label", expanded ? "Fechar menu" : "Abrir menu");
    nav?.classList.toggle("open", expanded);
  });
  nav?.querySelectorAll("a").forEach(link => link.addEventListener("click", () => {
    nav.classList.remove("open");
    menu?.setAttribute("aria-expanded", "false");
    menu?.setAttribute("aria-label", "Abrir menu");
  }));

  // Deep-linking works even if someone filters then navigates back.
  addEventListener("hashchange", () => {
    if (location.hash.startsWith("#fase-")) setFilter("all");
  });
  setFilter("all", { announce: false });
})();
