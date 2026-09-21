#!/usr/bin/env python3
"""Static builder for the AZSCO Security site (English + Arabic)."""
import os
import datetime
import html
import json

# Output to the repository root (this script lives in <repo>/tools).
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

LANGS = ("en", "ar")

PHONE = "(+965) 1808606"
PHONE_HREF = "+9651808606"
EMAIL = "info@azsco.com"          # general enquiries
EMAIL_SALES = "sales@azsco.com"   # sales and quotations
MAPS_URL = "https://maps.app.goo.gl/BN2Byxt6BCJ62XV26"
INSTAGRAM_URL = "https://www.instagram.com/azsco_security.co"
X_URL = "https://x.com/azsco_security"
FACEBOOK_URL = "https://www.facebook.com/profile.php?id=61593999123161"
WHATSAPP_URL = "https://wa.me/9651808606?text=Hello%20I%20would%20like%20more%20information"

# ---------------------------------------------------------------- assistant
# The widget posts to CHAT_ENDPOINT, a small proxy that holds the model API key
# server-side (backend/workers/chat-worker.js for Cloudflare, backend/api/chat.js
# for a Node host). The browser never sees a key and never receives the system
# prompt -- only the proxy builds it.
#
# Calling a model API straight from the browser was tried and abandoned: the
# providers reject browser-origin requests outright, and the key would be
# readable by anyone viewing source. There is deliberately no longer a switch
# for it.
CHAT_ENDPOINT = "https://azsco-website-chatbot.steep-band-c624.workers.dev/"

# Cloudflare Web Analytics: paste the token from the Cloudflare dashboard
# (Analytics & Logs -> Web Analytics -> add azsco.systems -> copy the token out of
# the snippet it shows). Left empty, no analytics script is emitted at all --
# the site ships clean rather than with a dead beacon. Chosen over Google
# Analytics because it sets no cookies and stores no personal data, so it
# needs no cookie banner and nothing changes in the privacy policy's terms.
ANALYTICS_TOKEN = ""

# Google Search Console verification. Paste only the content value from the
# "HTML tag" method (the long string, not the whole tag); empty emits nothing.
SEARCH_CONSOLE_TOKEN = ""

def search_console_tag():
    if not SEARCH_CONSOLE_TOKEN:
        return ""
    return '<meta name="google-site-verification" content="%s">\n' % SEARCH_CONSOLE_TOKEN

def analytics_tag():
    if not ANALYTICS_TOKEN:
        return ""
    return ('<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
            'data-cf-beacon=\'{"token": "%s"}\'></script>' % ANALYTICS_TOKEN)

# The contact form posts here: the same worker, on its /contact route, which
# relays the submission to the email address the WEB3FORMS_KEY was issued for.
# Without that secret set on the worker the route answers 503 and the form
# tells the visitor to call or email instead -- it never claims to have sent
# something it did not send.
CONTACT_ENDPOINT = CHAT_ENDPOINT.rstrip("/") + "/contact"

# The facts the assistant may rely on, and the only source of truth for them.
# `python3 tools/build.py` rewrites the generated block in both backend proxies
# from CHAT_FACTS and CHAT_RULES, so a deployed assistant cannot drift from what
# the site says. Edit here, rebuild, then redeploy the proxy.
CHAT_FACTS = """
COMPANY
- AZSCO Security Services Company (formerly Almail Zone Security Services),
  established 2014, headquartered in Qibla, Kuwait.
- Office: Floor 27B, Kuwait Building Tower, Fahad Al Salem St., Qibla, Kuwait.
- Telephone: (+965) 1808606.
- Email: info@azsco.com for general enquiries, sales@azsco.com for sales
  and quotations.
- Office hours: Sunday to Thursday, 8:30-16:30. Emergency response 24/7.
- CEO: Dr. Abdulaziz Almail.
- Certified ISO 9001:2015 for quality management, and compliant with
  Anti-Money Laundering standards.

WHAT AZSCO SELLS
AZSCO supplies, installs and maintains security systems, and also provides
security manpower. The website is a product catalogue in four categories:
- Video Surveillance: IP cameras (bullet, vandal-resistant dome, PTZ with
  optical zoom) and network video recorders with RAID storage.
- Intrusion & Fire: wireless alarm control hubs, motion detectors, door and
  window contacts, and combined smoke and heat detectors.
- Access Control: multi-door controllers, fingerprint and card readers, time
  and attendance terminals, and tripod turnstiles.
- Radio & Networking: digital two-way radios, LTE network radios, industrial
  cellular routers, and managed PoE switches.

HOW BUYING WORKS
- There are no prices on the site or in this chat. Security systems are quoted
  per site because cabling, mounting, power, existing infrastructure and device
  count all change the figure.
- The normal sequence is: free site survey, then a written quote covering
  equipment, installation and the first year of maintenance as one package.
- Visitors add products to a quote list on the site and send it with their site
  details. The list is stored in their own browser until they submit it.
- Catalogue entries describe the class of equipment AZSCO specifies, not a fixed
  manufacturer part number. The exact model is chosen after the survey.
- AZSCO prefers to install what it supplies, and does not warrant an
  installation it did not carry out. It can often take over and maintain a
  system installed by someone else after surveying it.

SERVICES ALONGSIDE THE PRODUCTS
- Facility Guarding, VIP Protection & Rapid Intervention, Security Patrols, and
  a 24/7 Central Operations Room that monitors guarded and alarmed sites and
  dispatches a rapid response.
- Installation, commissioning, scheduled preventive maintenance, warranty on
  both equipment and installation work, and staff training.

OTHER FACTS
- Officers are screened, licensed, uniformed, trained (first aid,
  fire-fighting, dealing with the public, dealing with accidents,
  self-defense) and supervised.
- Officers come from a range of nationalities: Kuwaiti, Indian, Egyptian,
  Chadian, Nigerian, Nepalese and stateless individuals.
- Serves government, commercial, financial, industrial, residential and many
  other sectors across Kuwait.
- The eight manufacturer lines behind the catalogue: Ajax, Rasilient,
  Avigilon, Teltonika, Inrico, Hikvision, Pelco and Motorola.
- Clients include Radisson Blu Hotel Kuwait, Millennium Hotels and Resorts,
  Kuwait Ports Authority, Alghanim Industries and Alnasser, among others.
- A free site survey is the normal first step for a new enquiry.
"""

CHAT_RULES = """
RULES
- Answer ONLY questions about AZSCO, its security services, and how to get in
  touch. For anything else, politely say it is outside what you can help with
  and offer to put the visitor in touch with the team.
- Use ONLY the facts above. If you do not know something - pricing, guard
  numbers, availability, contract terms, staff names - say so plainly and point
  the visitor to (+965) 1808606 or info@azsco.com. Never guess or invent.
- Never quote a price, promise a response time, or commit AZSCO to anything.
- Be brief: two or three short paragraphs at most. Plain text, no markdown
  headings or bullet lists.
- If a visitor appears to have an urgent security incident, tell them to call
  (+965) 1808606 immediately rather than continuing to chat.
"""

def chat_system_prompt(lang):
    reply_in = ("Reply in Arabic (Modern Standard Arabic), in a professional tone."
                if lang == "ar" else
                "Reply in English, in a professional tone.")
    return ("You are the AZSCO Assistant, the virtual assistant on the website of "
            "AZSCO, a security company in Kuwait.\n"
            + CHAT_FACTS + CHAT_RULES + "- " + reply_in)
FOUNDED = 2014
YEARS = datetime.date.today().year - FOUNDED

# Every visible string is a pair: (English, Arabic).
def t(pair, lang):
    return pair[0] if lang == "en" else pair[1]

def lang_attrs(lang):
    return 'lang="ar" dir="rtl"' if lang == "ar" else 'lang="en" dir="ltr"'

SITE_URL = "https://www.azsco.systems"

# Every page lives in its own directory (about/index.html, ar/services/index.html,
# ...) so the address bar never shows ".html" or the word "index" -- the
# directory's default document loads invisibly, the same way "/" already works.
# The home page is the one entry mapped to slug "": that resolves to the bare
# site root ("/", "/ar/") rather than "/home/", matching how every established
# site is built -- the homepage IS the root, not a named page beneath it. A
# /home/ alias is still written by write_redirects() below, so a link or a
# typed "azsco.systems/home" still arrives, it just forwards to "/".
# ROUTES is built further down, from the catalogue itself, so a category or
# product cannot exist in the data and be missing from the URL map.


def path_for(lang, fname):
    """Root-relative clean URL for a page: '/', '/about/', '/ar/services/'."""
    if fname == "404.html":
        return "/404.html" if lang == "en" else "/ar/404.html"
    slug = ROUTES[fname]
    prefix = "/ar" if lang == "ar" else ""
    return (prefix + "/") if slug == "" else f"{prefix}/{slug}/"

def out_file_for(lang, fname):
    """Filesystem path (relative to OUT) the page is physically written to."""
    if fname == "404.html":
        return "404.html" if lang == "en" else "ar/404.html"
    slug = ROUTES[fname]
    prefix = "ar/" if lang == "ar" else ""
    return f"{prefix}index.html" if slug == "" else f"{prefix}{slug}/index.html"

def link(lang, spec):
    """Resolve an internal link spec ('about.html', 'services.html#guarding')
    to a clean URL. Named link(), not href() -- 'href' is a loop variable
    throughout this file and would shadow a function of that name."""
    fname, _, anchor = spec.partition("#")
    path = path_for(lang, fname)
    return path + (f"#{anchor}" if anchor else "")

def canonical(lang, fname):
    return SITE_URL + path_for(lang, fname)

def other_lang_url(lang, fname):
    """The same page in the other language."""
    other = "ar" if lang == "en" else "en"
    return path_for(other, fname)

def asset(lang, path=""):
    """Assets are referenced by their root-relative path, so the reference is
    correct no matter how deeply the page's own URL is now nested."""
    return "/" + path
I = {
"shield":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
"shield-check":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>',
"flame":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2s4 4 4 8a4 4 0 0 1-8 0c0-1.5.5-2.5 1-3"/><path d="M12 22a7 7 0 0 0 7-7c0-3-2-5-3-7 0 3-2 4-4 4"/><path d="M12 22a7 7 0 0 1-7-7c0-2 1-3.5 2-4.5"/></svg>',
"alarm":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></svg>',
"camera":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m2 7 16-4 1.5 5.8L4 13z"/><path d="M6 12v5a2 2 0 0 0 2 2h2"/><circle cx="15" cy="17" r="3"/></svg>',
"lock":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
"users":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
"home":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 10 9-7 9 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/></svg>',
"eye":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg>',
"clock":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
"phone":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>',
"mail":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 6 10-6"/></svg>',
"pin":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>',
"check":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 13 4 4L19 7"/></svg>',
"arrow":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>',
"up":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5"/><path d="m6 11 6-6 6 6"/></svg>',
"plus":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M12 5v14"/><path d="M5 12h14"/></svg>',
"caret":'<svg class="caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
"close":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>',
"headset":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 14v-2a8 8 0 0 1 16 0v2"/><path d="M4 14h2a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z"/><path d="M20 14h-2a1 1 0 0 0-1 1v4a1 1 0 0 0 1 1h1a1 1 0 0 0 1-1z"/></svg>',
"cog":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-2.9 1.2v.1a2 2 0 1 1-4 0v-.1A1.7 1.7 0 0 0 7 19.4a1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0-1.2-2.9H1a2 2 0 1 1 0-4h.1A1.7 1.7 0 0 0 2.3 7a1.7 1.7 0 0 0-.3-1.9l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1A1.7 1.7 0 0 0 7 2.6h.1a2 2 0 1 1 4 0"/></svg>',
"award":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="9" r="6"/><path d="m8.2 13.8-1.4 7L12 18l5.2 2.8-1.4-7"/></svg>',
"target":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/></svg>',
"wallet":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 7a2 2 0 0 1 2-2h13v4"/><path d="M3 7v10a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-6a2 2 0 0 0-2-2H5a2 2 0 0 1-2-2z"/><circle cx="17" cy="14" r="1.2"/></svg>',
"grid":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>',
"file":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/><path d="M9 13h6"/><path d="M9 17h4"/></svg>',
"calendar":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4M16 3v4M3 10h18"/></svg>',
"route":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="6" cy="19" r="3"/><circle cx="18" cy="5" r="3"/><path d="M9 19h6a4 4 0 0 0 0-8H9a4 4 0 0 1 0-8h3"/></svg>',
"link":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>',
"phone-app":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="6" y="2" width="12" height="20" rx="2.5"/><path d="M11 18h2"/></svg>',
"facebook":'<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M14 8.5V7a1.5 1.5 0 0 1 1.5-1.5H17V2.6A17 17 0 0 0 14.9 2.5C12.3 2.5 10.6 4 10.6 7v1.5H8V12h2.6v9.5H14V12h2.6l.5-3.5z"/></svg>',
"x":'<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 3h3l-6.6 7.5L21.7 21h-6l-4.7-6.1L5.6 21h-3l7-8L2.6 3h6.1l4.2 5.6zm-1 16h1.7L7.6 4.7H5.8z"/></svg>',
"instagram":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="1.2" fill="currentColor" stroke="none"/></svg>',
"whatsapp":'<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2c-5.46 0-9.9 4.44-9.9 9.9 0 1.75.46 3.44 1.32 4.94L2 22l5.25-1.38a9.9 9.9 0 0 0 4.78 1.22h.01c5.46 0 9.9-4.44 9.9-9.9 0-2.64-1.03-5.13-2.9-7a9.82 9.82 0 0 0-7-2.9zm0 1.67c2.19 0 4.25.85 5.8 2.4a8.18 8.18 0 0 1 2.4 5.83c0 4.55-3.7 8.24-8.25 8.24a8.2 8.2 0 0 1-4.19-1.14l-.3-.18-3.12.82.83-3.03-.2-.32a8.17 8.17 0 0 1-1.26-4.38c0-4.55 3.7-8.24 8.29-8.24zM8.5 6.9c-.17 0-.44.06-.68.32-.23.26-.9.87-.9 2.12s.92 2.46 1.05 2.63c.13.17 1.79 2.85 4.42 3.9 2.19.86 2.63.69 3.11.65.47-.04 1.52-.62 1.74-1.22.22-.6.22-1.11.16-1.22-.07-.1-.24-.17-.5-.3-.27-.13-1.54-.76-1.78-.85-.24-.08-.41-.13-.58.13-.17.26-.66.85-.81 1.02-.15.17-.3.19-.56.06-.26-.13-1.09-.4-2.08-1.28-.77-.68-1.29-1.53-1.44-1.79-.15-.26-.02-.4.11-.53.12-.12.27-.3.4-.45.13-.15.17-.26.26-.43.08-.17.04-.32-.02-.45-.06-.13-.58-1.42-.8-1.94-.21-.51-.42-.44-.58-.45z"/></svg>',
"whatsapp":'<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15L2 22l5.2-1.4A10 10 0 1 0 12 2zm0 18a8 8 0 0 1-4.1-1.1l-.3-.2-3 .8.8-3-.2-.3A8 8 0 1 1 12 20zm4.4-5.8c-.2-.1-1.4-.7-1.6-.8s-.4-.1-.5.1-.6.8-.7 1-.3.2-.5.1a6.6 6.6 0 0 1-3.2-2.8c-.2-.4.2-.4.6-1.2a.5.5 0 0 0 0-.5l-.7-1.7c-.2-.4-.4-.4-.5-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4 5 5 0 0 0 2.3.5 2.7 2.7 0 0 0 1.8-1.3 2.2 2.2 0 0 0 .2-1.3c-.1-.1-.3-.2-.5-.3z"/></svg>',
}

I["chat"] = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
             '<path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 9 9 0 0 1-3.3-.6L3 21l1.8-5a8.3 8.3 0 0 1-.8-3.6'
             'A8.4 8.4 0 0 1 12.5 3 8.4 8.4 0 0 1 21 11.5z"/></svg>')

I["expand"] = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
               'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
               '<path d="M15 3h6v6"/><path d="M9 21H3v-6"/><path d="M21 3l-7 7"/><path d="M3 21l7-7"/></svg>')

I["send"] = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
             '<path d="M22 2 11 13"/><path d="M22 2l-7 20-4-9-9-4z"/></svg>')

I["globe"] = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/>'
              '<path d="M12 3a15 15 0 0 1 0 18a15 15 0 0 1 0-18z"/></svg>')
def logo(variant="dark"):
    """Brand lockup. `dark` is the black artwork for light backgrounds;
    `light` is the white artwork used on dark backgrounds (the footer)."""
    src = "AZSCO_Logo_white.png" if variant == "light" else "AZSCO_Logo.png"
    return ('<img class="brand-logo" src="assets/img/%s" '
            'alt="AZSCO Security" width="347" height="160">' % src)


# ============================================================ shared strings
COMPANY   = ("AZSCO Security Services Company", "شركة أزكو لخدمات حراسة المنشآت ذ.م.م")
# The company's own profile document: "Azsco Security Services LLC, formerly
# known as Almail Zone Security Services." Used once, in the About page story.
FORMER_NAME = ("Almail Zone Security Services", "شركة الميل زون للخدمات الأمنية")
SITE_NAME = ("AZSCO Security", "أزسكو للأمن")
TAGLINE   = ("Security &amp; Guarding", "الأمن والحراسة")
ADDRESS_1L = ("Floor 27B, Kuwait Building Tower, Fahad Al Salem St., Qibla, Kuwait",
              "الدور 27B، برج مبنى الكويت، شارع فهد السالم، القبلة، الكويت")
ADDRESS_BR = ("Floor 27B, Kuwait Building Tower,<br>Fahad Al Salem St., Qibla, Kuwait",
              "الدور 27B، برج مبنى الكويت،<br>شارع فهد السالم، القبلة، الكويت")
HOURS      = ("Sunday &ndash; Thursday, 8:30 AM &ndash; 4:30 PM", "الأحد &ndash; الخميس، 8:30 صباحاً &ndash; 4:30 مساءً")
HOURS_FOOT = ("Sunday &ndash; Thursday, 8:30 AM &ndash; 4:30 PM<br>Emergency response 24/7",
              "الأحد &ndash; الخميس، 8:30 صباحاً &ndash; 4:30 مساءً<br>استجابة الطوارئ على مدار الساعة")
RESPONSE_24 = ("24/7 Response", "استجابة على مدار الساعة")
LANG_SWITCH = ("العربية", "English")
LANG_SWITCH_SHORT = ("ع", "EN")
LANG_SWITCH_LABEL = ("Switch to Arabic", "التبديل إلى الإنجليزية")

UI = {
    "consult":    ("Request a Consultation", "اطلب استشارة"),
    "consult_m":  ("Request a Consultation", "اطلب استشارة"),
    "learn":      ("Learn more", "اعرف المزيد"),
    "more_about": ("More About Us", "المزيد عنّا"),
    "explore":    ("Explore Our Services", "تصفّح خدماتنا"),
    "talk":       ("Talk to Our Team", "تحدّث مع فريقنا"),
    "req_quote":  ("Request a Quote", "اطلب عرض سعر"),
    "home":       ("Home", "الرئيسية"),
    "menu_open":  ("Open menu", "فتح القائمة"),
    "menu_close": ("Close menu", "إغلاق القائمة"),
    "to_top":     ("Back to top", "العودة إلى الأعلى"),
    "whatsapp":   ("Chat with us on WhatsApp", "تواصل معنا عبر واتساب"),
    "skip":       ("Skip to content", "تخطّي إلى المحتوى"),
    "call_now":   ("Call Now", "اتصل الآن"),
    "get_quote":  ("Get a Quote", "عرض سعر"),
    "call_us":    ("Call us anytime", "اتصل بنا في أي وقت"),
    "social":     ("AZSCO on social media", "أزسكو على وسائل التواصل"),
    "map_label":  ("AZSCO office location on Google Maps (opens in a new tab)",
                   "موقع مكتب أزسكو على خرائط جوجل (يفتح في تبويب جديد)"),
    "home_label": ("AZSCO Security — home", "أزسكو للأمن — الصفحة الرئيسية"),
    "main_nav":   ("Main navigation", "التنقل الرئيسي"),
    "mob_nav":    ("Mobile navigation", "قائمة التنقل للجوال"),
}

