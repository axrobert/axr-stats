# Comece aqui — AXR Stats (prévia)

Guia para quem **nunca criou uma GitHub Action**. Você não precisa programar, instalar Python nem informar suas credenciais ao site.

> O projeto está em prévia e não possui release estável v1. O exemplo usa uma referência mutável do projeto; fixe um SHA revisado antes de usar permanentemente.

## 1. Crie ou abra seu perfil GitHub

Seu repositório de perfil deve ter o mesmo nome do seu usuário no GitHub. Exemplo: o usuário **meunome** usa um repositório público **meunome/meunome** com README.md. Se já existe, não crie outro.

## 2. Configure o WakaTime

Instale o plugin oficial no editor e confirme atividade no [painel WakaTime](https://wakatime.com/dashboard). Obtenha um **token OAuth pessoal** em [WakaTime OAuth](https://wakatime.com/oauth). A API Key do plugin do editor **não substitui** o token OAuth.

Os cards gerados serão públicos. Eles podem revelar horas, linguagens, datas e ranking.

## 3. Armazene o token como GitHub Secret

No seu repositório de perfil, abra **Settings → Secrets and variables → Actions → New repository secret**.

**Name:** WAKATIME_OAUTH_TOKEN

**Secret:** cole apenas o token OAuth. Nunca coloque seu valor no README, JSON, workflow, screenshots, issues ou mensagens.

## 4. Instale o workflow

Abra o [exemplo do AXR Stats](../examples/consumer-workflow.yml), clique em **Raw** e copie o arquivo.

No repositório de perfil, clique em **Add file → Create new file**. Digite este caminho exato:

~~~
.github/workflows/axr-stats.yml
~~~

Cole o workflow e confirme **Commit changes**.

O exemplo concede **contents: write** para atualizar as imagens no seu próprio repositório. A referência **axrobert/axr-stats@main** é mutável e serve apenas à prévia. Para uso duradouro, substitua-a por um SHA completo de commit revisado do projeto. Ainda não existe @v1.

## 5. Execute pela primeira vez

Abra **Actions → Update AXR Stats → Run workflow** na branch principal.

Se falhar, confira a primeira etapa vermelha:

| Mensagem | Verificação |
| --- | --- |
| Token ausente | Confirme o nome exato do Secret no repositório de perfil |
| HTTP 401 | OAuth inválido/expirado; gere outro token e atualize o Secret |
| HTTP 403 | Verifique as permissões OAuth autorizadas |
| HTTP 429 | Limite temporário; tente em outro momento |
| Permission denied ao publicar | Verifique Actions → General → Workflow permissions e proteções da branch |
| Sem atividade | Verifique se há dados no painel WakaTime e acesso ao histórico |
| Workflow não aparece | Confirme o caminho e a branch padrão do arquivo |

Não compartilhe valores de tokens em logs de erro ou capturas de tela.

## 6. Coloque os cards no README

Após uma execução bem-sucedida, abra a pasta **assets/axr-stats** do seu repositório. Os arquivos gerados estarão nela.

Copie este exemplo para o README do seu perfil:

~~~html
<p align="center">
  <img src="assets/axr-stats/lifetime.png" alt="Tempo total de programação" width="700">
  <img src="assets/axr-stats/languages.svg" alt="Linguagens programadas" width="700">
</p>
~~~

Se configurar layout ou tamanho no **axr-stats.json**, a Action gerará **README-snippet.md**, que contém um trecho pronto para copiar. O JSON é opcional.

**Continuar:** [personalizador](https://axrobert.github.io/axr-stats/customize/) · [documentação](https://axrobert.github.io/axr-stats/docs/) · [segurança](SECURITY.md).

Se surgir outro problema, abra uma [issue](https://github.com/axrobert/axr-stats/issues/new) sem expor dados privados.
