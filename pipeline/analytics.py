"""Puxa os números do canal (YouTube Analytics API + Data API).

Uso:
  python3 pipeline/analytics.py --days 28 --out registro/metricas/AAAA-MM-DD.json
  python3 pipeline/analytics.py --retencao <VIDEO_ID> --out retencao.csv     # curva de retenção (para pipeline/yt/retencao.py)

Mostra, por vídeo: views, minutos assistidos, duração média, % média assistida,
inscritos ganhos, likes, comentários e compartilhamentos, mais o multiplicador sobre a mediana do canal.
"""
import argparse
import datetime as dt
import json
import os
import statistics

from common import google_access_token, http

METRICS = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,likes,comments,shares"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--out")
    ap.add_argument("--retencao", help="ID do vídeo: salva a curva de retenção em CSV (posição %, % assistindo)")
    a = ap.parse_args()
    token = google_access_token()
    auth = {"Authorization": f"Bearer {token}"}
    if a.retencao:
        rep = http("GET", "https://youtubeanalytics.googleapis.com/v2/reports", headers=auth, params={
            "ids": "channel==MINE", "startDate": "2020-01-01", "endDate": dt.date.today().isoformat(),
            "metrics": "audienceWatchRatio", "dimensions": "elapsedVideoTimeRatio", "filters": f"video=={a.retencao}"})
        linhas = sorted((r[0] * 100, r[1] * 100) for r in rep.get("rows", []))
        if not linhas:
            raise SystemExit("A API não devolveu curva de retenção para esse vídeo (precisa de views suficientes e de estar público).")
        saida = a.out or f"retencao-{a.retencao}.csv"
        with open(saida, "w", encoding="utf-8") as f:
            f.write("posicao_pct,assistindo_pct\n" + "\n".join(f"{x:.2f},{y:.2f}" for x, y in linhas) + "\n")
        print(f"{len(linhas)} pontos em {saida}. Leia com: python3 pipeline/yt/retencao.py {saida} --duration <segundos>")
        return
    end = dt.date.today()
    start = end - dt.timedelta(days=a.days)
    rep = http("GET", "https://youtubeanalytics.googleapis.com/v2/reports", headers=auth, params={
        "ids": "channel==MINE", "startDate": start.isoformat(), "endDate": end.isoformat(),
        "metrics": METRICS, "dimensions": "video", "sort": "-views", "maxResults": 200})
    cols = [c["name"] for c in rep.get("columnHeaders", [])]
    rows = [dict(zip(cols, r)) for r in rep.get("rows", [])]
    ids = [r["video"] for r in rows]
    titles = {}
    for i in range(0, len(ids), 50):
        r = http("GET", "https://www.googleapis.com/youtube/v3/videos", headers=auth,
                 params={"part": "snippet,contentDetails,status", "id": ",".join(ids[i:i + 50])})
        for v in r.get("items", []):
            titles[v["id"]] = {"title": v["snippet"]["title"], "publishedAt": v["snippet"]["publishedAt"],
                               "privacy": v["status"]["privacyStatus"], "duration": v["contentDetails"]["duration"]}
    med = statistics.median([r["views"] for r in rows]) if rows else 0
    for r in rows:
        r.update(titles.get(r["video"], {}))
        r["multiple"] = round(r["views"] / med, 2) if med else None
    out = {"generatedAt": dt.datetime.now().isoformat(timespec="minutes"), "period": [start.isoformat(), end.isoformat()],
           "medianViews": med, "videos": rows}
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(rows)} vídeos com dados · mediana {med} views ({start} a {end})")
    for r in rows:
        print(f"{(r['multiple'] or 0):>6}x {r['views']:>8} views  {r['averageViewPercentage']:>5.1f}% assistido  "
              f"+{r['subscribersGained']} inscr.  {r.get('title', r['video'])[:70]}")


if __name__ == "__main__":
    main()
