"""Busca vídeos virais recentes do nicho pela YouTube Data API v3.

Uso:
  python3 pipeline/research.py --days 14 --out producao/<id>/pesquisa.json
  python3 pipeline/research.py --days 7 --q "termo 1" --q "termo 2"

Sem --q, usa as palavras-chave da seção "Nicho e público" de CANAL.md.
Custo de cota: 100 unidades por termo (search.list) + ~1 por 50 vídeos.
"""
import argparse
import datetime as dt
import json
import os
import re
import statistics

from common import ROOT, env, http

API = "https://www.googleapis.com/youtube/v3"


def keywords_from_canal():
    text = open(os.path.join(ROOT, "CANAL.md"), encoding="utf-8").read()
    m = re.search(r"\*\*Palavras-chave de pesquisa\*\*[^:]*:\s*(.+)", text)
    if not m or "[DEFINIR" in m.group(1):
        raise SystemExit("Defina as palavras-chave em CANAL.md ou passe --q.")
    return [k.strip(" .;\"'") for k in re.split(r"[,;]", m.group(1)) if k.strip()]


def iso_duration(s):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    if not m:
        return 0
    h, mi, se = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + se


def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--q", action="append")
    ap.add_argument("--per-term", type=int, default=25)
    ap.add_argument("--region", default="BR")
    ap.add_argument("--lang", default="pt")
    ap.add_argument("--out")
    a = ap.parse_args()

    key = env("YOUTUBE_API_KEY")
    terms = a.q or keywords_from_canal()
    after = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=a.days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids, found_by = [], {}
    for q in terms:
        r = http("GET", f"{API}/search", params={
            "part": "snippet", "q": q, "type": "video", "order": "viewCount", "publishedAfter": after,
            "regionCode": a.region, "relevanceLanguage": a.lang, "maxResults": min(a.per_term, 50), "key": key})
        for it in r.get("items", []):
            vid = it["id"]["videoId"]
            if vid not in found_by:
                ids.append(vid)
            found_by.setdefault(vid, []).append(q)

    videos = []
    for group in chunks(ids, 50):
        r = http("GET", f"{API}/videos", params={"part": "snippet,statistics,contentDetails", "id": ",".join(group), "key": key})
        videos += r.get("items", [])
    chan_ids = sorted({v["snippet"]["channelId"] for v in videos})
    subs = {}
    for group in chunks(chan_ids, 50):
        r = http("GET", f"{API}/channels", params={"part": "statistics", "id": ",".join(group), "key": key})
        for c in r.get("items", []):
            subs[c["id"]] = int(c["statistics"].get("subscriberCount", 0) or 0)

    now = dt.datetime.now(dt.timezone.utc)
    rows = []
    for v in videos:
        sn, st = v["snippet"], v.get("statistics", {})
        views = int(st.get("viewCount", 0) or 0)
        pub = dt.datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00"))
        days = max((now - pub).total_seconds() / 86400, 0.25)
        s = subs.get(sn["channelId"], 0)
        dur = iso_duration(v["contentDetails"].get("duration"))
        rows.append({
            "id": v["id"], "url": f"https://www.youtube.com/watch?v={v['id']}", "title": sn["title"],
            "channel": sn["channelTitle"], "channelId": sn["channelId"], "subscribers": s,
            "publishedAt": sn["publishedAt"], "ageDays": round(days, 1), "durationSec": dur,
            "isShort": dur <= 180, "views": views, "viewsPerDay": round(views / days),
            "likes": int(st.get("likes", st.get("likeCount", 0)) or 0), "comments": int(st.get("commentCount", 0) or 0),
            "multiple": round(views / s, 2) if s else None, "terms": found_by.get(v["id"], []),
            "description": sn.get("description", "")[:400],
        })
    rows.sort(key=lambda r: (r["multiple"] or 0), reverse=True)
    med = statistics.median([r["viewsPerDay"] for r in rows]) if rows else 0
    out = {"generatedAt": now.isoformat(), "days": a.days, "terms": terms, "medianViewsPerDay": med, "videos": rows}

    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(rows)} vídeos dos últimos {a.days} dias · mediana {med} views/dia")
    for r in rows[:25]:
        kind = "SHORT" if r["isShort"] else f"{r['durationSec'] // 60}min"
        print(f"{(r['multiple'] or 0):>7}x  {r['viewsPerDay']:>8}/dia  {kind:>5}  {r['channel'][:22]:<22}  {r['title'][:80]}")


if __name__ == "__main__":
    main()
