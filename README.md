# AZSCO Security — Website

The AZSCO Security website (azsco.systems) — a Kuwait-based provider of security services:
facility guarding, VIP protection and rapid intervention, a central operations room, security
patrols, and security systems.

Built as plain HTML, CSS and vanilla JavaScript with no build dependencies, so it can be
served from any static host (GitHub Pages, S3, Netlify, nginx) by copying the repository root.

## Languages

The site is bilingual. English is served from the repository root and Arabic from `ar/`,
with `dir="rtl"` and an Arabic type stack (Cairo / Tajawal). Every page carries `hreflang`
alternates for both languages plus `x-default`, and a globe button in the header switches
between them **on the same page** — Arabic Services goes to English Services, not to the home
page.

Both language versions are generated from one set of templates in `tools/build.py`: every
visible string is an `(English, Arabic)` pair, so the two trees cannot drift apart
structurally. Right-to-left is handled by `dir="rtl"` plus one `[dir="rtl"]` block at the end
of the stylesheet covering what direction alone does not mirror — physical borders and
offsets, the drawer sliding in from the left, and the arrows. Phone numbers and email
addresses are wrapped in `dir="ltr"` so they read correctly inside Arabic text.

> **Most Arabic copy is AZSCO's own**, taken directly from the bilingual company profile
> supplied by the client (About, Objective/Vision/Mission, Values, CEO's message, Services,
> Sectors, Nationalities, Training, Equipment, Uniforms, Certifications). Page furniture around
> that content — section eyebrows and leads, the FAQ, the privacy policy — is a translation of
> English copy I wrote, and still needs a native review before launch. The Arabic names in
> `CLIENTS` (`tools/build.py`) are my own renderings of client brand names for the ones not
> already bilingual on their own logo, not text supplied by AZSCO — worth confirming, especially
> the couple of legal-form company names.

## Pages

| Page | English URL | Arabic URL |
| --- | --- | --- |
| Home — hero, services, sectors served, why-us, process, partners | `/` | `/ar/` |
| About AZSCO — story, objective/vision/mission, values, commitment, nationalities, training, equipment, uniforms, certifications, CEO's message, clients, stats, FAQ | `/about/` | `/ar/about/` |
| All services, with a detail section per service | `/services/` | `/ar/services/` |
| Our clients — logo panel and a named list | `/clients/` | `/ar/clients/` |
| Strategic partnerships | `/partners/` | `/ar/partners/` |
| Contact details and enquiry form | `/contact/` | `/ar/contact/` |
| Privacy policy | `/privacy-policy/` | `/ar/privacy-policy/` |
| Not-found page | `/404.html` | `/ar/404.html` |

## URLs

Every URL is clean: no `.html`, and the homepage is the bare site root — never `/index`
and never `/home`, which is how virtually every established site is built (nobody links
`apple.com/home`). That's achieved without any server config, in a way that works
unchanged on GitHub Pages: each page is written to its own directory as `index.html`
(`about/index.html`, `ar/services/index.html`, ...), which every static host serves
invisibly as the directory's default document — the same mechanism that already makes
`/` show no filename at all.

`tools/build.py` owns this: `ROUTES` maps each logical page to a slug, `path_for(lang,
fname)` turns that into the clean URL, and `out_file_for(lang, fname)` turns it into the
file the builder writes. Every internal link in the templates goes through `link(lang,
spec)` (a plain string like `"about.html"`, or `"services.html#guarding"` for an
in-page anchor) — nothing constructs a URL by hand, so the two languages and every
generated link stay structurally in sync.

**Old links keep working.** The flat filenames this replaced (`about.html`,
`ar/services.html`, ...) are regenerated as tiny redirect pages — a `meta
http-equiv="refresh"` plus a `rel="canonical"` pointing at the new clean URL — so a
bookmark, an inbound link, or a page Google already indexed still arrives. The same
mechanism backs a `/home/` and `/ar/home/` alias: not the canonical address, but a
working one for anyone who types or shares it expecting a homepage to live there.

`assets/js/main.js`'s `markActive()` highlights the current nav item by comparing
normalized *paths* (`/about/` against `/about/`), not filenames — it has to, now that a
page's identity in the URL is a directory, not a file.

## Structure

```
.
├── index.html, about/index.html, services/index.html, ...   # English pages
├── ar/index.html, ar/about/index.html, ...                  # Arabic pages
├── about.html, ar/services.html, home/index.html, ...       # redirect stubs (generated)
├── assets/
│   ├── css/style.css     # all styling (design tokens, layout, components, responsive)
│   ├── js/main.js        # nav, mobile drawer, scroll reveal, counters, accordions, form validation
│   └── img/               # brand lockup, white variant, favicons, photos/
├── tools/build.py        # regenerates every page, both languages, and the redirect stubs
├── backend/              # chat widget's server-side proxy — not part of what GitHub Pages serves
│   ├── api/chat.js       # Vercel / Netlify / Deno variant
│   ├── workers/chat-worker.js  # Cloudflare Workers variant (currently deployed)
│   └── README.md         # deployment steps for either one
├── robots.txt
├── sitemap.xml
└── 404.html, ar/404.html                                     # kept flat: GitHub Pages requirement
```