CHAT = {
  "launcher": ("AZSCO Assistant", "مساعد أزسكو"),
  "title": ("AZSCO Assistant", "مساعد أزسكو"),
  "sub": ("Ask about our security services", "اسأل عن خدماتنا الأمنية"),
  "greeting": ("Hello. I am the AZSCO Assistant. What can I help you with today? You can ask about our guarding services, the areas we cover, or how to request a quote.",
               "مرحباً. أنا مساعد أزسكو. كيف يمكنني مساعدتك اليوم؟ يمكنك السؤال عن خدمات الحراسة لدينا، أو المناطق التي نغطيها، أو كيفية طلب عرض سعر."),
  "placeholder": ("Type your question&hellip;", "اكتب سؤالك&hellip;"),
  "send": ("Send message", "إرسال الرسالة"),
  "close": ("Close assistant", "إغلاق المساعد"),
  "expand": ("Expand assistant", "توسيع المساعد"),
  "collapse": ("Collapse assistant", "تصغير المساعد"),
  "open": ("Open the AZSCO Assistant", "فتح مساعد أزسكو"),
  "suggest": [
    ("What services do you offer?", "ما الخدمات التي تقدّمونها؟"),
    ("How do I request a quote?", "كيف أطلب عرض سعر؟"),
    ("What areas do you cover?", "ما المناطق التي تغطونها؟"),
  ],
  "error": ("Sorry, I could not reach the assistant just now. Please try again, or contact our team directly on (+965) 1808606 or info@azsco.com.",
            "عذراً، تعذّر الوصول إلى المساعد في الوقت الحالي. يُرجى المحاولة مرة أخرى، أو التواصل مع فريقنا مباشرة على (+965) 1808606 أو info@azsco.com."),
  "offline": ("The assistant is not connected yet. Please contact our team on (+965) 1808606 or info@azsco.com and we will be glad to help.",
              "لم يتم تفعيل المساعد بعد. يُرجى التواصل مع فريقنا على (+965) 1808606 أو info@azsco.com وسيسعدنا مساعدتك."),
  "foot": ("AI assistant — may be inaccurate. For anything binding, contact our team.",
           "مساعد ذكاء اصطناعي — قد تكون إجاباته غير دقيقة. لأي أمر مُلزم يُرجى التواصل مع فريقنا."),
}

# No "Home" item: the logo links to the home page in both the header and the
# mobile drawer, so a separate entry would be a second route to the same place.
# ============================================================ catalogue model
# This site sells security systems hardware. The catalogue is a two-level
# model -- CATEGORIES, then PRODUCTS belonging to one category each -- and
# every page below is generated from it, so the navigation, the filters, the
# category pages, the product pages and the sitemap cannot disagree about
# what is in stock.
#
# Pricing is deliberately absent. Security systems are quoted per site after
# a survey, so a product's call to action adds it to a quote basket (held in
# the browser, see assets/js/main.js) rather than a cart.

# Extra interface strings for the catalogue. The furniture the original
# services site needed (UI above) is unchanged.
UI.update({
    "browse":      ("Browse Products", "تصفّح المنتجات"),
    "all_products": ("All Products", "جميع المنتجات"),
    "add_quote":   ("Add to quote", "أضف إلى طلب العرض"),
    "added":       ("Added", "تمت الإضافة"),
    "view_quote":  ("View quote", "عرض الطلب"),
    "quote_req":   ("Request a Quote", "اطلب عرض سعر"),
    "your_quote":  ("Your Quote", "طلب العرض"),
    "quote_items": ("items in your quote", "صنف في طلبك"),
    "filters":     ("Filter", "تصفية"),
    "clear_all":   ("Clear all", "مسح الكل"),
    "category":    ("Category", "الفئة"),
    "brand_lines": ("Brand line", "العلامة التجارية"),
    "showing":     ("Showing", "عرض"),
    "of":          ("of", "من"),
    "products":    ("products", "منتج"),
    "no_match":    ("No products match those filters.",
                    "لا توجد منتجات مطابقة لهذه التصفية."),
    "no_match_cta": ("Clear the filters, or tell us what you need and we will source it.",
                     "امسح عوامل التصفية، أو أخبرنا بما تحتاجه وسنقوم بتوفيره."),
    "specs":       ("Specifications", "المواصفات"),
    "key_specs":   ("Key specifications", "أبرز المواصفات"),
    "full_specs":  ("Full specifications", "المواصفات الكاملة"),
    "highlights":  ("Highlights", "المزايا"),
    "typical_use": ("Typical applications", "التطبيقات النموذجية"),
    "related":     ("Related products", "منتجات ذات صلة"),
    "view_product": ("View product", "عرض المنتج"),
    "in_category": ("in this category", "في هذه الفئة"),
    "view_cat":    ("View category", "عرض الفئة"),
    "remove":      ("Remove", "إزالة"),
    "qty":         ("Qty", "الكمية"),
    "quote_empty": ("Your quote is empty", "طلب العرض فارغ"),
    "quote_empty_t": ("Add products from the catalogue and they will collect here, ready to send to our team in one enquiry.",
                      "أضف المنتجات من الكتالوج لتتجمّع هنا، جاهزة لإرسالها إلى فريقنا في طلب واحد."),
    "quote_note":  ("Prices are quoted per site after a free survey, so the catalogue carries specifications rather than price tags.",
                    "تُحدَّد الأسعار لكل موقع بعد معاينة مجانية، لذا يعرض الكتالوج المواصفات بدلاً من الأسعار."),
    "supplied_by": ("Supplied from", "يُورَّد من"),
    "part_of":     ("Part of", "ضمن"),
    "sku":         ("Reference", "الرمز"),
    "explore_cat": ("Explore Categories", "تصفّح الفئات"),
    "all_brands":  ("All Brands", "جميع العلامات"),
    "installed":   ("Supplied, installed and maintained by AZSCO",
                    "توريد وتركيب وصيانة من أزسكو"),
})

# No "Home" item: the logo links home from both the header and the drawer.
# Products leads, because the catalogue is what this site is for.
NAV = [
    (("Products", "المنتجات"), "products.html", [
        (("All Products", "جميع المنتجات"), "products.html"),
        (("Video Surveillance", "المراقبة بالفيديو"), "cat-video-surveillance"),
        (("Intrusion &amp; Fire", "الإنذار والحريق"), "cat-intrusion-fire"),
        (("Access Control", "التحكم بالدخول"), "cat-access-control"),
        (("Radio &amp; Networking", "الاتصال والشبكات"), "cat-radio-networking"),
    ]),
    (("Brands", "العلامات التجارية"), "brands.html", []),
    (("Support", "التركيب والصيانة"), "support.html", []),
    (("About", "من نحن"), "about.html", []),
    (("Contact", "اتصل بنا"), "contact.html", []),
]

FOOTER = {
    "blurb": ("AZSCO supplies, installs and maintains security systems across Kuwait — "
              "surveillance, intrusion and fire detection, access control, and the radio "
              "and network hardware that ties them together. Established 2014, ISO 9001:2015 certified.",
              "تقوم أزسكو بتوريد وتركيب وصيانة الأنظمة الأمنية في جميع أنحاء الكويت — "
              "المراقبة، وكشف التسلل والحريق، والتحكم بالدخول، وأجهزة الاتصال والشبكات التي تربطها معاً. "
              "تأسست عام 2014، وحاصلة على شهادة الأيزو 9001:2015."),
    "cat_head": ("Catalogue", "الكتالوج"),
    "com_head": ("Company", "الشركة"),
    "con_head": ("Get in touch", "تواصل معنا"),
    "email_general": ("General enquiries", "الاستفسارات العامة"),
    "email_sales": ("Sales and quotations", "المبيعات وعروض الأسعار"),
    "rights": ("All rights reserved.", "جميع الحقوق محفوظة."),
    "privacy": ("Privacy Policy", "سياسة الخصوصية"),
    "contact": ("Contact", "اتصل بنا"),
    "company": [
        (("Home", "الرئيسية"), "index.html"),
        (("About AZSCO", "من نحن"), "about.html"),
        (("Brands", "العلامات التجارية"), "brands.html"),
        (("Installation &amp; Support", "التركيب والصيانة"), "support.html"),
        (("Contact", "اتصل بنا"), "contact.html"),
        (("Privacy Policy", "سياسة الخصوصية"), "privacy-policy.html"),
    ],
}

CTA_DEFAULT = (
    ("Not sure which system fits your site?",
     "لست متأكداً من النظام المناسب لموقعك؟"),
    ("Tell us what you need to protect. We survey the site free of charge, specify the "
     "equipment, and quote the supply, installation and maintenance as one package.",
     "أخبرنا بما تريد حمايته. نقوم بمعاينة الموقع مجاناً، ونحدّد المواصفات، "
     "ونقدّم عرضاً شاملاً للتوريد والتركيب والصيانة."),
)

# ---------------------------------------------------------------- categories
CATEGORIES = [
    {
        "slug": "video-surveillance",
        "icon": "camera",
        "name": ("Video Surveillance", "المراقبة بالفيديو"),
        "tag": ("Cameras, recorders and video storage",
                "كاميرات وأجهزة تسجيل وتخزين"),
        "lead": ("IP cameras and recording for sites that need to see what happened and "
                 "who was there. Fixed cameras for entrances, perimeters and corridors, "
                 "PTZ for wide areas, and recorders sized so footage is still there when "
                 "it is asked for — feeding our Central Operations Room where the site is monitored.",
                 "كاميرات شبكية وأنظمة تسجيل للمواقع التي تحتاج إلى معرفة ما حدث ومَن كان هناك. "
                 "كاميرات ثابتة للمداخل والأسوار والممرات، وكاميرات متحركة للمساحات الواسعة، "
                 "وأجهزة تسجيل بسعة تضمن بقاء التسجيلات عند الحاجة إليها — "
                 "متصلة بغرفة العمليات المركزية لدينا حيث تُراقَب المواقع."),
        "apps": [("Building entrances and lobbies", "مداخل المباني والاستقبال"),
                 ("Perimeters and car parks", "الأسوار ومواقف السيارات"),
                 ("Retail floors and stockrooms", "صالات البيع والمخازن"),
                 ("Warehouses and industrial yards", "المستودعات والساحات الصناعية")],
    },
    {
        "slug": "intrusion-fire",
        "icon": "alarm",
        "name": ("Intrusion &amp; Fire", "الإنذار والحريق"),
        "tag": ("Alarm panels, detectors and sounders",
                "لوحات إنذار وكواشف وصفّارات"),
        "lead": ("Detection that raises the alarm the moment a door opens, a room is "
                 "entered out of hours, or smoke is detected. Wireless throughout, so a "
                 "working building can be protected without cutting channels into finished "
                 "walls — and every alarm reports to the monitoring room, not just to a siren.",
                 "أنظمة كشف تُطلق الإنذار فور فتح باب، أو دخول غرفة خارج أوقات العمل، "
                 "أو رصد دخان. لاسلكية بالكامل، بحيث يمكن حماية مبنى قائم دون شقّ الجدران "
                 "المشطّبة — وكل إنذار يُبلَّغ إلى غرفة المراقبة، لا إلى صفّارة فقط."),
        "apps": [("Offices and clinics out of hours", "المكاتب والعيادات خارج الدوام"),
                 ("Villas and residential compounds", "الفلل والمجمعات السكنية"),
                 ("Stockrooms, safes and server rooms", "المخازن والخزائن وغرف الخوادم"),
                 ("Unmanned sites and plant rooms", "المواقع غير المأهولة وغرف المعدات")],
    },
    {
        "slug": "access-control",
        "icon": "lock",
        "name": ("Access Control", "التحكم بالدخول"),
        "tag": ("Controllers, readers, turnstiles and attendance",
                "لوحات تحكم وقارئات وبوابات وحضور"),
        "lead": ("Control of who goes where, and a record of it afterwards. Card, fingerprint "
                 "and face credentials on doors, lifts and turnstiles, with rules by person, "
                 "door and time of day — and the same terminals doubling as the time and "
                 "attendance system, so one installation answers both questions.",
                 "تحكّم في مَن يدخل إلى أين، وسجلّ بذلك بعد وقوعه. بطاقات وبصمات وتعرّف على "
                 "الوجه على الأبواب والمصاعد والبوابات، مع صلاحيات حسب الشخص والباب والوقت — "
                 "وتعمل الأجهزة نفسها كنظام للحضور والانصراف، فيُجيب تركيب واحد عن السؤالين."),
        "apps": [("Staff-only and restricted areas", "المناطق المحظورة وللموظفين فقط"),
                 ("Reception and visitor management", "الاستقبال وإدارة الزوّار"),
                 ("Labour accommodation and gates", "سكن العمال والبوابات"),
                 ("Payroll-grade attendance records", "سجلات حضور معتمدة للرواتب")],
    },
    {
        "slug": "radio-networking",
        "icon": "headset",
        "name": ("Radio &amp; Networking", "الاتصال والشبكات"),
        "tag": ("Two-way radio, routers and PoE switching",
                "أجهزة اتصال لاسلكي وراوترات ومبدّلات"),
        "lead": ("What the other three categories run on. Two-way radio so guards and "
                 "supervisors reach each other and the operations room without relying on "
                 "personal phones, and the routers and PoE switching that carry cameras, "
                 "controllers and alarms — including sites with no fixed line.",
                 "البنية التي تعمل عليها الفئات الثلاث الأخرى. أجهزة اتصال لاسلكي تتيح "
                 "للحرّاس والمشرفين التواصل فيما بينهم ومع غرفة العمليات دون الاعتماد على "
                 "الهواتف الشخصية، والراوترات والمبدّلات التي تحمل الكاميرات ولوحات التحكم "
                 "والإنذارات — بما في ذلك المواقع بلا خط ثابت."),
        "apps": [("Guard and supervisor communications", "اتصالات الحرّاس والمشرفين"),
                 ("Sites with no fixed line", "المواقع بلا خط ثابت"),
                 ("Camera and controller backbones", "شبكات الكاميرات ولوحات التحكم"),
                 ("Temporary and event networks", "شبكات المواقع المؤقتة والفعاليات")],
    },
]

CAT_BY_SLUG = {c["slug"]: c for c in CATEGORIES}

# The eight technology partners from AZSCO's company profile. They are the
# lines we supply, install and maintain; the catalogue entries above are
# specified per site from these lines rather than sold as fixed SKUs.
BRANDS = [
    ("Ajax",      ("Wireless intrusion and fire detection", "كشف التسلل والحريق لاسلكياً"), ["intrusion-fire"]),
    ("Hikvision", ("IP cameras, recorders and access control", "كاميرات شبكية وأجهزة تسجيل وتحكم بالدخول"), ["video-surveillance", "access-control"]),
    ("Avigilon",  ("High-definition surveillance and video analytics", "مراقبة عالية الدقة وتحليلات فيديو"), ["video-surveillance"]),
    ("Pelco",     ("Professional cameras and video management", "كاميرات احترافية وإدارة فيديو"), ["video-surveillance"]),
    ("Rasilient", ("Purpose-built video recording and storage", "تسجيل وتخزين فيديو مخصّص"), ["video-surveillance"]),
    ("Motorola",  ("Two-way radio and dispatch systems", "أجهزة اتصال لاسلكي وأنظمة إرسال"), ["radio-networking"]),
    ("Inrico",    ("Network radio over LTE", "أجهزة اتصال عبر شبكات LTE"), ["radio-networking"]),
    ("Teltonika", ("Industrial routers and network hardware", "راوترات صناعية وأجهزة شبكات"), ["radio-networking"]),
]

SECTORS = [
    ("Government", "جهات حكومية"), ("Banking &amp; finance", "البنوك والمال"),
    ("Hotels &amp; hospitality", "الفنادق والضيافة"), ("Retail &amp; malls", "التجزئة والمجمعات"),
    ("Industrial &amp; logistics", "الصناعة واللوجستيات"), ("Healthcare", "الرعاية الصحية"),
    ("Education", "التعليم"), ("Residential compounds", "المجمعات السكنية"),
    ("Ports &amp; terminals", "الموانئ والمحطات"), ("Construction sites", "مواقع الإنشاءات"),
    ("Offices &amp; towers", "المكاتب والأبراج"), ("Events &amp; venues", "الفعاليات والمواقع"),
]


