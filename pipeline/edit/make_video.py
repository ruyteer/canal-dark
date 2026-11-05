"""Monta e renderiza o vídeo longo e os Shorts a partir de producao/<id>/plan.json.

Uso:
  python3 pipeline/edit/make_video.py producao/<id> --transcribe   # transcreve (se preciso), monta o longo, confere e tira capturas
  python3 pipeline/edit/make_video.py producao/<id> --render       # renderiza o longo e todos os Shorts
  python3 pipeline/edit/make_video.py producao/<id> --render --only short-2
  python3 pipeline/edit/make_video.py producao/<id> --snap --only short-1   # só capturas de um Short

Saída: producao/<id>/render/longo.mp4 e short-N.mp4, mais os projetos HyperFrames em hf-<nome>/.
"""
import argparse
import glob
import html
import json
import os
import re
import shutil
import subprocess
import sys

EDIT = os.path.dirname(os.path.abspath(__file__))
HF = os.path.join(EDIT, "node_modules", ".bin", "hyperframes")
ENV = dict(os.environ, DO_NOT_TRACK="1", HYPERFRAMES_NO_TELEMETRY="1", HYPERFRAMES_SKIP_SKILLS="1")
shell = sorted(glob.glob("/opt/pw-browsers/chromium_headless_shell-*/**/headless_shell", recursive=True))
if shell:
    ENV["PRODUCER_HEADLESS_SHELL_PATH"] = shell[-1]


def sh(cmd, cwd=None, capture=False):
    r = subprocess.run(cmd, cwd=cwd, env=ENV, text=True, capture_output=capture)
    if r.returncode != 0:
        if capture:
            sys.stderr.write((r.stdout or "")[-3000:] + (r.stderr or "")[-3000:])
        sys.exit(f"falhou: {' '.join(cmd[:4])}…")
    return r.stdout if capture else ""


def probe_duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True, check=True).stdout.strip())


# ---------- transcript ----------
def transcribe(prod):
    out = os.path.join(prod, "transcript.json")
    if os.path.exists(out):
        return out
    res = sh([HF, "transcribe", "narracao.mp3", "--model", "small", "--language", "pt", "--json"], cwd=prod, capture=True)
    info = json.loads(res.strip().splitlines()[-1])
    if os.path.abspath(info["transcriptPath"]) != os.path.abspath(out):
        shutil.copy(info["transcriptPath"], out)
    print(f"transcrição: {info.get('wordCount')} palavras")
    return out


def load_words(prod, fixes):
    raw = json.load(open(os.path.join(prod, "transcript.json")))
    raw = raw if isinstance(raw, list) else raw.get("words", [])
    words = []
    for w in raw:
        t, s, e = w["text"], w["start"], w["end"]
        parts = fixes.get(t, t).split()
        n = len(parts) or 1
        for k, p in enumerate(parts):
            words.append({"t": p, "s": s + (e - s) * k / n, "e": s + (e - s) * (k + 1) / n})
    return words


def group_words(words, max_words):
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        if len(cur) >= max_words or re.search(r"[.,?!:;]$", w["t"]) or (nxt and nxt["s"] - w["e"] >= 0.15) or not nxt:
            groups.append(cur)
            cur = []
    return groups


# ---------- window helpers (Shorts) ----------
def clip_items(items, ws, we, has_end=True):
    out = []
    for it in items:
        s = it["start"]
        e = it.get("end", s + 2.5)
        if e <= ws or s >= we:
            continue
        n = dict(it)
        n["start"] = max(s, ws) - ws
        if has_end:
            n["end"] = min(e, we) - ws
        if "media_start" in it:
            n["media_start"] = it.get("media_start", 0) + max(0, ws - s)
        out.append(n)
    return out


