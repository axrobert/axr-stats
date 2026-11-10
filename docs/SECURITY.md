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
