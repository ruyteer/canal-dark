"""Gera a narração com a voz clonada no ElevenLabs.

Uso:
  python3 pipeline/tts.py producao/<id>/narracao.txt producao/<id>/narracao.mp3 [--model eleven_v4]

Modelo padrão: eleven_v4 (até 10 mil caracteres por pedido: a narração inteira vai de uma vez).
Textos maiores que --max-chars são divididos por parágrafo e unidos no fim.
Precisa de ELEVENLABS_API_KEY. A voz vem do voice_id em CANAL.md.
"""
import argparse
import os
import subprocess
import tempfile

from common import duration, env, http


def split_text(text, max_chars):
    parts, cur = [], ""
    for para in [p.strip() for p in text.split("\n") if p.strip()]:
        if len(cur) + len(para) + 1 > max_chars and cur:
            parts.append(cur)
            cur = para
        else:
            cur = (cur + "\n\n" + para).strip()
    if cur:
        parts.append(cur)
    return parts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text_file")
    ap.add_argument("out")
    ap.add_argument("--model", default="eleven_v4")
    ap.add_argument("--max-chars", type=int, default=9000)
    ap.add_argument("--stability", type=float, default=0.5)
    ap.add_argument("--similarity", type=float, default=1.0)
    a = ap.parse_args()

    key = env("ELEVENLABS_API_KEY")
    # Fonte única da voz: o voice_id em CANAL.md. A variável de ambiente só é usada se o CANAL.md não tiver um.
    import re
    from common import ROOT
    m = re.search(r"voice_id `([A-Za-z0-9]+)`", open(os.path.join(ROOT, "CANAL.md"), encoding="utf-8").read())
    voice = m.group(1) if m else env("ELEVENLABS_VOICE_ID", required=False)
    if not voice:
        raise SystemExit("Defina a voz em CANAL.md (voice_id).")
    info = http("GET", f"https://api.elevenlabs.io/v1/voices/{voice}", headers={"xi-api-key": key})
    print(f"voz: {info.get('name', '?')} ({voice})")
    text = open(a.text_file, encoding="utf-8").read()
    parts = split_text(text, a.max_chars)
    tmp = tempfile.mkdtemp(prefix="tts-")
    files = []
    for i, p in enumerate(parts):
        audio, _ = http("POST", f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
                        params={"output_format": "mp3_44100_128"},
                        headers={"xi-api-key": key, "Accept": "audio/mpeg"},
                        json_body={"text": p, "model_id": a.model,
                                   "voice_settings": {"stability": a.stability, "similarity_boost": a.similarity}},
                        raw=True, timeout=600)
        f = os.path.join(tmp, f"part{i:02d}.mp3")
        open(f, "wb").write(audio)
        files.append(f)
        print(f"parte {i + 1}/{len(parts)}: {len(p)} caracteres")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    if len(files) == 1:
        os.replace(files[0], a.out)
    else:
        lst = os.path.join(tmp, "list.txt")
        open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c:a", "libmp3lame", "-b:a", "128k", a.out], check=True)
    print(f"narração: {a.out} ({duration(a.out):.1f} s)")


if __name__ == "__main__":
    main()
