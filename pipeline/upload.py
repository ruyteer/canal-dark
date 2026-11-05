"""Sobe um vídeo para o YouTube como privado e AGENDADO (nunca público na hora).

Uso:
  python3 pipeline/upload.py <video.mp4> --meta <upload.json> --days 1 --at 18:00 [--registry <id>:<tipo>]

--days / --at: publica daqui a N dias no horário dado (horário de Brasília). Padrão: amanhã, 18:00.
O vídeo fica privado até essa hora; o dono do canal revisa, muda o horário ou publica antes pelo Studio.

upload.json:
  {"title": "...", "description": "...", "tags": ["..."], "categoryId": "22",
   "thumbnail": "caminho/opcional.jpg", "syntheticMedia": false}

Não existe opção para publicar na hora: a visibilidade é fixada em "private" com publishAt.
"""
import datetime as dt
from zoneinfo import ZoneInfo
import argparse
import http.client as httpclient
import json
import os
import sys
import urllib.parse

from common import google_access_token, http
import registry


def publish_time(days, at):
    tz = ZoneInfo("America/Sao_Paulo")
    h, m = (int(x) for x in at.split(":"))
    when = (dt.datetime.now(tz) + dt.timedelta(days=days)).replace(hour=h, minute=m, second=0, microsecond=0)
    if when < dt.datetime.now(tz) + dt.timedelta(hours=12):
        when += dt.timedelta(days=1)
    return when


def upload(path, meta, publish_at):
    token = google_access_token()
    body = {
        "snippet": {
            "title": meta["title"][:100],
            "description": meta.get("description", "")[:4900],
            "tags": meta.get("tags", [])[:30],
            "categoryId": str(meta.get("categoryId", "22")),
            "defaultLanguage": "pt-BR",
            "defaultAudioLanguage": "pt-BR",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": bool(meta.get("syntheticMedia", False)),
        },
    }
    size = os.path.getsize(path)
    content, headers = http("POST", "https://www.googleapis.com/upload/youtube/v3/videos",
                            params={"uploadType": "resumable", "part": "snippet,status"},
                            headers={"Authorization": f"Bearer {token}", "X-Upload-Content-Type": "video/mp4",
                                     "X-Upload-Content-Length": str(size)},
                            json_body=body, raw=True)
    loc = urllib.parse.urlparse(headers["Location"])
    conn = httpclient.HTTPSConnection(loc.netloc, timeout=3600)
    with open(path, "rb") as f:
        conn.request("PUT", loc.path + "?" + loc.query, body=f,
                     headers={"Authorization": f"Bearer {token}", "Content-Type": "video/mp4", "Content-Length": str(size)})
        resp = conn.getresponse()
        data = resp.read()
    if resp.status not in (200, 201):
        sys.exit(f"Upload falhou ({resp.status}): {data[:600]!r}")
    video = json.loads(data)
    if video.get("status", {}).get("privacyStatus") != "private":
        print("ATENÇÃO: o vídeo não voltou como privado. Confira no Studio agora.")
    thumb = meta.get("thumbnail")
    if thumb and os.path.exists(thumb):
        try:
            img = open(thumb, "rb").read()
            http("POST", "https://www.googleapis.com/upload/youtube/v3/thumbnails/set", params={"videoId": video["id"]},
                 headers={"Authorization": f"Bearer {token}", "Content-Type": "image/jpeg"}, data=img)
        except RuntimeError as e:
            print(f"Miniatura não enviada (a conta precisa estar verificada por telefone): {e}")
    return video


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--meta", required=True)
    ap.add_argument("--registry", help="<id>:<tipo>, ex.: 2026-11-12-salarios:longo")
    ap.add_argument("--days", type=int, default=1, help="publicar daqui a N dias (mínimo 1)")
    ap.add_argument("--at", default="18:00", help="horário de Brasília, HH:MM")
    a = ap.parse_args()
    meta = json.load(open(a.meta, encoding="utf-8"))
    when = publish_time(max(a.days, 1), a.at)
    v = upload(a.video, meta, when)
    url = f"https://www.youtube.com/watch?v={v['id']}"
    sched = v.get("status", {}).get("publishAt")
    label = when.strftime("%d/%m %H:%M")
    print(f"enviado como privado, agendado para {label} (Brasília): {url}")
    if not sched:
        print("ATENÇÃO: o YouTube não aceitou o agendamento (projeto da API ainda sem auditoria?). O vídeo ficou só privado.")
    print(f"editar no Studio: https://studio.youtube.com/video/{v['id']}/edit")
    if a.registry:
        pid, kind = a.registry.split(":", 1)
        status = f"agendado para {label}" if sched else "privado (agendamento não aceito)"
        registry.set_item(pid, kind, {"title": meta["title"], "youtube_id": v["id"], "url": url,
                                      "status": status, "publish_at": when.isoformat(), "file": a.video})
        registry.render_table()


if __name__ == "__main__":
    main()