# ---------------------------------------------------------------- products
# Catalogue entries describe the class of equipment AZSCO specifies, supplies
# and installs -- an outdoor 4K bullet camera, a four-door controller -- not a
# fixed manufacturer part number. That is deliberate: the exact model is
# chosen per site from the brand lines in BRANDS once the survey is done, and
# a spec sheet nailed to one part number would go out of date the first time a
# vendor revised its range. Figures below are the class's working envelope;
# the quoted model's own datasheet governs on delivery.
#
# specs: (label, value) pairs, both bilingual. Values are wrapped in <span
# dir="ltr"> by spec_value() where they are numeric, so "8 MP" and
# "2.8-12 mm" read correctly inside Arabic.
PRODUCTS = [
    # ------------------------------------------------ video surveillance
    {
        "slug": "ip-bullet-camera-4k", "cat": "video-surveillance", "icon": "camera",
        "featured": True,
        "name": ("4K IP Bullet Camera", "كاميرا بوليت شبكية بدقة 4K"),
        "kind": ("Outdoor fixed camera", "كاميرا خارجية ثابتة"),
        "blurb": ("A long-range outdoor camera for entrances, perimeters and car parks, "
                  "with a motorised lens that is set once at commissioning and infrared "
                  "that keeps a usable picture after dark.",
                  "كاميرا خارجية بعيدة المدى للمداخل والأسوار ومواقف السيارات، بعدسة "
                  "مُحرّكة تُضبط مرة واحدة عند التشغيل، وأشعة تحت حمراء تحافظ على صورة "
                  "واضحة بعد حلول الظلام."),
        "highlights": [("Reads plates and faces at the gate, not just movement",
                        "تُميّز اللوحات والوجوه عند البوابة، لا الحركة فقط"),
                       ("Holds its picture in Kuwait summer heat and glare",
                        "تحافظ على جودة الصورة في حرارة الكويت ووهجها"),
                       ("One cable for power and video", "كابل واحد للطاقة والفيديو")],
        "specs": [(("Resolution", "الدقة"), ("8 MP (3840 &times; 2160)", "8 ميجابكسل (3840 &times; 2160)")),
                  (("Lens", "العدسة"), ("2.8&ndash;12 mm motorised varifocal", "2.8&ndash;12 ملم متغيّرة البعد")),
                  (("Night vision", "الرؤية الليلية"), ("Infrared to 60 m", "أشعة تحت حمراء حتى 60 م")),
                  (("Weather rating", "مقاومة الطقس"), ("IP67", "IP67")),
                  (("Power", "التغذية"), ("PoE (802.3af) or 12 V DC", "PoE (802.3af) أو 12 فولت")),
                  (("Analytics", "التحليلات"), ("Line crossing, intrusion, loitering", "تجاوز خط، تسلل، تسكّع")),
                  (("Local storage", "تخزين محلي"), ("microSD to 256 GB", "بطاقة microSD حتى 256 جيجابايت"))],
    },
    {
        "slug": "ip-dome-camera-4k", "cat": "video-surveillance", "icon": "camera",
        "featured": False,
        "name": ("4K Vandal-Resistant Dome Camera", "كاميرا قبّة مضادة للتخريب بدقة 4K"),
        "kind": ("Indoor / outdoor dome", "كاميرا قبّة داخلية / خارجية"),
        "blurb": ("A low-profile dome for lobbies, corridors and retail floors, in a "
                  "housing rated to survive a deliberate kick — the usual choice where a "
                  "camera is within reach of the public.",
                  "كاميرا قبّة منخفضة الارتفاع للاستقبال والممرات وصالات البيع، ضمن هيكل "
                  "مصمّم لتحمّل الضرب المتعمّد — الخيار المعتاد حيث تكون الكاميرا في "
                  "متناول الجمهور."),
        "highlights": [("Survives tampering where cameras are reachable",
                        "تقاوم العبث حيث تكون الكاميرات في المتناول"),
                       ("Wide view covers a room from one position",
                        "زاوية واسعة تغطي الغرفة من موضع واحد"),
                       ("Handles backlit doorways without silhouettes",
                        "تتعامل مع المداخل ذات الإضاءة الخلفية دون ظلال")],
        "specs": [(("Resolution", "الدقة"), ("8 MP (3840 &times; 2160)", "8 ميجابكسل (3840 &times; 2160)")),
                  (("Lens", "العدسة"), ("2.8 mm fixed, 110&deg; view", "2.8 ملم ثابتة، زاوية 110&deg;")),
                  (("Night vision", "الرؤية الليلية"), ("Infrared to 30 m", "أشعة تحت حمراء حتى 30 م")),
                  (("Impact rating", "مقاومة الصدمات"), ("IK10 vandal-resistant", "IK10 مضادة للتخريب")),
                  (("Weather rating", "مقاومة الطقس"), ("IP67", "IP67")),
                  (("Dynamic range", "المدى الديناميكي"), ("120 dB WDR", "120 ديسيبل WDR")),
                  (("Power", "التغذية"), ("PoE (802.3af)", "PoE (802.3af)"))],
    },
    {
        "slug": "ptz-camera-25x", "cat": "video-surveillance", "icon": "eye",
        "featured": True,
        "name": ("PTZ Camera, 25&times; Optical Zoom", "كاميرا متحركة بتقريب بصري 25&times;"),
        "kind": ("Pan / tilt / zoom camera", "كاميرا دوّارة بتقريب"),
        "blurb": ("One camera covering ground that would otherwise need several — yards, "
                  "compounds and long perimeters — and zooming in far enough to identify "
                  "rather than merely detect. Follows a moving subject on its own.",
                  "كاميرا واحدة تغطي مساحة كانت ستحتاج إلى عدة كاميرات — الساحات "
                  "والمجمعات والأسوار الطويلة — وتقرّب بما يكفي للتعرّف لا للكشف فقط. "
                  "وتتتبّع الهدف المتحرك تلقائياً."),
        "highlights": [("Covers a whole yard from a single mast",
                        "تغطي ساحة كاملة من عمود واحد"),
                       ("Auto-tracks a subject once it starts moving",
                        "تتتبّع الهدف تلقائياً بمجرد تحرّكه"),
                       ("Presets return it to key points on alarm",
                        "مواضع مبرمجة تعيدها إلى النقاط المهمة عند الإنذار")],
        "specs": [(("Resolution", "الدقة"), ("4 MP", "4 ميجابكسل")),
                  (("Optical zoom", "التقريب البصري"), ("25&times;", "25&times;")),
                  (("Pan / tilt", "الدوران / الميل"), ("360&deg; endless pan, 90&deg; tilt", "دوران 360&deg; مستمر، ميل 90&deg;")),
                  (("Night vision", "الرؤية الليلية"), ("Infrared to 150 m", "أشعة تحت حمراء حتى 150 م")),
                  (("Tracking", "التتبّع"), ("Automatic subject tracking", "تتبّع تلقائي للهدف")),
                  (("Weather rating", "مقاومة الطقس"), ("IP66", "IP66")),
                  (("Power", "التغذية"), ("Hi-PoE (802.3bt) or 24 V AC", "Hi-PoE (802.3bt) أو 24 فولت"))],
    },
    {
        "slug": "nvr-16-channel", "cat": "video-surveillance", "icon": "grid",
        "featured": False,
        "name": ("16-Channel Network Video Recorder", "مسجّل فيديو شبكي بـ 16 قناة"),
        "kind": ("Recording and storage", "تسجيل وتخزين"),
        "blurb": ("Where the footage actually lives. Sized at survey so the retention the "
                  "site needs — thirty days, ninety, whatever the policy says — is still "
                  "on the disk when someone comes asking for it.",
                  "المكان الذي تُحفظ فيه التسجيلات فعلياً. تُحدَّد سعته عند المعاينة بحيث "
                  "تبقى مدة الاحتفاظ المطلوبة — ثلاثون يوماً أو تسعون أو ما تقتضيه السياسة "
                  "— متاحة عند طلبها."),
        "highlights": [("Powers the cameras as well as recording them",
                        "تغذّي الكاميرات بالطاقة إضافة إلى تسجيلها"),
                       ("Keeps recording through a single disk failure",
                        "يواصل التسجيل رغم تعطّل قرص واحد"),
                       ("Exports a clip with its own integrity stamp",
                        "يصدّر المقاطع مع ختم تحقّق من سلامتها")],
        "specs": [(("Channels", "القنوات"), ("16 IP cameras", "16 كاميرا شبكية")),
                  (("Built-in PoE", "منافذ PoE"), ("16 ports", "16 منفذاً")),
                  (("Drive bays", "أقراص التخزين"), ("4 bays, to 10 TB each", "4 فتحات، حتى 10 تيرابايت لكل منها")),
                  (("Redundancy", "الحماية من الأعطال"), ("RAID 0 / 1 / 5 / 10", "RAID 0 / 1 / 5 / 10")),
                  (("Compression", "الضغط"), ("H.265+ / H.264+", "H.265+ / H.264+")),
                  (("Output", "المخرجات"), ("Dual HDMI, 4K", "منفذا HDMI بدقة 4K")),
                  (("Remote access", "الوصول عن بُعد"), ("Mobile app and web client", "تطبيق للجوال وواجهة ويب"))],
    },
    # ------------------------------------------------ intrusion and fire
    {
        "slug": "wireless-alarm-hub", "cat": "intrusion-fire", "icon": "shield",
        "featured": True,
        "name": ("Wireless Alarm Control Hub", "لوحة تحكم إنذار لاسلكية"),
        "kind": ("Alarm panel", "لوحة إنذار"),
        "blurb": ("The panel every detector reports to, and the point that reaches our "
                  "operations room. Two independent paths out — fixed line and cellular — "
                  "so cutting one does not silence the building.",
                  "اللوحة التي تُبلّغ إليها جميع الكواشف، ونقطة الاتصال بغرفة العمليات "
                  "لدينا. لها مساران مستقلان للخروج — خط ثابت وشبكة خلوية — بحيث لا يؤدي "
                  "قطع أحدهما إلى إسكات المبنى."),
        "highlights": [("Reports to the operations room, not just a siren",
                        "يُبلّغ غرفة العمليات، لا صفّارة فقط"),
                       ("Stays online on cellular if the line is cut",
                        "يبقى متصلاً عبر الشبكة الخلوية إذا قُطع الخط"),
                       ("Runs through a power cut on its own battery",
                        "يعمل أثناء انقطاع الكهرباء ببطاريته")],
        "specs": [(("Devices supported", "عدد الأجهزة"), ("Up to 100", "حتى 100 جهاز")),
                  (("Radio range", "مدى الإرسال"), ("To 2,000 m open ground", "حتى 2000 م في الأماكن المفتوحة")),
                  (("Connectivity", "الاتصال"), ("Ethernet plus dual SIM LTE", "إيثرنت مع شريحتي LTE")),
                  (("Battery backup", "البطارية الاحتياطية"), ("Up to 16 hours", "حتى 16 ساعة")),
                  (("Partitions", "الأقسام"), ("Up to 9 independent groups", "حتى 9 مجموعات مستقلة")),
                  (("Reporting", "الإبلاغ"), ("Monitoring centre and mobile app", "مركز المراقبة وتطبيق الجوال"))],
    },
    {
        "slug": "wireless-motion-detector", "cat": "intrusion-fire", "icon": "target",
        "featured": False,
        "name": ("Wireless Motion Detector", "كاشف حركة لاسلكي"),
        "kind": ("Intrusion detector", "كاشف تسلل"),
        "blurb": ("Covers a room and calls the hub the moment someone is in it out of "
                  "hours. Tuned to ignore a cat or a small dog, so a site with animals is "
                  "not woken by its own alarm every night.",
                  "يغطي الغرفة ويُبلّغ اللوحة فور دخول أحد إليها خارج أوقات العمل. مضبوط "
                  "لتجاهل القطط والكلاب الصغيرة، فلا يوقَظ الموقع الذي فيه حيوانات بإنذاره "
                  "كل ليلة."),
        "highlights": [("No cabling through finished walls",
                        "بلا تمديدات في الجدران المشطّبة"),
                       ("Ignores pets under 20 kg", "يتجاهل الحيوانات دون 20 كجم"),
                       ("Reports its own battery before it dies",
                        "يُبلّغ عن بطاريته قبل نفادها")],
        "specs": [(("Detection range", "مدى الكشف"), ("12 m, 88&deg; field", "12 م، مجال 88&deg;")),
                  (("Pet immunity", "مناعة الحيوانات"), ("Animals to 20 kg", "حيوانات حتى 20 كجم")),
                  (("Battery life", "عمر البطارية"), ("Up to 5 years", "حتى 5 سنوات")),
                  (("Tamper", "الحماية من العبث"), ("Case and wall tamper", "حماية الغطاء والتثبيت")),
                  (("Mounting", "التركيب"), ("Wall or corner bracket", "حامل جداري أو ركني"))],
    },
    {
        "slug": "door-window-contact", "cat": "intrusion-fire", "icon": "lock",
        "featured": False,
        "name": ("Wireless Door &amp; Window Contact", "كاشف فتح للأبواب والنوافذ لاسلكي"),
        "kind": ("Opening detector", "كاشف فتح"),
        "blurb": ("The cheapest useful thing on a perimeter: it reports the door opening "
                  "at all, which is usually the first fact anyone wants. Small enough to "
                  "sit on a frame without being noticed.",
                  "أبسط عنصر مفيد على المحيط: يُبلّغ عن فتح الباب أصلاً، وهي عادة أول "
                  "معلومة يحتاجها أي شخص. صغير بما يكفي ليُركّب على الإطار دون أن يُلاحَظ."),
        "highlights": [("Fits a frame without drilling the door",
                        "يُركّب على الإطار دون ثقب الباب"),
                       ("Takes a wired sensor on its spare input",
                        "يقبل كاشفاً سلكياً على مدخله الإضافي"),
                       ("Five-year battery", "بطارية تدوم خمس سنوات")],
        "specs": [(("Gap detection", "مسافة الكشف"), ("To 20 mm", "حتى 20 ملم")),
                  (("Battery life", "عمر البطارية"), ("Up to 5 years", "حتى 5 سنوات")),
                  (("Auxiliary input", "مدخل إضافي"), ("One wired zone", "منطقة سلكية واحدة")),
                  (("Tamper", "الحماية من العبث"), ("Case and wall tamper", "حماية الغطاء والتثبيت")),
                  (("Finish", "اللون"), ("White or brown", "أبيض أو بني"))],
    },
    {
        "slug": "smoke-heat-detector", "cat": "intrusion-fire", "icon": "flame",
        "featured": True,
        "name": ("Wireless Smoke &amp; Heat Detector", "كاشف دخان وحرارة لاسلكي"),
        "kind": ("Fire detector", "كاشف حريق"),
        "blurb": ("Two ways of noticing a fire in one device — smoke, and a rise in "
                  "temperature — because each misses fires the other catches. Sounds the "
                  "whole set at once, not just the one that tripped.",
                  "طريقتان لاكتشاف الحريق في جهاز واحد — الدخان وارتفاع الحرارة — لأن كلاً "
                  "منهما يفوته ما يكتشفه الآخر. ويُطلق الإنذار في جميع الكواشف معاً، لا في "
                  "الذي رصد الحريق فقط."),
        "highlights": [("Smoke and heat sensing in one unit",
                        "استشعار الدخان والحرارة في وحدة واحدة"),
                       ("All detectors sound together", "تُطلق جميع الكواشف الإنذار معاً"),
                       ("Alerts the phone as well as the room",
                        "ينبّه الهاتف كما ينبّه الغرفة")],
        "specs": [(("Sensors", "المستشعرات"), ("Optical smoke plus 60 &deg;C heat", "دخان بصري مع حرارة 60 &deg;م")),
                  (("Sounder", "الصفّارة"), ("85 dB at 3 m", "85 ديسيبل على بُعد 3 م")),
                  (("Interlink", "الترابط"), ("All detectors sound together", "إطلاق متزامن لجميع الكواشف")),
                  (("Battery life", "عمر البطارية"), ("Up to 4 years", "حتى 4 سنوات")),
                  (("Self-test", "الفحص الذاتي"), ("Automatic, reports faults", "تلقائي، ويُبلّغ عن الأعطال"))],
    },
    # ------------------------------------------------ access control
    {
        "slug": "four-door-controller", "cat": "access-control", "icon": "cog",
        "featured": True,
        "name": ("Four-Door Access Controller", "لوحة تحكم بالدخول لأربعة أبواب"),
        "kind": ("Door controller", "لوحة تحكم بالأبواب"),
        "blurb": ("The panel that decides whether a door opens. Keeps its rules and its "
                  "event log locally, so the doors carry on working correctly when the "
                  "network or the server is down.",
                  "اللوحة التي تقرّر ما إذا كان الباب سيُفتح. تحتفظ بالصلاحيات وسجلّ "
                  "الأحداث محلياً، فتستمر الأبواب في العمل بشكل صحيح عند تعطّل الشبكة أو "
                  "الخادم."),
        "highlights": [("Doors keep working if the network drops",
                        "تستمر الأبواب في العمل عند انقطاع الشبكة"),
                       ("Releases every door on a fire alarm",
                        "يفتح جميع الأبواب عند إنذار الحريق"),
                       ("Encrypted reader wiring (OSDP)",
                        "توصيل مشفّر للقارئات (OSDP)")],
        "specs": [(("Doors", "الأبواب"), ("4 doors, 8 readers", "4 أبواب، 8 قارئات")),
                  (("Cardholders", "حاملو البطاقات"), ("Up to 100,000", "حتى 100,000")),
                  (("Event buffer", "سجلّ الأحداث"), ("300,000 events offline", "300,000 حدث دون اتصال")),
                  (("Reader protocol", "بروتوكول القارئ"), ("OSDP and Wiegand", "OSDP و Wiegand")),
                  (("Network", "الشبكة"), ("TCP/IP", "TCP/IP")),
                  (("Fire interface", "واجهة الحريق"), ("Fail-safe release input", "مدخل فتح عند الإنذار")),
                  (("Power", "التغذية"), ("12 V DC with battery backup", "12 فولت مع بطارية احتياطية"))],
    },
    {
        "slug": "fingerprint-card-reader", "cat": "access-control", "icon": "check",
        "featured": False,
        "name": ("Fingerprint &amp; Card Reader", "قارئ بصمة وبطاقة"),
        "kind": ("Door reader", "قارئ أبواب"),
        "blurb": ("A reader for doors where a borrowed card is a real risk. Takes a "
                  "fingerprint, a card, or both together where the area warrants it, and "
                  "is rated for an outdoor doorway.",
                  "قارئ للأبواب التي تشكّل فيها البطاقة المُعارة خطراً فعلياً. يقبل البصمة "
                  "أو البطاقة أو كليهما معاً حيث تستدعي المنطقة ذلك، وهو مصنّف للاستخدام "
                  "في المداخل الخارجية."),
        "highlights": [("A fingerprint cannot be lent to a colleague",
                        "لا يمكن إعارة البصمة لزميل"),
                       ("Card and fingerprint together for sensitive doors",
                        "بطاقة وبصمة معاً للأبواب الحسّاسة"),
                       ("Rated for an outdoor doorway", "مصنّف للمداخل الخارجية")],
        "specs": [(("Fingerprint capacity", "سعة البصمات"), ("3,000 templates", "3000 بصمة")),
                  (("Card types", "أنواع البطاقات"), ("MIFARE and DESFire", "MIFARE و DESFire")),
                  (("Verification", "التحقق"), ("Under 1 second", "أقل من ثانية")),
                  (("Protocol", "البروتوكول"), ("OSDP or Wiegand", "OSDP أو Wiegand")),
                  (("Weather rating", "مقاومة الطقس"), ("IP65", "IP65"))],
    },
    {
        "slug": "time-attendance-terminal", "cat": "access-control", "icon": "clock",
        "featured": False,
        "name": ("Time &amp; Attendance Terminal", "جهاز حضور وانصراف"),
        "kind": ("Attendance terminal", "جهاز حضور"),
        "blurb": ("Turns the same door hardware into the attendance record payroll needs. "
                  "Face recognition means staff clock in without touching anything and "
                  "without handing a card to a friend at the gate.",
                  "يحوّل أجهزة الأبواب نفسها إلى سجلّ حضور يخدم الرواتب. التعرّف على الوجه "
                  "يعني تسجيل الحضور دون لمس أي شيء ودون تمرير بطاقة إلى زميل عند البوابة."),
        "highlights": [("Face recognition — nothing to touch or lend",
                        "تعرّف على الوجه — بلا لمس أو إعارة"),
                       ("Exports straight into payroll", "تصدير مباشر إلى نظام الرواتب"),
                       ("Works as a door reader as well",
                        "يعمل كقارئ أبواب أيضاً")],
        "specs": [(("Credentials", "وسائل التعريف"), ("Face, fingerprint and card", "الوجه والبصمة والبطاقة")),
                  (("Face capacity", "سعة الوجوه"), ("1,500 faces", "1500 وجه")),
                  (("Display", "الشاشة"), ("4.3-inch touchscreen", "شاشة لمس 4.3 بوصة")),
                  (("Network", "الشبكة"), ("TCP/IP and Wi-Fi", "TCP/IP وواي فاي")),
                  (("Export", "التصدير"), ("Payroll-ready reports", "تقارير جاهزة للرواتب"))],
    },
    {
        "slug": "tripod-turnstile", "cat": "access-control", "icon": "users",
        "featured": False,
        "name": ("Tripod Turnstile", "بوابة دوّارة ثلاثية"),
        "kind": ("Pedestrian barrier", "حاجز للمشاة"),
        "blurb": ("Makes one person per credential physically true at a busy entrance, "
                  "which a door alone never does. Arms drop clear on power loss so the "
                  "lane becomes an exit route.",
                  "يجعل قاعدة «شخص واحد لكل تصريح» أمراً ملموساً عند المداخل المزدحمة، "
                  "وهو ما لا يحقّقه الباب وحده. وتنخفض الأذرع عند انقطاع الكهرباء ليصبح "
                  "الممر مخرجاً للطوارئ."),
        "highlights": [("One credential, one person through",
                        "تصريح واحد، شخص واحد يعبر"),
                       ("Arms drop clear on power loss", "تنخفض الأذرع عند انقطاع الكهرباء"),
                       ("Stainless body for lobbies and gatehouses",
                        "هيكل ستانلس للاستقبال وغرف البوابات")],
        "specs": [(("Body", "الهيكل"), ("304 stainless steel", "ستانلس ستيل 304")),
                  (("Throughput", "معدل العبور"), ("Up to 30 people per minute", "حتى 30 شخصاً في الدقيقة")),
                  (("Direction", "الاتجاه"), ("Bi-directional, configurable", "اتجاهان، قابل للضبط")),
                  (("On power loss", "عند انقطاع الكهرباء"), ("Arms drop to free passage", "تنخفض الأذرع لفتح الممر")),
                  (("Integration", "التكامل"), ("Accepts any standard reader", "يقبل أي قارئ قياسي"))],
    },
    # ------------------------------------------------ radio and networking
    {
        "slug": "digital-two-way-radio", "cat": "radio-networking", "icon": "headset",
        "featured": True,
        "name": ("Digital Two-Way Radio", "جهاز اتصال لاسلكي رقمي"),
        "kind": ("Handheld radio", "جهاز محمول"),
        "blurb": ("What a guard actually carries. Pressing one button reaches the whole "
                  "shift at once, which a phone call cannot do, and it keeps working when "
                  "the mobile network is congested or down.",
                  "الجهاز الذي يحمله الحارس فعلياً. ضغطة زر واحدة تصل إلى الوردية بأكملها، "
                  "وهو ما لا تحقّقه المكالمة الهاتفية، ويستمر في العمل عند ازدحام شبكة "
                  "الجوال أو تعطّلها."),
        "highlights": [("One press reaches the whole shift",
                        "ضغطة واحدة تصل إلى الوردية كاملة"),
                       ("Man-down and lone-worker alerts",
                        "تنبيهات السقوط والعامل المنفرد"),
                       ("A full shift on one battery", "وردية كاملة ببطارية واحدة")],
        "specs": [(("Mode", "النمط"), ("DMR Tier II and analogue", "DMR Tier II وتناظري")),
                  (("Band", "النطاق"), ("UHF 400&ndash;470 MHz", "UHF 400&ndash;470 ميجاهرتز")),
                  (("Power", "القدرة"), ("4 W", "4 واط")),
                  (("Channels", "القنوات"), ("1,000", "1000")),
                  (("Battery life", "عمر البطارية"), ("Up to 24 hours", "حتى 24 ساعة")),
                  (("Rating", "التصنيف"), ("IP67, dust and water", "IP67، غبار وماء")),
                  (("Safety", "السلامة"), ("Man-down and lone-worker", "السقوط والعامل المنفرد"))],
    },
    {
        "slug": "lte-network-radio", "cat": "radio-networking", "icon": "route",
        "featured": False,
        "name": ("LTE Network Radio", "جهاز اتصال عبر شبكة LTE"),
        "kind": ("Wide-area radio", "جهاز واسع النطاق"),
        "blurb": ("A radio that talks over the mobile network instead of its own "
                  "repeaters, so patrols spread across Kuwait stay on one talk group "
                  "without a licence or a mast.",
                  "جهاز اتصال يعمل عبر شبكة الجوال بدلاً من أجهزة إعادة الإرسال الخاصة، "
                  "فتبقى الدوريات المنتشرة في أنحاء الكويت على مجموعة تحدّث واحدة دون "
                  "ترخيص أو برج."),
        "highlights": [("Nationwide range with no repeaters to build",
                        "تغطية على مستوى البلاد دون بناء أبراج"),
                       ("GPS puts every patrol on the map",
                        "نظام تحديد المواقع يُظهر كل دورية على الخريطة"),
                       ("Talk groups changed from the office",
                        "تُعدَّل مجموعات التحدّث من المكتب")],
        "specs": [(("Network", "الشبكة"), ("4G LTE and Wi-Fi", "4G LTE وواي فاي")),
                  (("Coverage", "التغطية"), ("Anywhere with carrier signal", "أينما توفّرت تغطية المشغّل")),
                  (("Talk groups", "مجموعات التحدّث"), ("Unlimited, managed centrally", "غير محدودة، تُدار مركزياً")),
                  (("Location", "الموقع"), ("GPS tracking", "تتبّع عبر GPS")),
                  (("Licence", "الترخيص"), ("No radio licence required", "لا يتطلب ترخيص تردد")),
                  (("Rating", "التصنيف"), ("IP65", "IP65"))],
    },
    {
        "slug": "industrial-lte-router", "cat": "radio-networking", "icon": "link",
        "featured": False,
        "name": ("Industrial LTE Router", "راوتر صناعي بشبكة LTE"),
        "kind": ("Cellular router", "راوتر خلوي"),
        "blurb": ("Puts a site online where there is no fixed line — a gatehouse, a yard, "
                  "a tower under construction — and fails over to a second SIM rather than "
                  "taking the cameras offline with it.",
                  "يوصل الموقع بالإنترنت حيث لا يوجد خط ثابت — غرفة بوابة أو ساحة أو برج "
                  "قيد الإنشاء — وينتقل تلقائياً إلى شريحة ثانية بدلاً من أن يقطع الاتصال "
                  "عن الكاميرات."),
        "highlights": [("Connects a site with no fixed line",
                        "يوصل موقعاً بلا خط ثابت"),
                       ("Second SIM takes over automatically",
                        "شريحة ثانية تتولّى الاتصال تلقائياً"),
                       ("Rated for a hot plant room", "مصنّف لغرف المعدات الحارة")],
        "specs": [(("Cellular", "الشبكة الخلوية"), ("4G LTE Cat 6", "4G LTE الفئة 6")),
                  (("SIM slots", "فتحات الشرائح"), ("Dual SIM with auto failover", "شريحتان مع تبديل تلقائي")),
                  (("Ethernet", "الإيثرنت"), ("4 &times; Gigabit", "4 &times; جيجابت")),
                  (("Wi-Fi", "الواي فاي"), ("Dual-band Wi-Fi 5", "واي فاي 5 ثنائي النطاق")),
                  (("Operating range", "نطاق التشغيل"), ("&minus;40 to +75 &deg;C", "&minus;40 إلى +75 &deg;م")),
                  (("Security", "الأمان"), ("IPsec and OpenVPN", "IPsec و OpenVPN")),
                  (("Mounting", "التركيب"), ("DIN rail", "قضيب DIN"))],
    },
    {
        "slug": "managed-poe-switch-16", "cat": "radio-networking", "icon": "grid",
        "featured": False,
        "name": ("16-Port Managed PoE Switch", "مبدّل شبكة مُدار بـ 16 منفذ PoE"),
        "kind": ("Network switch", "مبدّل شبكة"),
        "blurb": ("Carries power and data to cameras, readers and access panels on one "
                  "cable each, and can be told to power-cycle a frozen camera remotely "
                  "instead of sending someone up a ladder.",
                  "ينقل الطاقة والبيانات إلى الكاميرات والقارئات ولوحات التحكم بكابل واحد "
                  "لكل جهاز، ويمكن إصدار أمر له بإعادة تشغيل كاميرا متوقفة عن بُعد بدلاً من "
                  "إرسال فنّي بسلّم."),
        "highlights": [("One cable carries power and data",
                        "كابل واحد ينقل الطاقة والبيانات"),
                       ("Restart a frozen camera from the office",
                        "إعادة تشغيل كاميرا متوقفة من المكتب"),
                       ("Keeps cameras on their own VLAN",
                        "يعزل الكاميرات على شبكة افتراضية خاصة")],
        "specs": [(("PoE ports", "منافذ PoE"), ("16 &times; PoE+ (802.3at)", "16 &times; PoE+ (802.3at)")),
                  (("Uplinks", "منافذ الربط"), ("2 &times; SFP gigabit", "2 &times; SFP جيجابت")),
                  (("Power budget", "ميزانية الطاقة"), ("250 W total", "250 واط إجمالاً")),
                  (("Management", "الإدارة"), ("VLAN, QoS, IGMP snooping", "VLAN و QoS و IGMP")),
                  (("Remote reset", "إعادة التشغيل عن بُعد"), ("Per-port power cycling", "لكل منفذ على حدة")),
                  (("Mounting", "التركيب"), ("1U rack mount", "رف بارتفاع 1U"))],
    },
]

