---
name: design-md
description: Biblioteca de 84 DESIGN.md prontos, sistemas de design inspirados em marcas conhecidas (Stripe, Linear, Apple, Notion, Vercel, Airbnb, Spotify, Tesla e outras), do VoltAgent/awesome-design-md. Use quando o usuário pedir uma interface, site, landing page, app ou design system "no estilo de" uma marca, quiser escolher uma inspiração visual pronta, pedir um arquivo DESIGN.md ou quiser criar um design system no Claude Design a partir de um DESIGN.md.
license: MIT
---

# Biblioteca DESIGN.md

84 arquivos em `references/<slug>/DESIGN.md`. Cada um descreve a linguagem visual de uma marca (cores, tipografia, espaçamento, componentes, regras e o motivo de cada escolha) num formato que agentes conseguem seguir. São análises inspiradas nas marcas, não material oficial delas. A biblioteca é atualizada automaticamente a partir do VoltAgent/awesome-design-md (licença MIT).

## Como usar

1. **Escolher.** Abra `references/INDEX.md`: catálogo por categoria, uma linha por marca, com o slug.
   - Marca citada pelo nome: ache o slug no índice (ex.: Linear → `linear.app`, Mistral → `mistral.ai`).
   - Só um clima ("escuro e técnico", "editorial e quente"): proponha 2 ou 3 opções do índice, com o motivo de cada uma, e deixe o usuário escolher.
   - Marca fora da lista: diga que ela não está na biblioteca e ofereça a mais próxima.
2. **Ler inteiro.** Leia `references/<slug>/DESIGN.md` do começo ao fim antes de desenhar. O cabeçalho YAML (quando existe) traz os tokens; o corpo traz as regras e os motivos.
3. **Aplicar.**
   - Projeto de código: copie o arquivo para a raiz do projeto como `DESIGN.md` (se já existir um, pergunte antes de substituir) e construa a interface seguindo os tokens e as regras.
   - Chat ou artefato: use o arquivo como fonte única de cores, tipos, espaçamentos e componentes.
   - Claude Design: entregue o arquivo e oriente o usuário a enviá-lo em claude.ai/design → **Create new design system** → **Add assets**, ou a anexá-lo num protótipo com o pedido "Create a design system from this DESIGN.md".
4. **Manter o sistema.** Quando o arquivo não cobrir um caso, decida pelo raciocínio que ele explica, não por gosto. Fonte proprietária: use o substituto que o arquivo indica.

## Limites

- É inspiração de estilo: não reproduza logotipos, nomes ou textos da marca de um jeito que a página se passe pela empresa real.
- Esta skill cobre só a biblioteca. Para extrair o design de um site que não está nela, use uma ferramenta de extração.
