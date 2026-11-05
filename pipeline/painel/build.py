"""Gera o painel do canal (pipeline/painel/dist/index.html) a partir de registro/videos.json e CANAL.md.

Uso: python3 pipeline/painel/build.py
Depois publique dist/index.html com a ferramenta Artifact no MESMO link guardado em CANAL.md → "Painel"
(veja pipeline/painel/README.md). O arquivo é autocontido: os dados vão embutidos na página.
"""
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def canal_field(text, label):
    m = re.search(r"\*\*" + re.escape(label) + r":\*\*\s*(.+)", text)
    v = m.group(1).strip() if m else ""
    return "" if "[DEFINIR" in v else v


def main():
    reg = json.load(open(os.path.join(ROOT, "registro", "videos.json"), encoding="utf-8"))
    canal = open(os.path.join(ROOT, "CANAL.md"), encoding="utf-8").read()
    links = []
    for label in ("Link da oferta principal", "Link do painel (artefato)"):
        v = canal_field(canal, label)
        for u in re.findall(r"https?://\S+", v):
            links.append({"label": label.replace(" (artefato)", ""), "url": u.rstrip(").,")})
    vendas = os.path.join(ROOT, "vendas", "produtos")
    if os.path.isdir(vendas):
        for name in sorted(os.listdir(vendas)):
            cfg = os.path.join(vendas, name, "pagina.json")
            if os.path.exists(cfg):
                p = json.load(open(cfg, encoding="utf-8"))
                if p.get("url_publicada"):
                    links.append({"label": f"Página de vendas: {p.get('nome', name)}", "url": p["url_publicada"]})
                if p.get("checkout", {}).get("url"):
                    links.append({"label": f"Checkout: {p.get('nome', name)}", "url": p["checkout"]["url"]})
    data = {
        "canal": canal_field(canal, "Nicho") or "Meu canal",
        "atualizado": dt.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "videos": reg.get("videos", []),
        "links": links,
    }
    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    os.makedirs(os.path.join(HERE, "dist"), exist_ok=True)
    out = os.path.join(HERE, "dist", "index.html")
    open(out, "w", encoding="utf-8").write(tpl.replace("/*DADOS*/null", blob))
    print(out)


if __name__ == "__main__":
    sys.exit(main())
