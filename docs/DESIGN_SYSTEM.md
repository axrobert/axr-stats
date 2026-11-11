# AXR Stats — visual system

## Principles

- Consistent geometry and predictable spacing: no cramped labels or floating metrics.
- One header baseline and one footer baseline for cards displayed together.
- Quiet dark backgrounds, a single accent, and strong readable hierarchy.
- Never manufacture official WakaTime ranks or historical totals.

## Card layout tokens

| Token | Standard |
| --- | --- |
| Paired card canvas | 350 × 300 pixels |
| Header title baseline | 45 px |
| Subtitle baseline | 70 px |
| Content value baseline | 179 px |
| Footer divider | y = 251 px |
| Footer text baseline | 280 px |
| Corner radius | 18 px |
| Safe inset | 28 px |

Charts use SVG so numeric values remain selectable and data-driven. The lifetime card may be composed into a PNG when it includes an illustrated badge. Two adjacent README cards must share **exact viewBox dimensions** and **equal width attributes**.

## Rank artwork — 12 levels

The current collection consists of **12 original 512 × 512 transparent PNG badges** and 12 SVG wrappers containing the exact same raster artwork.

- Authoritative metadata: `assets/badges/current/ranks.json`
- Assets: `assets/badges/current/01-iniciante.png` through `12-soberano.png`, plus `.svg`
- 12 thresholds (hours): 0, 50, 150, 300, 500, 800, 1,200, 1,800, 2,500, 3,500, 5,000, 8,000
- Old trials: `assets/badges/legacy/*.svg`
- Renderer: `src/render_rank_png.py` composes the actual badge into the dynamic card.

The supplied SVG files embed PNG data and **are not editable vector paths**. Preserve high-resolution PNGs as the canonical artwork. Use consistent transparent padding and do not overwrite current files with interim legacy art.

## Theme palette

| Theme | Background | Accent | Highlight |
| --- | --- | --- | --- |
| Midnight | #0c1220 | #5caeff | #54d2a0 |
| Graphite | #111317 | #c3a7ff | #58d7b0 |
| Aurora | #0a171b | #5de2c5 | #c3ef8e |

## Tier thresholds

| Tier | Rank | Hours |
| ---: | --- | ---: |
| 01 | Iniciante | 0 |
| 02 | Aprendiz | 50 |
| 03 | Estudante | 150 |
| 04 | Desenvolvedor | 300 |
| 05 | Especialista | 500 |
| 06 | Avançado | 800 |
| 07 | Elite | 1,200 |
| 08 | Mestre | 1,800 |
| 09 | Arquiteto | 2,500 |
| 10 | Sábio | 3,500 |
| 11 | Lendário | 5,000 |
| 12 | Soberano | 8,000 |

Star progress reflects a *custom tier calculation*, not an official GitHub/WakaTime endorsement. All artwork can be replaced without changing these rules.

## Publishing checklist

1. Run the Python unit tests and inspect the generated SVG XML.
2. Ensure the README and website use the same current asset paths.
3. Test 320px, 768px and wide desktop widths.
4. Use neutral fictional sample data on public product previews.
5. Keep OAuth secrets in the consuming repository; never insert them into URLs or static site JavaScript.

## Website visual refinement

The public site now uses `site/style.css` as its single canonical stylesheet. The original cascade (base, docs, refinement, motion) has been preserved in one file. New component rules belong in that stylesheet, not a new override layer.

## Motion, icons and footer (site V0.9)

- Common scripts: `site/ui.js` and `site/ui.css`, included in the homepage and all eight documentation pages.
- Motion: optional IntersectionObserver reveals, short carousel headline typing, passive scroll progress and active documentation table of contents.
- Navigation: native smooth scroll with `prefers-reduced-motion` override. A back-to-top control has a visible focus state and is unavailable until useful.
- Visual: editorial footer shared with Docs, minimal shadows, structured link groups, no layout-shifting scrolljacking.
- Icons: local Lucide SVG symbol sprite, via `site/icons/lucide.svg`. Source license retained at `site/icons/LICENSE`. Never copy PanelUI proprietary components or require React simply to get icons.
- No animation should block access to content; reduced-motion users see complete headlines without typing.
- The brand may change independently from icon vendors. Icon sprites use the original open source ISC license.

## Styling architecture — Visual Foundation

`site/style.css` is shared by the homepage and all eight docs pages. The former `site/refinement.css`, `site/ui.css`, and `site/docs/docs.css` were consolidated and removed. The existing cascade order was retained, and the progressive-cleanup policy is to edit original component rules instead of adding yet another override block.
