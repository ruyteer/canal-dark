"""Busca e baixa mídias para a edição.

Comandos:
  coverr-search "<busca>"                 clipes gratuitos do Coverr (os premium são ignorados)
  coverr-get <slug> <saida.mp4>           baixa em 1080p
  mixkit-video <tag>                      lista clipes de uma tag do Mixkit (ex.: video-game, abstract, neon)
  mixkit-get <id> <saida.mp4>             baixa no maior tamanho público (1080 ou 720)
  meme-list [categoria]                   memes do MemeScreens (reactions, funny, effects, gaming, animals, dance)
  meme-get <slug> <saida.webm|.mp4> [--start s] [--dur s] [--crop w:h:x:y] [--height 600] [--sim 0.16] [--nokey]
                                           baixa, recorta o fundo verde e gera WebM com transparência
  sfx-search "<busca>"                    sons do Myinstants
  sfx-get <arquivo.mp3> <saida.mp3> [--dur s]   baixa, corta o silêncio inicial e normaliza
  music-list <genero>                     faixas do Mixkit (ambient, hip-hop, chill, lo-fi-beats, corporate, electronica)
  music-get <id> <saida.mp3>
  sheet <pasta> <saida.png>               folha com um quadro de cada vídeo da pasta, para conferir

Sites que respondem 403 ou pedem verificação não devem ser contornados.
"""
import glob
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

from common import download, duration, fetch_text, run


def coverr_search(q):
    t = fetch_text("https://coverr.co/s?q=" + urllib.parse.quote(q))
    seen = []
    for m in re.finditer(r'alt="([^"]+)" src="https://cdn\.coverr\.co/videos/([a-z0-9-]+)/thumbnail', t):
        alt, slug = html.unescape(m.group(1)), m.group(2)
        if "premium" in slug or "paywall" in slug or slug in [s for s, _ in seen]:
            continue
        seen.append((slug, alt))
    for s, alt in seen[:15]:
        print(f"{s} | {alt}")


def coverr_get(slug, out):
    if "premium" in slug:
        sys.exit("Clipe premium do Coverr: só com conta paga. Escolha outro.")
    download(f"https://cdn.coverr.co/videos/{slug}/1080p.mp4", out)
    print(out, f"{duration(out):.1f}s")


def mixkit_video(tag):
    t = fetch_text(f"https://mixkit.co/free-stock-video/{tag}/")
    for slug in sorted(set(re.findall(r"/free-stock-video/([a-z0-9-]+-\d+)/", t))):
        print(slug.rsplit("-", 1)[1], slug)


def mixkit_get(vid, out):
    last = None
    for size in ("1080", "720"):
        try:
            download(f"https://assets.mixkit.co/videos/{vid}/{vid}-{size}.mp4", out)
            print(out, size, f"{duration(out):.1f}s")
            return
        except RuntimeError as e:
            last = e
    sys.exit(f"Não consegui baixar {vid}: {last}")


def meme_list(cat=None):
    url = f"https://memescreens.com/category/{cat}" if cat else "https://memescreens.com/"
    t = fetch_text(url)
    for s in sorted(set(re.findall(r'href="/clips/([^"]+)"', t))):
        print(s)


def key_color(path, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", path, "-frames:v", "1", "-vf",
                          "crop=4:4:6:6,scale=1:1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return raw[:3].hex()


def meme_get(slug, out, start=0.0, dur=2.5, crop=None, height=600, sim=0.16, nokey=False):
    page = fetch_text(f"https://memescreens.com/clips/{slug}")
    m = re.search(r'https://media\.memescreens\.com/[^"]+\.(?:mp4|webm|mov)', page)
    if not m:
        sys.exit("Não achei o vídeo do meme nessa página.")
    src = out + ".src" + os.path.splitext(m.group(0))[1]
    download(m.group(0), src)
    vf = []
    if crop:
        vf.append(f"crop={crop}")
    if nokey or out.endswith(".mp4"):
        vf += [f"scale=-2:{height}", "fps=30"]
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", src, "-an", "-vf", ",".join(vf),
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out])
    else:
        c = key_color(src, start)
        vf += [f"chromakey=0x{c}:{sim}:0.06", "despill=type=green:mix=0.6", f"scale=-2:{height}", "format=yuva420p"]
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", src, "-an", "-vf", ",".join(vf),
             "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-auto-alt-ref", "0", "-b:v", "2M", "-r", "30", out])
    os.remove(src)
    print(out, f"{dur}s")


