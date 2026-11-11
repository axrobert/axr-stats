# AXR Stats — Website V0.4

GitHub Pages is a responsive, light-themed discovery experience inspired by the user's supplied reference layout. No branded character art or third-party intellectual property is copied.

## Features

- Three-slide, manually operated hero carousel
- Seven-tier rank gallery with text search and accessible detail dialog
- Local-only hour simulator with next-tier progress
- Fictional demonstration cards with explicit disclaimers
- Installation guide linking to WakaTime OAuth and GitHub repository secrets

## Technical rules

- Plain HTML, CSS, and JavaScript. No backend or user accounts.
- Relative paths for project-hosted GitHub Pages under /axr-stats/.
- Responsive breakpoints at 1050px, 760px, and 500px.
- Accessible focus outlines, navigation landmarks, dialog, and reduced-motion handling.
- All seven interchangeable rank illustrations are loaded from assets/badges/*.png.
- Token collection is forbidden in browser code. OAuth belongs in GitHub Actions Secrets.

## Checks

Run python -m unittest discover -s tests -v, then review mobile and desktop layouts. Merging to main runs the Pages workflow. Reusable Action remains a development preview, not a stable v1 release.

## Styling architecture

The homepage and eight documentation routes share `site/style.css`. No new CSS override layers should be introduced. Interactive JavaScript remains separated by concern into `site/ui.js`, `site/app.js` and `site/docs/docs.js`.

## Roadmap experience

The public visual roadmap is `site/roadmap/index.html`, served as `/roadmap/`. It shares `site/style.css` and `site/ui.js`, plus the page-scoped `site/roadmap/roadmap.js`. Interactive filters update only presentation; content and evidence links remain present and accessible without JavaScript. The path diagram has a linear responsive fallback and honors reduced-motion preferences. Keep phases, statuses and evidence synchronized with `docs/ROADMAP.md` and the release checklist. Do not claim dates or completion percentages without evidence.
