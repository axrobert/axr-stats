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
- `colors`: objeto opcional com os tokens `background`, `surface`, `outline`, `text`, `muted`, `accent` e `success`, sempre no formato `#RRGGBB`.

Valores informados por CLI/`with` prevalecem sobre o JSON. Os demais vêm do JSON e, na ausência deste, dos padrões anteriores. A paleta customizada altera os cards SVG e, por consequência, o card rasterizado; **não recolore os 12 emblemas artísticos**.

## Segurança e limitações

Não coloque tokens OAuth, chaves ou segredos no arquivo de configuração; o parser recusa campos não documentados. O arquivo é somente de apresentação, não autentica usuários, não coleta dados nem substitui o GitHub Actions Secret.

Esta entrega inicia a Fase 2. Editor visual, escolhas de layout e seleção individual de cards continuam planejados; nenhuma release estável foi publicada.