# ---------- build one composition ----------
def build(prod, plan, name, cfg, orient, window=None, hook=None):
    proj = os.path.join(prod, f"hf-{name}")
    os.makedirs(proj, exist_ok=True)
    for f in ("hyperframes.json", "meta.json"):
        src = os.path.join(EDIT, "project", f)
        if os.path.exists(src):
            shutil.copy(src, proj)
    assets_link = os.path.join(proj, "assets")
    if not os.path.exists(assets_link):
        os.symlink(os.path.abspath(os.path.join(prod, "assets")), assets_link)

    W, H = (1920, 1080) if orient == "landscape" else (1080, 1920)
    narr_src = os.path.join(prod, "narracao.mp3")
    narr_dst = os.path.join(proj, "narracao.mp3")
    words = load_words(prod, plan.get("fixes", {}))
    bg, memes, sfx = cfg.get("bg", []), cfg.get("memes", []), cfg.get("sfx", [])
    music, offer = cfg.get("music"), cfg.get("offer")
    if window:
        ws, we = window
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ws), "-to", str(we), "-i", narr_src,
                        "-c:a", "libmp3lame", "-b:a", "160k", narr_dst], check=True)
        DUR = round(we - ws, 2)
        words = [dict(w, s=w["s"] - ws, e=w["e"] - ws) for w in words if w["s"] >= ws - 0.01 and w["e"] <= we + 0.05]
        bg, memes = clip_items(bg, ws, we), clip_items(memes, ws, we)
        sfx = [dict(x, start=x["start"] - ws) for x in sfx if ws <= x["start"] < we - 0.3]
        offer = None
        if music:
            music = dict(music, media_start=music.get("media_start", 0) + ws)
    else:
        shutil.copy(narr_src, narr_dst)
        DUR = round(probe_duration(narr_src), 2)

    media, js = [], ["const tl = gsap.timeline({ paused: true });"]
    for i, b in enumerate(bg):
        s, e = b["start"], min(b["end"], DUR)
        media.append(f'<video id="bg{i:02d}" class="clip bg" src="{b["file"]}" muted playsinline data-start="{s:.2f}" '
                     f'data-duration="{e - s:.2f}" data-media-start="{b.get("media_start", 0)}" data-track-index="1"></video>')
        a, z = (1.0, 1.07) if i % 2 == 0 else (1.07, 1.0)
        js.append(f'tl.fromTo("#bg{i:02d}", {{scale: {a}}}, {{scale: {z}, duration: {e - s:.2f}, ease: "none"}}, {s:.2f});')
    for i, m in enumerate(memes):
        s, e, kind = m["start"], min(m["end"], DUR), m.get("kind", "side")
        media.append(f'<video id="meme{i}" class="clip meme {kind}" src="{m["file"]}" muted playsinline '
                     f'data-start="{s:.2f}" data-duration="{e - s:.2f}" data-media-start="{m.get("media_start", 0)}" data-track-index="3"></video>')
        if kind == "full":
            js.append(f'tl.fromTo("#meme{i}", {{opacity: 0}}, {{opacity: 1, duration: 0.08}}, {s:.2f});')
        else:
            js.append(f'tl.fromTo("#meme{i}", {{scale: 0.4, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.28, ease: "back.out(2)"}}, {s:.2f});')
            js.append(f'tl.to("#meme{i}", {{scale: 0.6, opacity: 0, duration: 0.16, ease: "power2.in"}}, {max(e - 0.17, s + 0.3):.2f});')
    media.append(f'<audio id="narr" src="narracao.mp3" data-start="0" data-duration="{DUR}" data-volume="1" data-track-index="5"></audio>')
    for i, x in enumerate(sfx):
        d = probe_duration(os.path.join(prod, x["file"]))
        d = min(d, DUR - x["start"])
        media.append(f'<audio id="sfx{i}" src="{x["file"]}" data-start="{x["start"]:.2f}" data-duration="{d:.2f}" '
                     f'data-volume="{x.get("volume", 0.45)}" data-track-index="{6 + i % 2}"></audio>')
    if not music:
        sys.exit("O plano não tem música de fundo (longo.music). Música lo-fi é obrigatória: veja CANAL.md.")
    # Música de fundo em loop até o fim do vídeo (as faixas costumam ter 1 a 3 min).
    md = probe_duration(os.path.join(prod, music["file"]))
    ms = music.get("media_start", 0) % max(md - 1, 1)
    vol = music.get("volume", 0.14)
    t, k = 0.0, 0
    while t < DUR - 0.05:
        seg = min(md - ms, DUR - t)
        first, last = k == 0, t + seg >= DUR - 0.05
        fin = 1.5 if first else 0.8
        fout = 2.0 if last else 0.8
        media.append(f'<audio id="music{k}" src="{music["file"]}" data-start="{t:.2f}" data-duration="{seg:.2f}" '
                     f'data-media-start="{ms:.2f}" data-volume="{vol}" data-fade-in="{fin}" data-fade-out="{fout}" '
                     f'data-track-index="{8 + k % 2}"></audio>')
        t += seg
        ms = 0.0
        k += 1

    caps = []
    groups = group_words(words, plan.get("caption_words", 3 if orient == "landscape" else 2))
    for gi, g in enumerate(groups):
        spans = " ".join(f'<span class="w" id="g{gi}w{wi}">{html.escape(re.sub(r"[.,;:]+$", "", w["t"]))}</span>' for wi, w in enumerate(g))
        caps.append(f'<div class="grp" id="g{gi}">{spans}</div>')
        gs = max(g[0]["s"] - 0.05, 0.12)
        ge = g[-1]["e"] + 0.08
        if gi + 1 < len(groups):
            ge = min(ge, groups[gi + 1][0]["s"] - 0.06)
        ge = min(max(ge, gs + 0.25), DUR - 0.02)
        js.append(f'tl.set("#g{gi}", {{visibility: "visible"}}, {gs:.3f});')
        js.append(f'tl.fromTo("#g{gi}", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.12, ease: "power2.out"}}, {gs:.3f});')
        for wi, w in enumerate(g):
            js.append(f'tl.fromTo("#g{gi}w{wi}", {{color: "#ffffff", scale: 1}}, {{color: "{plan.get("accent", "#FFD43B")}", scale: 1.08, duration: 0.07}}, {w["s"]:.3f});')
            js.append(f'tl.to("#g{gi}w{wi}", {{color: "#ffffff", scale: 1, duration: 0.1}}, {max(w["e"], w["s"] + 0.12):.3f});')
        js.append(f'tl.to("#g{gi}", {{opacity: 0, duration: 0.08}}, {ge - 0.08:.3f});')
        js.append(f'tl.set("#g{gi}", {{opacity: 0, visibility: "hidden"}}, {ge:.3f});')

    overlays = []
    if offer:
        overlays.append(f'<div id="offer"><span class="dot"></span><span>{html.escape(offer.get("text", "Link na descrição"))}</span></div>')
        js.append(f'tl.fromTo("#offer", {{opacity: 0, y: -20}}, {{opacity: 1, y: 0, duration: 0.35, ease: "power2.out"}}, {offer["start"]:.2f});')
        js.append(f'tl.to("#offer", {{opacity: 0, duration: 0.3}}, {offer["end"] - 0.3:.2f});')
    if hook:
        overlays.append(f'<div id="hook">{html.escape(hook)}</div>')
        js.append('tl.fromTo("#hook", {opacity: 0, y: -16}, {opacity: 1, y: 0, duration: 0.3, ease: "power2.out"}, 0.15);')
    js.append(f'tl.fromTo("#fadein", {{opacity: 1}}, {{opacity: 0, duration: 0.4}}, 0);')
    js.append(f'tl.fromTo("#fade", {{opacity: 0}}, {{opacity: 1, duration: 0.6, ease: "power1.in"}}, {DUR - 0.65:.2f});')
    js.append('window.__timelines["main"] = tl;')

    tpl = open(os.path.join(EDIT, "template.tpl")).read()
    doc = (tpl.replace("{{ORIENT}}", orient).replace("{{W}}", str(W)).replace("{{H}}", str(H)).replace("{{DUR}}", str(DUR))
              .replace("{{ACCENT}}", plan.get("accent", "#FFD43B")).replace("{{FONT}}", plan.get("font", "Inter"))
              .replace("{{MEDIA}}", "\n      ".join(media)).replace("{{CAPTIONS}}", "\n        ".join(caps))
              .replace("{{OVERLAYS}}", "\n      ".join(overlays)).replace("{{JS}}", "\n      ".join(js)))
    open(os.path.join(proj, "index.html"), "w").write(doc)
    lint = subprocess.run([HF, "lint"], cwd=proj, env=ENV, text=True, capture_output=True)
    errors = [l for l in lint.stdout.splitlines() if "✗" in l]
    summary = [l for l in lint.stdout.splitlines() if "error(s)" in l]
    print(f"{name}: {DUR}s, {len(bg)} fundos, {len(memes)} memes, {len(sfx)} sons · {summary[-1].strip() if summary else ''}")
    for l in errors:
        print("  ", l.strip())
    return proj, DUR, (memes, bg)


