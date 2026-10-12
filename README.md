# awesome-design-md (plugin)

Empacota os DESIGN.md do [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) (MIT) como um plugin com uma skill, `design-md`, para o app do Claude (chat, Cowork) e o Claude Code. A lista [VoltAgent/awesome-claude-design](https://github.com/VoltAgent/awesome-claude-design) aponta para os mesmos arquivos.

## Instalar

No app do Claude (web ou desktop): **Customize > Plugins > Add > Add marketplace**, informe este repositório (`owner/repo`) e ligue **Sync automatically**. Depois adicione o plugin `awesome-design-md`.

Ele fica salvo na conta: aparece no chat e baixa sozinho no Claude Code (CLI e desktop) como plugin sincronizado. Não instale também pela linha de comando do Claude Code, ou a skill aparece duplicada.

Só para quem usa o Claude Code sem o app (Claude Code 2.1.275 ou mais novo):

```
/plugin install awesome-design-md --marketplace nikemafia044-a11y/awesome-design-md-plugin
```

## Atualização

O workflow `.github/workflows/sync.yml` roda todo dia (e sob demanda em **Actions**). Ele baixa o upstream, roda `scripts/build.py` e só faz commit quando algum DESIGN.md mudou, subindo a versão do plugin. Com **Sync automatically** ligado, o app recebe a versão nova sozinho.

Para gerar localmente: `python scripts/build.py --upstream <clone do awesome-design-md>`.

Em repositório público, o GitHub desliga workflows agendados depois de 60 dias sem atividade. Se isso acontecer, reative em **Actions**.
