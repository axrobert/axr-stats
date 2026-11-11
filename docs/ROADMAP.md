# Roadmap

## Phase 0 — Prototype complete
- Working original SVG generator inside the `axrobert/axrobert` profile.
- Live WakaTime OAuth, all-time activity, public leaderboard and emblems.

## Phase 1 — Standalone release (in progress)
- Separate repository and documentation.
- Original brand SVG, previews, tier emblems and themes.
- Test matrix and browser screenshot/render regression tests (done).
- Consumer-style offline integration and batch output safety (done; product PR #11).
- Real external GitHub Action installation in `axrobert/axrobert` (passed; [smoke run](https://github.com/axrobert/axrobert/actions/runs/42962893687)). Used the existing OAuth secret with `contents: read`, a fixed Action commit, an isolated output path, and no commits to the profile.
- Validate on another account/OS and review token scopes before claiming broad compatibility (pending).
- Pin remaining GitHub Action dependencies and publish `v1` only after the maintainer approves code/assets licensing and release QA.
- Decide and publish the open-source license.

## Phase 1.5 — Product identity & visual polish (current)
- Consistent component geometry and restrained, editorial visual identity.
- Clean up excessive borders, pill buttons and repeated rounded cards.
- Refine homepage, Docs, rank gallery, responsiveness and keyboard states.
- Perform real visual QA on mobile and desktop before claiming complete.
- Twelve illustrated ranks (corrected PNG/SVG supplied by maintainer, including `Elite_CORRIGIDO`) imported and linked to the site and generators.

## Phase 2 — Personalization (in progress; preview)
- User-defined color tokens, typography, layouts and size presets.
- Additional rank styles and transparent standalone insignias.
- JSON configuration file for theme, timezone, output and validated hex color tokens (implemented).
- Local browser palette workbench at `/customize/` with actual production-rendered SVG templates, fictional stats, six card types, and JSON export (no browser access to WakaTime).
- Deterministic preview builder uses the Python renderer during Pages/Visual QA builds and never contacts external services.
- Preset themes and CLI usage documented; preview layout matches production SVGs for all six types.
- Pre-2.3 quality gate: OAuth redirect/response hardening, safe output paths, selective staging, offline security regressions, beginner onboarding and Python dependency audit (completed; PR #20).
- Phase 2.3.1 (completed; PR #21): Languages SVG density via `language_rows` (5/8/10), real previews and strict validation.
- Phase 2.3.2 (completed; PR #22): `typography` scale (90/100/108%), `show_rank_stars` toggle, six-card preview parity and offline lazy-loaded fixtures. Further internal arrangements remain planned.
- Phase 2.3.3 (completed; PR #23): optional SVG subtitles using `show_card_subtitles` with real preview parity.
- Phase 2.4 (completed; PR #25): beginner-focused progressive disclosure, safe local JSON import, validated output paths and timezone, Activity gauge text clearance, browser QA on 6 viewport widths, and CONTEXT.md handoff. Next: installation wizard and newcomer testing.
- Phase 2.2: validated `cards` selection, README `layout` (`stacked` / `paired`), `size` (`compact` / `standard` / `large`), live composition preview, and generated README snippet. Internal SVG geometry and typography controls remain planned.

## Phase 3 — Public product
- Browser-based card builder with live preview.
- Multilingual documentation, installation wizard and one-click workflow template.
- Optional GitHub activity metrics with clearly labeled data provenance.

## Guiding principle
Original visuals, real metrics, privacy-first architecture. Never fake a global ranking or exaggerate tracked hours.