PROD_BY_SLUG = {p["slug"]: p for p in PRODUCTS}

def products_in(cat_slug):
    return [p for p in PRODUCTS if p["cat"] == cat_slug]

def brands_for(cat_slug):
    return [b for b in BRANDS if cat_slug in b[2]]


# ============================================================ page copy
HOME = {
    "title": ("Security Systems for Kuwait &mdash; Supplied, Installed and Maintained | AZSCO",
              "أنظمة أمنية للكويت &mdash; توريد وتركيب وصيانة | أزسكو"),
    "desc": ("Surveillance cameras, intrusion and fire alarms, access control, two-way radio "
             "and network hardware &mdash; supplied, installed and maintained across Kuwait by "
             "AZSCO. Free site survey, one quote for the whole system.",
             "كاميرات مراقبة، وأنظمة إنذار وحريق، وتحكم بالدخول، وأجهزة اتصال لاسلكي وشبكات "
             "&mdash; توريد وتركيب وصيانة في جميع أنحاء الكويت من أزسكو. معاينة مجانية وعرض "
             "واحد للنظام بالكامل."),
    "eyebrow": ("Security systems &mdash; Kuwait", "أنظمة أمنية &mdash; الكويت"),
    "h1": ("SECURITY SYSTEMS, SPECIFIED FOR YOUR SITE",
           "أنظمة أمنية مُصمّمة لموقعك"),
    "lead": ("Cameras, alarms, access control and the network behind them &mdash; from one "
             "supplier who surveys the site, installs the equipment and maintains it "
             "afterwards. No box-shifting: every system is specified for the building it "
             "goes into.",
             "كاميرات وأنظمة إنذار وتحكم بالدخول والشبكة التي تربطها &mdash; من مورّد واحد "
             "يعاين الموقع ويُركّب المعدات ويتولّى صيانتها بعد ذلك. لسنا بائعي صناديق: كل "
             "نظام يُصمّم للمبنى الذي سيُركّب فيه."),
    "pick_head": ("Start with what you need to protect",
                  "ابدأ بما تريد حمايته"),
    "pick_sub": ("Four categories, one quote.", "أربع فئات، وعرض سعر واحد."),
    "assur": [("Free site survey before any quote", "معاينة مجانية قبل أي عرض سعر"),
              ("Licensed installers, ISO 9001:2015", "فنّيون مرخّصون، أيزو 9001:2015"),
              ("Maintenance and 24/7 monitoring", "صيانة ومراقبة على مدار الساعة")],
    "cat_eyebrow": ("Catalogue", "الكتالوج"),
    "cat_head": ("What we supply", "ما نقوم بتوريده"),
    "cat_lead": ("Four product categories that are normally specified together &mdash; a camera "
                 "is only as useful as the recorder behind it, and neither is any use without "
                 "the network carrying them.",
                 "أربع فئات من المنتجات تُحدَّد عادةً معاً &mdash; فالكاميرا لا تفيد أكثر من "
                 "المسجّل الذي خلفها، وكلاهما بلا فائدة دون الشبكة التي تحملهما."),
    "feat_eyebrow": ("Popular specifications", "مواصفات مطلوبة"),
    "feat_head": ("Frequently specified", "الأكثر طلباً"),
    "feat_lead": ("The equipment that appears in most of the systems we quote. Add anything "
                  "here to a quote and tell us about the site &mdash; we will confirm the exact "
                  "model after the survey.",
                  "المعدات التي تتكرّر في معظم الأنظمة التي نقدّم عروضاً لها. أضف أياً منها "
                  "إلى طلب عرض وأخبرنا عن الموقع &mdash; وسنؤكّد الطراز الدقيق بعد المعاينة."),
    "how_eyebrow": ("How we work", "كيف نعمل"),
    "how_head": ("Supply is the middle step, not the whole job",
                 "التوريد خطوة في المنتصف، لا العمل كله"),
    "how_lead": ("Equipment bought without a survey tends to be the wrong equipment, and "
                 "equipment installed without maintenance stops working quietly. We quote "
                 "all three together.",
                 "المعدات التي تُشترى دون معاينة غالباً ما تكون غير مناسبة، والمعدات التي "
                 "تُركّب دون صيانة تتوقف عن العمل بصمت. لذلك نقدّم الثلاثة في عرض واحد."),
    "steps": [
        (("Survey", "المعاينة"),
         ("We walk the site, find the blind spots and the ways in, and agree what actually "
          "needs covering before anything is priced.",
          "نتفقّد الموقع، ونحدّد النقاط العمياء ومسارات الدخول، ونتفق على ما يحتاج تغطية "
          "فعلاً قبل تسعير أي شيء.")),
        (("Specify &amp; quote", "التحديد والتسعير"),
         ("You get a drawing, a device schedule and one price covering equipment, "
          "installation and the first year of maintenance.",
          "تحصل على مخطّط وجدول للأجهزة وسعر واحد يشمل المعدات والتركيب والسنة الأولى من "
          "الصيانة.")),
        (("Install &amp; commission", "التركيب والتشغيل"),
         ("Our own technicians cable, mount and configure the system, then hand it over "
          "tested with your staff trained on it.",
          "يقوم فنّيونا بالتمديد والتركيب والضبط، ثم يُسلّمون النظام مُختبراً مع تدريب "
          "موظفيكم عليه.")),
        (("Maintain &amp; monitor", "الصيانة والمراقبة"),
         ("Scheduled service visits, a call-out number that answers, and optional "
          "connection to our 24/7 Central Operations Room.",
          "زيارات صيانة مجدولة، ورقم استدعاء يُجيب فعلاً، وربط اختياري بغرفة العمليات "
          "المركزية لدينا على مدار الساعة.")),
    ],
    "brand_eyebrow": ("Brand lines", "العلامات التجارية"),
    "brand_head": ("The lines we supply", "العلامات التي نورّدها"),
    "brand_lead": ("Eight manufacturers behind the catalogue. Which line a site ends up with "
                   "depends on what it needs, not on what we happen to hold.",
                   "ثماني شركات مصنّعة خلف الكتالوج. والعلامة التي يستقر عليها الموقع تعتمد "
                   "على احتياجه، لا على ما يتوفر لدينا."),
    "sector_eyebrow": ("Where it goes in", "أين تُركّب"),
    "sector_head": ("Sectors we equip", "القطاعات التي نخدمها"),
    "sector_lead": ("The same four categories, specified very differently for a bank, a "
                    "warehouse and a residential compound.",
                    "الفئات الأربع نفسها، تُحدَّد بشكل مختلف تماماً للبنك والمستودع "
                    "والمجمّع السكني."),
}

STATS = [
    ("founded", ("Established in Kuwait", "التأسيس في الكويت")),
    ("years",   ("Years of operation", "سنوات من العمل")),
    ("brands",  ("Manufacturer lines", "علامات مصنّعة")),
    ("247",     ("Operations room", "غرفة العمليات")),
]

ABOUT = {
    "title": ("About AZSCO &mdash; Security Systems Integrator in Kuwait | AZSCO",
              "من نحن &mdash; شركة أنظمة أمنية في الكويت | أزسكو"),
    "desc": ("AZSCO Security Services Company, established 2014 in Kuwait. We supply, "
             "install and maintain security systems, backed by licensed manpower and a "
             "24/7 central operations room. ISO 9001:2015 certified.",
             "شركة أزسكو للخدمات الأمنية، تأسست عام 2014 في الكويت. نقوم بتوريد وتركيب "
             "وصيانة الأنظمة الأمنية، مدعومة بكوادر مرخّصة وغرفة عمليات مركزية تعمل على "
             "مدار الساعة. حاصلون على أيزو 9001:2015."),
    "h1": ("ABOUT AZSCO", "من نحن"),
    "sub": ("A Kuwaiti security company that both installs the system and answers it.",
            "شركة أمنية كويتية تُركّب النظام وتستجيب له."),
    "story_eyebrow": ("Our story", "قصتنا"),
    "story_head": ("Equipment and the people behind it",
                   "المعدات ومَن يقف خلفها"),
    "story": [
        ("AZSCO Security Services Company &mdash; formerly Almail Zone Security Services &mdash; "
         "was established in Kuwait in 2014. It began as a manpower company: licensed, "
         "trained and supervised officers guarding facilities across the country.",
         "تأسست شركة أزسكو للخدمات الأمنية &mdash; وكانت تُعرف سابقاً بشركة الميل زون "
         "للخدمات الأمنية &mdash; في الكويت عام 2014. بدأت كشركة كوادر أمنية: أفراد "
         "مرخّصون ومدرّبون وخاضعون للإشراف يحرسون المنشآت في جميع أنحاء البلاد."),
        ("Security systems followed, because the two problems are one problem. A camera "
         "nobody watches records an incident for later; a guard without cameras covers "
         "one place at a time. We now supply and install the systems as well as staffing "
         "the sites, and our Central Operations Room watches both.",
         "ثم جاءت الأنظمة الأمنية، لأن المشكلتين في الحقيقة مشكلة واحدة. فالكاميرا التي "
         "لا يراقبها أحد تسجّل الحادث للاطلاع لاحقاً، والحارس بلا كاميرات يغطي مكاناً "
         "واحداً في كل مرة. واليوم نقوم بتوريد الأنظمة وتركيبها إلى جانب تزويد المواقع "
         "بالكوادر، وتراقب غرفة العمليات المركزية لدينا الاثنين معاً."),
        ("That is the difference between us and a hardware supplier: we are the people "
         "the alarm reaches. A system we install can report to a room that is staffed at "
         "three in the morning, and to a patrol that can be at the site shortly after.",
         "هذا هو الفرق بيننا وبين مورّد الأجهزة: نحن الجهة التي يصلها الإنذار. فالنظام "
         "الذي نُركّبه يمكن أن يُبلّغ غرفة مأهولة في الثالثة فجراً، ودورية تصل إلى الموقع "
         "بعد ذلك بوقت قصير."),
    ],
    "ovm": [
        ("target", ("Objective", "هدفنا"),
         ("To protect what our clients have built &mdash; their premises, their people and "
          "their property &mdash; with systems that are specified honestly and maintained "
          "properly.",
          "حماية ما بناه عملاؤنا &mdash; منشآتهم وأفرادهم وممتلكاتهم &mdash; بأنظمة تُحدَّد "
          "بصدق وتُصان كما ينبغي.")),
        ("eye", ("Vision", "رؤيتنا"),
         ("To be the security partner Kuwaiti organisations call first, trusted for the "
          "advice as much as for the equipment.",
          "أن نكون الشريك الأمني الذي تتصل به المؤسسات الكويتية أولاً، موثوقين في المشورة "
          "بقدر ما نحن موثوقون في المعدات.")),
        ("shield", ("Mission", "مهمتنا"),
         ("To deliver security systems and manpower to a consistent standard, through "
          "trained people, documented processes and equipment we are prepared to stand "
          "behind.",
          "تقديم أنظمة وكوادر أمنية بمستوى ثابت، عبر أشخاص مدرّبين وإجراءات موثّقة ومعدات "
          "نقف خلفها.")),
    ],
    "why_eyebrow": ("Why buy the system from us", "لماذا تشتري النظام منّا"),
    "why_head": ("What a supplier alone cannot offer",
                 "ما لا يستطيع المورّد وحده تقديمه"),
    "why": [
        ("headset", ("The alarm reaches a staffed room", "الإنذار يصل إلى غرفة مأهولة"),
         ("Our Central Operations Room is manned around the clock, so a system we install "
          "can report to people rather than to an empty inbox.",
          "غرفة العمليات المركزية لدينا مأهولة على مدار الساعة، فالنظام الذي نُركّبه يمكن "
          "أن يُبلّغ أشخاصاً لا بريداً فارغاً.")),
        ("route", ("A patrol can be sent", "يمكن إرسال دورية"),
         ("Because we also provide the manpower, a confirmed alarm can put a patrol on "
          "site instead of ending as a notification on someone's phone.",
          "لأننا نوفّر الكوادر أيضاً، يمكن لإنذار مؤكَّد أن يضع دورية في الموقع بدلاً من "
          "أن ينتهي كإشعار على هاتف أحدهم.")),
        ("cog", ("One contract for the whole system", "عقد واحد للنظام بالكامل"),
         ("Survey, equipment, installation, commissioning and maintenance come from one "
          "company, so there is nobody to blame it on when something stops working.",
          "المعاينة والمعدات والتركيب والتشغيل والصيانة من شركة واحدة، فلا يوجد طرف آخر "
          "يُلقى عليه اللوم عند تعطّل شيء ما.")),
        ("award", ("Certified and accountable", "معتمدون ومسؤولون"),
         ("ISO 9001:2015 certified and licensed in Kuwait, with the documentation a "
          "government or banking client is required to ask for.",
          "حاصلون على أيزو 9001:2015 ومرخّصون في الكويت، مع الوثائق التي يُلزَم العميل "
          "الحكومي أو المصرفي بطلبها.")),
    ],
    "faq_eyebrow": ("Questions", "أسئلة"),
    "faq_head": ("Common questions", "أسئلة شائعة"),
    "faq": [
        (("Do you sell equipment without installation?",
          "هل تبيعون المعدات دون تركيب؟"),
         ("We prefer not to. Most systems that fail do so because of how they were "
          "installed or configured, not because of the hardware, and we will not warrant "
          "an installation we did not carry out. For a site with its own competent "
          "technical team, talk to us &mdash; we will look at it case by case.",
          "نفضّل ألّا نفعل. فمعظم الأنظمة التي تفشل تفشل بسبب طريقة التركيب أو الضبط، لا "
          "بسبب الأجهزة، ولا نضمن تركيباً لم نقم به. أما المواقع التي لديها فريق فني "
          "كفؤ، فتواصلوا معنا &mdash; وسندرس كل حالة على حدة.")),
        (("Why are there no prices on the site?",
          "لماذا لا توجد أسعار على الموقع؟"),
         ("Because the same camera costs different amounts on different buildings. Cable "
          "runs, mounting, power, existing infrastructure and the number of devices all "
          "move the figure. A price quoted before the survey would be a guess, so we "
          "survey first and then quote once.",
          "لأن الكاميرا نفسها تكلّف مبالغ مختلفة في مبانٍ مختلفة. فمسارات الكابلات "
          "والتثبيت والتغذية الكهربائية والبنية القائمة وعدد الأجهزة كلها تغيّر الرقم. "
          "والسعر قبل المعاينة سيكون تخميناً، لذا نعاين أولاً ثم نقدّم عرضاً واحداً.")),
        (("Can you take over a system somebody else installed?",
          "هل يمكنكم تولّي نظام ركّبته جهة أخرى؟"),
         ("Often, yes. We survey what is there, tell you honestly what is worth keeping "
          "and what is past its life, and quote the gap. Taking over a sound installation "
          "is cheaper for you than replacing it, and we will say so when that is the case.",
          "غالباً نعم. نعاين الموجود، ونخبركم بصراحة بما يستحق الإبقاء عليه وما انتهى "
          "عمره الافتراضي، ونقدّم عرضاً للفارق. فتولّي تركيب سليم أقل كلفة عليكم من "
          "استبداله، وسنقول ذلك عندما يكون هو الحال.")),
        (("How quickly can a system be installed?",
          "كم يستغرق تركيب النظام؟"),
         ("It depends on size and on how much cabling a finished building needs. A small "
          "office is usually days; a compound or a tower is weeks and is programmed around "
          "your operations. The survey gives you a schedule, not just a price.",
          "يعتمد على الحجم وعلى حجم التمديدات التي يحتاجها مبنى مشطّب. فالمكتب الصغير "
          "يستغرق أياماً عادةً، والمجمّع أو البرج أسابيع تُجدوَل حول سير عملكم. وتمنحكم "
          "المعاينة جدولاً زمنياً لا سعراً فقط.")),
        (("Do you maintain the system after installation?",
          "هل تقومون بصيانة النظام بعد التركيب؟"),
         ("Yes, and we would rather you took the contract. Detectors drift, lenses "
          "attract dust, batteries expire and disks fill. Scheduled visits catch those "
          "before the night they matter.",
          "نعم، ونفضّل أن تأخذوا عقد الصيانة. فالكواشف تنحرف، والعدسات تتّسخ، والبطاريات "
          "تنتهي، والأقراص تمتلئ. والزيارات المجدولة تكتشف ذلك قبل الليلة التي يهمّ فيها.")),
    ],
}

