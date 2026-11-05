"""Funções compartilhadas pelo pipeline. Só biblioteca padrão."""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "Mozilla/5.0 (canal-dark pipeline)"


def env(name, required=True):
    v = os.environ.get(name, "").strip()
    if required and not v:
        sys.exit(f"Falta a variável de ambiente {name}. Configure nas chaves do ambiente (nunca no chat).")
    return v


def http(method, url, *, params=None, headers=None, data=None, json_body=None, timeout=120, raw=False):
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params, doseq=True)
    h = {"User-Agent": UA}
    h.update(headers or {})
    body = data
    if json_body is not None:
        body = json.dumps(json_body).encode()
        h.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            content = r.read()
            if raw:
                return content, r.headers
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="ignore")[:800]
        raise RuntimeError(f"HTTP {e.code} em {url.split('?')[0]}: {detail}") from None


def fetch_text(url, timeout=60):
    content, _ = http("GET", url, raw=True, timeout=timeout)
    return content.decode(errors="ignore")


def download(url, out, timeout=300):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    content, _ = http("GET", url, raw=True, timeout=timeout)
    with open(out, "wb") as f:
        f.write(content)
    return out


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def google_access_token():
    """Troca o refresh token por um access token do Google."""
    r = http("POST", "https://oauth2.googleapis.com/token", data=urllib.parse.urlencode({
        "client_id": env("YOUTUBE_CLIENT_ID"),
        "client_secret": env("YOUTUBE_CLIENT_SECRET"),
        "refresh_token": env("YOUTUBE_REFRESH_TOKEN"),
        "grant_type": "refresh_token",
    }).encode(), headers={"Content-Type": "application/x-www-form-urlencoded"})
    return r["access_token"]
