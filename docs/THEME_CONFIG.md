# Configuração de temas — prévia da Fase 2

A geração agora aceita um arquivo JSON **opcional**, sem dependência adicional no Python. Os valores padrão anteriores continuam funcionando.

```bash
python src/run_action.py --config examples/axr-stats.json
```

No GitHub Actions:

```yaml
- uses: axrobert/axr-stats@main  # Prévia mutável. Para produção, fixe SHA revisado.
  with:
    wakatime-oauth-token: ${{ secrets.WAKATIME_OAUTH_TOKEN }}
    config-path: axr-stats.json
```

Arquivo de exemplo: [`examples/axr-stats.json`](../examples/axr-stats.json).

## Campos aceitos

- `theme`: `midnight`, `graphite` ou `aurora`.
- `timezone`: fuso IANA (por exemplo, `America/Maceio`).
- `output`: pasta relativa de saída.
- `cards`: lista não vazia dos cards a publicar: `lifetime`, `languages`, `activity`, `ranking`, `heatmap` e `emblem`. Omitir publica todos. A seleção remove apenas saídas gerenciadas pela ferramenta que não foram selecionadas.
- `layout`: `stacked` (vertical) ou `paired` (duas colunas). Afeta apenas o snippet do README, não as dimensões nativas do SVG.
- `size`: `compact`, `standard`, `large`. Define as larguras HTML do snippet (não faz upscale da imagem).
- `language_rows`: `5`, `8` ou `10` (padrão). Controla o número máximo de linguagens e a altura interna do card SVG de Linguagens.
- `typography`: `compact` (90%), `standard` (100%, padrão) ou `large` (108%). Ajusta a escala dos textos do SVG; o tamanho externo permanece igual.
- `show_rank_stars`: `true` (padrão) ou `false`. Mostra ou oculta as estrelas de progresso dos cards Tempo total e Emblema; a insígnia original permanece.
- `header_style`: `standard` (padrão, título + descrição + marca lateral) ou `minimal` (título e divisor, sem descrição). Aplica-se ao cabeçalho de todos os seis SVGs, sem alterar as métricas.
- `colors`: objeto opcional com os tokens `background`, `surface`, `outline`, `text`, `muted`, `accent` e `success`, sempre no formato `#RRGGBB`.

Valores informados por CLI/`with` prevalecem sobre o JSON. Os demais vêm do JSON e, na ausência deste, dos padrões anteriores. A paleta customizada altera os cards SVG e, por consequência, o card rasterizado; **não recolore os 12 emblemas artísticos**.

## Segurança e limitações

Não coloque tokens OAuth, chaves ou segredos no arquivo de configuração; o parser recusa campos não documentados. O arquivo é somente de apresentação, não autentica usuários, não coleta dados nem substitui o GitHub Actions Secret.

A Fase 2 agora inclui prévias reais dos seis **templates SVG** no [Theme Workbench](https://axrobert.github.io/axr-stats/customize/). As prévias são produzidas pelo gerador Python, com **fixtures fictícias e determinísticas** em `scripts/generate_preview_cards.py`. No GitHub Pages, apenas os SVGs estáticos são carregados; o JavaScript recolore os sete tokens conhecidos e pode baixar um SVG de **demonstração**. Os números não mudam e nenhum token OAuth é utilizado no navegador.

Para gerar as prévias localmente:

```bash
python scripts/generate_preview_cards.py --output site/customize/previews
```

Esses SVGs são artefatos do build, não registros reais da conta. A imagem de rank embutida é mantida sem recoloração. A **seleção individual de cards para publicação** já está disponível, junto com layouts de README vertical/duas colunas e larguras compacta/padrão/ampla. O arquivo `README-snippet.md` é criado quando `layout` ou `size` está presente no JSON. O SVG mantém sua geometria e desenho originais. A opção `cards` pode ser usada isoladamente sem gerar snippet. Nenhuma release estável foi publicada.

## Exemplo de publicação seletiva

```json
{
  "theme": "midnight",
  "output": "assets/axr-stats",
  "cards": ["lifetime", "languages", "activity", "emblem"],
  "layout": "paired",
  "size": "standard"
}
```

A Action gera somente os SVGs selecionados e os PNGs correspondentes quando aplicável. O snippet gerado contém apenas links relativos aos cards publicados. O layout é voltado para a apresentação no README do GitHub e não altera a renderização interna dos SVGs. Outros arquivos pessoais no diretório de destino são preservados.

## Fase 2.3.1 — Densidade do card de Linguagens

Use `"language_rows": 5`, `8` ou `10` no `axr-stats.json`. O renderizador Python modifica o número de linhas e a altura do **SVG de Linguagens**, com prévia correspondente no [personalizador](https://axrobert.github.io/axr-stats/customize/). O valor é validado estritamente; outros números, strings ou booleanos são rejeitados. A opção não recalcula dados, não muda o ranking e não modifica os emblemas. O padrão **10** mantém a saída antiga. Outros controles de tipografia e composição interna continuarão nas próximas etapas da Fase 2.3.

## Fase 2.3.2 — Tipografia e elementos internos

```json
{
  "typography": "large",
  "show_rank_stars": false,
  "language_rows": 8
}
```

O editor apresenta três escalas tipográficas seguras e uma opção para ocultar as estrelas dos cards de Tempo total e Emblema. O cálculo das horas e das classificações oficiais não muda. As prévias são SVGs derivados do próprio renderizador Python, com números fictícios. O navegador carrega apenas o card selecionado, sem conexão com a API do WakaTime.

**Compatibilidade:** omitir `typography` e `show_rank_stars` mantém exatamente os valores anteriores: `standard` e `true`. A opção `large` pode precisar de revisão visual quando nomes de linguagens forem excepcionalmente longos; os valores são limitados para reduzir colisões.

## Fase 2.3.3 — Cabeçalho dos cards

Defina `"header_style": "minimal"` para um cabeçalho mais discreto, sem a descrição secundária e sem a barra vertical. A opção padrão é `"standard"` e conserva o SVG anterior. Não são alterados horas, ranking, largura, altura ou artes dos emblemas. O [personalizador](https://axrobert.github.io/axr-stats/customize/) carrega a prévia real para ambos os estilos, sem OAuth.