## Running locally

Serve the folder rather than opening `index.html` directly — the clean URLs
(`/about/`, `/ar/services/`) rely on directory-index resolution, which only a real
server provides; `file://` cannot follow them.

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Editing

`tools/build.py` also writes `sitemap.xml`, built from the pages that actually exist, so it
cannot list a page that has been removed.


The pages share a header, footer, navigation and call-to-action band. To keep those in sync,
they are generated by `tools/build.py`, which holds the shared templates, the navigation model
and each page's content. After editing that file, regenerate the HTML:

```bash
python3 tools/build.py
```

CSS and JavaScript are edited directly in `assets/` — the builder does not touch them.

Site-wide details (phone, email, address) are defined once at the top of `tools/build.py`.

## Brand and palette

The palette is strictly black and white — no hue anywhere in the stylesheet. Colour is
handled by four contextual custom properties (`--accent`, `--accent-strong`, `--accent-soft`,
`--accent-ink`) declared once on `:root` for light surfaces, then re-declared on every dark
surface (`.hero`, `.cta`, `.stats`, `.site-footer`, `.div-card`, …). Components reference the
tokens rather than literal colours, so a button, icon or badge inverts automatically depending
on which surface it sits on.

Because hue can no longer distinguish anything, two conventions do that work instead: inline
prose links are underlined, and form errors are marked with weight, a heavier border, an inset
rule and a warning glyph rather than red.

Brand assets in `assets/img/`:

| File | Use |
| --- | --- |
| `AZSCO_Logo.png` | Supplied lockup — header, Open Graph image |
| `AZSCO_Logo_white.png` | White version of the same artwork, for dark backgrounds (footer) |
| `favicon-32.png`, `favicon-192.png`, `apple-touch-icon.png` | Generated from the shield mark in the supplied logo |

All text meets WCAG AA contrast (verified programmatically against composited backgrounds).

## Mobile

The phone layout is not just the desktop layout stacked. Breakpoints at 768px, 640px and
400px change the shape of the page:

- **Short, scannable blocks stay in columns** rather than becoming one long list — partners
  and statistics go two-up, and the footer's Company and Services link lists sit side by side.
- **Process steps become rows** (number beside the text) instead of stacked blocks.
- **The hero tightens** — smaller headline, tighter leading and less padding — so the first
  screen carries the message and the buttons rather than only the headline.
- **The nav drawer groups its sections.** Services and Divisions collapse behind toggles, one
  open at a time, and the group matching the current page opens automatically. Collapsed
  links are `visibility:hidden`, so they stay out of the tab order and the accessibility tree.
- **A persistent Call / Get a Quote bar** sits at the bottom of the viewport, with page
  padding and a raised back-to-top button so it never covers content, and `env(safe-area-inset-bottom)`
  respected on notched devices.
- **Every standalone link is at least 44px tall.** Links inside a sentence are deliberately
  left inline so prose is not broken up.

## AZSCO Assistant (chat widget)

A chat widget sits in the bottom-left corner of every page (bottom-right in Arabic, mirrored
with the rest of the layout), labelled **AZSCO Assistant**. It opens a panel with suggested
questions, supports an expand toggle — a wider panel on desktop, full screen on phones — and
keeps the conversation across page navigation via `sessionStorage`.

**The browser never sees an API key.** The widget posts to a Cloudflare Worker
(`backend/workers/chat-worker.js`, deployed separately — see `backend/README.md`), which holds
the key server-side and calls Google Gemini's API on the widget's behalf:

```
browser ─────▶ Cloudflare Worker ──key──▶ Gemini API
```

Calling the model API straight from the page was tried and dropped: providers don't allow
browser-origin requests (no CORS), so the widget opened but every reply failed — and the key
would have been readable by anyone viewing source. There is deliberately no switch for it now.

- `assets/js/chat.js` — the widget. Reads its endpoint and every visible string from the
  markup, so it holds no key, no prompt and no copy of its own.
- `backend/workers/chat-worker.js` — the proxy currently deployed. Also carries the contact
  form's `/contact` route.
- `backend/api/chat.js` — the same chat proxy for a Node host (Vercel / Netlify / Deno).
- `backend/README.md` — deployment steps and environment variables for either one.

Both proxies enforce `ALLOWED_ORIGIN` themselves and rate-limit per IP, rather than trusting
the browser to discard a reply the free-tier quota has already paid for.

