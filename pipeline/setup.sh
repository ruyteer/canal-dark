#!/usr/bin/env bash
# Prepara uma sessão nova para rodar o pipeline do canal.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export DO_NOT_TRACK=1 HYPERFRAMES_NO_TELEMETRY=1 HYPERFRAMES_SKIP_SKILLS=1

command -v ffmpeg >/dev/null || { echo "ffmpeg não encontrado"; exit 1; }
command -v node >/dev/null || { echo "node não encontrado"; exit 1; }

cd "$ROOT/pipeline/edit"
if [ ! -d node_modules/hyperframes ]; then
  npm install --silent --no-audit --no-fund >/dev/null 2>&1 || npm install --no-audit --no-fund
fi

cd "$ROOT"
node -e "require('playwright')" 2>/dev/null || [ -d pipeline/edit/node_modules/playwright ] || {
  (cd pipeline/edit && npm install --no-save --silent playwright >/dev/null 2>&1 && npx playwright install chromium >/dev/null 2>&1) || echo "  aviso: instale o playwright (miniaturas, PDF)"; }

echo "== chaves (só a presença, nunca o valor)"
for v in ELEVENLABS_API_KEY ELEVENLABS_VOICE_ID YOUTUBE_API_KEY YOUTUBE_CLIENT_ID YOUTUBE_CLIENT_SECRET YOUTUBE_REFRESH_TOKEN UNSPLASH_ACCESS_KEY PEXELS_API_KEY; do
  if [ -n "${!v:-}" ]; then echo "  ok      $v"; else echo "  FALTA   $v"; fi
done
grep -q "\[DEFINIR" "$ROOT/CANAL.md" && echo "== CANAL.md ainda tem campos [DEFINIR]" || true
echo "== pronto"