SUPPORT = {
    "title": ("Installation, Maintenance &amp; Support | AZSCO Security Systems",
              "التركيب والصيانة والدعم | أنظمة أزسكو الأمنية"),
    "desc": ("Installation, commissioning, maintenance contracts, warranty and 24/7 "
             "monitoring for security systems across Kuwait, delivered by AZSCO's own "
             "technicians.",
             "التركيب والتشغيل وعقود الصيانة والضمان والمراقبة على مدار الساعة للأنظمة "
             "الأمنية في جميع أنحاء الكويت، ينفّذها فنّيو أزسكو."),
    "h1": ("INSTALLATION &amp; SUPPORT", "التركيب والدعم"),
    "sub": ("Our own technicians install it, and the same company keeps it running.",
            "فنّيونا هم مَن يُركّبه، والشركة نفسها هي مَن يُبقيه يعمل."),
    "lead_eyebrow": ("What comes with the equipment", "ما يأتي مع المعدات"),
    "lead_head": ("The parts of the job that are not the box",
                  "أجزاء العمل التي ليست الصندوق"),
    "blocks": [
        ("pin", ("Site survey", "معاينة الموقع"),
         ("Free, and before any price. We walk the building, identify entry points and "
          "blind spots, check what power and cabling already exist, and agree the device "
          "schedule with you.",
          "مجانية، وقبل أي سعر. نتفقّد المبنى، ونحدّد نقاط الدخول والمناطق العمياء، "
          "ونفحص ما هو متوفر من تغذية وتمديدات، ونتفق معكم على جدول الأجهزة.")),
        ("cog", ("Installation &amp; commissioning", "التركيب والتشغيل"),
         ("Cabling, mounting, configuration and testing by AZSCO technicians &mdash; not "
          "subcontracted. Handover includes as-built drawings and training for your staff.",
          "التمديد والتثبيت والضبط والاختبار على يد فنّيي أزسكو &mdash; دون مقاولين من "
          "الباطن. ويشمل التسليم مخططات التنفيذ الفعلي وتدريباً لموظفيكم.")),
        ("calendar", ("Maintenance contracts", "عقود الصيانة"),
         ("Scheduled preventive visits &mdash; lenses cleaned, detectors tested, batteries "
          "and disks replaced before they fail &mdash; plus a call-out commitment for faults "
          "between visits.",
          "زيارات وقائية مجدولة &mdash; تنظيف العدسات واختبار الكواشف واستبدال البطاريات "
          "والأقراص قبل تعطّلها &mdash; مع التزام بالاستجابة للأعطال بين الزيارات.")),
        ("headset", ("24/7 monitoring", "مراقبة على مدار الساعة"),
         ("Optional connection to our Central Operations Room, which is staffed at every "
          "hour and can dispatch an AZSCO patrol to a confirmed alarm.",
          "ربط اختياري بغرفة العمليات المركزية لدينا، المأهولة في كل ساعة، والقادرة على "
          "إرسال دورية أزسكو عند تأكّد الإنذار.")),
        ("award", ("Warranty", "الضمان"),
         ("Manufacturer warranty on the equipment, and our own warranty on the "
          "installation work. Faults inside the period are corrected at no charge.",
          "ضمان المُصنّع على المعدات، وضماننا على أعمال التركيب. وتُصحَّح الأعطال داخل "
          "فترة الضمان دون رسوم.")),
        ("users", ("Training", "التدريب"),
         ("Your staff are shown how to use what was installed &mdash; arming, reviewing "
          "footage, adding and removing a cardholder &mdash; because a system nobody can "
          "operate is not installed, it is just present.",
          "يُدرَّب موظفوكم على استخدام ما تم تركيبه &mdash; التفعيل ومراجعة التسجيلات "
          "وإضافة حامل بطاقة أو إزالته &mdash; فالنظام الذي لا يعرف أحد تشغيله ليس "
          "مُركّباً، بل موجوداً فقط.")),
    ],
}

QUOTE = {
    "title": ("Request a Quote | AZSCO Security Systems",
              "اطلب عرض سعر | أنظمة أزسكو الأمنية"),
    "desc": ("Send AZSCO your list of security equipment and site details for a quotation "
             "covering supply, installation and maintenance in Kuwait.",
             "أرسل إلى أزسكو قائمة المعدات الأمنية وتفاصيل الموقع للحصول على عرض سعر يشمل "
             "التوريد والتركيب والصيانة في الكويت."),
    "h1": ("REQUEST A QUOTE", "اطلب عرض سعر"),
    "sub": ("Your selected equipment, plus a few details about the site.",
            "المعدات التي اخترتها، مع بعض التفاصيل عن الموقع."),
    "how": [
        (("1. You send the list", "1. ترسل القائمة"),
         ("Whatever you have added here, plus what the site is and roughly how big.",
          "ما أضفته هنا، مع بيان طبيعة الموقع وحجمه تقريباً.")),
        (("2. We survey, free", "2. نعاين مجاناً"),
         ("An engineer visits, checks the building and confirms what it actually needs.",
          "يزور مهندس الموقع ويتفقّد المبنى ويؤكّد ما يحتاجه فعلاً.")),
        (("3. One written quote", "3. عرض خطي واحد"),
         ("Equipment, installation and maintenance in a single priced document.",
          "المعدات والتركيب والصيانة في وثيقة مسعّرة واحدة.")),
    ],
    "form_head": ("Site &amp; contact details", "بيانات الموقع والتواصل"),
    "form_note": ("We reply within one working day. For anything urgent, call &mdash; the "
                  "number answers around the clock.",
                  "نردّ خلال يوم عمل واحد. ولأي أمر عاجل، اتصل &mdash; فالرقم يُجيب على "
                  "مدار الساعة."),
}

CONTACT = {
    "title": ("Contact AZSCO &mdash; Security Systems in Kuwait | AZSCO",
              "اتصل بأزسكو &mdash; أنظمة أمنية في الكويت | أزسكو"),
    "desc": ("Contact AZSCO Security in Kuwait. Floor 27B, Kuwait Building Tower, Fahad Al "
             "Salem St., Qibla. Tel (+965) 1808606. Free site survey for security systems.",
             "تواصل مع أزسكو للأمن في الكويت. الدور 27B، برج مبنى الكويت، شارع فهد السالم، "
             "القبلة. هاتف (+965) 1808606. معاينة مجانية لأنظمة الأمن."),
    "h1": ("CONTACT US", "اتصل بنا"),
    "sub": ("Talk to the team about a site, a system or a fault.",
            "تحدّث مع الفريق بشأن موقع أو نظام أو عطل."),
    "office": ("Office", "المكتب"),
    "hours_h": ("Office hours", "ساعات العمل"),
    "phone_h": ("Telephone", "الهاتف"),
    "email_h": ("Email", "البريد الإلكتروني"),
    "emerg": ("Emergency and monitoring: 24 hours, every day.",
              "الطوارئ والمراقبة: 24 ساعة، كل يوم."),
}

PRIVACY = {
    "title": ("Privacy Policy | AZSCO Security Systems", "سياسة الخصوصية | أنظمة أزسكو الأمنية"),
    "desc": ("How AZSCO Security handles the information you send through this website, "
             "including quote requests and the assistant.",
             "كيف تتعامل أزسكو للأمن مع المعلومات التي ترسلها عبر هذا الموقع، بما في ذلك "
             "طلبات عروض الأسعار والمساعد."),
    "h1": ("PRIVACY POLICY", "سياسة الخصوصية"),
    "sub": ("What this site collects, and what it does not.",
            "ما يجمعه هذا الموقع، وما لا يجمعه."),
    "sections": [
        (("What we collect", "ما الذي نجمعه"),
         ("Only what you type into a form and send: your name, company, email address, "
          "telephone number, the details you give about your site, and any products you "
          "added to a quote. Nothing is collected from you simply for reading a page.",
          "فقط ما تكتبه في النموذج وترسله: اسمك وشركتك وبريدك الإلكتروني ورقم هاتفك "
          "وتفاصيل موقعك والمنتجات التي أضفتها إلى طلب العرض. ولا يُجمع منك شيء لمجرد "
          "تصفّح صفحة.")),
        (("Your quote list stays in your browser", "قائمة طلبك تبقى في متصفحك"),
         ("Products you add to a quote are stored on your own device, in your browser, so "
          "the list survives moving between pages. It is not sent anywhere until you "
          "submit the form, and clearing the list removes it.",
          "تُحفظ المنتجات التي تضيفها إلى طلب العرض على جهازك، داخل متصفحك، لتبقى القائمة "
          "عند الانتقال بين الصفحات. ولا تُرسَل إلى أي جهة حتى ترسل النموذج، ومسح القائمة "
          "يزيلها.")),
        (("Why we use it", "لماذا نستخدمها"),
         ("To answer your enquiry, arrange a survey and prepare a quotation. We do not "
          "sell your information, and we do not send marketing you did not ask for.",
          "للردّ على استفسارك وترتيب معاينة وإعداد عرض السعر. ولا نبيع معلوماتك، ولا نرسل "
          "مواد تسويقية لم تطلبها.")),
        (("The assistant", "المساعد"),
         ("Messages you type into the on-page assistant are sent to our server, which "
          "passes them to a language-model provider to produce an answer. Do not put "
          "confidential site details or personal data into it &mdash; use the form or the "
          "telephone for those.",
          "تُرسَل الرسائل التي تكتبها في المساعد إلى خادمنا، الذي يمرّرها إلى مزوّد نموذج "
          "لغوي لتوليد الإجابة. لا تُدخل فيه تفاصيل حسّاسة عن الموقع أو بيانات شخصية "
          "&mdash; استخدم النموذج أو الهاتف لذلك.")),
        (("Cookies and analytics", "ملفات تعريف الارتباط والتحليلات"),
         ("This site sets no advertising or tracking cookies. If website analytics are "
          "enabled, they are of a kind that records no personal data and sets no cookie.",
          "لا يضع هذا الموقع ملفات تعريف ارتباط إعلانية أو تتبّعية. وإذا فُعّلت تحليلات "
          "الموقع، فهي من نوع لا يسجّل بيانات شخصية ولا يضع ملفات تعريف ارتباط.")),
        (("Keeping and deleting it", "الاحتفاظ والحذف"),
         ("Enquiries are kept only as long as needed to deal with them and to meet our "
          "record-keeping obligations. To ask what we hold about you, or to have it "
          "deleted, email us and we will action it.",
          "يُحتفظ بالاستفسارات للمدة اللازمة لمعالجتها والوفاء بالتزامات حفظ السجلات "
          "لدينا. وللاستفسار عمّا نحتفظ به عنك أو طلب حذفه، راسلنا وسننفّذ ذلك.")),
        (("Changes", "التعديلات"),
         ("If this policy changes, the revised version appears on this page.",
          "إذا تغيّرت هذه السياسة، تظهر النسخة المعدّلة على هذه الصفحة.")),
    ],
    "contact_line": ("Questions about this policy:", "أسئلة حول هذه السياسة:"),
}

NOTFOUND = {
    "title": ("Page Not Found | AZSCO Security Systems", "الصفحة غير موجودة | أنظمة أزسكو الأمنية"),
    "desc": ("That page does not exist. Browse the security systems catalogue or contact "
             "AZSCO in Kuwait.",
             "هذه الصفحة غير موجودة. تصفّح كتالوج الأنظمة الأمنية أو تواصل مع أزسكو في الكويت."),
    "h1": ("404", "404"),
    "head": ("We could not find that page", "تعذّر العثور على تلك الصفحة"),
    "text": ("The address may be out of date, or mistyped. The catalogue and the main "
             "pages are below.",
             "قد يكون العنوان قديماً أو مكتوباً بشكل خاطئ. الكتالوج والصفحات الرئيسية أدناه."),
}

CATALOGUE = {
    "title": ("Security Systems Catalogue &mdash; Cameras, Alarms, Access Control | AZSCO",
              "كتالوج الأنظمة الأمنية &mdash; كاميرات وإنذار وتحكم بالدخول | أزسكو"),
    "desc": ("Browse AZSCO's security systems catalogue: surveillance cameras and "
             "recorders, intrusion and fire detection, access control, two-way radio and "
             "network hardware. Supplied and installed in Kuwait.",
             "تصفّح كتالوج الأنظمة الأمنية من أزسكو: كاميرات المراقبة وأجهزة التسجيل، "
             "وكشف التسلل والحريق، والتحكم بالدخول، وأجهزة الاتصال والشبكات. توريد وتركيب "
             "في الكويت."),
    "h1": ("PRODUCT CATALOGUE", "كتالوج المنتجات"),
    "sub": ("Everything we supply, install and maintain &mdash; filter by category or brand line.",
            "كل ما نورّده ونركّبه ونصونه &mdash; صفِّ حسب الفئة أو العلامة التجارية."),
}

BRANDS_PAGE = {
    "title": ("Brands We Supply &mdash; Security Systems in Kuwait | AZSCO",
              "العلامات التي نورّدها &mdash; أنظمة أمنية في الكويت | أزسكو"),
    "desc": ("The eight manufacturer lines behind AZSCO's security systems catalogue: "
             "Ajax, Hikvision, Avigilon, Pelco, Rasilient, Motorola, Inrico and Teltonika.",
             "ثماني علامات مصنّعة خلف كتالوج الأنظمة الأمنية من أزسكو: أجاكس، هيكفيجن، "
             "أفيجيلون، بيلكو، راسيليينت، موتورولا، إنريكو، تيلتونيكا."),
    "h1": ("BRANDS WE SUPPLY", "العلامات التي نورّدها"),
    "sub": ("Eight manufacturer lines, specified per site rather than pushed as a default.",
            "ثماني علامات مصنّعة، تُحدَّد حسب الموقع لا تُفرض كخيار افتراضي."),
    "lead_head": ("Why the brand is the last decision, not the first",
                  "لماذا تكون العلامة آخر قرار لا أوله"),
    "lead": ("A brand is a means, not a specification. What a site needs &mdash; the coverage, "
             "the retention, the number of doors, whether there is a fixed line &mdash; is "
             "settled at the survey. Which of these lines delivers it best is settled "
             "afterwards, and we will tell you plainly when a cheaper line does the job.",
             "العلامة وسيلة لا مواصفة. فما يحتاجه الموقع &mdash; التغطية ومدة الاحتفاظ "
             "وعدد الأبواب ووجود خط ثابت من عدمه &mdash; يُحسم عند المعاينة. أما أي من هذه "
             "العلامات يحقّقه على نحو أفضل فيُحسم بعد ذلك، وسنقول لك بوضوح متى كانت علامة "
             "أقل كلفة كافية للمهمة."),
}

# Quote form labels. Errors are marked by weight, an inset rule and a warning
# glyph rather than colour -- the palette has no red to spend.
FORM = {
    "name":     ("Your name", "الاسم"),
    "company":  ("Company", "الشركة"),
    "email":    ("Email", "البريد الإلكتروني"),
    "phone":    ("Telephone", "الهاتف"),
    "interest": ("Mainly interested in", "الاهتمام الأساسي"),
    "choose":   ("Choose a category", "اختر فئة"),
    "mixed":    ("A complete system", "نظام متكامل"),
    "site":     ("About the site", "عن الموقع"),
    "site_ph":  ("What kind of building, roughly how big, and what you need to protect.",
                 "نوع المبنى، وحجمه تقريباً، وما الذي تريد حمايته."),
    "send_quote": ("Send quote request", "إرسال طلب العرض"),
    "sending":  ("Sending&hellip;", "جارٍ الإرسال&hellip;"),
    "sent":     ("Thank you — your request has been sent. We will reply within one working day.",
                 "شكراً لك — تم إرسال طلبك. وسنردّ خلال يوم عمل واحد."),
    "failed":   ("Sorry, your request could not be sent just now. Please call (+965) 1808606 "
                 "or email sales@azsco.com and we will pick it up straight away.",
                 "عذراً، تعذّر إرسال طلبك الآن. يُرجى الاتصال على (+965) 1808606 أو مراسلتنا "
                 "على sales@azsco.com وسنتابع طلبك فوراً."),
    "err_req":  ("This field is required", "هذا الحقل مطلوب"),
    "err_mail": ("Enter a valid email address", "أدخل بريداً إلكترونياً صحيحاً"),
}


# ============================================================ templates
FONTS_EN = ('<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700'
            '&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">')
FONTS_AR = ('<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700'
            '&family=Tajawal:wght@400;500;700&display=swap" rel="stylesheet">')

