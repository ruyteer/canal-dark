"""transcrever.py: baixa as LEGENDAS (não o vídeo) de uma lista de vídeos do YouTube e junta tudo em um .md.

Rode no SEU computador (o YouTube bloqueia download automático vindo de servidores na nuvem; do seu computador, com o seu IP, costuma funcionar).

  pip install yt-dlp
  python3 transcrever.py urls.txt                 # urls.txt: uma URL ou ID por linha
  python3 transcrever.py "https://youtu.be/sNCefXBrY_A" "https://youtu.be/OtbLL6OBNE4"

Saída: transcricoes.md (um bloco por vídeo, com título, canal, link e o texto com marcas de tempo a cada ~30 s).
Depois é só mandar o transcricoes.md para o Claude analisar. Usa só as legendas que o próprio YouTube mostra
em "Mostrar transcrição" (manuais ou automáticas). Vídeo sem legenda é pulado e listado no final.
"""
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import time


def ts(s):
    h, m, sec = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(sec.replace(",", "."))


def ler_vtt(path):
    """Devolve [(segundos, texto)] sem repetições (as legendas automáticas repetem linhas)."""
    cues, ult = [], ""
    t = 0.0
    for line in open(path, encoding="utf-8", errors="replace"):
        m = re.match(r"(\d+:\d\d:\d\d[.,]\d+|\d\d:\d\d[.,]\d+)\s*-->", line)
        if m:
            raw = m.group(1)
            t = ts(raw if raw.count(":") == 2 else "0:" + raw)
            continue
        line = re.sub(r"<[^>]+>", "", line).strip()
        if not line or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")) or "-->" in line:
            continue
        if line != ult:
            cues.append((t, line))
            ult = line
    return cues


def bloco(cues, passo=30):
    out, marca, buf = [], -passo, []
    for t, txt in cues:
        if t - marca >= passo and buf:
            out.append(f"[{int(marca // 60):02d}:{int(marca % 60):02d}] " + " ".join(buf))
            buf = []
        if not buf:
            marca = t
        buf.append(txt)
    if buf:
        out.append(f"[{int(marca // 60):02d}:{int(marca % 60):02d}] " + " ".join(buf))
    return "\n\n".join(out)


def baixar(url, pasta):
    vid = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", url)
    vid = vid.group(1) if vid else url.strip()
    cmd = [sys.executable, "-m", "yt_dlp", "--skip-download", "--write-auto-subs", "--write-subs", "--sub-langs", "pt.*,en.*,es.*",
           "--sub-format", "vtt", "--print-json", "--no-warnings", "--sleep-requests", "2", "--sleep-subtitles", "6", "-o", os.path.join(pasta, "%(id)s.%(ext)s"),
           f"https://www.youtube.com/watch?v={vid}"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    except FileNotFoundError:
        sys.exit("Python não encontrado.")
    if "No module named yt_dlp" in (r.stderr or ""):
        sys.exit("yt-dlp não está instalado neste Python. Rode: python3 -m pip install -U --pre yt-dlp")
    info = {}
    try:
        info = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        pass
    arqs = sorted(glob.glob(os.path.join(pasta, vid + ".*.vtt")))
    arqs.sort(key=lambda a: (0 if ".pt" in a else 1 if ".en" in a else 2))  # prefere o idioma do vídeo
    return vid, info, (arqs[0] if arqs else None), (r.stderr or "")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    urls = []
    for a in args:
        urls += [l.strip() for l in open(a, encoding="utf-8")] if os.path.isfile(a) else [a]
    urls = [u for u in urls if u and not u.startswith("#")]
    pulados, partes = [], []
    with tempfile.TemporaryDirectory() as pasta:
        for u in urls:
            for tentativa in range(3):  # se o YouTube limitar (429), espera e tenta de novo, sem pressa
                vid, info, vtt, err = baixar(u, pasta)
                if vtt or "429" not in err:
                    break
                espera = 90 * (tentativa + 1)
                print(f"   o YouTube limitou os pedidos (429). Aguardando {espera}s e tentando de novo...")
                time.sleep(espera)
            if vtt:
                time.sleep(10)  # intervalo entre vídeos
            if not vtt:
                linhas = [l for l in err.strip().splitlines() if l.strip()]
                motivo = linhas[-1] if linhas else "o YouTube não devolveu legenda para este vídeo"
                pulados.append((u, motivo))
                print("sem legenda:", u.split("#")[0].strip(), "\n   motivo:", motivo[:300])
                if "Sign in" in err or "bot" in err.lower():
                    print("   (o YouTube pediu confirmação de que você não é um robô: eu não contorno isso; tente de outra rede ou mande as transcrições copiadas do YouTube)")
                if "JavaScript runtime" in err or "js-runtimes" in err or "deno" in err.lower():
                    print("   (a versão nova do yt-dlp precisa de um executor de JavaScript: instale o Deno, https://deno.com, e tente de novo)")
                continue
            texto = bloco(ler_vtt(vtt))
            titulo = info.get("title", vid)
            print("ok:", titulo[:70])
            partes.append(f"# {titulo}\n\n- Canal: {info.get('channel', '?')}\n- Link: https://youtu.be/{vid}\n"
                          f"- Views: {info.get('view_count', '?')} · Duração: {info.get('duration_string', '?')}\n\n{texto}\n")
    with open("transcricoes.md", "w", encoding="utf-8") as f:
        f.write("\n\n---\n\n".join(partes))
        if pulados:
            f.write("\n\n---\n\n# Pulados\n\n" + "\n".join(f"- {u}: {e}" for u, e in pulados))
    print(f"\n{len(partes)} transcrições em transcricoes.md ({len(pulados)} puladas)")


if __name__ == "__main__":
    main()
