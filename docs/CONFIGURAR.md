# Configuração (feita uma vez, pelo dono do canal)

Leva uns 15 minutos. No fim, seis chaves (mais uma opcional, para fotos) ficam guardadas no ambiente do Claude. **Nenhuma chave vai no chat nem no repositório.**

## 1. Google Cloud (YouTube)

Use a conta Google **do canal dark**.

1. Abra https://console.cloud.google.com e crie um projeto chamado `canal-dark`.
2. **Ativar as APIs:** menu → *APIs e serviços* → *Biblioteca*. Procure e clique em **Ativar** em:
   - YouTube Data API v3
   - YouTube Analytics API
3. **Chave de API (para a pesquisa de virais):** *APIs e serviços* → *Credenciais* → *Criar credenciais* → *Chave de API*. Em *Restringir chave*, marque só **YouTube Data API v3**. Essa é a `YOUTUBE_API_KEY`.
4. **Tela de consentimento OAuth:** *Google Auth Platform* (ou *Tela de consentimento OAuth*):
   - Tipo de usuário: **Externo**. Nome do app: `canal-dark`. E-mail de suporte: o seu.
   - Em *Público-alvo*, adicione o e-mail do canal como **usuário de teste**.
   - Depois, clique em **Publicar app** (status *Em produção*). Em modo de teste o Google derruba a autorização a cada 7 dias. O aviso "app não verificado" que aparece no login é normal para uso próprio.
5. **Cliente OAuth (para subir vídeos e ler métricas):** *Clientes* (ou *Credenciais*) → *Criar cliente* → tipo **App para computador** → nome `canal-dark`. Copie o **ID do cliente** (`YOUTUBE_CLIENT_ID`) e a **chave secreta** (`YOUTUBE_CLIENT_SECRET`).
6. **Gerar o refresh token**, no seu computador (precisa de Python 3):

   ```bash
   curl -O https://raw.githubusercontent.com/<seu-usuario>/<seu-repositorio>/main/pipeline/get_refresh_token.py
   python3 get_refresh_token.py SEU_CLIENT_ID SEU_CLIENT_SECRET
   ```

   O navegador abre; entre com a conta do canal, clique em *Avançado → Acessar canal-dark (não seguro)* e aceite. O terminal mostra o `YOUTUBE_REFRESH_TOKEN`.

7. **Auditoria do YouTube (para poder publicar):** vídeos enviados pela API por projetos novos ficam travados como privados até o projeto passar pela auditoria gratuita do YouTube. Peça em https://support.google.com/youtube/contact/yt_api_form (*YouTube API Services – Audit and Quota Extension Form*). Descreva: "ferramenta interna que sobe vídeos do meu próprio canal como privados para eu revisar e publicar manualmente; também lê as métricas do meu canal". Enquanto a auditoria não sai, os vídeos continuam subindo como privados para você assistir; se o Studio não deixar publicar algum, os arquivos ficam listados em `registro/`.

## 2. ElevenLabs

1. https://elevenlabs.io → *Developers* (ou ícone do perfil) → *API Keys* → crie uma chave com permissão de **Text to Speech**. Essa é a `ELEVENLABS_API_KEY`.
2. *Voices* → a sua voz clonada → copie o **Voice ID**. Esse é o `ELEVENLABS_VOICE_ID`.

## 3. Fotos para miniaturas (opcional, grátis)

Uma das duas basta:

- **Unsplash:** https://unsplash.com/developers → *Your apps* → *New Application* → copie a **Access Key** (`UNSPLASH_ACCESS_KEY`).
- **Pexels:** https://www.pexels.com/api/ → *Your API Key* (`PEXELS_API_KEY`).

## 4. Guardar as chaves no ambiente do Claude

No Claude, abra o menu do ambiente de nuvem na barra de título da sessão → **Edit** → **Network secrets** (em apps antigos, *API credentials* ou *Environment variables*) e adicione:

| Nome | Valor |
|---|---|
| `YOUTUBE_API_KEY` | chave de API do passo 1.3 |
| `YOUTUBE_CLIENT_ID` | ID do cliente do passo 1.5 |
| `YOUTUBE_CLIENT_SECRET` | chave secreta do passo 1.5 |
| `YOUTUBE_REFRESH_TOKEN` | resultado do passo 1.6 |
| `ELEVENLABS_API_KEY` | chave do passo 2.1 |
| `ELEVENLABS_VOICE_ID` | ID do passo 2.2 (opcional: o `voice_id` de `CANAL.md` tem prioridade) |
| `UNSPLASH_ACCESS_KEY` ou `PEXELS_API_KEY` | passo 3 (opcional) |

As chaves valem a partir da **próxima sessão**. Para conferir, peça ao Claude: "rode `bash pipeline/setup.sh`". Ele mostra quais chaves existem, sem mostrar os valores.

## 5. Rede

Se o ambiente estiver em acesso de rede limitado, libere em **Network access → Allowed domains**: `googleapis.com`, `oauth2.googleapis.com`, `youtubeanalytics.googleapis.com`, `api.elevenlabs.io`, `coverr.co`, `cdn.coverr.co`, `mixkit.co`, `assets.mixkit.co`, `memescreens.com`, `media.memescreens.com`, `myinstants.com`, `cdn.jsdelivr.net`, `huggingface.co` (modelo de transcrição), `api.unsplash.com`, `images.unsplash.com`, `api.pexels.com`, `images.pexels.com`, `fonts.googleapis.com`, `fonts.gstatic.com`.