def ltr(text):
    """Keep phone numbers and emails readable inside right-to-left text."""
    return f'<span dir="ltr">{text}</span>'

def head(lang, fname, title, desc):
    a = asset(lang, "")
    return f'''<!DOCTYPE html>
<html {lang_attrs(lang)}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0d0d0d">
{search_console_tag()}
<link rel="canonical" href="{canonical(lang, fname)}">
<link rel="alternate" hreflang="en" href="{canonical("en", fname)}">
<link rel="alternate" hreflang="ar" href="{canonical("ar", fname)}">
<link rel="alternate" hreflang="x-default" href="{canonical("en", fname)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{t(SITE_NAME, lang)}">
<meta property="og:locale" content="{"ar_KW" if lang == "ar" else "en_US"}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical(lang, fname)}">
<meta property="og:image" content="{SITE_URL}/assets/img/og-share.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="AZSCO Security — professional security services for Kuwait">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE_URL}/assets/img/og-share.jpg">
<link rel="icon" type="image/png" sizes="32x32" href="{a}assets/img/favicon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="{a}assets/img/favicon-192.png">
<link rel="apple-touch-icon" href="{a}assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{FONTS_AR if lang == "ar" else FONTS_EN}
<link rel="stylesheet" href="{a}assets/css/style.css">
</head>
<body>
<a class="skip-link" href="#main">{t(UI["skip"], lang)}</a>
'''

def desktop_nav(lang):
    out = ['<ul class="nav">']
    for label, href, subs in NAV:
        if subs:
            out.append(f'<li><a href="{link(lang, href)}">{t(label, lang)} {I["caret"]}</a><ul class="subnav">')
            for s_label, s_href in subs:
                out.append(f'<li><a href="{link(lang, s_href)}">{t(s_label, lang)}</a></li>')
            out.append('</ul></li>')
        else:
            out.append(f'<li><a href="{link(lang, href)}">{t(label, lang)}</a></li>')
    out.append('</ul>')
    return "\n        ".join(out)

def mobile_nav(lang):
    out = ['<ul class="m-nav">']
    for n, (label, href, subs) in enumerate(NAV):
        if subs:
            out.append('<li class="m-group">')
            out.append(f'<button class="m-toggle" type="button" aria-expanded="false" '
                       f'aria-controls="m-sub-{n}">{t(label, lang)}{I["caret"]}</button>')
            out.append(f'<ul class="m-sub" id="m-sub-{n}">')
            for s_label, s_href in subs:
                out.append(f'<li><a href="{link(lang, s_href)}">{t(s_label, lang)}</a></li>')
            out.append('</ul></li>')
        else:
            out.append(f'<li><a href="{link(lang, href)}">{t(label, lang)}</a></li>')
    out.append('</ul>')
    return "\n      ".join(out)

def lang_link(lang, fname, cls="lang-switch"):
    other = "ar" if lang == "en" else "en"
    return (f'<a class="{cls}" href="{other_lang_url(lang, fname)}" lang="{other}" '
            f'dir="{"rtl" if other == "ar" else "ltr"}" '
            f'hreflang="{other}" aria-label="{t(UI["LANG_SWITCH_LABEL"], lang) if "LANG_SWITCH_LABEL" in UI else t(LANG_SWITCH_LABEL, lang)}">'
            f'{I["globe"]}<span class="lang-full">{t(LANG_SWITCH, lang)}</span>'
            f'<span class="lang-short">{t(LANG_SWITCH_SHORT, lang)}</span></a>')

def header(lang, fname):
    a = asset(lang, "")
    return f'''
<div class="topbar">
  <div class="wrap">
    <ul class="topbar-list">
      <li class="hide-sm">{I["pin"]}<a href="{MAPS_URL}" target="_blank" rel="noopener noreferrer" aria-label="{t(UI["map_label"], lang)}">{t(ADDRESS_1L, lang)}</a></li>
      <li>{I["phone"]}<a href="tel:{PHONE_HREF}" dir="ltr">{PHONE}</a></li>
      <li class="hide-md">{I["mail"]}<a href="mailto:{EMAIL}" dir="ltr">{EMAIL}</a></li>
      <li class="hide-md">{I["clock"]}<span>{t(RESPONSE_24, lang)}</span></li>
    </ul>
    <div class="topbar-end">
      <div class="topbar-social" aria-label="{t(UI["social"], lang)}">
        <a href="{FACEBOOK_URL}" target="_blank" rel="noopener noreferrer" aria-label="AZSCO on Facebook">{I["facebook"]}</a>
        <a href="{X_URL}" target="_blank" rel="noopener noreferrer" aria-label="AZSCO on X">{I["x"]}</a>
        <a href="{INSTAGRAM_URL}" target="_blank" rel="noopener noreferrer" aria-label="AZSCO on Instagram">{I["instagram"]}</a>
      </div>
    </div>
  </div>
</div>

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{link(lang, "index.html")}" aria-label="{t(UI["home_label"], lang)}">
      <img class="brand-logo" src="{a}assets/img/AZSCO_Logo.png" alt="{t(SITE_NAME, lang)}" width="347" height="160">
    </a>

    <nav aria-label="{t(UI["main_nav"], lang)}">
        {desktop_nav(lang)}
    </nav>

    <div class="header-cta">
      {lang_link(lang, fname, "lang-switch lang-switch--head")}
      <button class="burger" type="button" aria-label="{t(UI["menu_open"], lang)}" aria-expanded="false" aria-controls="mobile-nav"><span></span></button>
    </div>
  </div>
</header>

<div class="backdrop"></div>
<nav class="mobile-nav" id="mobile-nav" aria-label="{t(UI["mob_nav"], lang)}">
  <div class="mobile-nav-head">
    <img class="brand-logo" src="{a}assets/img/AZSCO_Logo.png" alt="{t(SITE_NAME, lang)}" width="347" height="160">
    <button class="close" type="button" aria-label="{t(UI["menu_close"], lang)}">{I["close"]}</button>
  </div>
      {mobile_nav(lang)}
  <div class="mobile-nav-foot">
    <a class="btn btn-primary" href="{link(lang, "contact.html")}">{t(UI["consult"], lang)}</a>
    <a class="m-contact" href="tel:{PHONE_HREF}">{I["phone"]}<span dir="ltr">{PHONE}</span></a>
    <a class="m-contact" href="mailto:{EMAIL}">{I["mail"]}<span dir="ltr">{EMAIL}</span></a>
  </div>
</nav>
'''

def chat_widget(lang):
    C = CHAT
    chips = "\n      ".join(
        f'<button type="button">{t(sug, lang)}</button>' for sug in C["suggest"])
    return f'''
<div data-azsco-chat data-endpoint="{CHAT_ENDPOINT}" data-lang="{lang}"
     data-greeting="{t(C["greeting"], lang)}"
     data-error="{t(C["error"], lang)}"
     data-offline="{t(C["offline"], lang)}"
     data-label-expand="{t(C["expand"], lang)}"
     data-label-collapse="{t(C["collapse"], lang)}">
  <button class="chat-launcher" type="button" aria-expanded="false" aria-controls="azsco-chat-panel" aria-label="{t(C["open"], lang)}">
    {I["chat"]}<span class="chat-launcher-text">{t(C["launcher"], lang)}</span>
  </button>

  <div class="chat-panel" id="azsco-chat-panel" role="dialog" aria-label="{t(C["title"], lang)}" hidden>
    <div class="chat-head">
      <span class="avatar">{I["chat"]}</span>
      <span>
        <b>{t(C["title"], lang)}</b>
        <small>{t(C["sub"], lang)}</small>
      </span>
      <span class="spacer"></span>
      <button class="chat-btn" type="button" data-chat-expand aria-pressed="false" aria-label="{t(C["expand"], lang)}">{I["expand"]}</button>
      <button class="chat-btn" type="button" data-chat-close aria-label="{t(C["close"], lang)}">{I["close"]}</button>
    </div>

    <div class="chat-log" role="log" aria-live="polite" aria-atomic="false"></div>

    <div class="chat-suggest">
      {chips}
    </div>

    <form class="chat-form">
      <label class="visually-hidden" for="azsco-chat-input">{t(C["placeholder"], lang)}</label>
      <textarea id="azsco-chat-input" rows="1" placeholder="{t(C["placeholder"], lang)}" maxlength="1000"></textarea>
      <button class="chat-send" type="submit" aria-label="{t(C["send"], lang)}">{I["send"]}</button>
    </form>
    <p class="chat-foot">{t(C["foot"], lang)}</p>
  </div>
</div>
'''

def footer(lang):
    a = asset(lang, "")
    links = "\n          ".join(
        f'<li><a href="{link(lang, href)}">{t(label, lang)}</a></li>' for label, href in FOOTER["links"])
    svc = "\n          ".join(
        f'<li><a href="{link(lang, "services.html#" + s["anchor"])}">{t(s["name"], lang)}</a></li>' for s in SERVICES)
    return f'''
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="brand" href="{link(lang, "index.html")}" aria-label="{t(UI["home_label"], lang)}">
          <img class="brand-logo" src="{a}assets/img/AZSCO_Logo_white.png" alt="{t(SITE_NAME, lang)}" width="347" height="160">
        </a>
        <p>{t(FOOTER["blurb"], lang)}</p>
        <div class="footer-social">
          <a href="{FACEBOOK_URL}" target="_blank" rel="noopener noreferrer" aria-label="AZSCO on Facebook">{I["facebook"]}</a>
          <a href="{X_URL}" target="_blank" rel="noopener noreferrer" aria-label="AZSCO on X">{I["x"]}</a>
          <a href="{INSTAGRAM_URL}" target="_blank" rel="noopener noreferrer" aria-label="AZSCO on Instagram">{I["instagram"]}</a>
        </div>
      </div>

      <div>
        <h4>{t(FOOTER["company"], lang)}</h4>
        <ul class="footer-links">
          {links}
        </ul>
      </div>

      <div>
        <h4>{t(FOOTER["services"], lang)}</h4>
        <ul class="footer-links">
          {svc}
        </ul>
      </div>

      <div>
        <h4>{t(FOOTER["touch"], lang)}</h4>
        <ul class="footer-contact">
          <li>{I["pin"]}<span>{t(ADDRESS_BR, lang)}</span></li>
          <li>{I["phone"]}<a href="tel:{PHONE_HREF}" dir="ltr">{PHONE}</a></li>
          <li>{I["mail"]}<span><a href="mailto:{EMAIL}" dir="ltr">{EMAIL}</a><small>{t(FOOTER["email_general"], lang)}</small></span></li>
          <li>{I["mail"]}<span><a href="mailto:{EMAIL_SALES}" dir="ltr">{EMAIL_SALES}</a><small>{t(FOOTER["email_sales"], lang)}</small></span></li>
          <li>{I["clock"]}<span>{t(HOURS_FOOT, lang)}</span></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <p>&copy; <span data-year>2026</span> {t(COMPANY, lang)}. {t(FOOTER["rights"], lang)}</p>
      <ul>
        <li><a href="{link(lang, "privacy-policy.html")}">{t(FOOTER["privacy"], lang)}</a></li>
        <li><a href="{link(lang, "contact.html")}">{t(FOOTER["contact"], lang)}</a></li>
      </ul>
    </div>
  </div>
</footer>

<button class="to-top" type="button" aria-label="{t(UI["to_top"], lang)}">{I["up"]}</button>
<a class="whatsapp-fab" href="{WHATSAPP_URL}" target="_blank" rel="noopener noreferrer" aria-label="{t(UI["whatsapp"], lang)}">{I["whatsapp"]}</a>

<div class="mobile-bar">
  <a class="mobile-bar-call" href="tel:{PHONE_HREF}">{I["phone"]}<span>{t(UI["call_now"], lang)}</span></a>
  <a class="mobile-bar-quote" href="{link(lang, "contact.html")}">{I["mail"]}<span>{t(UI["get_quote"], lang)}</span></a>
</div>
{chat_widget(lang)}
<script src="{a}assets/js/main.js"></script>
<script src="{a}assets/js/chat.js" defer></script>
{analytics_tag()}
</body>
</html>
'''

def banner(lang, title, sub, crumb):
    return f'''
<section class="page-banner">
  <div class="wrap">
    <p class="eyebrow">{t(SITE_NAME, lang)}</p>
    <h1>{title}</h1>
    <p>{sub}</p>
    <ul class="crumbs">
      <li><a href="{link(lang, "index.html")}">{t(UI["home"], lang)}</a></li>
      <li aria-current="page">{crumb}</li>
    </ul>
  </div>
</section>
'''

def cta(lang, pair=None):
    title, text = pair or CTA_DEFAULT
    return f'''
<section class="cta">
  <div class="wrap">
    <div>
      <h2>{t(title, lang)}</h2>
      <p>{t(text, lang)}</p>
    </div>
    <div class="btn-row">
      <a class="btn btn-primary" href="{link(lang, "contact.html")}">{t(UI["consult"], lang)} {I["arrow"]}</a>
      <a class="btn btn-outline" href="tel:{PHONE_HREF}" dir="ltr">{PHONE}</a>
    </div>
  </div>
</section>
'''

def stats_block(lang):
    cells = []
    for i, (kind, label) in enumerate(STATS):
        if kind == "founded":
            num = f'<span data-count="{FOUNDED}" data-plain>0</span>'
        elif kind == "years":
            num = f'<span data-years-since="{FOUNDED}" data-count="{YEARS}">0</span>+'
        elif kind == "247":
            num = '<span data-count="24">0</span>/<span data-count="7">0</span>'
        else:
            num = f'<span data-count="{len(PARTNERS)}">0</span>'
        cells.append(f'      <div class="stat reveal" data-delay="{i*80}">'
                     f'<span class="num" dir="ltr">{num}</span>'
                     f'<span class="label">{t(label, lang)}</span></div>')
    return ('<section class="section section--tight stats">\n  <div class="wrap">\n'
            '    <div class="grid grid-4">\n' + "\n".join(cells) +
            '\n    </div>\n  </div>\n</section>')

PAGES = {}

def page(lang, fname, title, desc, body):
    PAGES[(lang, fname)] = (head(lang, fname, title, desc) + header(lang, fname)
                            + f'<main id="main">\n{body}\n</main>' + footer(lang))

# ============================================================ routes
# Rebuilt from the catalogue so a category or product cannot exist in the data
# and be missing from the navigation, the sitemap or the URL map. Category and
# product pages nest under /products/, which path_for() and out_file_for()
# already handle -- a slug containing "/" simply becomes a deeper directory.
ROUTES = {
    "index.html": "",
    "products.html": "products",
    "brands.html": "brands",
    "support.html": "support",
    "quote.html": "quote",
    "about.html": "about",
    "contact.html": "contact",
    "privacy-policy.html": "privacy-policy",
}
for _c in CATEGORIES:
    ROUTES["cat-" + _c["slug"]] = "products/" + _c["slug"]
for _p in PRODUCTS:
    ROUTES["prod-" + _p["slug"]] = "products/" + _p["cat"] + "/" + _p["slug"]

def cat_route(c):
    return "cat-" + c["slug"]

def prod_route(p):
    return "prod-" + p["slug"]

# ============================================================ shared blocks
def chip_list(lang, items):
    """A wrapping row of pill chips for a plain enumeration."""
    return "\n".join(
        f'      <span class="chip reveal" data-delay="{min(i*30, 300)}">{t(item, lang)}</span>'
        for i, item in enumerate(items))

def tiles(lang, items, cols=3):
    return "\n".join(
        f'      <div class="tile reveal" data-delay="{(i%cols)*80}"><span class="ico">'
        f'{I[icon]}</span><div><h4>{t(title, lang)}</h4>'
        f'<p>{t(text, lang).replace("{YEARS}", str(YEARS))}</p></div></div>'
        for i, (icon, title, text) in enumerate(items))

def trail(lang, *crumbs):
    """Breadcrumbs. Every item but the last is (label, route); the last is a
    bare label for the current page."""
    out = [f'<li><a href="{link(lang, "index.html")}">{t(UI["home"], lang)}</a></li>']
    for c in crumbs[:-1]:
        out.append(f'<li><a href="{link(lang, c[1])}">{c[0]}</a></li>')
    out.append(f'<li aria-current="page">{crumbs[-1]}</li>')
    return "\n      ".join(out)

def banner(lang, title, sub, crumbs, lead=None):
    """Page banner. Narrower and quieter than the services site's, because on
    a catalogue the products are the page and the banner is just a label."""
    extra = f'\n    <p class="banner-lead">{lead}</p>' if lead else ""
    return f'''
<section class="page-banner">
  <div class="wrap">
    <ul class="crumbs">
      {trail(lang, *crumbs)}
    </ul>
    <h1>{title}</h1>
    <p>{sub}</p>{extra}
  </div>
</section>
'''

def cta(lang, pair=None):
    """Closing band. Points at the quote page rather than a consultation, since
    a quote is the action this site is asking for."""
    title, text = pair or CTA_DEFAULT
    return f'''
<section class="cta">
  <div class="wrap">
    <div>
      <h2>{t(title, lang)}</h2>
      <p>{t(text, lang)}</p>
    </div>
    <div class="btn-row">
      <a class="btn btn-primary" href="{link(lang, "quote.html")}">{t(UI["quote_req"], lang)} {I["arrow"]}</a>
      <a class="btn btn-outline" href="tel:{PHONE_HREF}" dir="ltr">{PHONE}</a>
    </div>
  </div>
</section>
'''

def stats_block(lang):
    cells = []
    for i, (kind, label) in enumerate(STATS):
        if kind == "founded":
            num = f'<span data-count="{FOUNDED}" data-plain>0</span>'
        elif kind == "years":
            num = f'<span data-years-since="{FOUNDED}" data-count="{YEARS}">0</span>+'
        elif kind == "247":
            num = '<span data-count="24">0</span>/<span data-count="7">0</span>'
        else:
            num = f'<span data-count="{len(BRANDS)}">0</span>'
        cells.append(f'      <div class="stat reveal" data-delay="{i*80}">'
                     f'<span class="num" dir="ltr">{num}</span>'
                     f'<span class="label">{t(label, lang)}</span></div>')
    return ('<section class="section section--tight stats">\n  <div class="wrap">\n'
            '    <div class="grid grid-4">\n' + "\n".join(cells) +
            '\n    </div>\n  </div>\n</section>')

def add_button(lang, p, cls="btn btn-primary btn-sm"):
    """The quote-basket trigger. Everything the basket needs to redisplay the
    line later travels on the button as data-, so assets/js/main.js needs no
    copy of the catalogue and no second source of truth for a product name."""
    cat = CAT_BY_SLUG[p["cat"]]
    return (f'<button type="button" class="{cls} js-add" '
            f'data-sku="{p["slug"]}" data-name="{t(p["name"], lang)}" '
            f'data-kind="{t(p["kind"], lang)}" data-cat="{t(cat["name"], lang)}" '
            f'data-added="{t(UI["added"], lang)}">'
            f'{I["plus"]}<span class="js-add-label">{t(UI["add_quote"], lang)}</span></button>')

def product_card(lang, p, n=0):
    """Catalogue card. Carries its category and brand lines as data- so the
    catalogue page can filter in the browser without a second data source."""
    cat = CAT_BY_SLUG[p["cat"]]
    brands = " ".join(b[0].lower() for b in brands_for(p["cat"]))
    specs = "".join(
        f'<li><span>{t(lab, lang)}</span><b dir="ltr">{t(val, lang)}</b></li>'
        for lab, val in p["specs"][:3])
    return f'''      <article class="p-card reveal" data-delay="{(n%3)*70}" data-cat="{p["cat"]}" data-brands="{brands}">
        <a class="p-card-media" href="{link(lang, prod_route(p))}" tabindex="-1" aria-hidden="true">
          <span class="ico">{I[p["icon"]]}</span>
        </a>
        <div class="p-card-body">
          <p class="p-kind">{t(cat["name"], lang)} &middot; {t(p["kind"], lang)}</p>
          <h3><a href="{link(lang, prod_route(p))}">{t(p["name"], lang)}</a></h3>
          <ul class="p-spec-mini">{specs}</ul>
        </div>
        <div class="p-card-foot">
          {add_button(lang, p)}
          <a class="more" href="{link(lang, prod_route(p))}">{t(UI["view_product"], lang)} {I["arrow"]}</a>
        </div>
      </article>'''

