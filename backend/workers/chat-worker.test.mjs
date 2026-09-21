/**
 * Tests for chat-worker.js — run with:  node backend/workers/chat-worker.test.mjs
 *
 * No dependencies and no network: fetch is stubbed, so the assertions below
 * check both what the worker answers and what it does NOT send onward. That
 * second part is the point — the origin check and the rate limit are only
 * worth anything if they stop the upstream call before the quota is spent.
 *
 * Needs Node 18+ (for the global Request / Response / fetch used by Workers).
 * This file is never deployed; only chat-worker.js is pasted into Cloudflare.
 */
import worker from './chat-worker.js';

let upstream = [];                         // what the worker sent onward
const realFetch = globalThis.fetch;
globalThis.fetch = async (url, init) => {
  upstream.push(String(url));
  if (String(url).includes('generativelanguage')) {
    return new Response(JSON.stringify({
      candidates: [{ content: { parts: [{ text: 'Hello from AZSCO.' }] } }],
    }), { status: 200 });
  }
  return new Response(JSON.stringify({ success: true }), { status: 200 });
};

const ENV = {
  GEMINI_API_KEY: 'test-gemini',
  WEB3FORMS_KEY: 'test-web3',
  ALLOWED_ORIGIN: 'https://www.azsco.systems,https://azsco.systems',
};

const post = (path, body, origin, ip = '1.1.1.1') =>
  worker.fetch(new Request('https://w.example' + path, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(origin ? { Origin: origin } : {}),
      'CF-Connecting-IP': ip,
    },
    body: JSON.stringify(body),
  }), ENV);

const CHAT = { lang: 'en', messages: [{ role: 'user', content: 'hi' }] };
const FORM = { name: 'A', email: 'a@b.com', phone: '+96599', message: 'hi', lang: 'en' };

let pass = 0, fail = 0;
const check = (label, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${label}${ok ? '' : `  got ${JSON.stringify(got)} want ${JSON.stringify(want)}`}`);
  ok ? pass++ : fail++;
};

/* --- origin enforcement --------------------------------------------- */
upstream = [];
let r = await post('/', CHAT, 'https://evil.example');
check('disallowed origin -> 403', r.status, 403);
check('disallowed origin never reaches Gemini', upstream.length, 0);
check('disallowed origin not echoed back', r.headers.get('access-control-allow-origin'), 'null');

upstream = [];
r = await post('/', CHAT, null);              // curl: no Origin header at all
check('no Origin header -> 403', r.status, 403);
check('no Origin never reaches Gemini', upstream.length, 0);

upstream = [];
r = await post('/', CHAT, 'https://azsco.systems', '2.2.2.2');
check('allowed origin -> 200', r.status, 200);
check('allowed origin reaches Gemini', upstream.length, 1);
check('allowed origin echoed', r.headers.get('access-control-allow-origin'), 'https://azsco.systems');
check('Vary: Origin set', r.headers.get('vary'), 'Origin');
check('reply passed through', (await r.json()).reply, 'Hello from AZSCO.');

/* --- unset ALLOWED_ORIGIN still works (fresh deployment) ------------- */
upstream = [];
r = await worker.fetch(new Request('https://w.example/', {
  method: 'POST', headers: { 'CF-Connecting-IP': '9.9.9.9' }, body: JSON.stringify(CHAT),
}), { GEMINI_API_KEY: 'k' });
check('unset ALLOWED_ORIGIN -> still 200', r.status, 200);

/* --- preflight ------------------------------------------------------- */
r = await worker.fetch(new Request('https://w.example/', {
  method: 'OPTIONS', headers: { Origin: 'https://azsco.systems' },
}), ENV);
check('preflight -> 204', r.status, 204);

/* --- rate limiting --------------------------------------------------- */
let statuses = [];
for (let i = 0; i < 15; i++) statuses.push((await post('/', CHAT, 'https://azsco.systems', '3.3.3.3')).status);
check('chat: first 12 pass', statuses.slice(0, 12).every(s => s === 200), true);
check('chat: 13th+ throttled', statuses.slice(12), [429, 429, 429]);

upstream = [];
statuses = [];
for (let i = 0; i < 7; i++) statuses.push((await post('/contact', FORM, 'https://azsco.systems', '4.4.4.4')).status);
check('contact: first 5 pass', statuses.slice(0, 5), [200, 200, 200, 200, 200]);
check('contact: 6th+ throttled', statuses.slice(5), [429, 429]);
check('contact: throttled ones sent no mail', upstream.length, 5);

/* --- a different IP is unaffected by someone else's limit ------------ */
check('other IP unaffected', (await post('/', CHAT, 'https://azsco.systems', '5.5.5.5')).status, 200);

/* --- contact validation still holds ---------------------------------- */
upstream = [];
r = await post('/contact', { ...FORM, website: 'spam' }, 'https://azsco.systems', '6.6.6.6');
check('honeypot -> 200 but no mail', [r.status, upstream.length], [200, 0]);

upstream = [];
r = await post('/contact', { ...FORM, email: 'nope' }, 'https://azsco.systems', '7.7.7.7');
check('bad email -> 400, no mail', [r.status, upstream.length], [400, 0]);

upstream = [];
r = await post('/contact', { name: 'A' }, 'https://azsco.systems', '8.8.8.8');
check('missing fields -> 400, no mail', [r.status, upstream.length], [400, 0]);

/* --- oversized body is refused before buffering ---------------------- */
upstream = [];
r = await post('/', { lang: 'en', messages: [{ role: 'user', content: 'x'.repeat(200000) }] },
                'https://azsco.systems', '10.10.10.10');
check('oversized body -> 400, no Gemini call', [r.status, upstream.length], [400, 0]);

/* --- missing secrets fail loudly, not silently ----------------------- */
r = await worker.fetch(new Request('https://w.example/contact', {
  method: 'POST', headers: { Origin: 'https://azsco.systems' }, body: JSON.stringify(FORM),
}), { ALLOWED_ORIGIN: ENV.ALLOWED_ORIGIN });
check('no WEB3FORMS_KEY -> 503', r.status, 503);

/* --- the generated prompt actually made it in ------------------------ */
const src = await (await import('node:fs/promises')).readFile(
  new URL('./chat-worker.js', import.meta.url), 'utf8');
check('prompt block generated', /const FACTS = `\n+COMPANY/.test(src), true);
// The site is now a catalogue, so what has to survive into the prompt is the
// catalogue itself: an assistant missing a category would deny AZSCO sells it.
for (const cat of ['Video Surveillance', 'Intrusion & Fire', 'Access Control', 'Radio & Networking']) {
  check(`category in prompt: ${cat}`, src.includes(cat), true);
}
// With no prices anywhere on the site, an assistant that quotes one is a
// business problem, not a cosmetic one -- so the rule has to be in the prompt.
check('no-pricing rule in prompt', /Never quote a price/.test(src), true);
check('quote-by-survey explained in prompt', src.includes('free site survey'), true);
check('hours correct in prompt', src.includes('8:30-16:30'), true);

globalThis.fetch = realFetch;
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