def sfx_search(q):
    t = fetch_text("https://www.myinstants.com/pt/search/?name=" + urllib.parse.quote(q))
    seen = []
    for f in re.findall(r"/media/sounds/([^'\"]+\.mp3)", t):
        if f not in seen:
            seen.append(f)
    print("\n".join(seen[:15]))


def sfx_get(name, out, dur=2.0):
    src = out + ".src.mp3"
    download("https://www.myinstants.com/media/sounds/" + name, src)
    fade = max(dur - 0.3, 0)
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af",
         f"silenceremove=start_periods=1:start_threshold=-40dB,atrim=0:{dur},afade=t=out:st={fade}:d=0.3,loudnorm=I=-18:TP=-2",
         "-ar", "44100", out])
    os.remove(src)
    print(out, f"{duration(out):.2f}s")


def music_list(genre):
    t = fetch_text(f"https://mixkit.co/free-stock-music/{genre}/")
    items = re.findall(r'"name":"([^"]+)","genre":"([^"]*)","byArtist":"([^"]*)","duration":"([^"]*)","url":"https://assets\.mixkit\.co/music/(\d+)/\d+\.mp3"', t)
    if not items:
        items = [(i, "", "", "", i) for i in sorted(set(re.findall(r"assets\.mixkit\.co/music/(\d+)/\1\.mp3", t)))]
    for name, g, artist, d, mid in items:
        print(f"{mid} | {name} | {g} | {artist} | {d}")


def music_get(mid, out):
    download(f"https://assets.mixkit.co/music/{mid}/{mid}.mp3", out)
    print(out, f"{duration(out):.1f}s")


def sheet(folder, out):
    files = sorted(glob.glob(os.path.join(folder, "*.mp4")) + glob.glob(os.path.join(folder, "*.webm")))
    if not files:
        sys.exit("Nenhum vídeo na pasta.")
    tmp = out + ".d"
    os.makedirs(tmp, exist_ok=True)
    for i, f in enumerate(files):
        name = os.path.splitext(os.path.basename(f))[0].replace("'", "")
        t = duration(f) * 0.4
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", f, "-frames:v", "1", "-vf",
             "scale=384:216:force_original_aspect_ratio=decrease,pad=384:216:(ow-iw)/2:(oh-ih)/2:color=gray,"
             f"drawtext=text='{name}':x=4:y=4:fontsize=14:fontcolor=yellow:box=1:boxcolor=black@0.6",
             os.path.join(tmp, f"{i:03d}.png")])
    cols = 4
    run(["ffmpeg", "-v", "error", "-y", "-pattern_type", "glob", "-i", os.path.join(tmp, "*.png"),
         "-filter_complex", f"tile={cols}x{(len(files) + cols - 1) // cols}", out])
    for p in glob.glob(os.path.join(tmp, "*.png")):
        os.remove(p)
    os.rmdir(tmp)
    print(out)


def opt(args, name, default, cast=str):
    if name in args:
        i = args.index(name)
        v = args[i + 1]
        del args[i:i + 2]
        return cast(v)
    return default


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    cmd = args.pop(0)
    if cmd == "coverr-search": coverr_search(" ".join(args))
    elif cmd == "coverr-get": coverr_get(*args)
    elif cmd == "mixkit-video": mixkit_video(args[0])
    elif cmd == "mixkit-get": mixkit_get(*args)
    elif cmd == "meme-list": meme_list(args[0] if args else None)
    elif cmd == "meme-get":
        nokey = "--nokey" in args
        if nokey:
            args.remove("--nokey")
        start = opt(args, "--start", 0.0, float); dur = opt(args, "--dur", 2.5, float)
        crop = opt(args, "--crop", None); height = opt(args, "--height", 600, int); sim = opt(args, "--sim", 0.16, float)
        meme_get(args[0], args[1], start, dur, crop, height, sim, nokey)
    elif cmd == "sfx-search": sfx_search(" ".join(args))
    elif cmd == "sfx-get":
        dur = opt(args, "--dur", 2.0, float)
        sfx_get(args[0], args[1], dur)
    elif cmd == "music-list": music_list(args[0])
    elif cmd == "music-get": music_get(*args)
    elif cmd == "sheet": sheet(*args)
    else:
        print(__doc__)
        sys.exit(1)
    time.sleep(0.5)


if __name__ == "__main__":
    main()
