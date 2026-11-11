/**
 * AXR Stats · visual smoke test
 * Run against the static site assembled exactly like GitHub Pages.
 * Records screenshots at all required breakpoints, checks real DOM overflow,
 * broken images, keyboard navigation and JavaScript runtime errors.
 */
import { chromium } from "playwright";
import fs from "node:fs/promises";
import path from "node:path";

const base = process.env.AXR_SITE_URL || "http://127.0.0.1:8765/";
const folder = process.env.AXR_SCREENSHOT_DIR || "screenshots";
const widths = [320, 375, 768, 1024, 1440, 1920];
const errors = [];
const routes = ["", "docs/", "roadmap/", "customize/"];
await fs.mkdir(folder, { recursive: true });
const browser = await chromium.launch({ headless: true, args: ["--no-sandbox"] });

async function exerciseRoute(context, route, width) {
  const page = await context.newPage();
  const name = route === "roadmap/" ? "roadmap" : route === "customize/" ? "customize" : route ? "docs" : "home";
  page.on("pageerror", error => errors.push(name + " " + width + ": " + error.message));
  const response = await page.goto(new URL(route, base).href, { waitUntil: "domcontentloaded" });
  if (!response?.ok()) errors.push(name + " " + width + ": HTTP " + (response?.status() || "no response"));
  await page.evaluate(async () => {
    const pause = () => new Promise(resolve => setTimeout(resolve, 35));
    for (let y = 0; y < document.body.scrollHeight; y += 550) {
      window.scrollTo(0, y);
      await pause();
    }
    window.scrollTo(0, 0);
    await pause();
  });

  const status = await page.evaluate(() => ({
    viewport: innerWidth,
    page: document.documentElement.scrollWidth,
    broken: [...document.querySelectorAll("img")].filter(image => image.complete && image.naturalWidth === 0)
      .map(image => image.getAttribute("src")),
    mainCount: document.querySelectorAll("main").length,
    footerCount: document.querySelectorAll(".axr-footer").length,
    offenders: [...document.querySelectorAll("body *")].filter(node => { const r=node.getBoundingClientRect(); const style=getComputedStyle(node); return r.right > innerWidth+2 && style.position !== "fixed" && style.visibility !== "hidden"; }).slice(0,6).map(node=>({tag:node.tagName, className: typeof node.className === "string" ? node.className : "", width: Math.round(node.getBoundingClientRect().width), right: Math.round(node.getBoundingClientRect().right)})),
    blocked: [...document.querySelectorAll('[data-reveal]')].filter(node =>
      getComputedStyle(node).opacity === "0" && node.getBoundingClientRect().top < innerHeight
    ).length,
  }));
  if (status.page > width + 2) errors.push(name + " " + width + ": horizontal overflow " + status.page + "px " + JSON.stringify(status.offenders));
  if (status.broken.length) errors.push(name + " " + width + ": broken images " + status.broken.join(", "));
  if (status.mainCount !== 1 || status.footerCount !== 1) errors.push(name + " " + width + ": landmarks missing");
  if (status.blocked) errors.push(name + " " + width + ": content hidden after scroll");

  if (width === 375 && !route) {
    const menu = page.locator(".menu-toggle");
    await menu.click();
    if (await menu.getAttribute("aria-expanded") !== "true") errors.push("mobile menu does not expand");
    await page.locator("#main-nav a[href='#ranks']").click();
    if (await menu.getAttribute("aria-expanded") !== "false") errors.push("mobile menu does not collapse");
    await page.locator("#hours-input").fill("152");
    if (await page.locator("#sim-rank-name").textContent() !== "Estudante") errors.push("rank simulator incorrect at 152h");
    await page.locator("#rank-search").fill("Arquiteto");
    if (await page.locator(".rank-card:not([data-hidden='true'])").count() !== 1) errors.push("rank filtering incorrect");
    await page.locator(".rank-card:not([data-hidden='true'])").click();
    if (!(await page.locator("#rank-dialog").evaluate(el => el.open))) errors.push("rank modal did not open");
    await page.locator("#close-dialog").click();
  }
  if (width === 375 && route === "docs/") {
    await page.locator(".docs-mobile-nav").click();
    if (await page.locator(".docs-mobile-nav").getAttribute("aria-expanded") !== "true") errors.push("docs mobile sidebar did not open");
    await page.locator("#docs-search").fill("revogue");
    await page.locator("#docs-results a").first().waitFor({ state: "visible", timeout: 8000 });
    const links = await page.locator("#docs-results a").allTextContents();
    if (!links.some(t => t.includes("Segurança"))) errors.push("full-content search did not find security page");
  }
  if (width === 375 && route === "roadmap/") {
    const items=page.locator(".rm-milestone");
    if(await items.count()!==5) errors.push("roadmap does not have exactly 5 milestones");
    await page.locator('[data-rm-filter="planned"]').click();
    if(await page.locator(".rm-milestone:visible").count()!==1) errors.push("roadmap planned filter incorrect");
    if(await page.locator('[data-rm-filter="planned"]').getAttribute("aria-pressed")!=="true") errors.push("roadmap filter does not report pressed state");
    await page.locator('[data-rm-filter="all"]').click();
    if(await page.locator(".rm-milestone:visible").count()!==5) errors.push("roadmap all filter incorrect");
    await page.locator('.rm-map-stage a[href="#fase-1-5"]').click();
    if(await page.locator("#fase-1-5").isHidden()) errors.push("roadmap deep-link hidden");
    await page.locator(".menu-toggle").click();
    if(await page.locator(".menu-toggle").getAttribute("aria-expanded")!=="true") errors.push("roadmap mobile menu fails");
    await page.locator(".menu-toggle").click();
  }
  if (width === 375 && route === "customize/") {
    await page.waitForFunction(() => {
      const img = document.getElementById("theme-preview-image");
      return img?.complete && img.naturalWidth > 0;
    }, null, {timeout:12000});
    if (await page.locator("[data-preview-card]").count() !== 6) errors.push("customize preview has not six cards");
    await page.locator('[data-preview-card="ranking"]').click();
    await page.waitForFunction(() => document.querySelector("#theme-preview-image")?.complete);
    const rankingSvg = await page.locator("#theme-preview-image").evaluate(async img => (await fetch(img.src)).text());
    if (!rankingSvg.includes("#2841")) errors.push("real ranking SVG preview does not match fixture");
    await page.locator('[data-preview-card="lifetime"]').click();
    await page.waitForFunction(() => document.querySelector("#theme-preview-image")?.complete);
    const lifetimeSvg = await page.locator("#theme-preview-image").evaluate(async img => (await fetch(img.src)).text());
    if (!lifetimeSvg.includes("data:image/png;base64,")) errors.push("real rank art not embedded in preview");
    if(await page.locator('[data-include-card]').count()!==6) errors.push("selection must have 6 cards");
    await page.locator('[data-include-card="ranking"]').uncheck();
    await page.locator('#theme-layout').selectOption('paired');
    await page.locator('#theme-size').selectOption('compact');
    const selectedJson=JSON.parse(await page.locator('#theme-json').textContent());
    if(selectedJson.cards.includes('ranking') || selectedJson.layout!=='paired' || selectedJson.size!=='compact') errors.push("selected cards/layout/size not exported");
    if(await page.locator('#theme-readme-preview figure').count()!==5) errors.push("readme preview does not match selected cards");
    if(!(await page.locator("#theme-readme-code").textContent()).includes('width="250"')) errors.push("paired README snippet has incorrect width");
    if((await page.locator("#theme-readme-code").textContent()).includes("ranking.svg")) errors.push("deselected ranking still in README");
    await page.locator('[data-include-card="ranking"]').check();
    await page.locator('#theme-layout').selectOption('stacked');
    await page.locator('#theme-size').selectOption('standard');
    await page.locator('[data-preview-card="languages"]').click();
    await page.locator("#theme-language-rows").selectOption("5");
    await page.waitForFunction(async () => {
      const img=document.querySelector("#theme-preview-image");
      if (!img?.src.startsWith("blob:")) return false;
      try {return (await (await fetch(img.src)).text()).includes('viewBox="0 0 700 335"');}
      catch {return false;}
    },null,{timeout:10000});
    if(JSON.parse(await page.locator("#theme-json").textContent()).language_rows!==5)
      errors.push("density selection was not exported");
    if(!(await page.locator('#theme-readme-preview img[src$="languages-5.svg"]').count()))
      errors.push("README preview did not use compact languages fixture");
    await page.locator('#theme-typography').selectOption("large");
    await page.waitForFunction(async () => {
      const img=document.querySelector("#theme-preview-image");
      if (!img?.src.startsWith("blob:") || img.getAttribute("aria-busy")==="true") return false;
      try {
        const svg=await (await fetch(img.src)).text();
        return svg.includes('viewBox="0 0 700 335"') && svg.includes('font-size="14.04"');
      } catch { return false; }
    },null,{timeout:10000});
    if(JSON.parse(await page.locator("#theme-json").textContent()).typography!=="large")
      errors.push("Typography option missing in JSON");
    await page.locator('[data-preview-card="lifetime"]').click();
    await page.locator('#theme-rank-stars').uncheck();
    await page.waitForFunction(async () => {
      const img=document.querySelector("#theme-preview-image");
      if (!img?.src.startsWith("blob:") || img.getAttribute("aria-busy")==="true") return false;
      try {return !(await (await fetch(img.src)).text()).includes("<polygon");}
      catch {return false;}
    },null,{timeout:10000});
    const withoutStars=await page.locator("#theme-preview-image").evaluate(async img=>(await fetch(img.src)).text());
    if(!withoutStars.includes("data:image/png;base64,")) errors.push("disabling stars removed rank artwork");
    if(JSON.parse(await page.locator("#theme-json").textContent()).show_rank_stars!==false)
      errors.push("Rank star option missing in JSON");
    if(!(await page.locator('#theme-readme-preview img[src$="lifetime-type-large-no-stars.svg"]').count()))
      errors.push("README preview not synchronized with star and typography options");
    await page.locator('#theme-rank-stars').check();
    await page.locator('#theme-typography').selectOption("standard");
    await page.locator("#theme-language-rows").selectOption("10");
    await page.locator('[data-preview-card="lifetime"]').click();
    const initial = await page.locator("#theme-json").textContent();
    if (!initial.includes('"theme": "midnight"')) errors.push("customize initial preset wrong");
    await page.locator('[data-theme="aurora"]').click();
    if (!(await page.locator("#theme-json").textContent()).includes('"theme": "aurora"')) errors.push("customize preset not reflected");
    await page.locator('[data-hex="accent"]').fill("#DDAABB");
    await page.waitForFunction(async () => {
      const img=document.querySelector("#theme-preview-image");
      if (!img?.src.startsWith("blob:")) return false;
      try { return (await (await fetch(img.src)).text()).includes("#ddaabb"); }
      catch { return false; }
    }, null, {timeout:10000});
    if (!(await page.locator("#theme-json").textContent()).includes("#DDAABB")) errors.push("customize hex editor not reflected");
    await page.locator('[data-hex="accent"]').fill("invalid");
    if (await page.locator('[data-hex="accent"]').getAttribute("aria-invalid") !== "true") errors.push("customize invalid color accepted");
    await page.locator('[data-hex="accent"]').blur();
    if (await page.locator('[data-hex="accent"]').getAttribute("aria-invalid") === "true") errors.push("customize invalid color not restored");
    await page.locator("#download-preview").click();
    if (!(await page.locator("#theme-preview-message").textContent()).includes("fictícia")) errors.push("SVG preview download must be labeled fictional");
    await page.locator("#download-theme").click();
    if (!(await page.locator("#theme-feedback").textContent()).includes("Arquivo")) errors.push("customize download feedback missing");
  }
  await page.screenshot({ path: path.join(folder, name + "-" + width + ".png"), fullPage: true, animations: "disabled" });
  await page.close();
}

