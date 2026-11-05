"""Gera o YOUTUBE_REFRESH_TOKEN. Rode no SEU computador, uma única vez.

  python3 get_refresh_token.py <CLIENT_ID> <CLIENT_SECRET>

1. Abre o navegador na tela de autorização do Google.
2. Entre com a conta do CANAL DARK e aceite.
3. O token aparece no terminal. Cole nas chaves do ambiente do Claude como YOUTUBE_REFRESH_TOKEN
   (menu do ambiente → Edit → Network secrets). Nunca cole no chat.

Só usa a biblioteca padrão do Python 3.
"""
import http.server
import json
import secrets
import sys
import urllib.parse
import urllib.request
import webbrowser

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]
PORT = 8765


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    cid, secret = sys.argv[1], sys.argv[2]
    redirect = f"http://127.0.0.1:{PORT}/"
    state = secrets.token_urlsafe(16)
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": redirect, "response_type": "code", "scope": " ".join(SCOPES),
        "access_type": "offline", "prompt": "consent", "state": state})
    result = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if q.get("state", [""])[0] == state and "code" in q:
                result["code"] = q["code"][0]
                msg = "Pronto. Pode fechar esta aba e voltar ao terminal."
            else:
                msg = "Algo deu errado. Volte ao terminal."
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(msg.encode())

        def log_message(self, *a):
            pass

    print("Abrindo o navegador. Se não abrir, acesse:\n" + url)
    webbrowser.open(url)
    srv = http.server.HTTPServer(("127.0.0.1", PORT), H)
    while "code" not in result:
        srv.handle_request()
    data = urllib.parse.urlencode({"code": result["code"], "client_id": cid, "client_secret": secret,
                                   "redirect_uri": redirect, "grant_type": "authorization_code"}).encode()
    tok = json.loads(urllib.request.urlopen("https://oauth2.googleapis.com/token", data=data).read())
    if "refresh_token" not in tok:
        sys.exit(f"O Google não devolveu refresh token: {tok}")
    print("\nYOUTUBE_REFRESH_TOKEN =\n" + tok["refresh_token"])
    print("\nCole esse valor nas chaves do ambiente do Claude (Network secrets). Não cole no chat.")


if __name__ == "__main__":
    main()
