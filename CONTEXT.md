# AXR Stats — CONTEXT.md

> Documento de continuidade e handoff entre conversas. **Atualizado: 2026-11-11.**
> Sempre confira o HEAD, a CI, os PRs, os Issues e o roadmap diretamente no GitHub antes de trabalhar. Este arquivo é um retrato, não substitui o estado real do repositório.

## 1. Identificação
- Projeto: **AXR Stats**, gerador de cards para README do GitHub com estatísticas autorizadas do WakaTime.
- Repositório: https://github.com/axrobert/axr-stats
- Site: https://axrobert.github.io/axr-stats/
- Editor: https://axrobert.github.io/axr-stats/customize/
- Documentação: https://axrobert.github.io/axr-stats/docs/
- Roadmap público: https://axrobert.github.io/axr-stats/roadmap/
- README pessoal que consome os cards: https://github.com/axrobert/axrobert
- Branch padrão: `main`.
- A versão estável `v1.0.0` **não deve ser publicada** sem aprovação explícita do mantenedor, revisão de licença e checklist de release.

## 2. Objetivo e limites fixos
1. Seis cards SVG principais: `lifetime`, `languages`, `activity`, `ranking`, `heatmap`, `emblem`. A Action também publica PNGs para lifetime/emblem quando selecionados.
2. O OAuth deve permanecer em `WAKATIME_OAUTH_TOKEN`, dentro dos GitHub Actions Secrets. Não colocar tokens em JSON, site, README, logs, issues ou exemplos.
3. Estatísticas reais são obtidas pela API oficial. Posições do leaderboard só são mostradas quando verificáveis; os **12 ranks por horas são classificação autoral do AXR Stats, não ranking oficial WakaTime**.
4. Todas as prévias web usam dados **fictícios**, gerados offline pelo mesmo Python, nunca via OAuth no navegador.
5. Preservar os 12 emblemas corrigidos em `assets/badges/current/`, inclusive `07-elite.png`. SVGs da coleção atual podem conter PNG incorporado; não são vetores nativos editáveis.
6. Evitar visual “AI slop”: espaçamento preciso, simetria, componentes com função real, poucos efeitos, ícones coerentes, movimento acessível e sem elementos cortados.
7. Preservar compatibilidade: se nenhuma opção nova for fornecida, a saída deve conservar os padrões anteriores. Sem refazer o projeto com React/Next/Tailwind sem motivo.
8. Trabalhar em branches com commits convencionais, testes e PR. Não fazer force push, reset, rebase, limpeza destrutiva, exposição de segredos ou release sem autorização.
9. O usuário quer um `CONTEXT.md` **atualizado após cada fase importante**, com branch/commit/PR/QA, próximos passos e problemas conhecidos. Oferecer cópia para download em cada entrega relevante.

## 3. Arquitetura
- `src/axr_stats.py`: coleta/valida dados oficiais, desenha SVGs, inclui emblemas, implementa `activity_card` e `presentation_theme`.
- `src/config.py`: whitelist, limites e validações do `axr-stats.json`.
- `src/run_action.py`: workflow da Action, publicação atômica, paths seguros, proteção contra symlinks.
- `src/layouts.py`: geração do snippet HTML do README em modo `stacked`/`paired`.
- `scripts/generate_preview_cards.py`: gera offline fixtures SVG de teste com variantes de aparência.
- `site/customize/index.html`, `customize.js`, `preview.js`: workbench estático, editor, prévias e exportação.
- `site/customize/import.js`: importador local de JSON, introduzido na Fase 2.4.
- `site/style.css`: stylesheet único compartilhado; manter abaixo do teto nos testes.
- `site/docs/**`: documentação em rotas distintas; índice em `site/docs/search-index.json`.
- `tests/browser_smoke.mjs`: Chromium/Playwright com múltiplas resoluções e screenshots.
- `.github/workflows/{test,visual-qa,pages,dependency-audit}.yml`: CI, teste visual, deploy e auditoria de dependências.

## 4. Fases concluídas / verificadas até o início deste handoff
- PR #20: hardening OAuth/redirecionamentos, limites de resposta e caminhos, Pillow 13.0.0/CairoSVG 2.9.1, `pip-audit` agendado, documentação para iniciantes.
- PR #21: quantidade de linguagens no card (5/8/10), paridade de renderização e prévia.
- PR #22: presets de tipografia (90/100/108%) e visibilidade das estrelas.
- PR #23: `show_card_subtitles` nos seis cards, preservando padrão.
- PR #24: alternativa de cabeçalho descartada, **fechada sem merge**.
- `main` no início da Fase 2.4: commit `5981d68999755510847a50fa1750870963314059`. CI e GitHub Pages estavam verdes.
- O bloco publicitário redundante no README pessoal foi removido anteriormente. Não reintroduzir: manter apenas os cards reais, com link discreto em Projects se necessário.

