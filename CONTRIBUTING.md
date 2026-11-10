# Contributing to AXR Stats

Thanks for contributing. Please keep visual changes consistent with `docs/DESIGN_SYSTEM.md` and never commit API tokens or credentials.

## Development flow

1. Create a descriptive branch and make focused commits.
2. Run `python -m unittest discover -s tests -v` locally.
3. Test generated XML with `xml.etree.ElementTree` and, if possible, render previews to check text clipping at their final viewBox size.
4. Update docs and previews when changing public behavior.
5. Open a pull request describing expected behavior, visual differences and testing evidence.

## Security and accuracy

- Send OAuth credentials **only** to the official WakaTime API over HTTPS.
- Clearly label custom level systems separately from official third-party rankings.
- Do not fabricate actual hours or leaderboard positions.
- Demo data belongs only in files explicitly marked as samples.

## Development notes

No dependency installation is required for running the core Python unit tests. Optional renderer packages may be used **locally** for visual review but are not required by the GitHub Action.