The system prompt lives in `CHAT_FACTS` and `CHAT_RULES` in `tools/build.py` and carries
AZSCO's facts (services, address, hours, partners, clients), instructing the model to answer
only from them, refuse pricing and commitments, and hand off to the team when it does not
know. That is the single source of truth: `python3 tools/build.py` rewrites the generated
`AZSCO-PROMPT` block in both proxy files from it, so a deployed assistant cannot drift from
what the site says. Edit it there, rebuild, then redeploy the Worker.

**Model replies are escaped before display.** `chat.js` escapes all HTML, then re-introduces a
closed set of formatting (bold, phone and email links) — nothing from the model reaches the
DOM as live markup.

## Content source

The company facts, service descriptions, About page copy, statistics and imagery come from
AZSCO's own official company profile (a bilingual PDF supplied directly by the client), which
is treated as the single source of truth over anything guessed earlier from public search
results. Three things worth knowing about how it was applied:

- **All five services are covered, including Security Systems.** An earlier phase of this site
  deliberately left out the source document's fifth service — Security Systems (CCTV, fire and
  theft alarms) — at the client's own standing direction to stay manpower-only. That direction
  was later reversed by the client, so `SERVICES` in `tools/build.py` now carries all five:
  Facility Guarding, VIP Protection & Rapid Intervention, Central Operations Room, Security
  Patrols, and Security Systems. The 8 technology partners on the Partners page are framed as
  the equipment behind that service and the Central Operations Room's monitoring.
- **Founding year corrected to 2014.** Earlier content (built before the official profile was
  available) said 2008. The source document is unambiguous — established 2014, formerly known
  as Almail Zone Security Services — and every mention (`FOUNDED` in `tools/build.py`, the
  About page story, the footer blurb) now reflects that.
- **Client list changed.** The official profile's client-logo panel (`clients-logos.jpg`,
  19 logos including Radisson Blu Hotel Kuwait, Alnasser, Millennium Hotels and Resorts and
  Kuwait Ports Authority) replaced an earlier, shorter client list that had included a name
  ("Xcite") not present in the official document — dropped in favour of the authoritative source.

## Notes

- **Contact form**: client-side validation only. It shows a confirmation message and does not
  submit anywhere. Point the `<form>` at a backend endpoint or form service to make it live.
- **Social links**: placeholder `#` hrefs in the top bar and footer, except Instagram
  (`INSTAGRAM_URL` in `tools/build.py`) — replace the rest with the real profile URLs.
- **Scope**: facility guarding, VIP protection and rapid intervention, a central operations
  room, security patrols, and security systems (CCTV, fire and theft alarms) — see
  "Content source" above for how the last one was added back after an earlier manpower-only
  phase.
- **Photography**: `assets/img/photos/` holds `hero.jpg`, the extracted `partners-logos.png`,
  `clients-logos.jpg` and `certifications.jpg` panels, and `uniforms/` (front and back photos
  for the four official uniform models — formal, winter, patrol, duty — extracted from the
  official company profile, which uses real AZSCO staff). See the README in that folder for
  slots, sizes and naming for anything added later. Brand assets stay in `assets/img/`.
- **Email**: two addresses, `EMAIL` (general) and `EMAIL_SALES` (sales) in
  `tools/build.py`, shown together in the footer and on the contact page.
- **Navigation**: there is no "Home" item; the logo links home in both the header and the
  mobile drawer. The footer and breadcrumbs still carry an explicit Home link.
- **Partners**: the 8 official technology partners (`PARTNERS` in `tools/build.py`, backing
  the partner count in the statistics row) render as a single logo-panel image
  (`assets/img/photos/partners-logos.png`) rather than individual tiles.
- **Map**: the contact page uses a styled address panel rather than an embedded map, so the
  page loads without third-party scripts. Replace with a map embed if required.
- **Statistics** come from AZSCO's own copy: founding year, years of experience (recalculated
  each year by `data-years-since`, so it never goes stale), 24/7 response and the partner count.
- **Clients**: render as a single logo-panel image (`assets/img/photos/clients-logos.jpg`);
  `CLIENTS_ALT` in `tools/build.py` holds the descriptive alt text.
- **Logos keep their own colour.** The palette rule is for the site's own UI — partner, client
  and certification logos are third-party marks shown as supplied, so those three images are
  the only place colour appears on the site.
- **Fonts**: Inter and Barlow Condensed are loaded from Google Fonts, with system-font
  fallbacks if that request is blocked.

## Browser support

Modern evergreen browsers. Layout uses CSS grid and custom properties; JavaScript is ES5-style
with `IntersectionObserver` feature detection, and every page remains readable with JavaScript
disabled. Respects `prefers-reduced-motion`.