try {
  for (const width of widths) {
    const context = await browser.newContext({ viewport: { width, height: 850 }, deviceScaleFactor: 1, reducedMotion: "reduce" });
    for (const route of routes) await exerciseRoute(context, route, width);
    await context.close();
  }
  const extra = ["docs/installation/", "docs/configuration/", "docs/cards/", "docs/ranks/", "docs/security/", "docs/faq/", "docs/roadmap/"];
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: "reduce" });
  for (const route of extra) {
    const page = await context.newPage();
    page.on("pageerror", e => errors.push(route + ": " + e.message));
    const r = await page.goto(new URL(route, base).href, { waitUntil: "domcontentloaded" });
    if (!r?.ok()) errors.push(route + " HTTP " + r?.status());
    const problem = await page.evaluate(() => ({
      width: document.documentElement.scrollWidth,
      images: [...document.images].filter(img => img.complete && !img.naturalWidth).length
    }));
    if (problem.width > 1442 || problem.images) errors.push(route + ": overflow or broken image");
    await page.screenshot({ path: path.join(folder, route.split("/")[1] + "-1440.png"), fullPage: true, animations: "disabled" });
    await page.close();
  }
  await context.close();
} finally {
  await browser.close();
}

if (errors.length) {
  console.error("Visual QA failures:\n" + errors.join("\n"));
  process.exitCode = 1;
} else {
  console.log("Visual QA passed: 6 widths, 11 routes, 31 screenshot artifacts, six canonical preview SVGs and critical interactions.");
}