def category_card(lang, c, n=0):
    count = len(products_in(c["slug"]))
    return f'''      <a class="cat-card reveal" data-delay="{n*80}" href="{link(lang, cat_route(c))}">
        <span class="ico">{I[c["icon"]]}</span>
        <h3>{t(c["name"], lang)}</h3>
        <p>{t(c["tag"], lang)}</p>
        <span class="cat-count"><b>{count}</b> {t(UI["products"], lang)} {I["arrow"]}</span>
      </a>'''

def spec_table(lang, p):
    rows = "\n".join(
        f'        <tr><th scope="row">{t(lab, lang)}</th><td dir="ltr">{t(val, lang)}</td></tr>'
        for lab, val in p["specs"])
    return f'''<table class="spec-table">
      <caption>{t(UI["full_specs"], lang)} &mdash; {t(p["name"], lang)}</caption>
      <tbody>
{rows}
      </tbody>
    </table>'''

def section_head(lang, eyebrow, head, lead=None, center=True):
    cls = "sec-head" + (" sec-head--center" if center else "")
    lead_html = f'\n    <p>{t(lead, lang)}</p>' if lead else ""
    return (f'  <div class="{cls} reveal">\n    <p class="eyebrow">{t(eyebrow, lang)}</p>\n'
            f'    <h2>{t(head, lang)}</h2>{lead_html}\n  </div>')

# ============================================================ pages
def build_home(lang):
    H = HOME
    picks = "\n".join(
        f'''          <a class="pick" href="{link(lang, cat_route(c))}">
            <span class="ico">{I[c["icon"]]}</span>
            <span class="pick-text"><b>{t(c["name"], lang)}</b><small>{t(c["tag"], lang)}</small></span>
            {I["arrow"]}
          </a>''' for c in CATEGORIES)
    assur = "\n".join(f'        <li>{I["check"]}<span>{t(a, lang)}</span></li>' for a in H["assur"])
    cats = "\n".join(category_card(lang, c, n) for n, c in enumerate(CATEGORIES))
    feat = "\n".join(product_card(lang, p, n)
                     for n, p in enumerate(p for p in PRODUCTS if p["featured"]))
    steps = "\n".join(
        f'''      <li class="step reveal" data-delay="{n*80}">
        <span class="step-n" dir="ltr">{n+1:02d}</span>
        <div><h3>{t(title, lang)}</h3><p>{t(text, lang)}</p></div>
      </li>''' for n, (title, text) in enumerate(H["steps"]))
    brand_items = "\n".join(
        f'''      <a class="brand-chip reveal" data-delay="{min(n*50, 300)}" href="{link(lang, "brands.html")}">
        <b>{name}</b><small>{t(tagline, lang)}</small></a>'''
        for n, (name, tagline, _cats) in enumerate(BRANDS))

    body = f'''
<section class="hero hero--catalogue">
  <div class="wrap">
    <div class="hero-text">
      <p class="eyebrow">{I["shield"]}{t(H["eyebrow"], lang)}</p>
      <h1>{t(H["h1"], lang)}</h1>
      <p class="lead">{t(H["lead"], lang)}</p>
      <div class="btn-row">
        <a class="btn btn-primary" href="{link(lang, "products.html")}">{t(UI["browse"], lang)} {I["arrow"]}</a>
        <a class="btn btn-outline" href="{link(lang, "quote.html")}">{t(UI["quote_req"], lang)}</a>
      </div>
      <ul class="assur">
{assur}
      </ul>
    </div>

    <aside class="hero-pick reveal" aria-label="{t(H["pick_head"], lang)}">
      <div class="hero-pick-head">
        <h2>{t(H["pick_head"], lang)}</h2>
        <p>{t(H["pick_sub"], lang)}</p>
      </div>
      <div class="pick-list">
{picks}
      </div>
    </aside>
  </div>
</section>

<section class="section" id="categories">
  <div class="wrap">
{section_head(lang, H["cat_eyebrow"], H["cat_head"], H["cat_lead"])}
    <div class="grid grid-4 cat-grid">
{cats}
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
{section_head(lang, H["feat_eyebrow"], H["feat_head"], H["feat_lead"])}
    <div class="grid grid-3 p-grid">
{feat}
    </div>
    <p class="center-cta"><a class="btn btn-outline" href="{link(lang, "products.html")}">{t(UI["all_products"], lang)} {I["arrow"]}</a></p>
  </div>
</section>

<section class="section section--dark">
  <div class="wrap">
{section_head(lang, H["how_eyebrow"], H["how_head"], H["how_lead"])}
    <ol class="steps">
{steps}
    </ol>
  </div>
</section>

<section class="section">
  <div class="wrap">
{section_head(lang, H["brand_eyebrow"], H["brand_head"], H["brand_lead"])}
    <div class="brand-row">
{brand_items}
    </div>
  </div>
</section>

{stats_block(lang)}

<section class="section section--alt">
  <div class="wrap">
{section_head(lang, H["sector_eyebrow"], H["sector_head"], H["sector_lead"])}
    <div class="chips">
{chip_list(lang, SECTORS)}
    </div>
  </div>
</section>

{cta(lang)}
'''
    page(lang, "index.html", t(H["title"], lang), t(H["desc"], lang), body)


def build_catalogue(lang):
    C = CATALOGUE
    cat_filters = "\n".join(
        f'''        <label class="f-check"><input type="checkbox" name="cat" value="{c["slug"]}">
          <span>{t(c["name"], lang)}</span><b>{len(products_in(c["slug"]))}</b></label>'''
        for c in CATEGORIES)
    brand_filters = "\n".join(
        f'''        <label class="f-check"><input type="checkbox" name="brand" value="{name.lower()}">
          <span>{name}</span><b>{sum(1 for p in PRODUCTS if p["cat"] in cats)}</b></label>'''
        for name, _tag, cats in BRANDS)
    cards = "\n".join(product_card(lang, p, n) for n, p in enumerate(PRODUCTS))

    body = f'''
{banner(lang, t(C["h1"], lang), t(C["sub"], lang), [t(UI["all_products"], lang)])}

<section class="section catalogue">
  <div class="wrap catalogue-wrap">

    <form class="filters" id="filters" aria-label="{t(UI["filters"], lang)}">
      <div class="filters-head">
        <h2>{t(UI["filters"], lang)}</h2>
        <button type="button" class="link-btn js-clear">{t(UI["clear_all"], lang)}</button>
      </div>
      <fieldset>
        <legend>{t(UI["category"], lang)}</legend>
{cat_filters}
      </fieldset>
      <fieldset>
        <legend>{t(UI["brand_lines"], lang)}</legend>
{brand_filters}
      </fieldset>
      <p class="filters-note">{t(UI["quote_note"], lang)}</p>
    </form>

    <div class="catalogue-main">
      <p class="result-count" role="status">
        {t(UI["showing"], lang)} <b class="js-count" dir="ltr">{len(PRODUCTS)}</b>
        {t(UI["of"], lang)} <span dir="ltr">{len(PRODUCTS)}</span> {t(UI["products"], lang)}
      </p>
      <div class="grid grid-3 p-grid js-results">
{cards}
      </div>
      <div class="empty js-empty" hidden>
        <span class="ico">{I["grid"]}</span>
        <h3>{t(UI["no_match"], lang)}</h3>
        <p>{t(UI["no_match_cta"], lang)}</p>
        <div class="btn-row">
          <button type="button" class="btn btn-outline js-clear">{t(UI["clear_all"], lang)}</button>
          <a class="btn btn-primary" href="{link(lang, "contact.html")}">{t(UI["talk"], lang)}</a>
        </div>
      </div>
    </div>

  </div>
</section>

{cta(lang)}
'''
    page(lang, "products.html", t(C["title"], lang), t(C["desc"], lang), body)


def build_category(lang, c):
    items = products_in(c["slug"])
    cards = "\n".join(product_card(lang, p, n) for n, p in enumerate(items))
    apps = "\n".join(f'        <li>{I["check"]}<span>{t(a, lang)}</span></li>' for a in c["apps"])
    lines = "\n".join(
        f'<li><b>{name}</b> &mdash; {t(tag, lang)}</li>' for name, tag, _c in brands_for(c["slug"]))
    others = "\n".join(category_card(lang, o, n)
                       for n, o in enumerate(x for x in CATEGORIES if x["slug"] != c["slug"]))
    title = (f'{t(c["name"], lang)} &mdash; ' +
             ("Security Systems in Kuwait | AZSCO" if lang == "en" else "أنظمة أمنية في الكويت | أزسكو"))

    body = f'''
{banner(lang, t(c["name"], lang), t(c["tag"], lang),
        [(t(UI["all_products"], lang), "products.html"), t(c["name"], lang)])}

<section class="section">
  <div class="wrap cat-intro">
    <div class="cat-intro-text reveal">
      <p class="eyebrow">{t(UI["category"], lang)}</p>
      <h2>{t(c["name"], lang)}</h2>
      <p>{t(c["lead"], lang)}</p>
      <ul class="check-list">
{apps}
      </ul>
    </div>
    <aside class="cat-intro-side reveal">
      <h3>{t(UI["supplied_by"], lang)}</h3>
      <ul class="line-list">
        {lines}
      </ul>
      <a class="btn btn-outline btn-sm" href="{link(lang, "brands.html")}">{t(UI["all_brands"], lang)} {I["arrow"]}</a>
    </aside>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="sec-head sec-head--center reveal">
      <p class="eyebrow">{t(UI["category"], lang)}</p>
      <h2>{len(items)} {t(UI["products"], lang)} {t(UI["in_category"], lang)}</h2>
    </div>
    <div class="grid grid-3 p-grid">
{cards}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head sec-head--center reveal">
      <h2>{t(UI["explore_cat"], lang)}</h2>
    </div>
    <div class="grid grid-3 cat-grid">
{others}
    </div>
  </div>
</section>

{cta(lang)}
'''
    page(lang, cat_route(c), title, t(c["lead"], lang)[:300], body)


def build_product(lang, p):
    c = CAT_BY_SLUG[p["cat"]]
    highs = "\n".join(f'        <li>{I["check"]}<span>{t(h, lang)}</span></li>' for h in p["highlights"])
    key = "\n".join(
        f'          <li><span>{t(lab, lang)}</span><b dir="ltr">{t(val, lang)}</b></li>'
        for lab, val in p["specs"][:4])
    apps = "\n".join(f'        <li>{I["check"]}<span>{t(a, lang)}</span></li>' for a in c["apps"])
    lines = ", ".join(b[0] for b in brands_for(p["cat"]))
    related = [x for x in products_in(p["cat"]) if x["slug"] != p["slug"]][:3]
    rel_cards = "\n".join(product_card(lang, r, n) for n, r in enumerate(related))
    title = f'{t(p["name"], lang)} &mdash; {t(c["name"], lang)} | AZSCO'

    body = f'''
<section class="p-detail">
  <div class="wrap">
    <ul class="crumbs">
      {trail(lang, (t(UI["all_products"], lang), "products.html"),
             (t(c["name"], lang), cat_route(c)), t(p["name"], lang))}
    </ul>

    <div class="p-detail-grid">
      <div class="p-visual reveal">
        <span class="ico">{I[p["icon"]]}</span>
        <p class="p-visual-cap">{t(UI["installed"], lang)}</p>
      </div>

      <div class="p-buy reveal">
        <p class="p-kind">{t(c["name"], lang)} &middot; {t(p["kind"], lang)}</p>
        <h1>{t(p["name"], lang)}</h1>
        <p class="lead">{t(p["blurb"], lang)}</p>

        <ul class="p-spec-key">
          <li class="p-spec-key-head">{t(UI["key_specs"], lang)}</li>
{key}
        </ul>

        <div class="p-buy-actions">
          {add_button(lang, p, "btn btn-primary js-add")}
          <a class="btn btn-outline" href="{link(lang, "quote.html")}">{t(UI["view_quote"], lang)}</a>
        </div>
        <p class="p-buy-note">{I["file"]}<span>{t(UI["quote_note"], lang)}</span></p>
        <p class="p-buy-lines"><b>{t(UI["supplied_by"], lang)}:</b> <span dir="ltr">{lines}</span></p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap p-info">
    <div class="p-info-main reveal">
      {spec_table(lang, p)}
    </div>
    <aside class="p-info-side">
      <div class="side-block reveal">
        <h3>{t(UI["highlights"], lang)}</h3>
        <ul class="check-list">
{highs}
        </ul>
      </div>
      <div class="side-block reveal">
        <h3>{t(UI["typical_use"], lang)}</h3>
        <ul class="check-list">
{apps}
        </ul>
      </div>
    </aside>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="sec-head sec-head--center reveal">
      <p class="eyebrow">{t(UI["part_of"], lang)} {t(c["name"], lang)}</p>
      <h2>{t(UI["related"], lang)}</h2>
    </div>
    <div class="grid grid-3 p-grid">
{rel_cards}
    </div>
  </div>
</section>

{cta(lang)}
'''
    page(lang, prod_route(p), title, t(p["blurb"], lang)[:300], body)



def build_brands(lang):
    B = BRANDS_PAGE
    cards = []
    for n, (name, tag, cats) in enumerate(BRANDS):
        cat_links = " ".join(
            f'<a class="tag" href="{link(lang, cat_route(CAT_BY_SLUG[s]))}">{t(CAT_BY_SLUG[s]["name"], lang)}</a>'
            for s in cats)
        count = sum(1 for p in PRODUCTS if p["cat"] in cats)
        cards.append(f'''      <article class="brand-card reveal" data-delay="{(n%4)*60}">
        <h3 dir="ltr">{name}</h3>
        <p>{t(tag, lang)}</p>
        <div class="brand-tags">{cat_links}</div>
        <span class="brand-count"><b>{count}</b> {t(UI["products"], lang)}</span>
      </article>''')
    body = f'''
{banner(lang, t(B["h1"], lang), t(B["sub"], lang), [t(UI["all_brands"], lang)])}

<section class="section">
  <div class="wrap narrow reveal">
    <h2>{t(B["lead_head"], lang)}</h2>
    <p class="rich">{t(B["lead"], lang)}</p>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="grid grid-4 brand-grid">
{chr(10).join(cards)}
    </div>
  </div>
</section>

{cta(lang)}
'''
    page(lang, "brands.html", t(B["title"], lang), t(B["desc"], lang), body)


def quote_labels(lang):
    """aria-labels for the basket rows, as JSON for main.js to read off the
    list element -- so the Arabic page's controls announce in Arabic."""
    return html.escape(json.dumps({
        "qty": t(("Quantity", "الكمية"), lang),
        "more": t(("Increase quantity", "زيادة الكمية"), lang),
        "less": t(("Decrease quantity", "إنقاص الكمية"), lang),
        "remove": t(UI["remove"], lang),
    }, ensure_ascii=False), quote=True)


def build_quote(lang):
    Q = QUOTE
    how = "\n".join(
        f'''      <li class="step reveal" data-delay="{n*80}">
        <span class="step-n" dir="ltr">{n+1:02d}</span>
        <div><h3>{t(title, lang)}</h3><p>{t(text, lang)}</p></div>
      </li>''' for n, (title, text) in enumerate(Q["how"]))
    cat_opts = "\n".join(
        f'            <option value="{t(c["name"], lang)}">{t(c["name"], lang)}</option>'
        for c in CATEGORIES)

    body = f'''
{banner(lang, t(Q["h1"], lang), t(Q["sub"], lang), [t(UI["your_quote"], lang)])}

<section class="section">
  <div class="wrap quote-wrap">

    <div class="quote-main">
      <div class="quote-list-head">
        <h2>{t(UI["your_quote"], lang)}</h2>
        <button type="button" class="link-btn js-clear-quote" hidden>{t(UI["clear_all"], lang)}</button>
      </div>

      <!-- Filled by assets/js/main.js from the basket in localStorage. The
           empty state is what the page ships with, so it is correct with
           JavaScript disabled rather than showing an empty table. -->
      <ul class="quote-list js-quote-list" hidden
          data-labels='{quote_labels(lang)}'></ul>

      <div class="empty js-quote-empty">
        <span class="ico">{I["file"]}</span>
        <h3>{t(UI["quote_empty"], lang)}</h3>
        <p>{t(UI["quote_empty_t"], lang)}</p>
        <a class="btn btn-primary" href="{link(lang, "products.html")}">{t(UI["browse"], lang)} {I["arrow"]}</a>
      </div>

      <form class="form quote-form" id="quote-form" novalidate
            data-endpoint="{CONTACT_ENDPOINT}" data-lang="{lang}"
            data-sending="{t(FORM["sending"], lang)}"
            data-sent="{t(FORM["sent"], lang)}"
            data-failed="{t(FORM["failed"], lang)}">
        <h2>{t(Q["form_head"], lang)}</h2>
        <!-- The basket is serialised into this field on submit. -->
        <input type="hidden" name="items" class="js-quote-items">
        <div class="f-row">
          <div class="field">
            <label for="q-name">{t(FORM["name"], lang)}</label>
            <input id="q-name" name="name" type="text" autocomplete="name" required>
            <p class="err" data-for="q-name"></p>
          </div>
          <div class="field">
            <label for="q-company">{t(FORM["company"], lang)}</label>
            <input id="q-company" name="company" type="text" autocomplete="organization">
            <p class="err" data-for="q-company"></p>
          </div>
        </div>
        <div class="f-row">
          <div class="field">
            <label for="q-email">{t(FORM["email"], lang)}</label>
            <input id="q-email" name="email" type="email" autocomplete="email" dir="ltr" required>
            <p class="err" data-for="q-email"></p>
          </div>
          <div class="field">
            <label for="q-phone">{t(FORM["phone"], lang)}</label>
            <input id="q-phone" name="phone" type="tel" autocomplete="tel" dir="ltr" required>
            <p class="err" data-for="q-phone"></p>
          </div>
        </div>
        <div class="field">
          <label for="q-interest">{t(FORM["interest"], lang)}</label>
          <select id="q-interest" name="interest">
            <option value="">{t(FORM["choose"], lang)}</option>
{cat_opts}
            <option value="{t(FORM["mixed"], lang)}">{t(FORM["mixed"], lang)}</option>
          </select>
        </div>
        <div class="field">
          <label for="q-msg">{t(FORM["site"], lang)}</label>
          <textarea id="q-msg" name="message" rows="5" required placeholder="{t(FORM["site_ph"], lang)}"></textarea>
          <p class="err" data-for="q-msg"></p>
        </div>
        <!-- Honeypot: a real visitor never sees or fills this. -->
        <input type="text" name="website" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
        <button class="btn btn-primary" type="submit">{t(FORM["send_quote"], lang)} {I["arrow"]}</button>
        <p class="form-note">{t(Q["form_note"], lang)}</p>
        <p class="form-msg" role="status" aria-live="polite"></p>
      </form>
    </div>

    <aside class="quote-side">
      <div class="side-block reveal">
        <h3>{t(UI["quote_req"], lang)}</h3>
        <ol class="steps steps--compact">
{how}
        </ol>
      </div>
      <div class="side-block side-block--dark reveal">
        <h3>{t(UI["call_us"], lang)}</h3>
        <p><a href="tel:{PHONE_HREF}" dir="ltr">{PHONE}</a></p>
        <p><a href="mailto:{EMAIL_SALES}" dir="ltr">{EMAIL_SALES}</a></p>
      </div>
    </aside>

  </div>
</section>
'''
    page(lang, "quote.html", t(Q["title"], lang), t(Q["desc"], lang), body)


