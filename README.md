# AZSCO Security Systems — Website

The AZSCO security systems website (azsco.systems) — a **product catalogue** for a
Kuwait-based supplier and installer of security systems: video surveillance, intrusion and
fire detection, access control, and the radio and network hardware behind them.

Built as plain HTML, CSS and vanilla JavaScript with no build dependencies, so it can be
served from any static host (GitHub Pages, S3, Netlify, nginx) by copying the repository root.

> **This is a catalogue, not a brochure.** The visual language — the strictly monochrome
> palette, the type stack, the header and footer, the assistant — is shared with AZSCO's
> services site. The page architecture is not: the pages here are a filtered catalogue,
> category pages, a page per product, and a quote basket.

## How buying works

There are **no prices anywhere on the site**, and that is deliberate rather than an omission
to fill in later. The same camera costs different amounts on different buildings once cable
runs, mounting, power, existing infrastructure and device count are known, so a figure
published before the survey would be a guess.

Instead every product has an **Add to quote** button. Selected products collect in a basket
held in the visitor's own browser, survive navigation between pages, and are sent as one
enquiry from `/quote/` along with the site details. The basket is never transmitted until
the form is submitted.

## Pages

| Page | English URL | Arabic URL |
| --- | --- | --- |
| Home — hero, categories, frequently specified products, process, brands, sectors | `/` | `/ar/` |
| Catalogue — all 16 products, filterable by category and brand line | `/products/` | `/ar/products/` |
| Category — one per category, with its products and brand lines | `/products/<category>/` | `/ar/products/<category>/` |
| Product — specifications, highlights, applications, related products | `/products/<category>/<product>/` | `/ar/products/<category>/<product>/` |
| Brands — the eight manufacturer lines behind the catalogue | `/brands/` | `/ar/brands/` |
| Quote — the basket and the enquiry form | `/quote/` | `/ar/quote/` |
| Installation & support — survey, commissioning, maintenance, warranty | `/support/` | `/ar/support/` |
| About AZSCO — story, objective/vision/mission, why buy the system here, FAQ | `/about/` | `/ar/about/` |
| Contact | `/contact/` | `/ar/contact/` |
| Privacy policy | `/privacy-policy/` | `/ar/privacy-policy/` |
| Not-found page | `/404.html` | `/ar/404.html` |

58 pages in total, both languages included.

## The catalogue model

`tools/build.py` holds the whole catalogue, and every page, filter, navigation entry and
sitemap row is generated from it — so a product cannot exist in the data and be missing from
the site, or appear in the navigation and 404 when clicked.

- **`CATEGORIES`** — four categories, each with its lead copy, typical applications and the
  brand lines that supply it.
- **`PRODUCTS`** — sixteen entries, each belonging to one category, carrying a blurb,
  highlights, and a table of `(label, value)` specification pairs.
- **`BRANDS`** — the eight manufacturer lines from AZSCO's company profile, each mapped to
  the categories it supplies. The counts on the Brands page and the catalogue's brand filter
  are both derived from that mapping.

`ROUTES` is rebuilt from `CATEGORIES` and `PRODUCTS` rather than written by hand, which is
what makes a product's URL (`/products/video-surveillance/ip-bullet-camera-4k/`) follow from
its data.

> **⚠ Catalogue entries describe equipment classes, not manufacturer part numbers.**
> A product here is "4K IP Bullet Camera", not a specific vendor SKU, and the figures are the
> class's working envelope rather than any one datasheet. This is intentional — the exact
> model is chosen per site after the survey, and a spec sheet nailed to one part number goes
> stale the first time a vendor revises its range. **Before launch, confirm these envelopes
> against the lines actually stocked**, and if you decide to sell named models instead, add a
> `model` field to `PRODUCTS` rather than editing the generated HTML.

## Languages

The site is bilingual: English from the repository root, Arabic from `ar/`, with `dir="rtl"`
and an Arabic type stack (Cairo / Tajawal). Every page carries `hreflang` alternates for both
languages plus `x-default`, and the globe button switches between them **on the same page** —
Arabic 4K IP Bullet Camera goes to English 4K IP Bullet Camera.

Both trees are generated from one set of templates, where every visible string is an
`(English, Arabic)` pair, so they cannot drift apart structurally. That includes the strings
JavaScript needs: the basket's `aria-label`s travel to `main.js` as JSON on the list element,
so the Arabic basket announces in Arabic.

> **Arabic copy needs a native review before launch.** The company facts (About, objective,
> vision, mission) come from AZSCO's own bilingual profile, but all catalogue copy — product
> names, blurbs, specification labels, the FAQ — is a translation of English I wrote for this
> site.

## URLs

Every URL is clean: no `.html`, and the homepage is the bare site root. Each page is written
to its own directory as `index.html`, which every static host serves as the directory's
default document — no server configuration, and it works unchanged on GitHub Pages.

