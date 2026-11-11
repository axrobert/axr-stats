# AXR Stats — Stable release checklist

**Status:** development preview; no stable release/tag has been published.

## Verified
- [x] Python CI, SVG/XML and PNG validation.
- [x] GitHub Pages + documentation with browser QA.
- [x] 12-rank integration and current emblem mapping.
- [x] Offline consumer tests and staged publishing; existing assets survive generation failures.
- [x] Real cross-repository GitHub Action smoke test — [profile workflow run #42962893687](https://github.com/axrobert/axrobert/actions/runs/42962893687) on 2026-11-11.
  - Product ref pinned to commit `913185763c3a1ab0fde2391a5259edb144b5a36b`.
  - Permissions: `contents: read`; WakaTime token from preexisting GitHub Actions secret.
  - Outputs validated: 6 SVG and 2 PNG in an isolated directory, no tracked files modified or pushed.

## Release gates — not yet fulfilled
- [ ] Maintainer chooses the **code license**. Nothing automatically grants open-source usage rights.
- [ ] Maintainer confirms a separate **illustration/brand licensing policy** for current and corrected icons.
- [x] Import 12 corrected rank illustrations supplied by the maintainer (including `Elite_CORRIGIDO`) into site/product and profile assets.
- [ ] Inspect the corrected images at final output resolution and verify render integration before stable launch.
- [x] Pin the product CI/Pages/visual workflow GitHub Actions dependencies to verified upstream commit SHAs (2026-11-11).
- [x] Pin direct Pillow/CairoSVG runtime versions and validate on the Python CI matrix.
- [ ] Continuously audit transitive package dependencies and supported runner environments before stable launch.
- [ ] Review WakaTime scopes, revocation, and third-party usage beyond this single connected profile.
- [ ] Verify documentation and public installation instructions using the final immutable tag or SHA.
- [ ] Final screenshots, accessible checks, changelog and release notes.

**Do not publish `v1`, `v1.0.0`, or a Marketplace listing until gates above have been explicitly reviewed.**

## Re-run the proven consumer check
The existing workflow lives in `axrobert/axrobert/.github/workflows/axr-action-smoke.yml`.
It is manual or runs on trusted pushes changing that workflow; it **does not publish cards**.
The pinned product commit must be deliberately updated for a new candidate before using
the smoke run as evidence for that candidate.

This is integration evidence for the tested environment, not a guarantee for all
WakaTime plans, token scopes, operating systems, or GitHub permission settings.
