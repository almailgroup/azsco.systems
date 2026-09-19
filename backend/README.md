# AZSCO Assistant — API proxy

This is the only part of the repository that isn't the static site: a small
server-side proxy for the AZSCO Assistant chat widget, deployed separately
(Cloudflare Workers, Vercel, ...) from wherever the site itself is hosted.
Nothing here is served by GitHub Pages — the frontend (everything else in the
repo) is unaffected by anything in this folder.

> Calling an LLM directly from the browser turned out not to work in
> production — most providers' APIs do not support being called from an
> arbitrary website's browser (no CORS), so the widget opens but every reply
> fails. This proxy is the fix: it holds the key server-side and the browser
> talks to it instead, on a domain that can send the right headers.
>
> **Provider: Google Gemini**, via a free API key from
> <https://aistudio.google.com/apikey> (no payment method required). The site
> started on Mistral, but its free tier rate-limits far too aggressively for
> live visitor traffic — a single test message could exhaust it. Gemini's free
> tier is built for exactly this kind of light, ongoing production use.
>
> Deploy one of the functions below, then set `CHAT_ENDPOINT` in
> `tools/build.py` and rebuild.

This proxy adds the API key server-side, so it never reaches the browser.

## What to deploy

| File | For |
| --- | --- |
| `backend/api/chat.js` | Vercel, Netlify Functions, Deno Deploy — anything running a Node/Edge function |
| `backend/workers/chat-worker.js` | Cloudflare Workers |

## Environment variables

| Name | Required | Notes |
| --- | --- | --- |
| `GEMINI_API_KEY` | yes | From <https://aistudio.google.com/apikey>. Set it as a secret, never in a file. |
| `GEMINI_MODEL` | no | Defaults to `gemini-2.5-flash`. See <https://ai.google.dev/gemini-api/docs/models> for current free-tier models and rate limits. |
| `ALLOWED_ORIGIN` | recommended | Comma-separated origins, e.g. `https://www.azsco.systems`. Without it any site can call your endpoint and spend your quota. |

## Deploying on Vercel

Vercel auto-detects a top-level `api/` folder as serverless functions, but
that folder now lives at `backend/api/`. Set the project's **Root Directory**
to `backend` in the Vercel project settings (or pass `--cwd backend` /
run the commands from inside `backend/`) so it finds `api/chat.js`:

```bash
cd backend
vercel deploy
vercel env add GEMINI_API_KEY         # paste the key when prompted
vercel env add ALLOWED_ORIGIN         # https://www.azsco.systems
```

The function is then served at `/api/chat` on whatever domain Vercel gives
that deployment — a separate domain from the site itself, since GitHub Pages
hosts the site. Point `CHAT_ENDPOINT` in `tools/build.py` at that domain's
`/api/chat` URL.

## Deploying on Cloudflare Workers

`backend/workers/chat-worker.js` has no imports, so it can be deployed
straight from the dashboard with no CLI or Node install:

1. Sign up free at <https://dash.cloudflare.com/sign-up> if you don't have an
   account.
2. **Workers & Pages → Create → Create Worker.** Give it a name (e.g.
   `azsco-chat`) and deploy the default template.
3. **Edit code**, delete the placeholder, paste in the full contents of
   `workers/chat-worker.js`, then **Save and deploy**.
4. **Settings → Variables and Secrets → Add.** Add `GEMINI_API_KEY` as a
   *secret* with your free key from <https://aistudio.google.com/apikey>.
   Add `ALLOWED_ORIGIN` as a plain variable set to
   `https://www.azsco.systems,https://azsco.systems` — the worker refuses any other
   origin before calling Gemini, so without it anyone can point their own site
   at your worker and spend the quota. For the contact form, also add
   `WEB3FORMS_KEY` as a *secret*. Save and deploy again.
5. Copy the worker's URL from the top of its dashboard page (looks like
   `https://azsco-chat.<your-subdomain>.workers.dev`).
6. Set `CHAT_ENDPOINT` to that URL in `tools/build.py`, then run
   `python3 tools/build.py`.

Prefer the command line instead:

```bash
npx wrangler deploy backend/workers/chat-worker.js --name azsco-chat
npx wrangler secret put GEMINI_API_KEY --name azsco-chat
```

Either way, keep this file's `FACTS` in sync by hand with `CHAT_FACTS` /
`CHAT_RULES` in `tools/build.py` and with `backend/api/chat.js` whenever the
business facts change — a deployed worker cannot read the static site's source.

## Checking it works

```bash
curl -X POST https://<your-deployment>/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"lang":"en","messages":[{"role":"user","content":"What services do you offer?"}]}'
```

A healthy response is `{"reply":"..."}`. If you get `{"error":"Assistant unavailable"}`,
check the function logs — the proxy deliberately does not return API errors to the
browser, so that key or quota problems are not exposed to visitors.

## Limits enforced by the proxy

- 1000 characters per message, 40 messages per request, 500 tokens per reply.
- Only `user` and `assistant` roles are accepted from the browser; the system
  prompt is added server-side and cannot be overridden by a visitor.

These are a first line of defence, not rate limiting. For a public site, also put
your host's rate limiting or WAF in front of the endpoint.