**Old links keep working.** The services site this replaced is redirected page by page rather
than left to 404 — `/services/` → `/products/`, `/clients/` → `/about/`, `/partners/` →
`/brands/` — in both the clean and the flat (`.html`) spelling, plus a `/home/` alias.

## Running locally

Serve the folder rather than opening `index.html` directly — the clean URLs rely on
directory-index resolution, which `file://` cannot follow.

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Editing

Pages are generated. After editing `tools/build.py`, regenerate:

```bash
python3 tools/build.py
```

It rewrites every page, the redirect stubs, `sitemap.xml` (built from the pages that actually
exist, so it cannot list a removed page) and the assistant's system prompt inside both backend
proxies. CSS and JavaScript are edited directly in `assets/` — the builder does not touch them.

Site-wide details (phone, email, address, social links) are defined once at the top of
`tools/build.py`.

## Brand and palette

The palette is strictly black and white — no hue anywhere in the stylesheet. Colour is handled
by contextual custom properties (`--accent`, `--accent-strong`, `--accent-soft`, `--accent-ink`)
declared once on `:root` for light surfaces and re-declared on every dark surface, so a button,
icon or badge inverts automatically depending on what it sits on.

Because hue cannot distinguish anything, two conventions do that work instead: prose links are
underlined, and form errors are marked with weight, a heavier border, an inset rule and a
warning glyph rather than red.

The catalogue ships **without product photography**. Each product card and product page shows
its category mark on a tinted ground rather than a placeholder image box. Drop real product
shots into `assets/img/photos/` and give `PRODUCTS` an `image` field when they are available.

## JavaScript

`assets/js/main.js` carries the navigation, scroll reveal, counters and accordions, plus three
catalogue behaviours:

- **The quote basket** — `localStorage`, read and written through guarded helpers (in private
  mode `localStorage` throws on access rather than returning null). Add buttons carry the
  product's name and kind as `data-` attributes, so the script holds no copy of the catalogue.
- **Catalogue filters** — category and brand checkboxes filter in the browser against `data-`
  attributes the builder wrote onto each card. With scripting off every card is simply
  visible, which is the correct catalogue, just unfiltered.
- **The quote form** — validates, appends the basket as a readable list, and posts to the
  worker's `/contact` route. It never reports a success it did not get: with no endpoint
  configured, or on a failed request, it says so and gives the phone number.

## AZSCO Assistant (chat widget)

A chat widget sits in the bottom-left corner of every page (bottom-right in Arabic). **The
browser never sees an API key** — the widget posts to a Cloudflare Worker
(`backend/workers/chat-worker.js`) which holds the key server-side:

```
browser ─────▶ Cloudflare Worker ──key──▶ model API
```

The system prompt lives in `CHAT_FACTS` and `CHAT_RULES` in `tools/build.py` and now describes
the catalogue, how quoting works, and that it must never quote a price. `python3 tools/build.py`
rewrites the generated `AZSCO-PROMPT` block in both proxy files from it, so a deployed assistant
cannot drift from what the site says. Edit there, rebuild, then redeploy the Worker.

Model replies are escaped before display: `chat.js` escapes all HTML, then re-introduces a
closed set of formatting — nothing from the model reaches the DOM as live markup.

## Mobile

The phone layout is not the desktop layout stacked. Breakpoints at 1040px, 768px, 640px and
400px change the shape of the page:

- **The filter sidebar stops being a sidebar** below 1040px and becomes a wrapping row of
  checkboxes above the results, so filtering stays reachable without a modal.
- **The two-column product page becomes one column**, visual first, then the buy panel.
- **Product cards go two-up, then one-up**, and each card's footer stacks so the add button is
  full width rather than crushed beside a link.
- **A persistent Call / Get a Quote bar** sits at the bottom of the viewport, carrying the same
  live basket count as the header, with `env(safe-area-inset-bottom)` respected.
- **Every standalone link is at least 44px tall.**

## Deployment notes

- **`CNAME`** is set to `azsco.systems`. Point the Pages custom domain at the same name.
- **The Worker's `ALLOWED_ORIGIN` must include this domain** (`https://www.azsco.systems,https://azsco.systems`)
  or both the assistant and the quote form will be refused from the live site.
- **Contact details** — phone, `info@` and `sales@` mailboxes, address and social links are
  real-world data carried over unchanged; they are not a function of which domain serves the site.
- **Social links** — placeholder `#` hrefs remain for any profile not yet set.
- **Analytics and Search Console** tokens are empty by default, and nothing is emitted until
  they are filled in, so the site ships clean rather than with a dead beacon.

## Browser support

Modern evergreen browsers. Layout uses CSS grid and custom properties; JavaScript is ES5-style
with `IntersectionObserver` feature detection, and every page remains readable and usable with
JavaScript disabled. Respects `prefers-reduced-motion`.