## 5. Fase ativa: 2.4 — Onboarding, importação e correção de layout
- Branch da implementação: `feat/phase24-onboarding-import-layout`, integrada à `main` no PR #25. Próxima tarefa: iniciar a Fase 2.5 (instalação guiada e testes com usuários iniciantes) em branch separada.
- Objetivos desta fase: simplificar a interface para leigos, esconder controles avançados, importar JSON local sem enviar dados, validar importação antes de mutar a UI, manter o README alinhado à pasta configurada e distanciar a curva do texto no card Atividade.
- Alterações preparadas na branch:
  - `src/axr_stats.py`: gauge do card Activity de `cy=218` para `cy=198`, textos em y=184 e y=207; mantém 350×300 e indicadores inferiores.
  - `site/customize/index.html`: painéis expansíveis para cores e opções avançadas, campos de pasta/fuso, seletor de JSON, link de instalação para iniciantes.
  - `site/customize/customize.js`: exportação de `output` e `timezone` com validação; snippet usa caminho configurado.
  - `site/customize/import.js`: leitura local de até 64 KB, whitelist de propriedades, validações de cards/cores/layout/ranks/caminhos/fuso, aplicação apenas após validação completa.
  - `site/style.css`: refinamento de painéis avançados, importador e foco acessível.
  - `tests/test_phase24_onboarding.py`: regressão de geometria e contratos de controles.
  - `tests/browser_smoke.mjs`: casos importados válidos/inválidos e alinhamento JSON/snippet.
  - README, `docs/THEME_CONFIG.md`, `docs/ROADMAP.md`, docs online e índice de busca atualizados.
- **Integração concluída:** PR #25 (https://github.com/axrobert/axr-stats/pull/25) integrado à `main` por squash commit `436a42e60634d4405d15bb8fcd893fe947fa8f5f`. CI Python 3.11/3.12/3.13 e Chromium Visual QA aprovados. Capturas inspecionadas em 320/375/768/1024/1440/1920. Verificar status do Pages para o novo commit antes de declarar a implantação final.
- Atenção especial: verificar que o importador está incluído no HTML, que o JSON inválido não altera controles, que o HTML mantém estrutura correta e que o medidor Activity não sobrepõe texto. Não inventar resultados.

## 6. Configuração pública
Campos aceitos: `theme`, `timezone`, `output`, `colors`, `cards`, `layout`, `size`, `language_rows`, `typography`, `show_rank_stars`, `show_card_subtitles`. O JSON não contém nem aceita token de API. A entrada `config-path` da Action aponta para o JSON no repositório do consumidor.

## 7. Próximos passos recomendados
1. Fase 2.4 finalizada no PR #25. Revisar nova `main` e status do deploy GitHub Pages, especialmente após mudanças futuras.
2. Atualizar este `CONTEXT.md` com PR, commit da `main`, resultados de QA e pendências reais.
3. Tornar a instalação para leigos mais simples: assistente orientado para copiar workflow e configuração, mensagens de erro claras e checklist da primeira execução.
4. Revisar SVGs com valores reais extremos (horas grandes, idiomas longos, ranking indisponível), acessibilidade, foco por teclado e densidade mobile.
5. Validar Action em outra conta de GitHub, revisar escopos OAuth, licença e checklist antes de considerar v1 estável.

## 8. Como retomar em outro chat
> “Continue o projeto AXR Stats no GitHub a partir do `CONTEXT.md` do repositório `axrobert/axr-stats`. Primeiro leia o contexto, confira `main`, branches, PRs, Actions e `docs/ROADMAP.md`; depois prossiga na fase ativa. Trabalhe diretamente nos arquivos, preserve os 12 emblemas e os dados reais, execute testes e atualize `CONTEXT.md` na entrega.”

**Importante:** este documento não substitui inspeção do código, nem autorização para mexer em segredos, licenças ou publicar release.

## 9. Conclusão da Fase 2.4 — verificação de 11/11/2026

- PR #25 incorporado por squash ao commit `436a42e60634d4405d15bb8fcd893fe947fa8f5f`.
- CI Python (3.11/3.12/3.13): passou. Chromium Visual QA: passou e gerou screenshots para 320, 375, 768, 1024, 1440 e 1920px.
- A implantação GitHub Pages após o merge deve ser verificada por execução associada ao HEAD da `main`, e não inferida da CI.
- Próxima fase recomendada: **2.5 — instalação guiada para iniciantes** (workflow passo a passo e tratamento de erros). Ainda não implementada neste documento.
