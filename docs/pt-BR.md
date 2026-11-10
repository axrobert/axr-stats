# AXR Stats — guia rápido em português

O AXR Stats gera cards SVG e emblemas para seu README do GitHub usando dados reais do WakaTime.

1. Gere um **token pessoal OAuth** em https://wakatime.com/oauth. A API Key de extensões não serve para consultas de estatísticas.
2. No repositório do seu perfil, crie um secret `WAKATIME_OAUTH_TOKEN`.
3. Copie `examples/consumer-workflow.yml` para `.github/workflows/axr-stats.yml` no repositório do perfil.
4. Depois que o repositório central estiver publicado, ajuste o `uses:` para uma versão real do AXR Stats.
5. Execute o workflow e cole no README o exemplo de `examples/readme-snippet.md`.

**Atenção:** este arquivo ZIP ainda é um projeto inicial, não uma GitHub Action publicada. Não cole tokens em chats, commits ou URLs. O sistema de níveis por horas é personalizado e não substitui o ranking público oficial.
