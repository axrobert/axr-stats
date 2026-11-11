<div align="center">

<img src="assets/brand/banner.svg" width="100%" alt="AXR Stats banner">

# AXR Stats

**Your coding journey, beautifully documented.**

Cards de programação, evolução por horas e medalhas personalizadas para perfis GitHub.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-2088FF?style=flat-square&logo=githubactions)
![Preview](https://img.shields.io/badge/Status-Development%20Preview-F59E0B?style=flat-square)

[**Website**](https://axrobert.github.io/axr-stats/) · [**Documentação**](https://axrobert.github.io/axr-stats/docs/) · [Instalação](https://axrobert.github.io/axr-stats/docs/installation/) · [Ranks](https://axrobert.github.io/axr-stats/docs/ranks/) · [Roadmap](https://axrobert.github.io/axr-stats/docs/roadmap/)

</div>

## Preview

<p align="center"><sub>DEMONSTRATION DATA — fictional values, not real account statistics.</sub></p>

<table>
<tr>
<td align="center" width="30%" valign="middle">
  <img src="assets/badges/current/03-estudante.png" alt="Example Artisan rank artwork" width="180">
  <p><strong>ESTUDANTE · TIER 03</strong></p>
  <sub>150+ cumulative hours</sub>
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

## Rank progression — 12 illustrated tiers

<div align="center">
  <img src="assets/badges/current/01-iniciante.png" width="82" alt="Tier 01 Iniciante">
  <img src="assets/badges/current/02-aprendiz.png" width="82" alt="Tier 02 Aprendiz">
  <img src="assets/badges/current/03-estudante.png" width="82" alt="Tier 03 Estudante">
  <img src="assets/badges/current/04-desenvolvedor.png" width="82" alt="Tier 04 Desenvolvedor">
  <img src="assets/badges/current/05-especialista.png" width="82" alt="Tier 05 Especialista">
  <img src="assets/badges/current/06-avancado.png" width="82" alt="Tier 06 Avançado">
  <img src="assets/badges/current/07-elite.png" width="82" alt="Tier 07 Elite">
  <img src="assets/badges/current/08-mestre.png" width="82" alt="Tier 08 Mestre">
  <img src="assets/badges/current/09-arquiteto.png" width="82" alt="Tier 09 Arquiteto">
  <img src="assets/badges/current/10-sabio.png" width="82" alt="Tier 10 Sábio">
  <img src="assets/badges/current/11-lendario.png" width="82" alt="Tier 11 Lendário">
  <img src="assets/badges/current/12-soberano.png" width="82" alt="Tier 12 Soberano">
</div>

| Tier | Rank | From (hours) | Until (exclusive) |
| :--: | :--- | ---: | ---: |
| 01 | Iniciante | 0 | 50 |
| 02 | Aprendiz | 50 | 150 |
| 03 | Estudante | 150 | 300 |
| 04 | Desenvolvedor | 300 | 500 |
| 05 | Especialista | 500 | 800 |
| 06 | Avançado | 800 | 1,200 |
| 07 | Elite | 1,200 | 1,800 |
| 08 | Mestre | 1,800 | 2,500 |
| 09 | Arquiteto | 2,500 | 3,500 |
| 10 | Sábio | 3,500 | 5,000 |
| 11 | Lendário | 5,000 | 8,000 |
| 12 | Soberano | 8,000 | ∞ |

The **12-level system** is original to AXR Stats and uses tracked programming hours, not an official WakaTime or GitHub rank. All 12 images are the original supplied **512 × 512 transparent PNGs**. SVG wrappers with embedded raster pixels are available under [assets/badges/current/](assets/badges/current/); they are not editable vector paths.

The rank catalog is maintained in [ranks.json](assets/badges/current/ranks.json). Earlier provisional graphics remain in the legacy directory for reference.

## Quick start

> [!IMPORTANT]
> **Development preview:** The reusable Action has no stable v1 tag yet. The sample workflow uses the mutable `@main` ref for **preview testing only**, not a stable release. Pin a reviewed full commit SHA before relying on it in production.

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
| [assets/badges/](assets/badges/) | Current 12-rank PNG/SVG collection |
| [assets/badges/legacy/](assets/badges/legacy/) | Archived experimental SVG badges |
| [assets/previews/](assets/previews/) | Fictional sample graphics; never real user data |
| [assets/brand/](assets/brand/) | Branding |
| [site/](site/) | GitHub Pages source |
| [docs/](docs/) | Documentation and design rules |
| [examples/](examples/) | Consumer workflow and profile snippet |
| [tests/](tests/) | Regression and asset checks |

## Status, contribution & support

The prototype is running on the maintainer's profile and the documentation website is published at [axrobert.github.io/axr-stats](https://axrobert.github.io/axr-stats/). Offline consumer integration tests and cross-platform visual QA are available. A real third-party GitHub repository installation with its own OAuth token and permission model still requires validation before a stable release.

See [Contributing](CONTRIBUTING.md), [Design system](docs/DESIGN_SYSTEM.md) and [Roadmap](docs/ROADMAP.md). Support links will be added after the maintainer configures an official donation account.

**Licensing:** No license granted yet. The code and generated art need an explicit licensing decision before v1. Publicly visible does not mean freely redistributable.

<sub>Independent project. Not affiliated with GitHub or WakaTime. Built with AI assistance and human curation.</sub>
