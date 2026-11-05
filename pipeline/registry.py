"""Registro de tudo que foi produzido e enviado (registro/videos.json + registro/README.md).

Uso:
  python3 pipeline/registry.py add <id> --title "..." --format "..." --theme "..."   # cria a entrada do vídeo
  python3 pipeline/registry.py set <id> <tipo> key=valor [key=valor...]            # tipo: longo, short-1...
  python3 pipeline/registry.py render-table
  python3 pipeline/registry.py recent [n]                                          # últimos n vídeos (para não repetir)
"""
import datetime as dt
import json
import os
import sys

from common import ROOT

PATH = os.path.join(ROOT, "registro", "videos.json")


def load():
    if os.path.exists(PATH):
        return json.load(open(PATH, encoding="utf-8"))
    return {"videos": []}


def save(d):
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    json.dump(d, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def get_video(d, pid):
    for v in d["videos"]:
        if v["id"] == pid:
            return v
    v = {"id": pid, "created": dt.date.today().isoformat(), "items": {}}
    d["videos"].append(v)
    return v


class _lock:
    """Trava o registro enquanto um processo lê e grava (uploads em paralelo não se atropelam)."""

    def __enter__(self):
        import fcntl
        os.makedirs(os.path.dirname(PATH), exist_ok=True)
        self.f = open(PATH + ".lock", "w")
        fcntl.flock(self.f, fcntl.LOCK_EX)

    def __exit__(self, *exc):
        import fcntl
        fcntl.flock(self.f, fcntl.LOCK_UN)
        self.f.close()


def add(pid, **fields):
    with _lock():
        d = load()
        v = get_video(d, pid)
        v.update({k: val for k, val in fields.items() if val is not None})
        save(d)


def set_item(pid, kind, fields):
    with _lock():
        d = load()
        v = get_video(d, pid)
        item = v["items"].setdefault(kind, {})
        item.update(fields)
        item["updated"] = dt.datetime.now().isoformat(timespec="minutes")
        save(d)


def render_table():
    d = load()
    lines = ["# Registro do canal", "",
             "Atualizado automaticamente. Tudo sobe como **privado e agendado para o dia seguinte**; você revisa, muda o horário ou publica antes pelo Studio.", "",
             "| Data | Vídeo | Formato | Tipo | Título | Link | Status |", "|---|---|---|---|---|---|---|"]
    for v in sorted(d["videos"], key=lambda x: x.get("created", ""), reverse=True):
        items = v.get("items") or {"—": {}}
        for kind, it in items.items():
            link = f"[abrir]({it['url']})" if it.get("url") else "—"
            lines.append(f"| {v.get('created', '')} | {v['id']} | {v.get('format', '')} | {kind} | "
                         f"{it.get('title', v.get('title', ''))} | {link} | {it.get('status', '')} |")
    open(os.path.join(ROOT, "registro", "README.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    cmd = a.pop(0)
    if cmd == "add":
        pid = a.pop(0)
        kv = dict(zip(a[0::2], a[1::2]))
        add(pid, title=kv.get("--title"), format=kv.get("--format"), theme=kv.get("--theme"))
        render_table()
    elif cmd == "set":
        pid, kind = a[0], a[1]
        set_item(pid, kind, dict(x.split("=", 1) for x in a[2:]))
        render_table()
    elif cmd == "render-table":
        render_table()
    elif cmd == "recent":
        n = int(a[0]) if a else 10
        for v in sorted(load()["videos"], key=lambda x: x.get("created", ""), reverse=True)[:n]:
            print(json.dumps({k: v.get(k) for k in ("id", "created", "title", "format", "theme", "assets")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
