# Security and privacy

- **OAuth only.** WakaTime API keys used by editor plugins are not supported for read access.
- Put your OAuth token in GitHub Actions **Secrets**, never in a README, commit, URL parameter, PR log, badge URL or public workflow.
- The generator sends the `Authorization: Bearer ...` header only to `https://api.wakatime.com`.
- No WakaTime credential is sent to a third-party SVG card server.
- The sample action uses the GitHub-managed `GITHUB_TOKEN` only through the consuming repository's standard checkout/commit workflow.
- Generated SVG cards are intentionally **public**. They disclose your chosen activity metrics, including total time, languages, dates and any public ranking. Only enable it if you're comfortable displaying these details.
- The ranking appears only if the official API returns a confirmed numeric position. Custom levels and stars are *not* WakaTime rankings.
- All SVG output is escaped and parsed as XML. When API validation fails, the update fails without replacing previous graphics.
- Depending on the WakaTime account and OAuth scopes, summaries or all-time data may not be available. An error does not mean there was no activity.
- Revoke the OAuth token at WakaTime if you suspect it has leaked.

The example consumer workflow grants `contents: write` so it can commit generated assets. For stricter permissions, split generation and publication between separate jobs.

## Consumer preview and publication integrity

- The public example intentionally uses the mutable `@main` ref as a **preview-only** reference. Before production use, pin a reviewed full commit SHA and monitor releases.
- `src/run_action.py` now writes all six SVGs and both PNGs to an isolated temporary directory. It validates SVG XML and PNG signatures before updating the consuming repository's destination.
- Existing unrelated files in the output directory are preserved. A failure before the final publication phase leaves previous images unchanged; a rename failure attempts rollback. This is **not** a durable filesystem transaction across power loss.
- GitHub Actions still needs `contents: write` only to commit generated output. Do not grant unrelated permissions, and protect the token using repository Secrets.
- Local fixture tests simulate a consuming repository without transmitting credentials or making real WakaTime API calls.
- **External integration verified (2026-11-11):** the separate `axrobert/axrobert` repository ran the Action pinned to product commit `913185763c3a1ab0fde2391a5259edb144b5a36b`, using its existing OAuth secret. [Workflow run 42962893687](https://github.com/axrobert/axrobert/actions/runs/42962893687) passed. The job had `contents: read`, validated six SVGs and two PNGs, and committed nothing. This proves that particular cross-repository workflow, **not** every account or runner combination.