def snapshot(proj, dur, memes):
    times = sorted({round(m["start"] + 0.6, 1) for m in memes} | {round(dur * f, 1) for f in (0.05, 0.3, 0.55, 0.8)})
    times = [t for t in times if 0 < t < dur][:16]
    shutil.rmtree(os.path.join(proj, "snaps"), ignore_errors=True)
    sh([HF, "snapshot", "--at", ",".join(map(str, times)), "--no-end", "--describe", "false", "-o", "snaps"], cwd=proj, capture=True)
    for f in sorted(glob.glob(os.path.join(proj, "snaps", "contact-sheet*.jpg"))):
        print("captura:", f)


def render(prod, proj, name):
    out_dir = os.path.join(prod, "render")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{name}.mp4")
    sh([HF, "render", "-q", "standard", "-f", "30", "-w", "4", "-o", out], cwd=proj, capture=True)
    print("render:", out, f"{os.path.getsize(out) / 1e6:.0f} MB")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prod")
    ap.add_argument("--transcribe", action="store_true")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--snap", action="store_true")
    ap.add_argument("--only")
    a = ap.parse_args()
    prod = os.path.abspath(a.prod)
    if not os.path.exists(HF):
        sys.exit("Rode antes: bash pipeline/setup.sh")
    if a.transcribe:
        transcribe(prod)
    plan = json.load(open(os.path.join(prod, "plan.json")))
    jobs = [("longo", plan["longo"], "landscape", None, None)]
    for s in plan.get("shorts", []):
        jobs.append((s["name"], plan["longo"], "portrait", (s["start"], s["end"]), s.get("hook")))
    if a.only:
        jobs = [j for j in jobs if j[0] == a.only]
    elif a.transcribe and not a.render:
        jobs = jobs[:1]
    for name, cfg, orient, window, hook in jobs:
        proj, dur, (memes, _) = build(prod, plan, name, cfg, orient, window, hook)
        if a.transcribe or a.snap:
            snapshot(proj, dur, memes)
        if a.render:
            render(prod, proj, name)


if __name__ == "__main__":
    main()
