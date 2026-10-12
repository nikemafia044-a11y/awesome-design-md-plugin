#!/usr/bin/env python3
"""Gera o plugin awesome-design-md a partir de um clone do VoltAgent/awesome-design-md.

Uso: python scripts/build.py --upstream <pasta do clone>

Só reescreve a skill e sobe a versão do plugin quando o conteúdo gerado muda,
para o app do Claude e o Claude Code receberem a atualização (eles comparam a versão).
"""
import argparse
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "awesome-design-md"
SKILL = PLUGIN / "skills" / "design-md"
STATE = ROOT / "sync-state.json"
MIN_BRANDS = 50  # abaixo disso o upstream provavelmente quebrou: não apaga a biblioteca
ENTRY = re.compile(r"^- \[\*\*(.+?)\*\*\]\(https://getdesign\.md/([^/)]+)/design-md\)\s*-\s*(.+?)\s*$")

SKILL_MD = """---
name: design-md
description: Biblioteca de __COUNT__ DESIGN.md prontos, sistemas de design inspirados em marcas conhecidas (Stripe, Linear, Apple, Notion, Vercel, Airbnb, Spotify, Tesla e outras), do VoltAgent/awesome-design-md. Use quando o usuário pedir uma interface, site, landing page, app ou design system "no estilo de" uma marca, quiser escolher uma inspiração visual pronta, pedir um arquivo DESIGN.md ou quiser criar um design system no Claude Design a partir de um DESIGN.md.
license: MIT
---

# Biblioteca DESIGN.md

__COUNT__ arquivos em `references/<slug>/DESIGN.md`. Cada um descreve a linguagem visual de uma marca (cores, tipografia, espaçamento, componentes, regras e o motivo de cada escolha) num formato que agentes conseguem seguir. São análises inspiradas nas marcas, não material oficial delas. A biblioteca é atualizada automaticamente a partir do VoltAgent/awesome-design-md (licença MIT).

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
"""


def read_text(path):
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def parse_collection(readme):
    """Categorias e entradas da seção '## Collection' do README do upstream."""
    cats, cur, inside = [], None, False
    for line in readme.splitlines():
        if line.startswith("## "):
            inside = line.strip() == "## Collection"
            continue
        if not inside:
            continue
        if line.startswith("### "):
            cur = (line[4:].strip(), [])
            cats.append(cur)
            continue
        m = ENTRY.match(line.strip())
        if m and cur is not None:
            cur[1].append((m.group(1), m.group(2), m.group(3)))
    return cats


def describe_unlisted(text, slug):
    """Nome e descrição de uma marca que tem pasta mas não está no README."""
    h1 = re.search(r"^# .*?Inspired by (.+?)\s*$", text, re.M)
    name = h1.group(1) if h1 else slug.replace("-", " ").title()
    desc = re.search(r'^description:\s*"?(.+?)"?\s*$', text, re.M)
    if desc:
        first = re.split(r"(?<=\.)\s", desc.group(1))[0]
        if len(first) > 160:
            first = first[:160].rsplit(" ", 1)[0].rstrip(" ,;:—-") + "…"
        return name, first
    return name, "Sem descrição no README do upstream."


def generate(upstream, out):
    brands = {p.parent.name: p for p in sorted((upstream / "design-md").glob("*/DESIGN.md"))}
    if len(brands) < MIN_BRANDS:
        sys.exit(f"Só {len(brands)} DESIGN.md no upstream (mínimo {MIN_BRANDS}); nada foi alterado.")

    cats = parse_collection(read_text(upstream / "README.md"))
    listed = set()
    lines = [f"# Índice: {len(brands)} DESIGN.md", "",
             "Caminho de cada arquivo: `references/<slug>/DESIGN.md`. "
             "Descrições copiadas do README do VoltAgent/awesome-design-md (em inglês).", ""]
    for cat, entries in cats:
        rows = [(n, s, d) for n, s, d in entries if s in brands]
        if not rows:
            continue
        lines += [f"## {cat}", ""]
        for name, slug, desc in rows:
            lines.append(f"- **{name}** (`{slug}`): {desc}")
            listed.add(slug)
        lines.append("")
    extra = [s for s in brands if s not in listed]
    if extra:
        lines += ["## Outros", ""]
        for slug in extra:
            name, desc = describe_unlisted(read_text(brands[slug]), slug)
            lines.append(f"- **{name}** (`{slug}`): {desc}")
        lines.append("")

    refs = out / "references"
    for slug, src in brands.items():
        (refs / slug).mkdir(parents=True, exist_ok=True)
        (refs / slug / "DESIGN.md").write_text(read_text(src), encoding="utf-8", newline="\n")
    (refs / "INDEX.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    skill_md = SKILL_MD.replace("__COUNT__", str(len(brands)))
    description = re.search(r"^description: (.+)$", skill_md, re.M).group(1)
    if len(description) > 1024:
        sys.exit(f"description com {len(description)} caracteres (limite do app: 1024).")
    (out / "SKILL.md").write_text(skill_md, encoding="utf-8", newline="\n")
    return len(brands), len(extra)


def tree_hash(folder):
    # Ordena pelo texto do caminho: Path ordena sem caixa no Windows e com caixa no Linux,
    # o que dava hashes diferentes no PC e no GitHub Actions para o mesmo conteúdo.
    h = hashlib.sha256()
    files = sorted((p.relative_to(folder).as_posix(), p) for p in folder.rglob("*") if p.is_file())
    for rel, p in files:
        h.update(rel.encode() + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()


def next_version(old, today):
    parts = (old or "").split(".")
    if len(parts) == 3 and parts[1] == today and parts[2].isdigit():
        return f"1.{today}.{int(parts[2]) + 1}"
    return f"1.{today}.0"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--upstream", required=True, type=Path, help="clone do VoltAgent/awesome-design-md")
    args = ap.parse_args()
    upstream = args.upstream.resolve()

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "design-md"
        count, extra = generate(upstream, out)
        digest = tree_hash(out)
        state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
        if state.get("content_hash") == digest and SKILL.exists():
            print(f"Sem mudanças ({count} DESIGN.md, versão {state.get('version')}).")
            return
        if SKILL.exists():
            shutil.rmtree(SKILL)
        shutil.copytree(out, SKILL)

    lic = upstream / "LICENSE"
    if lic.exists():
        for dest in (ROOT / "LICENSE", PLUGIN / "LICENSE"):
            dest.write_text(read_text(lic), encoding="utf-8", newline="\n")

    manifest_path = PLUGIN / ".claude-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
    manifest["version"] = next_version(manifest.get("version"), today)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    sha = subprocess.run(["git", "-C", str(upstream), "rev-parse", "HEAD"],
                         capture_output=True, text=True).stdout.strip() or "desconhecido"
    state = {"version": manifest["version"], "upstream_commit": sha, "brands": count,
             "content_hash": digest, "synced_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    STATE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Atualizado: {count} DESIGN.md ({extra} fora do README), versão {manifest['version']}, upstream {sha[:7]}.")


if __name__ == "__main__":
    main()