def build_support(lang):
    S = SUPPORT
    blocks = "\n".join(
        f'''      <article class="card reveal" data-delay="{(n%3)*70}">
        <span class="ico">{I[icon]}</span>
        <h3>{t(title, lang)}</h3>
        <p>{t(text, lang)}</p>
      </article>''' for n, (icon, title, text) in enumerate(S["blocks"]))
    body = f'''
{banner(lang, t(S["h1"], lang), t(S["sub"], lang), [t(UI["installed"], lang)])}

<section class="section">
  <div class="wrap">
{section_head(lang, S["lead_eyebrow"], S["lead_head"])}
    <div class="grid grid-3">
{blocks}
    </div>
  </div>
</section>

{stats_block(lang)}

{cta(lang)}
'''
    page(lang, "support.html", t(S["title"], lang), t(S["desc"], lang), body)


def build_about(lang):
    A = ABOUT
    story = "\n".join(f'    <p>{t(par, lang)}</p>' for par in A["story"])
    ovm = "\n".join(
        f'''      <article class="card reveal" data-delay="{n*80}">
        <span class="ico">{I[icon]}</span>
        <h3>{t(title, lang)}</h3>
        <p>{t(text, lang)}</p>
      </article>''' for n, (icon, title, text) in enumerate(A["ovm"]))
    why = tiles(lang, A["why"], cols=2)
    faq = "\n".join(
        f'''      <div class="acc reveal" data-delay="{n*60}">
        <button class="acc-btn" type="button" aria-expanded="false" aria-controls="faq-{n}">
          <span>{t(q, lang)}</span>{I["plus"]}
        </button>
        <div class="acc-panel" id="faq-{n}"><p>{t(a, lang)}</p></div>
      </div>''' for n, (q, a) in enumerate(A["faq"]))

    body = f'''
{banner(lang, t(A["h1"], lang), t(A["sub"], lang), [t(A["h1"], lang)])}

<section class="section">
  <div class="wrap narrow reveal">
    <p class="eyebrow">{t(A["story_eyebrow"], lang)}</p>
    <h2>{t(A["story_head"], lang)}</h2>
    <div class="rich">
{story}
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="grid grid-3">
{ovm}
    </div>
  </div>
</section>

{stats_block(lang)}

<section class="section">
  <div class="wrap">
{section_head(lang, A["why_eyebrow"], A["why_head"])}
    <div class="grid grid-2 tile-grid">
{why}
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap narrow">
{section_head(lang, A["faq_eyebrow"], A["faq_head"])}
    <div class="acc-list">
{faq}
    </div>
  </div>
</section>

{cta(lang)}
'''
    page(lang, "about.html", t(A["title"], lang), t(A["desc"], lang), body)


def build_contact(lang):
    C = CONTACT
    body = f'''
{banner(lang, t(C["h1"], lang), t(C["sub"], lang), [t(C["h1"], lang)])}

<section class="section">
  <div class="wrap contact-wrap">
    <div class="contact-cards">
      <article class="info-card reveal">
        <span class="ico">{I["pin"]}</span>
        <h3>{t(C["office"], lang)}</h3>
        <p><a href="{MAPS_URL}" target="_blank" rel="noopener noreferrer">{t(ADDRESS_BR, lang)}</a></p>
      </article>
      <article class="info-card reveal" data-delay="80">
        <span class="ico">{I["phone"]}</span>
        <h3>{t(C["phone_h"], lang)}</h3>
        <p><a href="tel:{PHONE_HREF}" dir="ltr">{PHONE}</a></p>
        <p class="muted">{t(C["emerg"], lang)}</p>
      </article>
      <article class="info-card reveal" data-delay="160">
        <span class="ico">{I["mail"]}</span>
        <h3>{t(C["email_h"], lang)}</h3>
        <p><a href="mailto:{EMAIL}" dir="ltr">{EMAIL}</a></p>
        <p><a href="mailto:{EMAIL_SALES}" dir="ltr">{EMAIL_SALES}</a></p>
      </article>
      <article class="info-card reveal" data-delay="240">
        <span class="ico">{I["clock"]}</span>
        <h3>{t(C["hours_h"], lang)}</h3>
        <p>{t(HOURS_FOOT, lang)}</p>
      </article>
    </div>

    <aside class="contact-aside reveal">
      <h2>{t(UI["quote_req"], lang)}</h2>
      <p>{t(CTA_DEFAULT[1], lang)}</p>
      <div class="btn-row">
        <a class="btn btn-primary" href="{link(lang, "quote.html")}">{t(UI["quote_req"], lang)} {I["arrow"]}</a>
        <a class="btn btn-outline" href="{link(lang, "products.html")}">{t(UI["browse"], lang)}</a>
      </div>
    </aside>
  </div>
</section>
'''
    page(lang, "contact.html", t(C["title"], lang), t(C["desc"], lang), body)


def build_privacy(lang):
    P = PRIVACY
    secs = "\n".join(
        f'    <h2>{t(head, lang)}</h2>\n    <p>{t(text, lang)}</p>'
        for head, text in P["sections"])
    body = f'''
{banner(lang, t(P["h1"], lang), t(P["sub"], lang), [t(P["h1"], lang)])}

<section class="section">
  <div class="wrap narrow rich reveal">
{secs}
    <p>{t(P["contact_line"], lang)} <a href="mailto:{EMAIL}" dir="ltr">{EMAIL}</a></p>
  </div>
</section>
'''
    page(lang, "privacy-policy.html", t(P["title"], lang), t(P["desc"], lang), body)


def build_404(lang):
    N = NOTFOUND
    links = "\n".join(
        f'        <a class="btn btn-outline btn-sm" href="{link(lang, cat_route(c))}">{t(c["name"], lang)}</a>'
        for c in CATEGORIES)
    body = f'''
<section class="section section--dark nf">
  <div class="wrap narrow">
    <p class="nf-code" dir="ltr">{t(N["h1"], lang)}</p>
    <h1>{t(N["head"], lang)}</h1>
    <p class="lead">{t(N["text"], lang)}</p>
    <div class="btn-row">
      <a class="btn btn-primary" href="{link(lang, "products.html")}">{t(UI["browse"], lang)} {I["arrow"]}</a>
      <a class="btn btn-outline" href="{link(lang, "index.html")}">{t(UI["home"], lang)}</a>
    </div>
    <div class="nf-links">
{links}
    </div>
  </div>
</section>
'''
    page(lang, "404.html", t(N["title"], lang), t(N["desc"], lang), body)

# ============================================================ write
SITEMAP_PRIORITY = {"index.html": "1.0", "products.html": "0.9"}
for _c in CATEGORIES:
    SITEMAP_PRIORITY[cat_route(_c)] = "0.8"
for _p in PRODUCTS:
    SITEMAP_PRIORITY[prod_route(_p)] = "0.7"
SITEMAP_PRIORITY.update({
    "brands.html": "0.6", "support.html": "0.6", "about.html": "0.6",
    "contact.html": "0.7", "quote.html": "0.7", "privacy-policy.html": "0.3",
})


# ============================================================ chrome overrides
# The header and footer below replace the ones above, which were built for a
# services site. Two things change, and both follow from selling products:
# the header carries a quote basket with a live count, and the footer's second
# column lists catalogue categories instead of services.

def header(lang, fname):
    a = asset(lang, "")
    return f'''
<div class="topbar">
  <div class="wrap">
    <ul class="topbar-list">
      <li class="hide-sm">{I["pin"]}<a href="{MAPS_URL}" target="_blank" rel="noopener noreferrer" aria-label="{t(UI["map_label"], lang)}">{t(ADDRESS_1L, lang)}</a></li>
      <li>{I["phone"]}<a href="tel:{PHONE_HREF}" dir="ltr">{PHONE}</a></li>
      <li class="hide-md">{I["mail"]}<a href="mailto:{EMAIL_SALES}" dir="ltr">{EMAIL_SALES}</a></li>
      <li class="hide-md">{I["clock"]}<span>{t(RESPONSE_24, lang)}</span></li>
    </ul>
    <div class="topbar-end">
      <div class="topbar-social" aria-label="{t(UI["social"], lang)}">
        <a href="{FACEBOOK_URL}" target="_blank" rel="noopener noreferrer" aria-label="AZSCO on Facebook">{I["facebook"]}</a>
        <a href="{X_URL}" target="_blank" rel="noopener noreferrer" aria-label="AZSCO on X">{I["x"]}</a>
        <a href="{INSTAGRAM_URL}" target="_blank" rel="noopener noreferrer" aria-label="AZSCO on Instagram">{I["instagram"]}</a>
      </div>
    </div>
  </div>
</div>

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{link(lang, "index.html")}" aria-label="{t(UI["home_label"], lang)}">
      <img class="brand-logo" src="{a}assets/img/AZSCO_Logo.png" alt="{t(SITE_NAME, lang)}" width="347" height="160">
    </a>

    <nav aria-label="{t(UI["main_nav"], lang)}">
        {desktop_nav(lang)}
    </nav>

    <div class="header-cta">
      {lang_link(lang, fname, "lang-switch lang-switch--head")}
      <!-- The count is written by assets/js/main.js from the basket; it ships
           at zero and hidden, so the markup is correct without JavaScript. -->
      <a class="quote-btn" href="{link(lang, "quote.html")}">
        {I["file"]}<span class="quote-btn-text">{t(UI["your_quote"], lang)}</span>
        <span class="quote-count js-quote-count" hidden dir="ltr">0</span>
      </a>
      <button class="burger" type="button" aria-label="{t(UI["menu_open"], lang)}" aria-expanded="false" aria-controls="mobile-nav"><span></span></button>
    </div>
  </div>
</header>

<div class="backdrop"></div>
<nav class="mobile-nav" id="mobile-nav" aria-label="{t(UI["mob_nav"], lang)}">
  <div class="mobile-nav-head">
    <img class="brand-logo" src="{a}assets/img/AZSCO_Logo.png" alt="{t(SITE_NAME, lang)}" width="347" height="160">
    <button class="close" type="button" aria-label="{t(UI["menu_close"], lang)}">{I["close"]}</button>
  </div>
      {mobile_nav(lang)}
  <div class="mobile-nav-foot">
    <a class="btn btn-primary" href="{link(lang, "quote.html")}">{t(UI["quote_req"], lang)}</a>
    <a class="m-contact" href="tel:{PHONE_HREF}">{I["phone"]}<span dir="ltr">{PHONE}</span></a>
    <a class="m-contact" href="mailto:{EMAIL_SALES}">{I["mail"]}<span dir="ltr">{EMAIL_SALES}</span></a>
  </div>
</nav>
'''


def footer(lang):
    a = asset(lang, "")
    company = "\n          ".join(
        f'<li><a href="{link(lang, href)}">{t(label, lang)}</a></li>'
        for label, href in FOOTER["company"])
    catalogue = "\n          ".join(
        [f'<li><a href="{link(lang, "products.html")}">{t(UI["all_products"], lang)}</a></li>'] +
        [f'<li><a href="{link(lang, cat_route(c))}">{t(c["name"], lang)}</a></li>' for c in CATEGORIES])
    return f'''
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="brand" href="{link(lang, "index.html")}" aria-label="{t(UI["home_label"], lang)}">
          <img class="brand-logo" src="{a}assets/img/AZSCO_Logo_white.png" alt="{t(SITE_NAME, lang)}" width="347" height="160">
        </a>
        <p>{t(FOOTER["blurb"], lang)}</p>
        <div class="footer-social">
          <a href="{FACEBOOK_URL}" target="_blank" rel="noopener noreferrer" aria-label="AZSCO on Facebook">{I["facebook"]}</a>
          <a href="{X_URL}" target="_blank" rel="noopener noreferrer" aria-label="AZSCO on X">{I["x"]}</a>
          <a href="{INSTAGRAM_URL}" target="_blank" rel="noopener noreferrer" aria-label="AZSCO on Instagram">{I["instagram"]}</a>
        </div>
      </div>

      <div>
        <h4>{t(FOOTER["cat_head"], lang)}</h4>
        <ul class="footer-links">
          {catalogue}
        </ul>
      </div>

      <div>
        <h4>{t(FOOTER["com_head"], lang)}</h4>
        <ul class="footer-links">
          {company}
        </ul>
      </div>

      <div>
        <h4>{t(FOOTER["con_head"], lang)}</h4>
        <ul class="footer-contact">
          <li>{I["pin"]}<span>{t(ADDRESS_BR, lang)}</span></li>
          <li>{I["phone"]}<a href="tel:{PHONE_HREF}" dir="ltr">{PHONE}</a></li>
          <li>{I["mail"]}<span><a href="mailto:{EMAIL}" dir="ltr">{EMAIL}</a><small>{t(FOOTER["email_general"], lang)}</small></span></li>
          <li>{I["mail"]}<span><a href="mailto:{EMAIL_SALES}" dir="ltr">{EMAIL_SALES}</a><small>{t(FOOTER["email_sales"], lang)}</small></span></li>
          <li>{I["clock"]}<span>{t(HOURS_FOOT, lang)}</span></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <p>&copy; <span data-year>2026</span> {t(COMPANY, lang)}. {t(FOOTER["rights"], lang)}</p>
      <ul>
        <li><a href="{link(lang, "privacy-policy.html")}">{t(FOOTER["privacy"], lang)}</a></li>
        <li><a href="{link(lang, "contact.html")}">{t(FOOTER["contact"], lang)}</a></li>
      </ul>
    </div>
  </div>
</footer>

<button class="to-top" type="button" aria-label="{t(UI["to_top"], lang)}">{I["up"]}</button>
<a class="whatsapp-fab" href="{WHATSAPP_URL}" target="_blank" rel="noopener noreferrer" aria-label="{t(UI["whatsapp"], lang)}">{I["whatsapp"]}</a>

<div class="mobile-bar">
  <a class="mobile-bar-call" href="tel:{PHONE_HREF}">{I["phone"]}<span>{t(UI["call_now"], lang)}</span></a>
  <a class="mobile-bar-quote" href="{link(lang, "quote.html")}">{I["file"]}<span>{t(UI["get_quote"], lang)}</span>
    <span class="quote-count js-quote-count" hidden dir="ltr">0</span></a>
</div>
{chat_widget(lang)}
<script src="{a}assets/js/main.js"></script>
<script src="{a}assets/js/chat.js" defer></script>
{analytics_tag()}
</body>
</html>
'''

BACKEND_FILES = (
    os.path.join("backend", "workers", "chat-worker.js"),
    os.path.join("backend", "api", "chat.js"),
)

PROMPT_BEGIN = "/* AZSCO-PROMPT:BEGIN"
PROMPT_END = "/* AZSCO-PROMPT:END */"


def backend_prompt_block():
    """The assistant's facts and rules, as a block of JavaScript.

    Spliced into each proxy between the markers below, so the prompt has one
    source of truth (CHAT_FACTS / CHAT_RULES above) even though the proxies are
    deployed separately from the site and cannot read this file at run time.
    """
    # The facts go into a JS template literal, so anything that would end it
    # early or start an interpolation has to be escaped.
    facts = CHAT_FACTS.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    rules = CHAT_RULES.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    return f"""{PROMPT_BEGIN} -- generated by tools/build.py. Do not edit by hand:
   edit CHAT_FACTS / CHAT_RULES in tools/build.py and rebuild. */
const FACTS = `{facts}`;

const RULES = `{rules}`;

function systemPrompt(lang) {{
  return `You are the AZSCO Assistant, the virtual assistant on the website of AZSCO,
a security company in Kuwait.
${{FACTS}}${{RULES}}- ${{lang === 'ar'
      ? 'Reply in Arabic (Modern Standard Arabic), in a professional tone.'
      : 'Reply in English, in a professional tone.'}}`;
}}
{PROMPT_END}"""


def sync_backend_prompt():
    """Rewrites the generated prompt block in each proxy; returns those changed."""
    block = backend_prompt_block()
    changed = []
    for rel in BACKEND_FILES:
        path = os.path.join(OUT, rel)
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        head, mark, rest = src.partition(PROMPT_BEGIN)
        if not mark:
            raise SystemExit(f"{rel}: missing {PROMPT_BEGIN} marker")
        _, mark, tail = rest.partition(PROMPT_END)
        if not mark:
            raise SystemExit(f"{rel}: missing {PROMPT_END} marker")
        out = head + block + tail
        if out != src:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(out)
            changed.append(rel)
    return changed


def write_sitemap():
    """Built from the pages that exist, with an alternate for each language."""
    today = datetime.date.today().isoformat()
    rows = []
    for fname, priority in SITEMAP_PRIORITY.items():
        for lang in LANGS:
            alts = "".join(
                f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{canonical(l, fname)}"/>'
                for l in LANGS)
            rows.append(f'  <url>\n    <loc>{canonical(lang, fname)}</loc>{alts}\n'
                        f'    <lastmod>{today}</lastmod>\n    <priority>{priority}</priority>\n  </url>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
           '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + "\n".join(rows) + "\n</urlset>\n")
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(xml)
    return len(rows)

def write_redirect(out_path, target_url, lang="en"):
    """A minimal page that immediately forwards to target_url and tells search
    engines that URL is the real one. Used for two things: the flat ".html"
    URLs this migration retires (about.html -> /about/, ...), so a bookmark or
    a result already indexed by a search engine still arrives; and the /home/
    alias, for anyone who types or shares "azsco.systems/home" expecting it to
    work even though the homepage itself lives at the site root."""
    html = f'''<!DOCTYPE html>
<html {lang_attrs(lang)}>
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url={target_url}">
<link rel="canonical" href="{target_url}">
<meta name="robots" content="noindex">
<title>{t(SITE_NAME, lang)}</title>
</head>
<body>
<p><a href="{target_url}">{t(SITE_NAME, lang)}</a></p>
</body>
</html>
'''
    full = os.path.join(OUT, out_path)
    os.makedirs(os.path.dirname(full) or OUT, exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(html)


if __name__ == "__main__":
    for lang in LANGS:
        build_home(lang)
        build_catalogue(lang)
        for c in CATEGORIES:
            build_category(lang, c)
        for p in PRODUCTS:
            build_product(lang, p)
        build_brands(lang)
        build_quote(lang)
        build_support(lang)
        build_about(lang)
        build_contact(lang)
        build_privacy(lang)
        build_404(lang)

    for (lang, fname), html in PAGES.items():
        out_path = out_file_for(lang, fname)
        full = os.path.join(OUT, out_path)
        os.makedirs(os.path.dirname(full) or OUT, exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(html)
    print("wrote", len(PAGES), "pages")

    # The services site this replaced lived at these addresses. They are kept
    # as redirects to the nearest page here rather than left to 404, so an
    # inbound link or an indexed result still arrives somewhere useful.
    # Pages the catalogue replaced. Both spellings are redirected: the clean
    # URL that was canonical (/services/) and the flat one it superseded
    # (/services.html), so neither an indexed result nor an old bookmark 404s.
    RETIRED = {
        "services": "products.html",   # the services site's catalogue equivalent
        "clients": "about.html",
        "partners": "brands.html",
        "home": "index.html",          # alias, never canonical
    }
    redirects = 0
    for lang in LANGS:
        prefix = "" if lang == "en" else "ar/"
        for slug, target in RETIRED.items():
            url = canonical(lang, target)
            write_redirect(f"{prefix}{slug}/index.html", url, lang)
            write_redirect(f"{prefix}{slug}.html", url, lang)
            redirects += 2
        # The flat ".html" spelling of each current page, for anything that
        # linked to it before the clean URLs existed.
        for fname in ("about.html", "contact.html", "privacy-policy.html",
                      "products.html", "brands.html", "support.html", "quote.html"):
            write_redirect(prefix + fname, canonical(lang, fname), lang)
            redirects += 1
    print("wrote", redirects, "redirect stubs")

    print("wrote sitemap.xml with", write_sitemap(), "urls")
    synced = sync_backend_prompt()
    print("backend prompt:", ", ".join(synced) if synced else "already in sync")
