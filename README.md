<div align="center">

<img src="assets/brand/banner.svg" width="100%" alt="AXR Stats banner">

# AXR Stats

**Your coding journey, beautifully documented.**

Cards de programação, evolução por horas e medalhas personalizadas para perfis GitHub.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-2088FF?style=flat-square&logo=githubactions)
![Preview](https://img.shields.io/badge/Status-Development%20Preview-F59E0B?style=flat-square)

[**Website**](https://axrobert.github.io/axr-stats/) · [Installation](#quick-start) · [Ranks](#rank-progression) · [Roadmap](docs/ROADMAP.md) · [Português](docs/pt-BR.md)

</div>

## Preview

<p align="center"><sub>DEMONSTRATION DATA — fictional values, not real account statistics.</sub></p>

<table>
<tr>
<td align="center" width="30%" valign="middle">
  <img src="assets/badges/03-artisan.png" alt="Example Artisan rank artwork" width="180">
  <p><strong>ARTISAN · TIER 03</strong></p>
  <sub>100+ cumulative hours</sub>
</td>
<td width="70%" valign="middle">
  <h3>Make progress visible.</h3>
  <p>Track your lifetime coding time, your most-used languages and your daily activity, with optional verified WakaTime leaderboard results.</p>
  <p>The rank system is original to AXR Stats; the medals are replaceable PNGs. Charts use generated SVGs for sharp text and dynamic data.</p>
</td>
</tr>
</table>

<p align="center"><img src="assets/previews/languages.svg" width="100%" alt="Languages chart using fictional history"></p>
<p align="center">
  <img src="assets/previews/activity.svg" width="49%" alt="Illustrative daily activity">
  <img src="assets/previews/ranking.svg" width="49%" alt="Illustrative public WakaTime ranking">
</p>
<p align="center"><img src="assets/previews/heatmap.svg" width="100%" alt="Illustrative activity heatmap"></p>

## Features

| Card | Shows |
| :--- | :--- |
| **Lifetime** | Tracked hours, custom tier, stars and progress |
| **Languages** | All-time language distribution from WakaTime |
| **Activity** | Today’s coding time and recent daily average |
| **Ranking** | Public WakaTime position, when verifiable |
| **Heatmap** | Past 30 days of activity |
| **Emblem** | Transparent, replaceable rank illustration |

Three themes are available: **Midnight**, **Graphite**, and **Aurora**. The Action reads the official WakaTime API using an OAuth token from GitHub Actions Secrets. The token is never placed in public images.

## Rank progression

<div align="center">
  <img src="assets/badges/01-novice.png" width="76" alt="Novice">
  <img src="assets/badges/02-explorer.png" width="76" alt="Explorer">
  <img src="assets/badges/03-artisan.png" width="76" alt="Artisan">
  <img src="assets/badges/04-specialist.png" width="76" alt="Specialist">
  <img src="assets/badges/05-veteran.png" width="76" alt="Veteran">
  <img src="assets/badges/06-master.png" width="76" alt="Master">
  <img src="assets/badges/07-legend.png" width="76" alt="Legend">
</div>

| Tier | Name | Cumulative hours |
| :--: | :--- | ---: |
| 01 | Novice | 0 |
| 02 | Explorer | 25 |
| 03 | Artisan | 100 |
| 04 | Specialist | 250 |
| 05 | Veteran | 500 |
| 06 | Master | 1,000 |
| 07 | Legend | 2,500 |

These are **AXR Stats progression tiers**, not official WakaTime or GitHub ranks. The current illustrated medals are provisional and can be replaced individually without changing rank logic.

## Quick start

> [!IMPORTANT]
> **Development preview:** The reusable Action has no stable v1 tag yet. The sample workflow references a future release and **does not work unmodified** today. Test the source before using it publicly.

1. Generate a personal OAuth token at [WakaTime OAuth](https://wakatime.com/oauth). An editor API key is not a substitute.
2. Add the token as the repository Actions secret **WAKATIME_OAUTH_TOKEN**.
3. Review the [consumer workflow](examples/consumer-workflow.yml) and [security guidance](docs/SECURITY.md).
4. For local testing, run Python unit tests and the generator:

    python -m unittest discover -s tests -v

    python src/axr_stats.py --theme midnight --timezone America/Maceio --output dist

The second command requires the WAKATIME_OAUTH_TOKEN environment variable. **Never commit or share its value.** The PNG composer uses Pillow and CairoSVG; see the [Action definition](action.yml).

## Repository layout

| Path | Contents |
| :--- | :--- |
| [src/](src/) | Official WakaTime API client and image renderers |
| [assets/badges/](assets/badges/) | Current interchangeable PNG rank illustrations |
| [assets/badges/legacy/](assets/badges/legacy/) | Archived experimental SVG badges |
| [assets/previews/](assets/previews/) | Fictional sample graphics; never real user data |
| [assets/brand/](assets/brand/) | Branding |
| [site/](site/) | GitHub Pages source |
| [docs/](docs/) | Documentation and design rules |
| [examples/](examples/) | Consumer workflow and profile snippet |
| [tests/](tests/) | Regression and asset checks |

## Status, contribution & support

The prototype is running on the maintainer's profile and the documentation website is published at [axrobert.github.io/axr-stats](https://axrobert.github.io/axr-stats/). Third-party installation and cross-platform visual QA are still required before a stable release.

See [Contributing](CONTRIBUTING.md), [Design system](docs/DESIGN_SYSTEM.md) and [Roadmap](docs/ROADMAP.md). Support links will be added after the maintainer configures an official donation account.

**Licensing:** No license granted yet. The code and generated art need an explicit licensing decision before v1. Publicly visible does not mean freely redistributable.

<sub>Independent project. Not affiliated with GitHub or WakaTime. Built with AI assistance and human curation.</sub>
