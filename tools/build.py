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

WHAT AZSCO DOES
AZSCO provides security manpower and security systems. Services:
- Facility Guarding: trained, uniformed officers guarding apartments, malls,
  banks, stores, offices, compounds, industrial sites and events.
- VIP Protection & Rapid Intervention: physically and technically qualified
  personal guards for individuals needing a high level of security, plus
  rapid-intervention response to critical sites.
- Central Operations Room: a 24/7 monitoring and communications room that
  keeps continuous contact with every AZSCO-guarded site and dispatches a
  rapid response to any incident.
- Security Patrols: scheduled patrols by trained officers equipped with the
  necessary tools, reinforcing the security of guarded sites and areas.
- Security Systems: advanced, site-specific systems -- surveillance cameras
  and fire and theft alarm systems -- installed and monitored by AZSCO, with
  alerts routed to the Central Operations Room for rapid patrol intervention.

OTHER FACTS
- Officers are screened, licensed, uniformed, trained (first aid,
  fire-fighting, dealing with the public, dealing with accidents,
  self-defense) and supervised.
- Officers come from a range of nationalities: Kuwaiti, Indian, Egyptian,
  Chadian, Nigerian, Nepalese and stateless individuals.
- Serves government, commercial, financial, industrial, residential and many
  other sectors across Kuwait.
- Technology partners whose equipment powers AZSCO's Security Systems service
  and Central Operations Room monitoring: Ajax, Rasilient, Avigilon,
  Teltonika, Inrico, Hikvision, Pelco and Motorola.
- Clients include Radisson Blu Hotel Kuwait, Millennium Hotels and Resorts,
  Kuwait Ports Authority, Alghanim Industries and Alnasser, among others --
  see the Clients page for more.
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
ROUTES = {
    "index.html": "",
    "about.html": "about",
    "services.html": "services",
    "clients.html": "clients",
    "partners.html": "partners",
    "contact.html": "contact",
    "privacy-policy.html": "privacy-policy",
}

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
NAV = [
    (("About", "من نحن"), "about.html", []),
    (("Services", "خدماتنا"), "services.html", [
        (("All Services", "جميع الخدمات"), "services.html"),
        (("Facility Guarding", "حراسة المنشآت"), "services.html#guarding"),
        (("VIP Protection &amp; Rapid Intervention", "حماية الشخصيات والتدخل السريع"), "services.html#protection"),
        (("Central Operations Room", "غرفة عمليات مركزية"), "services.html#operations"),
        (("Security Patrols", "دوريات أمنية"), "services.html#patrols"),
        (("Security Systems", "أنظمة أمنية"), "services.html#systems"),
    ]),
    (("Clients", "عملاؤنا"), "clients.html", []),
    (("Partners", "شركاؤنا"), "partners.html", []),
    (("Contact", "اتصل بنا"), "contact.html", []),
]

FOOTER = {
    "blurb": ("AZSCO Security Services Company has been protecting premises, assets and people across Kuwait since 2014, with professionally trained, licensed and closely supervised security personnel.",
              "تعمل شركة أزسكو لخدمات حراسة المنشآت على حماية المنشآت والممتلكات والأشخاص في جميع أنحاء الكويت منذ عام 2014، بكوادر أمنية مدرّبة ومرخّصة وتخضع لإشراف دقيق."),
    "company": ("Company", "الشركة"),
    "services": ("Services", "الخدمات"),
    "touch": ("Get In Touch", "تواصل معنا"),
  "email_general": ("General enquiries", "الاستفسارات العامة"),
  "email_sales": ("Sales &amp; quotations", "المبيعات وعروض الأسعار"),
    "links": [
        (("Home", "الرئيسية"), "index.html"),
        (("About AZSCO", "عن أزسكو"), "about.html"),
        (("Our Services", "خدماتنا"), "services.html"),
        (("Our Clients", "عملاؤنا"), "clients.html"),
        (("Our Partners", "شركاؤنا"), "partners.html"),
        (("Contact Us", "اتصل بنا"), "contact.html"),
    ],
    "rights": ("All rights reserved.", "جميع الحقوق محفوظة."),
    "privacy": ("Privacy Policy", "سياسة الخصوصية"),
    "contact": ("Contact", "اتصل بنا"),
}

CTA_DEFAULT = (
    ("Ready to secure what matters most?", "هل أنت مستعد لحماية ما يهمّك؟"),
    ("Talk to an AZSCO security consultant about a site survey and a tailored proposal for your premises.",
     "تحدّث مع مستشار أمني من أزسكو حول معاينة الموقع وإعداد عرض مخصّص لمنشأتك."),
)

# ============================================================ services
SERVICES = [
  {"anchor": "guarding", "icon": "shield",
   "name": ("Facility Guarding", "حراسة المنشآت"),
   "card": ("A comprehensive range of security services for facilities of every kind, delivered by a team known for its efficiency and professionalism.",
            "مجموعة شاملة من الخدمات الأمنية لمختلف المنشآت، يقدّمها فريق يتميّز بكفاءته واحترافيته."),
   "intro": ("AZSCO offers a comprehensive range of security services for various facilities. The security team is known for its efficiency and professionalism, undergoing extensive training that covers emergency handling, surveillance techniques and maintaining site security.",
             "تقدّم أزسكو مجموعة شاملة من الخدمات الأمنية في مختلف المنشآت. يتميّز فريق الحراسة بكفاءته واحترافيته، حيث يخضع لتدريبات مكثّفة تغطي التعامل مع الحالات الطارئة وتقنيات المراقبة وحفظ الأمن في المواقع."),
   "points": [
     ("Static officers for facilities of every kind", "أفراد أمن ثابتون لمختلف أنواع المنشآت"),
     ("Screened, licensed and uniformed personnel", "كوادر مدقّقة أمنياً ومرخّصة وبزي رسمي"),
     ("Extensive training in emergency handling", "تدريبات مكثّفة على التعامل مع الحالات الطارئة"),
     ("Surveillance techniques and site security", "تقنيات المراقبة وحفظ الأمن في المواقع"),
     ("Day, night and rotating shift patterns", "ورديات صباحية وليلية ودوّارة"),
   ]},
  {"anchor": "protection", "icon": "target",
   "name": ("VIP Protection &amp; Rapid Intervention", "حماية الشخصيات والتدخل السريع"),
   "card": ("Rapid intervention for critical sites and personal protection for individuals who need a high level of security, through physically and technically qualified guards.",
            "خدمات تدخّل سريع للمواقع المهمة وحماية شخصية للأفراد الذين يحتاجون إلى مستوى عالٍ من الأمان، عبر حراس مؤهلين جسمانياً وفنياً."),
   "intro": ("AZSCO provides rapid intervention services to critical sites to ensure security control, along with personal protection services for individuals requiring a high level of security through physically and technically qualified personal guards.",
             "تقدّم أزسكو خدمات التدخّل السريع للمواقع المهمة لضمان ضبط الأمن، إلى جانب خدمات الحماية الشخصية للأفراد المهمين الذين يحتاجون إلى مستوى عالٍ من الأمان، من خلال توفير حراس شخصيين مؤهلين جسمانياً وفنياً."),
   "points": [
     ("Rapid intervention for critical sites", "تدخّل سريع للمواقع المهمة"),
     ("Personal protection for high-profile individuals", "حماية شخصية للأفراد المهمين"),
     ("Physically and technically qualified personal guards", "حراس شخصيون مؤهلون جسمانياً وفنياً"),
     ("Close protection and escort details", "فرق حماية شخصية ومرافقة"),
     ("Pre-assignment risk assessment", "تقييم للمخاطر قبل التكليف"),
   ]},
  {"anchor": "operations", "icon": "eye",
   "name": ("Central Operations Room", "غرفة عمليات مركزية"),
   "card": ("A 24/7 operations room equipped with the latest monitoring and communication technology, in continuous contact with every site AZSCO guards.",
            "غرفة عمليات تعمل على مدار الساعة، مجهّزة بأحدث تقنيات المراقبة والاتصال، وعلى تواصل مستمر مع كل موقع تحرسه أزسكو."),
   "intro": ("The Central Operations Room is a core AZSCO offering, ensuring safety and rapid response to any security incident. Equipped with the latest monitoring and communication technology, it operates 24/7, allowing continuous surveillance and immediate communication with every site AZSCO guards. The team consists of trained, specialised personnel capable of handling a wide range of security situations.",
             "تُعدّ غرفة العمليات المركزية إحدى الخدمات الأساسية التي توفّرها أزسكو لضمان الأمان والاستجابة السريعة لأي حادث أمني. وهي مجهّزة بأحدث تقنيات المراقبة والاتصالات، وتعمل على مدار الساعة، مما يتيح مراقبة مستمرة وتواصلاً فورياً مع المواقع الأمنية التي تتولى أزسكو حراستها. يتألّف فريق غرفة العمليات من كوادر مدرّبة ومتخصصة، قادرة على التعامل مع مختلف المواقف الأمنية."),
   "points": [
     ("Operating 24 hours a day, 7 days a week", "تعمل على مدار 24 ساعة طوال أيام الأسبوع"),
     ("Latest monitoring and communication technology", "أحدث تقنيات المراقبة والاتصالات"),
     ("Continuous surveillance of every guarded site", "مراقبة مستمرة لكل موقع مُحروس"),
     ("Immediate communication with officers on site", "تواصل فوري مع الأفراد في الموقع"),
     ("Trained, specialised operations personnel", "كوادر عمليات مدرّبة ومتخصصة"),
   ]},
  {"anchor": "patrols", "icon": "route",
   "name": ("Security Patrols", "دوريات أمنية"),
   "card": ("Organised, specialised patrols by a trained team of officers, equipped with modern technical means to keep a visible security presence across your site.",
            "دوريات أمنية متخصصة ومنظّمة يقوم بها فريق مدرّب من حراس الأمن، مزوّدين بوسائل تقنية حديثة للحفاظ على حضور أمني ظاهر في موقعك."),
   "intro": ("A specialised patrol service that strengthens security and surveillance across the facilities and areas AZSCO guards. It consists of organised patrols carried out by a trained team of security officers, equipped with the necessary equipment and modern technical means to ensure the highest level of efficiency and effectiveness.",
             "خدمة دوريات أمنية متخصصة تهدف إلى تعزيز الأمان والرقابة على المنشآت والمناطق التي تتولى أزسكو حراستها. تتضمّن دوريات أمنية منظّمة يقوم بها فريق مدرّب من حراس الأمن، مزوّدين بالمعدات اللازمة والوسائل التقنية الحديثة لضمان أعلى مستوى من الكفاءة والفعالية."),
   "points": [
     ("Organised, scheduled and random patrol visits", "زيارات دوريات منظّمة ومجدولة وعشوائية"),
     ("Trained team of security officers", "فريق مدرّب من حراس الأمن"),
     ("Modern technical means and equipment", "وسائل تقنية حديثة ومعدّات لازمة"),
     ("Coordinated with the Central Operations Room", "تنسيق مع غرفة العمليات المركزية"),
     ("Time-stamped patrol reports for every visit", "تقارير دوريات موثّقة بالوقت لكل زيارة"),
   ]},
  {"anchor": "systems", "icon": "camera",
   "name": ("Security Systems", "أنظمة أمنية"),
   "card": ("Advanced, site-specific security systems — surveillance cameras and fire and theft alarms — feeding real-time alerts to our Central Operations Room.",
            "أنظمة أمنية متطوّرة ومخصّصة لكل موقع — كاميرات مراقبة وأنظمة إنذار ضد الحريق والسرقة — ترسل تنبيهات فورية إلى غرفة عملياتنا المركزية."),
   "intro": ("AZSCO offers a comprehensive service in security system solutions, tailored to meet the needs of the facilities and sites under its protection. This service focuses on providing advanced, site-specific security systems, ensuring the highest levels of protection and safety. Solutions include surveillance cameras, fire and theft alarm systems and other modern security technologies, helping monitor activity in and around the facility around the clock and enabling rapid patrol intervention based on alarms received by the Central Operations Room.",
             "تقدّم أزسكو خدمة متكاملة في مجال حلول الأنظمة الأمنية، مصمّمة خصيصاً لتلبية احتياجات المنشآت والمواقع التي تتولى حمايتها. تركّز هذه الخدمة على توفير نظم أمنية متطوّرة ومخصّصة لكل موقع، بما يضمن أعلى مستويات الحماية والأمان. تشمل الحلول كاميرات مراقبة وأنظمة إنذار ضد الحريق والسرقة وغيرها من التقنيات الأمنية الحديثة، وتساعد في رصد الأنشطة داخل المنشأة وحولها على مدار اليوم، وتتيح إمكانية التدخّل السريع للدوريات بناءً على الإنذارات التي تصل إلى غرفة العمليات المركزية."),
   "points": [
     ("Surveillance cameras (CCTV) tailored to each site", "كاميرات مراقبة مخصّصة لكل موقع"),
     ("Fire and theft alarm systems", "أنظمة إنذار ضد الحريق والسرقة"),
     ("Round-the-clock monitoring in and around the facility", "مراقبة على مدار الساعة داخل المنشأة وحولها"),
     ("Alerts routed directly to the Central Operations Room", "تنبيهات تصل مباشرة إلى غرفة العمليات المركزية"),
     ("Rapid patrol intervention triggered by system alarms", "تدخّل سريع للدوريات عند تفعيل إنذارات الأنظمة"),
   ]},
]

VALUES = [
    ("Trust", "الثقة"), ("Cooperation", "التعاون"), ("Quality", "الجودة"),
    ("Innovation", "الإبتكار"), ("Focus", "التركيز"), ("Determination", "الإصرار"),
]

NATIONALITIES = [
    ("Kuwaiti", "كويتية"), ("Indian", "هندية"), ("Egyptian", "مصرية"),
    ("Chadian", "تشادية"), ("Nigerian", "نيجيرية"), ("Nepalese", "نيبالية"),
    ("Stateless individuals", "غير محددي الجنسية"),
]

TRAINING = [
    ("plus",         ("First Aid", "الإسعافات الأولية")),
    ("flame",        ("Fire-Fighting", "مكافحة الحرائق")),
    ("users",        ("Dealing with the Public", "التعامل مع الجمهور")),
    ("shield-check", ("Dealing with Accidents", "التعامل مع الحوادث")),
    ("shield",       ("Self-Defense", "الدفاع عن النفس")),
]

EQUIPMENT = [
    ("Walkie Talkie", "جهاز اتصال لاسلكي"),
    ("Flashlight", "كشاف يدوي"),
    ("Baton", "العصا"),
    ("Fire Extinguisher", "طفاية حريق"),
    ("First Aid Kit", "حقيبة إسعافات أولية"),
    ("Metal Detectors", "الكاشفات المعدنية"),
]

CERTIFICATIONS = [
    ("ISO 9001:2015 certified quality management system.",
     "حاصلة على شهادة 9001:2015 ISO لنظام إدارة الجودة."),
    ("Certified compliant with Anti-Money Laundering standards.",
     "حاصلة على شهادة الالتزام بمعايير مكافحة غسل الأموال."),
]

UNIFORMS = [
    ("formal", ("Formal Uniform", "الزي الرسمي")),
    ("winter", ("Winter Uniform", "الزي الشتوي")),
    ("patrol", ("Patrol Uniform", "زي الدوريات")),
    ("security", ("Duty Uniform", "زي المناوبة")),
]

# 8 official technology partners; rendered as a single logo panel image
# (assets/img/photos/partners-logos.png), this list backs the count shown in
# the statistics row and the image's alt text.
PARTNERS = ["Ajax", "Rasilient", "Avigilon", "Teltonika", "Inrico", "Hikvision", "Pelco", "Motorola"]

CLIENTS_ALT = ("Logos of AZSCO clients including Radisson Blu Hotel Kuwait, Alnasser, Millennium Hotels and Resorts, Kuwait Ports Authority and others",
               "شعارات عملاء أزسكو، ومنهم فندق راديسون بلو الكويت، والنصر، وميلينيوم للفنادق والمنتجعات، والهيئة العامة لموانئ الكويت وغيرهم")
PARTNERS_ALT = ("Logos of AZSCO technology partners: Ajax, Rasilient, Avigilon, Teltonika, Inrico, Hikvision, Pelco and Motorola",
                "شعارات شركاء أزسكو التقنيين: Ajax وRasilient وAvigilon وTeltonika وInrico وHikvision وPelco وMotorola")
CERT_ALT = ("AZSCO certification badges: SCK, IAS accredited and ISO 9001",
            "شهادات أزسكو: SCK، معتمدة من IAS، وISO 9001")
SECTORS_ALT = ("Icons for the 15 sectors AZSCO protects: government, commercial, financial, "
               "industrial, public facilities, events, tourist sites, residential complexes, "
               "ports and airports, critical infrastructure, warehousing, transport and "
               "logistics, protected areas, sports and recreation, and vital infrastructure",
               "أيقونات للقطاعات الـ15 التي تحميها أزسكو: الحكومية والتجارية والمالية والصناعية "
               "والمرافق العامة والفعاليات والمواقع السياحية والمجمعات السكنية والموانئ "
               "والمطارات والبنية التحتية الحيوية والمخازن والنقل واللوجستيات والمناطق "
               "المحمية والمرافق الرياضية والترفيهية والمنشآت الحيوية")
HERO_SVG = '''<svg viewBox="0 0 320 300" role="img" aria-label="Illustration of a monitored, protected building">
<defs><linearGradient id="hg" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#9a9a9a"/></linearGradient></defs>
<rect x="70" y="70" width="180" height="180" rx="10" fill="none" stroke="rgba(255,255,255,.28)" stroke-width="2"/>
<rect x="100" y="100" width="120" height="120" rx="8" fill="rgba(255,255,255,.10)" stroke="url(#hg)" stroke-width="2"/>
<path d="M160 118l38 14v26c0 24-16 42-38 50-22-8-38-26-38-50v-26z" fill="none" stroke="url(#hg)" stroke-width="3"/>
<path d="m148 168 9 9 20-20" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="70" cy="70" r="7" fill="#ffffff"/><circle cx="250" cy="70" r="7" fill="#ffffff"/>
<circle cx="70" cy="250" r="7" fill="#ffffff"/><circle cx="250" cy="250" r="7" fill="#ffffff"/>
<path d="M40 160h30M250 160h30M160 40v30M160 250v30" stroke="rgba(255,255,255,.28)" stroke-width="2" stroke-linecap="round"/>
</svg>'''

ABOUT_SVG = '''<svg viewBox="0 0 320 300" role="img" aria-label="Illustration of AZSCO security operations">
<defs><linearGradient id="ag" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#9a9a9a"/></linearGradient></defs>
<rect x="46" y="96" width="70" height="130" rx="6" fill="rgba(255,255,255,.16)" stroke="url(#ag)" stroke-width="2"/>
<rect x="126" y="56" width="70" height="170" rx="6" fill="rgba(255,255,255,.24)" stroke="url(#ag)" stroke-width="2"/>
<rect x="206" y="120" width="70" height="106" rx="6" fill="rgba(255,255,255,.09)" stroke="url(#ag)" stroke-width="2"/>
<g fill="rgba(255,255,255,.35)">
<rect x="58" y="112" width="16" height="14" rx="2"/><rect x="86" y="112" width="16" height="14" rx="2"/>
<rect x="58" y="140" width="16" height="14" rx="2"/><rect x="86" y="140" width="16" height="14" rx="2"/>
<rect x="138" y="76" width="16" height="14" rx="2"/><rect x="166" y="76" width="16" height="14" rx="2"/>
<rect x="138" y="104" width="16" height="14" rx="2"/><rect x="166" y="104" width="16" height="14" rx="2"/>
<rect x="218" y="140" width="16" height="14" rx="2"/><rect x="246" y="140" width="16" height="14" rx="2"/>
</g>
<path d="M161 150l30 11v21c0 19-13 33-30 40-17-7-30-21-30-40v-21z" fill="#0d0d0d" stroke="url(#ag)" stroke-width="3"/>
<path d="m150 182 8 8 17-17" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M30 236h260" stroke="rgba(255,255,255,.25)" stroke-width="3" stroke-linecap="round"/>
</svg>'''

# ============================================================ home
HOME = {
  "title": ("AZSCO Security | Professional Security Services for Kuwait",
            "أزسكو للأمن | خدمات أمنية احترافية في الكويت"),
  "desc": ("AZSCO Security Services Company provides professional security services in Kuwait since 2014 — facility guarding, VIP protection and rapid intervention, a 24/7 central operations room, security patrols, and security systems.",
           "تقدّم شركة أزسكو لخدمات حراسة المنشآت خدمات أمنية احترافية في الكويت منذ عام 2014 — حراسة المنشآت، وحماية الشخصيات والتدخّل السريع، وغرفة عمليات مركزية على مدار الساعة، ودوريات أمنية، وأنظمة أمنية."),
  "badge": ("Licensed Security Provider &mdash; Kuwait", "مزوّد خدمات أمنية مرخّص &mdash; الكويت"),
  "h1a": ("Professional Security", "خدمات أمنية"),
  "h1b": ("Services for Kuwait", "احترافية في الكويت"),
  "lead": ("AZSCO is committed to providing unparalleled security services that ensure the safety and peace of mind of our clients &mdash; delivered by highly trained, licensed and closely supervised security personnel.",
           "تلتزم أزسكو بتقديم خدمات أمنية لا تُضاهى تضمن سلامة عملائنا وراحة بالهم &mdash; عبر كوادر أمنية مدرّبة تدريباً عالياً ومرخّصة وتخضع لإشراف دقيق."),
  "points": [("Guarding Kuwait since 2014", "نحرس الكويت منذ عام 2014"),
             ("Licensed &amp; vetted personnel", "كوادر مرخّصة ومدقّقة أمنياً"),
             ("24/7 supervision &amp; response", "إشراف واستجابة على مدار الساعة")],
  "card_h": ("What We Guard", "ما الذي نحرسه"),
  "card_p": ("Security officers for every kind of premises across Kuwait.",
             "أفراد أمن لجميع أنواع المنشآت في جميع أنحاء الكويت."),
  "card_items": [
    ("shield", ("Facility Guarding", "حراسة المنشآت"),
     ("Static officers for facilities of every kind.", "أفراد أمن ثابتون لمختلف أنواع المنشآت.")),
    ("target", ("VIP Protection &amp; Rapid Intervention", "حماية الشخصيات والتدخل السريع"),
     ("Qualified personal guards and rapid intervention.", "حراس شخصيون مؤهلون وتدخّل سريع.")),
    ("eye", ("Central Operations Room", "غرفة عمليات مركزية"),
     ("24/7 monitoring and immediate communication.", "مراقبة وتواصل فوري على مدار الساعة.")),
  ],
  "svc_eyebrow": ("Our Services", "خدماتنا"),
  "svc_h2": ("Our Security Services", "خدماتنا الأمنية"),
  "svc_lead": ("From manned guarding to mobile patrols and event security, every deployment is tailored to the specific requirements of each client.",
               "من الحراسة الأمنية إلى الدوريات المتنقلة وأمن الفعاليات، تُصمَّم كل خطة انتشار وفق متطلبات كل عميل على حدة."),
  "about_eyebrow": ("About AZSCO", "عن أزسكو"),
  "about_h2": ("A Leading Provider of Security Services in Kuwait", "مزوّد رائد للخدمات الأمنية في الكويت"),
  "about_lead": ("AZSCO Security Services Company was established in 2014 and is headquartered in Qibla, Kuwait. Our team of highly trained and experienced security professionals is equipped with the latest technology and equipment to ensure the safety of your property and assets.",
                 "تأسّست شركة أزسكو لخدمات حراسة المنشآت عام 2014 ويقع مقرّها في القبلة بالكويت. ويضمّ فريقنا كوادر أمنية مدرّبة وذات خبرة، مجهّزة بأحدث التقنيات والمعدات لضمان سلامة ممتلكاتك وأصولك."),
  "about_checks": [
    (("Customized solutions", "حلول مخصّصة"),
     ("We understand that every client has unique security needs, and tailor our solutions to the specific requirements of each site.",
      "ندرك أن لكل عميل احتياجات أمنية فريدة، ولذلك نصمّم حلولنا وفق متطلبات كل موقع.")),
    (("Cost-effective and efficient", "فعّالة من حيث التكلفة والكفاءة"),
     ("Our goal is to provide the highest level of security and peace of mind, while keeping our services efficient and affordable.",
      "هدفنا تقديم أعلى مستوى من الأمن وراحة البال، مع الحفاظ على كفاءة خدماتنا وتكلفتها المعقولة.")),
    (("Available around the clock", "متاحون على مدار الساعة"),
     ("Our team of dedicated professionals is available 24 hours a day, 7 days a week.",
      "فريقنا من المتخصصين المتفانين متاح على مدار 24 ساعة طوال أيام الأسبوع.")),
  ],
  "sec_eyebrow": ("Where We Guard", "أين نحرس"),
  "sec_h2": ("Sectors We Protect", "القطاعات التي نحميها"),
  "sec_lead": ("AZSCO is distinguished in offering security services such as security guards for apartments, malls, banks, stores and much more.",
               "تتميّز أزسكو بتقديم خدمات أمنية مثل حراس الأمن للشقق والمجمّعات التجارية والبنوك والمتاجر وغيرها الكثير."),
  "why_eyebrow": ("Why AZSCO", "لماذا أزسكو"),
  "why_h2": ("Why Clients Choose Us", "لماذا يختارنا العملاء"),
  "why_lead": ("A strong reputation for quality and reliability, built on people, technology and accountability.",
               "سمعة قوية في الجودة والموثوقية، مبنية على الكوادر والتقنية والمساءلة."),
  "why_tiles": [
    ("award", ("Proven Reputation", "سمعة راسخة"),
     ("A leading provider of security services in Kuwait, trusted for quality and reliability across commercial, industrial and residential sites.",
      "مزوّد رائد للخدمات الأمنية في الكويت، موثوق به في الجودة والموثوقية عبر المواقع التجارية والصناعية والسكنية.")),
    ("users", ("Trained Professionals", "كوادر مدرّبة"),
     ("Highly trained and experienced security personnel, screened, licensed and supervised to a consistent operating standard.",
      "كوادر أمنية مدرّبة وذات خبرة، مدقّقة أمنياً ومرخّصة وتخضع لإشراف وفق معيار تشغيلي ثابت.")),
    ("award2", ("Established 2014", "تأسّست عام 2014"),
     ("Guarding Kuwait for over {YEARS} years, with continuous growth that testifies to our commitment to excellence.",
      "نحرس الكويت منذ أكثر من {YEARS} عاماً، بنموّ متواصل يشهد على التزامنا بالتميّز.")),
    ("target", ("Tailored to You", "مصمّمة لك"),
     ("Every client has unique security needs. We design customized solutions around your risk profile, site and operating hours.",
      "لكل عميل احتياجات أمنية فريدة. نصمّم حلولاً مخصّصة وفق مستوى المخاطر لديك وموقعك وساعات عملك.")),
    ("wallet", ("Cost-Effective", "فعّالة من حيث التكلفة"),
     ("The highest level of security and peace of mind, delivered in a way that stays efficient and commercially sensible.",
      "أعلى مستوى من الأمن وراحة البال، مقدَّم بأسلوب يحافظ على الكفاءة والجدوى التجارية.")),
    ("headset", ("24/7 Availability", "متاحون على مدار الساعة"),
     ("Our dedicated professionals are available 24 hours a day, 7 days a week &mdash; for supervision, response and support.",
      "متخصصونا المتفانون متاحون على مدار 24 ساعة طوال أيام الأسبوع &mdash; للإشراف والاستجابة والدعم.")),
  ],
  "proc_eyebrow": ("How We Work", "كيف نعمل"),
  "proc_h2": ("Our Process", "آلية عملنا"),
  "proc_lead": ("A straightforward path from first conversation to a protected, maintained site.",
                "مسار واضح من أول حديث حتى موقع محمي ومُدار."),
  "steps": [
    (("Consultation", "الاستشارة"), ("We listen to your requirements, operating hours and concerns to understand what actually needs protecting.",
      "نستمع إلى متطلباتك وساعات عملك ومخاوفك لنفهم ما يحتاج فعلاً إلى الحماية.")),
    (("Site Survey", "معاينة الموقع"), ("Our specialists assess the premises, identify vulnerabilities and map patrol routes, access points and risk.",
      "يقيّم مختصّونا المنشأة ويحدّدون نقاط الضعف ويرسمون مسارات الدوريات ونقاط الدخول والمخاطر.")),
    (("Tailored Proposal", "عرض مخصّص"), ("You receive a clear deployment plan and quotation &mdash; posts, shifts and cover &mdash; scoped to your budget.",
      "تحصل على خطة انتشار وعرض سعر واضحين &mdash; النقاط والورديات والتغطية &mdash; ضمن ميزانيتك.")),
    (("Deploy &amp; Supervise", "الانتشار والإشراف"), ("Officers are briefed and deployed, then supervised and audited with 24/7 support behind them.",
      "يتم إحاطة الأفراد ونشرهم، ثم الإشراف عليهم وتدقيق عملهم بدعم متواصل على مدار الساعة.")),
  ],
  "part_eyebrow": ("Our Partners", "شركاؤنا"),
  "part_h2": ("Strategic Partnerships", "شراكات استراتيجية"),
  "part_lead": ("AZSCO has established strategic partnerships with leading industry players to enhance the range and quality of our security solutions.",
                "أقامت أزسكو شراكات استراتيجية مع كبرى الشركات في القطاع لتعزيز نطاق وجودة حلولنا الأمنية."),
  "part_btn": ("About Our Partnerships", "عن شراكاتنا"),
}

STATS = [
    ("founded", ("Established in Kuwait", "تأسّست في الكويت")),
    ("years",   ("Years of Experience", "عاماً من الخبرة")),
    ("247",     ("Monitoring &amp; Response", "المتابعة والاستجابة")),
    ("partners",("Technology Partners", "شركاء التقنية")),
]

# ============================================================ about
ABOUT = {
  "title": ("About Us | AZSCO Security Kuwait", "من نحن | أزسكو للأمن الكويت"),
  "desc": ("AZSCO Security Services Company was established in 2014 in Qibla, Kuwait, offering facility guarding, VIP protection and rapid intervention, a central operations room, and security patrols.",
           "تأسّست شركة أزسكو لخدمات حراسة المنشآت عام 2014 في القبلة بالكويت، وتقدّم حراسة المنشآت، وحماية الشخصيات والتدخّل السريع، وغرفة عمليات مركزية، ودوريات أمنية."),
  "banner_h": ("About AZSCO", "عن أزسكو"),
  "banner_p": ("A leading provider of security services in Kuwait, with a strong reputation for quality and reliability.",
               "مزوّد رائد للخدمات الأمنية في الكويت، بسمعة قوية في الجودة والموثوقية."),
  "crumb": ("About", "من نحن"),
  "story_eyebrow": ("Our Story", "قصّتنا"),
  "story_h2": ("Protecting Kuwait Since 2014", "نحمي الكويت منذ عام 2014"),
  "story": [
    ("AZSCO Security Services Company &mdash; formerly known as Almail Zone Security Services &mdash; was established in 2014 in Kuwait. AZSCO specialises in comprehensive security services including facility guarding, personal protection, security patrols, a central operations room and security systems, delivered by carefully selected, well-trained personnel.",
     "تأسّست شركة أزسكو لخدمات حراسة المنشآت &mdash; المعروفة سابقاً بـ&laquo;شركة الميل زون للخدمات الأمنية&raquo; &mdash; عام 2014 في الكويت. ركّزت أزسكو على توفير خدمات أمنية متكاملة تشمل حراسة المنشآت وحماية الشخصيات والدوريات الأمنية وغرفة عمليات مركزية وأنظمة أمنية، من خلال كوادر مدرّبة يتم اختيارهم بعناية."),
    ("AZSCO is committed to continuous development and embracing modern technologies, such as advanced security systems and specialised applications for managing sites and security personnel, aiming to deliver exceptional security services to its clients.",
     "أظهرت أزسكو التزاماً قوياً بالتطوير المستمر وتبنّي التقنيات الحديثة مثل الأنظمة الأمنية المتطوّرة وتطبيقات خاصة لإدارة المواقع وأفراد الأمن، وذلك لتقديم خدمات أمنية مميّزة إلى عملائها."),
    ("AZSCO is dedicated to forging long-term relationships with clients in both the public and private sectors, built on trust, collaboration, quality and development, with a focus on rapid response and efficient risk and threat management. Its continuous success and growth are a testament to its commitment to excellence and innovation in providing security and guarding services.",
     "تلتزم أزسكو ببناء علاقات طويلة الأمد مع عملائها في القطاعين العام والخاص، وتعتمد في ذلك على معايير الثقة والتعاون والجودة والتطوير، مع التركيز على الاستجابة السريعة والكفاءة في إدارة المخاطر والتهديدات الأمنية. يشهد نجاحها ونموّها المستمر على التزامها بالتميّز والابتكار في تقديم خدمات الحراسة والأمن لعملائها."),
  ],
  "badge": (("2014", "2014"), ("Established", "سنة التأسيس")),
  "mvv": [
    ("award", ("Objective", "الهدف"),
     ("To provide the highest levels of security and protection to our clients.",
      "توفير أعلى مستويات الأمان والحماية لعملائنا.")),
    ("eye", ("Vision", "الرؤية"),
     ("At AZSCO, we are committed to achieving the highest standards of quality and innovation. Our goal is to lead in providing security services and solutions in Kuwait and the region, building a Kuwaiti brand with global standards that extends its expertise internationally.",
      "نحن في أزسكو ملتزمون بتحقيق أعلى مستويات الجودة والابتكار، ونطمح لأن نكون في طليعة مقدّمي خدمات الحراسة والحلول الأمنية في الكويت والمنطقة. نهدف إلى بناء علامة تجارية كويتية بمعايير عالمية، تنقل خبراتها إلى العالمية.")),
    ("target", ("Mission", "الرسالة"),
     ("At AZSCO, we understand that our clients seek exceptional and effective security services that reflect their status. To achieve this, we focus on attracting and developing highly specialised and trained administrative, supervisory and security personnel, relying on the latest technologies and technological solutions.",
      "في أزسكو، ندرك أن عملاءنا يبحثون عن خدمات أمنية مميّزة وفعّالة تتناسب مع مكانتهم. لتحقيق هذا، نركّز على جذب وتطوير كوادر إدارية وإشرافية وأمنية ذوي تخصّص وتدريب عالٍ، ونعتمد في عملنا على أحدث التقنيات والحلول التكنولوجية.")),
  ],
  "values_eyebrow": ("Our Values", "قيمنا"),
  "values_h2": ("What We Stand On", "ما نقوم عليه"),
  "commit_eyebrow": ("What Sets Us Apart", "ما يميّزنا"),
  "commit_h2": ("Our Commitment", "التزامنا"),
  "commit_lead": ("Everything we do is measured against one standard: does it make our client safer?",
                  "كل ما نقوم به يُقاس بمعيار واحد: هل يجعل عميلنا أكثر أماناً؟"),
  "commit_tiles": [
    ("users", ("Highly Trained Personnel", "كوادر عالية التدريب"),
     ("Our security professionals are screened, licensed, trained and supervised &mdash; and equipped with what they need to do the job properly.",
      "كوادرنا الأمنية مدقّقة أمنياً ومرخّصة ومدرّبة وتخضع للإشراف &mdash; ومجهّزة بما تحتاجه لأداء العمل على أكمل وجه.")),
    ("route", ("Managed, Not Just Staffed", "إدارة لا مجرّد توفير أفراد"),
     ("Field supervisors, unannounced shift audits and documented reporting, so a contract is actively managed rather than simply filled.",
      "مشرفون ميدانيون وتدقيق مفاجئ للورديات وتقارير موثّقة، ليكون العقد مُداراً فعلياً لا مجرّد عقد مُنفَّذ.")),
    ("target", ("Customized Solutions", "حلول مخصّصة"),
     ("Every client has unique security needs. We survey, assess and plan deployments around your site rather than selling a fixed package.",
      "لكل عميل احتياجات أمنية فريدة. نعاين ونقيّم ونخطّط الانتشار وفق موقعك بدلاً من بيع باقة جاهزة.")),
    ("clock", ("Available 24/7", "متاحون على مدار الساعة"),
     ("Our team of dedicated professionals is available 24 hours a day, 7 days a week to provide the highest level of security and peace of mind.",
      "فريقنا من المتخصصين المتفانين متاح على مدار 24 ساعة طوال أيام الأسبوع لتقديم أعلى مستوى من الأمن وراحة البال.")),
  ],
  "ceo_eyebrow": ("A Word From Our Leadership", "كلمة من إدارتنا"),
  "ceo_h2": ("CEO&rsquo;s Message", "كلمة الرئيس التنفيذي"),
  "ceo": [
    ("Our commitment at AZSCO extends beyond just achieving success and profitability. We believe in the importance of maintaining our principles and values towards our employees, clients and community. Therefore, AZSCO&rsquo;s management prioritises the welfare, comfort and development of our security operations. Our employees are partners in success and a fundamental pillar in achieving it.",
     "التزامنا يتجاوز مجرّد تحقيق النجاح والربحية في شركة أزسكو. نحن نؤمن بأهمية الحفاظ على مبادئنا وقيمنا تجاه موظفينا وعملائنا والمجتمع، ولذا تعتبر إدارة شركة أزسكو رفاهية الموظفين وراحتهم وتطوير العمل الأمني أولوية. موظفو أزسكو شركاء في النجاح ولبنة أساسية في تحقيقه."),
    ("We continuously strive to provide a humane working environment that meets their basic needs without focusing on costs. Despite the high costs, we are committed to continuous development and adopting modern technologies, as they enhance work efficiency and quality. These technologies contribute to providing distinguished security services that protect the community and properties from risks, thereby building strong and sustainable relationships with our clients.",
     "نسعى دائماً لتوفير بيئة عمل إنسانية تلبّي احتياجاتهم الأساسية دون التركيز على التكلفة. كما نعمل على التطوير المستمر وتبنّي التقنيات الحديثة رغم تكلفتها العالية، إلا أنها تعزّز كفاءة وجودة العمل وتسهم في تقديم خدمات أمنية متميّزة لحماية المجتمع والممتلكات من المخاطر، وبالتالي بناء علاقات قوية ومستدامة مع عملائنا."),
  ],
  "ceo_line": ("(Our Employees &mdash; Our Clients)", "(موظفونا &mdash; عملاؤنا)"),
  "ceo_thanks": ("Thank you for your trust in us; with you, we rise.",
                 "شكراً لكم على ثقتكم بنا، بكم نرتقي."),
  "ceo_by": ("Dr. Abdulaziz Almail &mdash; Chief Executive Officer", "د. عبدالعزيز الميل &mdash; الرئيس التنفيذي"),
  "clients_eyebrow": ("Our Clients", "عملاؤنا"),
  "clients_h2": ("Trusted Across Kuwait", "موثوقون في جميع أنحاء الكويت"),
  "clients_lead": ("AZSCO is committed to building long-term relationships with its clients in both the public and private sectors.",
                   "تلتزم أزسكو ببناء علاقات طويلة الأمد مع عملائها في القطاعين العام والخاص."),
  "clients_btn": ("View All Clients", "عرض جميع العملاء"),
  "nat_eyebrow": ("Our People", "كوادرنا"),
  "nat_h2": ("Available Nationalities", "الجنسيات المتوفرة"),
  "nat_lead": ("AZSCO fields security guards from a range of nationalities. A diverse workforce brings cultural range, varied skills and multiple languages, along with a healthy, positive spirit of competition.",
               "توفّر أزسكو حرّاس أمن من جنسيات متعدّدة. يمنح تنوّع الكوادر تنوّعاً ثقافياً ومهارات متعدّدة وتعدّد لغات، إلى جانب خلق روح تنافس إيجابية."),
  "train_eyebrow": ("Preparedness", "الجاهزية"),
  "train_h2": ("Training Courses", "الدورات التدريبية"),
  "train_lead": ("Every AZSCO guard is trained across a range of courses designed to prepare them for a wide range of security and emergency situations, raising their efficiency and professionalism.",
                 "يخضع كل حارس في أزسكو لدورات تدريبية متنوّعة تُعدّه لمواجهة مجموعة واسعة من المواقف الأمنية والطارئة، ما يرفع كفاءته واحترافيته."),
  "equip_eyebrow": ("Equipped for the Job", "مجهّزون للمهمة"),
  "equip_h2": ("Security Equipment", "المعدات الأمنية"),
  "equip_lead": ("Security guards need the right equipment on hand to perform their duties effectively and safely.",
                 "يحتاج حرّاس الأمن إلى مجموعة من المعدات الأمنية لأداء واجباتهم بفعالية وأمان."),
  "uniform_eyebrow": ("On Site", "في الميدان"),
  "uniform_h2": ("Uniform Models", "نماذج الزي الرسمي"),
  "uniform_lead": ("Uniforms designed with safety, comfort and a professional appearance in mind, reflecting our commitment to exceptional security services.",
                   "أزياء صُمّمت لتراعي معايير الأمان والراحة والمظهر المهني، وتعكس التزامنا بتقديم خدمات أمنية متميّزة."),
  "cert_eyebrow": ("Independently Verified", "معتمدة رسمياً"),
  "cert_h2": ("Certifications", "الشهادات"),
  "faq_eyebrow": ("Questions", "أسئلة"),
  "faq_h2": ("Frequently Asked", "الأسئلة الشائعة"),
  "faq": [
    (("What areas does AZSCO cover?", "ما المناطق التي تغطيها أزسكو؟"),
     ("AZSCO provides security manpower across Kuwait, from our office at {ADDR}. Call {PHONE} to discuss coverage for your site.",
      "توفّر أزسكو كوادر أمنية في جميع أنحاء الكويت، انطلاقاً من مكتبنا في {ADDR}. اتصل على {PHONE} لمناقشة تغطية موقعك.")),
    (("What kinds of premises do you guard?", "ما أنواع المنشآت التي تحرسونها؟"),
     ("AZSCO is distinguished in offering security services such as security guards for apartments, malls, banks, stores and much more, along with offices, compounds, industrial sites and events. Every deployment is planned around the specific requirements of the client.",
      "تتميّز أزسكو بتقديم خدمات أمنية مثل حراس الأمن للشقق والمجمّعات التجارية والبنوك والمتاجر وغيرها الكثير، إضافة إلى المكاتب والمجمّعات والمواقع الصناعية والفعاليات. وتُخطَّط كل عملية انتشار وفق متطلبات العميل تحديداً.")),
    (("How quickly can officers be deployed?", "ما السرعة التي يمكن بها نشر الأفراد؟"),
     ("Timelines depend on the number of posts, the shift pattern and any vetting the site requires. After a free site survey we issue a proposal with a clear deployment schedule, the officers assigned and the supervision arrangements that come with them.",
      "تعتمد المدة على عدد النقاط ونمط الورديات وأي تدقيق أمني يتطلبه الموقع. وبعد معاينة مجانية للموقع نصدر عرضاً يتضمّن جدولاً واضحاً للانتشار والأفراد المكلّفين وترتيبات الإشراف المرافقة لهم.")),
    (("Is support available outside working hours?", "هل الدعم متاح خارج ساعات العمل؟"),
     ("Our office hours are Sunday to Thursday, 8:30 AM to 4:30 PM, but our team of dedicated professionals is available 24 hours a day, 7 days a week for supervision, emergency response and escalations.",
      "ساعات عمل مكتبنا من الأحد إلى الخميس، من 8:30 صباحاً إلى 4:30 مساءً، لكن فريقنا من المتخصصين متاح على مدار 24 ساعة طوال أيام الأسبوع للإشراف والاستجابة للطوارئ والحالات العاجلة.")),
  ],
}

# ============================================================ services page
SERVICES_PAGE = {
  "title": ("Security Services in Kuwait | AZSCO Security",
            "خدمات أمنية في الكويت | أزسكو للأمن"),
  "desc": ("AZSCO security services in Kuwait: facility guarding, VIP protection and rapid intervention, a central operations room, security patrols, and security systems.",
           "خدمات أزسكو الأمنية في الكويت: حراسة المنشآت، وحماية الشخصيات والتدخل السريع، وغرفة عمليات مركزية، ودوريات أمنية، وأنظمة أمنية."),
  "banner_h": ("Our Services", "خدماتنا"),
  "banner_p": ("A comprehensive range of security services — manpower, a central operations room and monitored security systems — tailored to each client.",
               "مجموعة شاملة من الخدمات الأمنية — كوادر أمنية، وغرفة عمليات مركزية، وأنظمة أمنية مراقَبة — مصمّمة لكل عميل."),
  "crumb": ("Services", "خدماتنا"),
  "over_eyebrow": ("Overview", "نظرة عامة"),
  "over_h2": ("What AZSCO Delivers", "ما تقدّمه أزسكو"),
  "over_lead": ("Every post, patrol and detail is planned around your premises, your operating hours and your risk &mdash; never a fixed package.",
                "تُخطَّط كل نقطة حراسة ودورية ومهمة وفق منشأتك وساعات عملك ومستوى المخاطر لديك &mdash; وليس وفق باقة جاهزة."),
  "service_label": ("Service", "الخدمة"),
  "people_eyebrow": ("Our People", "كوادرنا"),
  "people_h2": ("Trained, Vetted, Supervised", "مدرّبون، مدقّقون، تحت الإشراف"),
  "people_lead": ("The strength of a manned security contract is the standard behind every shift.",
                  "قوة عقد الحراسة الأمنية تكمن في المعيار الذي يقف خلف كل وردية."),
  "people_tiles": [
    ("shield-check", ("Screened &amp; Licensed", "مدقّقون ومرخّصون"),
     ("Every officer is background checked and licensed before deployment, and briefed on site-specific post orders.",
      "يخضع كل فرد للتدقيق الأمني والترخيص قبل نشره، ويُحاط بتعليمات الموقع الخاصة.")),
    ("award", ("Continuously Trained", "تدريب مستمر"),
     ("Ongoing training in entry control, emergency procedures, fire response, customer service and incident reporting.",
      "تدريب متواصل على ضبط الدخول وإجراءات الطوارئ والاستجابة للحرائق وخدمة العملاء وكتابة تقارير الحوادث.")),
    ("headset", ("Actively Supervised", "إشراف فعّال"),
     ("Field supervisors, shift audits and an operations team reachable 24 hours a day, 7 days a week.",
      "مشرفون ميدانيون وتدقيق للورديات وفريق عمليات يمكن الوصول إليه على مدار 24 ساعة طوال أيام الأسبوع.")),
  ],
  "cta": (("Not sure which service you need?", "لست متأكداً من الخدمة التي تحتاجها؟"),
          ("Book a free site survey. We will assess your premises and recommend the right deployment of officers, patrols and supervision.",
           "احجز معاينة مجانية للموقع. سنقيّم منشأتك ونوصي بالانتشار المناسب من الأفراد والدوريات والإشراف.")),
}

# ============================================================ clients page
# The 19 client logos legible in the official company profile's "Our
# Clients" panel (assets/img/photos/clients-logos.jpg), listed here as text
# for accessibility and for anyone who wants the names without reading the
# image. A handful of marks in that panel carry no readable name and are
# intentionally left out of this list -- the image itself is the complete,
# authoritative record.
CLIENTS = [
    ("Radisson Blu Hotel Kuwait", "فندق راديسون بلو الكويت"),
    ("Ream — Trusted Partners", "ريم - شركاء موثوقون"),
    ("Alnasser", "النصر"),
    ("Massaleh Real Estate", "المصالح العقارية"),
    ("Wataniya Resort", "منتجع الوطنية"),
    ("Al-Ahleia Switchgear Co. K.S.C.C.", "شركة الأهلية للوحات الكهربائية"),
    ("Ewan Complex", "مجمع إيوان"),
    ("NBTC", "NBTC"),
    ("Awtad", "أوتاد"),
    ("National Contracting Co. Ltd. (NCC)", "الشركة الوطنية للمقاولات المحدودة"),
    ("National Investments Company", "الشركة الوطنية للاستثمارات"),
    ("Millennium Hotels and Resorts", "فنادق ومنتجعات ميلينيوم"),
    ("Sahara Kuwait", "صحارى الكويت"),
    ("Alghanim Industries", "صناعات الغانم"),
    ("Wafra Real Estate", "وفرة العقارية"),
    ("Kuwait Ports Authority", "مؤسسة الموانئ الكويتية"),
    ("SHBC", "SHBC"),
    ("Ministry of Electricity &amp; Water", "وزارة الكهرباء والماء"),
    ("The Regency", "الريجنسي"),
]

CLIENTS_PAGE = {
  "title": ("Our Clients | AZSCO Security Kuwait", "عملاؤنا | أزسكو للأمن الكويت"),
  "desc": ("AZSCO is trusted by hotels, real estate developers, government bodies and industrial groups across Kuwait, including Radisson Blu Hotel Kuwait, Millennium Hotels and Resorts and Kuwait Ports Authority.",
           "تحظى أزسكو بثقة الفنادق والمطوّرين العقاريين والجهات الحكومية والمجموعات الصناعية في جميع أنحاء الكويت، ومنها فندق راديسون بلو الكويت وفنادق ومنتجعات ميلينيوم ومؤسسة الموانئ الكويتية."),
  "banner_h": ("Our Clients", "عملاؤنا"),
  "banner_p": ("Long-term relationships with clients across Kuwait's public and private sectors.",
               "علاقات طويلة الأمد مع عملائنا في القطاعين العام والخاص في الكويت."),
  "crumb": ("Clients", "عملاؤنا"),
  "eyebrow": ("Trusted Across Kuwait", "موثوقون في جميع أنحاء الكويت"),
  "h2": ("Organisations That Rely on AZSCO", "جهات تثق بأزسكو"),
  "lead": ("AZSCO is dedicated to forging long-term relationships with clients in both public and private sectors, built on trust, collaboration, quality and development.",
           "تلتزم أزسكو ببناء علاقات طويلة الأمد مع عملائها في القطاعين العام والخاص، ترتكز على الثقة والتعاون والجودة والتطوير."),
  "list_eyebrow": ("The List", "القائمة"),
  "list_h2": ("Some of the Organisations We Protect", "بعض الجهات التي نحرسها"),
  "cta": (("Don't see your sector listed?", "لا ترى قطاعك ضمن القائمة؟"),
          ("AZSCO protects premises across government, commercial, financial, industrial, residential and many other sectors. Talk to us about yours.",
           "تحرس أزسكو منشآت في القطاعات الحكومية والتجارية والمالية والصناعية والسكنية وقطاعات أخرى عديدة. تحدّث معنا عن قطاعك.")),
}

# ============================================================ partners page
PARTNERS_PAGE = {
  "title": ("Our Partners | AZSCO Security Kuwait", "شركاؤنا | أزسكو للأمن الكويت"),
  "desc": ("AZSCO has established strategic partnerships with leading industry players to enhance the range and quality of our security solutions in Kuwait.",
           "أقامت أزسكو شراكات استراتيجية مع كبرى الشركات في القطاع لتعزيز نطاق وجودة حلولنا الأمنية في الكويت."),
  "banner_h": ("Our Partners", "شركاؤنا"),
  "banner_p": ("AZSCO has established strategic partnerships with leading industry players to enhance the range and quality of our security solutions.",
               "أقامت أزسكو شراكات استراتيجية مع كبرى الشركات في القطاع لتعزيز نطاق وجودة حلولنا الأمنية."),
  "crumb": ("Partners", "شركاؤنا"),
  "eyebrow": ("Strategic Partnerships", "شراكات استراتيجية"),
  "h2": ("Backed by the Industry&rsquo;s Best", "بدعم من الأفضل في القطاع"),
  "lead": ("AZSCO has partnerships with many global technology brands, whose cameras, alarms and monitoring equipment power our Security Systems service and support every site our officers protect.",
           "لدى أزسكو شراكات مع العديد من العلامات التجارية التقنية العالمية، حيث تدعم كاميراتها وأنظمة إنذارها ومعدات المراقبة الخاصة بها خدمة الأنظمة الأمنية لدينا وكل موقع يحميه أفرادنا."),
  "why_eyebrow": ("Why It Matters", "لماذا يهمّ ذلك"),
  "why_h2": ("What Our Partnerships Give You", "ما الذي تمنحك إياه شراكاتنا"),
  "tiles": [
    ("award", ("Established Brands", "علامات تجارية راسخة"),
     ("We work with recognised global manufacturers, so the products specified on a project are supported and available for years.",
      "نتعامل مع مصنّعين عالميين معروفين، لتبقى المنتجات المعتمدة في المشروع مدعومة ومتوفّرة لسنوات.")),
    ("target", ("The Right Fit", "الخيار الأنسب"),
     ("Partnerships give us options, so each project gets the product that suits the site rather than the one we happen to stock.",
      "توفّر لنا الشراكات خيارات متعددة، ليحصل كل مشروع على المنتج الذي يناسب الموقع لا المنتج المتوفّر لدينا صدفة.")),
    ("users", ("Backing Our Officers", "دعم لأفرادنا"),
     ("Reliable equipment on site supports the officers guarding it, from the entry system at the door to the cameras they watch.",
      "المعدات الموثوقة في الموقع تدعم الأفراد الذين يحرسونه، من نظام الدخول عند الباب إلى الكاميرات التي يتابعونها.")),
  ],
  "join_eyebrow": ("Work With Us", "اعمل معنا"),
  "join_h2": ("Become an AZSCO Partner", "كن شريكاً لأزسكو"),
  "join_lead": ("We are always interested in working with manufacturers, distributors, consultants and contractors who share our standard of delivery.",
                "يسعدنا دائماً التعاون مع المصنّعين والموزّعين والاستشاريين والمقاولين الذين يشاركوننا معايير التنفيذ."),
  "join_p": ("If your products or services would strengthen what we offer clients in Kuwait, we would like to hear from you. Send an outline of your proposal to {EMAIL} or call {PHONE}.",
             "إذا كانت منتجاتك أو خدماتك تعزّز ما نقدّمه لعملائنا في الكويت، يسرّنا أن نسمع منك. أرسل ملخّصاً لعرضك إلى {EMAIL} أو اتصل على {PHONE}."),
  "join_btn": ("Start a Conversation", "ابدأ الحوار"),
}

# ============================================================ contact page
CONTACT = {
  "title": ("Contact AZSCO Security | Kuwait", "اتصل بأزسكو للأمن | الكويت"),
  "desc": ("Contact AZSCO Security in Kuwait. Office: Floor 27B, Kuwait Building Tower, Fahad Al Salem St., Qibla, Kuwait. Tel (+965) 1808606. Email info@azsco.com. Request a free site survey.",
           "تواصل مع أزسكو للأمن في الكويت. المكتب: الدور 27B، برج مبنى الكويت، شارع فهد السالم، القبلة، الكويت. هاتف (+965) 1808606. بريد إلكتروني info@azsco.com. اطلب معاينة مجانية للموقع."),
  "banner_h": ("Contact Us", "اتصل بنا"),
  "banner_p": ("Talk to AZSCO about guarding or a free site survey. Our team is available 24 hours a day, 7 days a week.",
               "تحدّث مع أزسكو حول خدمات الحراسة أو معاينة مجانية للموقع. فريقنا متاح على مدار 24 ساعة طوال أيام الأسبوع."),
  "crumb": ("Contact", "اتصل بنا"),
  "cards": [
    ("pin",  ("Visit Our Office", "زُر مكتبنا"), None),
    ("phone",("Call Us", "اتصل بنا"), ("24/7 emergency response", "استجابة للطوارئ على مدار الساعة")),
    ("mail", ("Email Us", "راسلنا"), None),
  ],
  "form_eyebrow": ("Get In Touch", "تواصل معنا"),
  "form_h2": ("Request a Free Site Survey", "اطلب معاينة مجانية للموقع"),
  "form_lead": ("Tell us a little about your premises and what you need protected. One of our security consultants will contact you to arrange a survey and prepare a tailored proposal.",
                "أخبرنا قليلاً عن منشأتك وما تحتاج إلى حمايته. سيتواصل معك أحد مستشارينا الأمنيين لترتيب المعاينة وإعداد عرض مخصّص."),
  "fields": {
    "name":    ("Full Name", "الاسم الكامل"),
    "name_ph": ("Your name", "اسمك"),
    "company": ("Company", "الشركة"),
    "company_ph": ("Company name", "اسم الشركة"),
    "email":   ("Email", "البريد الإلكتروني"),
    "phone":   ("Phone", "الهاتف"),
    "service": ("Inquiry Type", "نوع الاستفسار"),
    "select":  ("Please select&hellip;", "اختر&hellip;"),
    "message": ("How Can We Help?", "كيف يمكننا مساعدتك؟"),
    "message_ph": ("Tell us about your site, the number of officers or posts you need, operating hours, and what you need protected.",
                   "أخبرنا عن موقعك، وعدد الأفراد أو النقاط التي تحتاجها، وساعات العمل، وما تريد حمايته."),
    "submit":  ("Send Enquiry", "إرسال الطلب"),
    "note":    ("By submitting this form you agree to our {PRIVACY}. For urgent matters please call {PHONE}.",
                "بإرسال هذا النموذج فإنك توافق على {PRIVACY}. وللأمور العاجلة يُرجى الاتصال على {PHONE}."),
    "req":     ("This field is required.", "هذا الحقل مطلوب."),
    "bad_email": ("Please enter a valid email address.", "يُرجى إدخال بريد إلكتروني صحيح."),
    "bad_phone": ("Please enter a valid phone number.", "يُرجى إدخال رقم هاتف صحيح."),
    "choose":  ("Please choose an inquiry type.", "يُرجى اختيار نوع الاستفسار."),
  },
  "options": [
    ("general", ("General Inquiry", "استفسار عام")),
    ("service", ("Inquiry About a Service", "استفسار عن خدمة")),
  ],
  "quote_prefill": ("I would like a quote for: {SERVICE}. ",
                     "أرغب في الحصول على عرض سعر لـ: {SERVICE}. "),
  "office_hours": ("Office hours", "ساعات العمل"),
  "emergency": ("Emergency response", "الاستجابة للطوارئ"),
  "emergency_v": ("Available 24 hours a day, 7 days a week", "متاحة على مدار 24 ساعة طوال أيام الأسبوع"),
  "cta": (("Prefer to speak to someone now?", "تفضّل التحدّث مع أحدهم الآن؟"),
          ("Our team is available 24 hours a day, 7 days a week for urgent security matters.",
           "فريقنا متاح على مدار 24 ساعة طوال أيام الأسبوع للأمور الأمنية العاجلة.")),
  "sent": ("Thank you for contacting AZSCO. Your enquiry has been sent — a member of our team will respond shortly. For urgent matters call (+965) 1808606.",
           "شكراً لتواصلك مع أزسكو. تم إرسال طلبك وسيتواصل معك أحد أعضاء فريقنا قريباً. وللأمور العاجلة اتصل على (+965) 1808606."),
  "sending": ("Sending your enquiry&hellip;", "جارٍ إرسال طلبك&hellip;"),
  "send_failed": ("Sorry, your enquiry could not be sent just now. Please call (+965) 1808606 or email sales@azsco.com and we will pick it up straight away.",
                  "عذراً، تعذّر إرسال طلبك في الوقت الحالي. يُرجى الاتصال على (+965) 1808606 أو مراسلتنا على sales@azsco.com وسنتابع طلبك فوراً."),
  "honeypot": ("Leave this field empty", "اترك هذا الحقل فارغاً"),
}

# ============================================================ 404
NOTFOUND = {
  "title": ("Page Not Found | AZSCO Security", "الصفحة غير موجودة | أزسكو للأمن"),
  "desc": ("The page you requested could not be found on the AZSCO Security website.",
           "الصفحة التي طلبتها غير موجودة على موقع أزسكو للأمن."),
  "eyebrow": ("Error 404", "خطأ 404"),
  "h1": ("Page Not Found", "الصفحة غير موجودة"),
  "lead": ("The page you are looking for may have been moved or no longer exists. Let us get you back to safety.",
           "ربما تم نقل الصفحة التي تبحث عنها أو لم تعد موجودة. دعنا نعيدك إلى برّ الأمان."),
  "back": ("Back to Home", "العودة إلى الرئيسية"),
  "contact": ("Contact Us", "اتصل بنا"),
}

# ============================================================ privacy policy
PRIVACY = {
  "title": ("Privacy Policy | AZSCO Security", "سياسة الخصوصية | أزسكو للأمن"),
  "desc": ("AZSCO Security privacy policy — how we collect, use, share and protect the personal information you provide through our website and services.",
           "سياسة الخصوصية لدى أزسكو للأمن — كيف نجمع المعلومات الشخصية التي تقدّمها عبر موقعنا وخدماتنا ونستخدمها ونشاركها ونحميها."),
  "banner_h": ("Privacy Policy", "سياسة الخصوصية"),
  "banner_p": ("How AZSCO collects, uses and protects the personal information you share with us.",
               "كيف تجمع أزسكو المعلومات الشخصية التي تشاركها معنا وتستخدمها وتحميها."),
  "crumb": ("Privacy Policy", "سياسة الخصوصية"),
  "updated": ("Last updated: January 2026", "آخر تحديث: يناير 2026"),
  "intro": ("{COMPANY} (&ldquo;AZSCO&rdquo;, &ldquo;we&rdquo;, &ldquo;us&rdquo;) respects your privacy. This policy explains what personal information we collect through this website and our services, how we use it, and the choices available to you.",
            "تحترم {COMPANY} (&laquo;أزسكو&raquo;، &laquo;نحن&raquo;) خصوصيتك. توضّح هذه السياسة المعلومات الشخصية التي نجمعها عبر هذا الموقع وخدماتنا، وكيفية استخدامنا لها، والخيارات المتاحة أمامك."),
  "sections": [
    (("Information We Collect", "المعلومات التي نجمعها"),
     [("p", ("We collect information that you provide directly to us, and a limited amount of technical information collected automatically when you visit this website.",
             "نجمع المعلومات التي تقدّمها لنا مباشرة، وقدراً محدوداً من المعلومات التقنية التي تُجمع تلقائياً عند زيارتك لهذا الموقع.")),
      ("ul", [("<b>Information you provide:</b> your name, company, email address, telephone number, the service you are enquiring about, and any details you include in an enquiry or quotation request.",
               "<b>المعلومات التي تقدّمها:</b> اسمك، والشركة، والبريد الإلكتروني، ورقم الهاتف، والخدمة التي تستفسر عنها، وأي تفاصيل تدرجها في الاستفسار أو طلب عرض السعر."),
              ("<b>Technical information:</b> browser type, device type, approximate location, referring page and pages viewed, collected through server logs and cookies.",
               "<b>المعلومات التقنية:</b> نوع المتصفح، ونوع الجهاز، والموقع التقريبي، والصفحة المُحيلة والصفحات التي تمت زيارتها، وتُجمع عبر سجلات الخادم وملفات تعريف الارتباط."),
              ("<b>Service information:</b> where you become a client, records relating to site surveys, deployments, shift rosters, patrol visits and incident reports.",
               "<b>معلومات الخدمة:</b> عندما تصبح عميلاً، السجلات المتعلقة بمعاينات المواقع وخطط الانتشار وجداول الورديات وزيارات الدوريات وتقارير الحوادث.")])]),
    (("How We Use Your Information", "كيف نستخدم معلوماتك"),
     [("ul", [("To respond to your enquiry and prepare quotations or proposals.", "للردّ على استفسارك وإعداد عروض الأسعار أو المقترحات."),
              ("To arrange and carry out site surveys, deployments, patrols and supervision.", "لترتيب وتنفيذ معاينات المواقع وخطط الانتشار والدوريات والإشراف."),
              ("To provide customer support and manage our contractual relationship with you.", "لتقديم دعم العملاء وإدارة علاقتنا التعاقدية معك."),
              ("To improve this website, our services and our communications.", "لتحسين هذا الموقع وخدماتنا وتواصلنا."),
              ("To comply with legal, regulatory and licensing obligations in the State of Kuwait.", "للامتثال للالتزامات القانونية والتنظيمية والترخيصية في دولة الكويت.")])]),
    (("Cookies", "ملفات تعريف الارتباط"),
     [("p", ("This website does not use advertising or tracking cookies. The AZSCO Assistant chat widget stores your conversation in your own browser (session storage) so it survives moving between pages; it is cleared when you close the tab and is never sent anywhere except to answer your questions. Where we measure visitor numbers, we use a privacy-friendly analytics service that sets no cookies and does not identify individual visitors. You can clear this storage at any time through your browser settings.",
             "لا يستخدم هذا الموقع ملفات تعريف ارتباط للإعلانات أو التتبّع. يحتفظ مساعد أزسكو بمحادثتك داخل متصفحك أنت (تخزين الجلسة) لتبقى متاحة أثناء تنقّلك بين الصفحات، وتُمسح عند إغلاق التبويب ولا تُرسل إلى أي جهة إلا للردّ على أسئلتك. وعند قياس أعداد الزوار نستخدم خدمة تحليلات تحترم الخصوصية لا تضع ملفات تعريف ارتباط ولا تحدّد هوية الزوار. ويمكنك مسح هذا التخزين في أي وقت من إعدادات متصفحك."))]),
    (("Sharing Your Information", "مشاركة معلوماتك"),
     [("p", ("We do not sell your personal information. We may share it with:", "نحن لا نبيع معلوماتك الشخصية. وقد نشاركها مع:")),
      ("ul", [("Service providers who support our operations, such as hosting and IT providers, under confidentiality obligations.",
               "مزوّدي الخدمات الذين يدعمون عملياتنا، مثل مزوّدي الاستضافة وتقنية المعلومات، بموجب التزامات السرية."),
              ("Technology partners and manufacturers where necessary to fulfil warranty or support obligations on products supplied for a project.",
               "شركاء التقنية والمصنّعين عند الضرورة للوفاء بالتزامات الضمان أو الدعم للمنتجات المورَّدة لمشروع ما."),
              ("Competent authorities where disclosure is required by law or to protect life and property.",
               "الجهات المختصة عندما يكون الإفصاح مطلوباً بموجب القانون أو لحماية الأرواح والممتلكات.")])]),
    (("Data Security", "أمن البيانات"),
     [("p", ("We apply appropriate technical and organisational measures to protect personal information against unauthorised access, loss or misuse. No method of transmission or storage is completely secure, but we work to protect your information and to review our safeguards regularly.",
             "نطبّق تدابير تقنية وتنظيمية مناسبة لحماية المعلومات الشخصية من الوصول غير المصرّح به أو الفقدان أو سوء الاستخدام. ولا توجد وسيلة نقل أو تخزين آمنة تماماً، لكننا نعمل على حماية معلوماتك ومراجعة إجراءاتنا الوقائية بانتظام."))]),
    (("Data Retention", "الاحتفاظ بالبيانات"),
     [("p", ("We keep personal information only for as long as necessary for the purposes described in this policy, or for as long as required by applicable law, contract or licensing requirements.",
             "نحتفظ بالمعلومات الشخصية للمدة اللازمة للأغراض الموضّحة في هذه السياسة فقط، أو للمدة التي يقتضيها القانون المعمول به أو العقد أو متطلبات الترخيص."))]),
    (("Your Rights", "حقوقك"),
     [("p", ("You may request access to the personal information we hold about you, ask us to correct inaccurate information, or ask us to delete information where we are not required to retain it. To make a request, contact us using the details below.",
             "يمكنك طلب الاطّلاع على المعلومات الشخصية التي نحتفظ بها عنك، أو مطالبتنا بتصحيح المعلومات غير الدقيقة، أو حذف المعلومات التي لا يُلزمنا القانون بالاحتفاظ بها. ولتقديم طلب، تواصل معنا عبر البيانات أدناه."))]),
    (("Client Premises and Monitoring", "منشآت العملاء والمراقبة"),
     [("p", ("Where AZSCO officers work at a client&rsquo;s premises, any CCTV or entry system at that site remains the client&rsquo;s own, and the client is responsible for how it is used. AZSCO processes such data only as instructed by the client and as permitted by applicable law.",
             "عندما يعمل أفراد أزسكو في منشأة أحد العملاء، تبقى أي كاميرات مراقبة أو أنظمة دخول في ذلك الموقع ملكاً للعميل، ويتحمّل العميل مسؤولية كيفية استخدامها. ولا تعالج أزسكو هذه البيانات إلا وفق تعليمات العميل وبما يسمح به القانون المعمول به."))]),
    (("Third-Party Links", "روابط الجهات الخارجية"),
     [("p", ("This website may link to third-party sites. We are not responsible for the privacy practices or content of those sites, and we encourage you to read their privacy policies.",
             "قد يتضمّن هذا الموقع روابط لمواقع تابعة لجهات خارجية. ولسنا مسؤولين عن ممارسات الخصوصية أو المحتوى في تلك المواقع، وننصحك بقراءة سياسات الخصوصية الخاصة بها."))]),
    (("Changes to This Policy", "التعديلات على هذه السياسة"),
     [("p", ("We may update this policy from time to time. The revised version will be posted on this page with an updated date.",
             "قد نحدّث هذه السياسة من وقت لآخر. وستُنشر النسخة المعدّلة على هذه الصفحة مع تاريخ التحديث."))]),
  ],
  "contact_h": ("Contact Us", "اتصل بنا"),
  "contact_p": ("If you have questions about this Privacy Policy or how we handle your information, please contact us:",
                "إذا كانت لديك أسئلة حول سياسة الخصوصية هذه أو كيفية تعاملنا مع معلوماتك، يُرجى التواصل معنا:"),
  "tel_label": ("Telephone:", "الهاتف:"),
  "email_label": ("Email:", "البريد الإلكتروني:"),
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

# ============================================================ shared blocks
def service_cards(lang):
    return "\n".join(
        f'''      <article class="card reveal" data-delay="{n*80}">
        <span class="ico">{I[s["icon"]]}</span>
        <h3>{t(s["name"], lang)}</h3>
        <p>{t(s["card"], lang)}</p>
        <a class="more" href="{link(lang, "services.html#" + s["anchor"])}">{t(UI["learn"], lang)} {I["arrow"]}</a>
      </article>''' for n, s in enumerate(SERVICES))

def chip_list(lang, items):
    """A wrapping row of pill chips for a plain enumeration -- sectors,
    values, nationalities, equipment -- where a dozen-plus items would make
    an icon-tile grid noisy. `items` is a list of (en, ar) pairs."""
    return "\n".join(
        f'      <span class="chip reveal" data-delay="{min(i*30, 300)}">{t(item, lang)}</span>'
        for i, item in enumerate(items))

def logo_panel(src, alt_pair, lang, cls=""):
    """A white bordered panel holding a supplied logo-wall image (partners or
    clients), so it reads as a deliberate panel on any section background
    rather than a stray white rectangle."""
    return (f'<div class="logo-panel{(" " + cls) if cls else ""} reveal">'
            f'<img src="/{src}" alt="{t(alt_pair, lang)}" loading="lazy"></div>')

def tiles(lang, items, cols=3):
    return "\n".join(
        f'      <div class="tile reveal" data-delay="{(i%cols)*80}"><span class="ico">'
        f'{I["award"] if icon == "award2" else I[icon]}</span><div><h4>{t(title, lang)}</h4>'
        f'<p>{t(text, lang).replace("{YEARS}", str(YEARS))}</p></div></div>'
        for i, (icon, title, text) in enumerate(items))

# ============================================================ pages
def build_home(lang):
    H = HOME
    cards = "\n".join(
        f'          <li><span class="ico">{I[icon]}</span><span><b>{t(title, lang)}</b>'
        f'<span>{t(desc, lang)}</span></span></li>' for icon, title, desc in H["card_items"])
    points = "\n".join(f'          <li>{I["check"]} {t(p, lang)}</li>' for p in H["points"])
    checks = "\n".join(
        f'          <li><span class="ico">{I["check"]}</span><span><b>{t(a, lang)}</b>'
        f'<span>{t(b, lang)}</span></span></li>' for a, b in H["about_checks"])
    steps = "\n".join(
        f'      <div class="step reveal" data-delay="{i*80}"><span class="n">{i+1:02d}</span>'
        f'<h4>{t(a, lang)}</h4><p>{t(b, lang)}</p></div>'
        for i, (a, b) in enumerate(H["steps"]))

    body = f'''
<section class="hero">
  <div class="wrap">
    <div class="hero-grid">
      <div>
        <span class="hero-badge">{I["shield-check"]} {t(H["badge"], lang)}</span>
        <h1>{t(H["h1a"], lang)}<em>{t(H["h1b"], lang)}</em></h1>
        <p class="lead">{t(H["lead"], lang)}</p>
        <div class="btn-row">
          <a class="btn btn-primary" href="{link(lang, "contact.html")}">{t(UI["consult"], lang)} {I["arrow"]}</a>
          <a class="btn btn-outline" href="{link(lang, "services.html")}">{t(UI["explore"], lang)}</a>
        </div>
        <ul class="hero-points">
{points}
        </ul>
      </div>

      <aside class="hero-card reveal" data-delay="120">
        <h3>{t(H["card_h"], lang)}</h3>
        <p>{t(H["card_p"], lang)}</p>
        <ul class="hero-card-list">
{cards}
        </ul>
      </aside>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(H["svc_eyebrow"], lang)}</p>
      <h2>{t(H["svc_h2"], lang)}</h2>
      <p>{t(H["svc_lead"], lang)}</p>
    </div>
    <div class="grid grid-3">
{service_cards(lang)}
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(H["sec_eyebrow"], lang)}</p>
      <h2>{t(H["sec_h2"], lang)}</h2>
      <p>{t(H["sec_lead"], lang)}</p>
    </div>
    {logo_panel("assets/img/photos/service-sectors.png", SECTORS_ALT, lang)}
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="split">
      <div class="split-visual reveal">
        <div class="visual-frame">{HERO_SVG}</div>
        <div class="visual-badge"><b dir="ltr">24/7</b><span>{t(("Always On Duty", "على أهبة الاستعداد"), lang)}</span></div>
      </div>
      <div class="reveal" data-delay="120">
        <p class="eyebrow">{t(H["about_eyebrow"], lang)}</p>
        <h2>{t(H["about_h2"], lang)}</h2>
        <p class="lead">{t(H["about_lead"], lang)}</p>
        <ul class="check-list">
{checks}
        </ul>
        <div class="btn-row">
          <a class="btn btn-dark" href="{link(lang, "about.html")}">{t(UI["more_about"], lang)} {I["arrow"]}</a>
        </div>
      </div>
    </div>
  </div>
</section>

{stats_block(lang)}

<section class="section section--alt">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(H["why_eyebrow"], lang)}</p>
      <h2>{t(H["why_h2"], lang)}</h2>
      <p>{t(H["why_lead"], lang)}</p>
    </div>
    <div class="grid grid-3">
{tiles(lang, H["why_tiles"])}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(H["proc_eyebrow"], lang)}</p>
      <h2>{t(H["proc_h2"], lang)}</h2>
      <p>{t(H["proc_lead"], lang)}</p>
    </div>
    <div class="steps">
{steps}
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(H["part_eyebrow"], lang)}</p>
      <h2>{t(H["part_h2"], lang)}</h2>
      <p>{t(H["part_lead"], lang)}</p>
    </div>
    {logo_panel("assets/img/photos/partners-logos.png", PARTNERS_ALT, lang)}
    <div class="center" style="margin-top:44px">
      <a class="btn btn-dark" href="{link(lang, "partners.html")}">{t(H["part_btn"], lang)} {I["arrow"]}</a>
    </div>
  </div>
</section>

{cta(lang)}
'''
    page(lang, "index.html", t(H["title"], lang), t(H["desc"], lang), body)

def build_about(lang):
    A = ABOUT
    story = "\n        ".join(
        ('<p class="lead">' if i == 0 else '<p>') + t(p, lang) + '</p>'
        for i, p in enumerate(A["story"]))
    mvv = "\n".join(
        f'      <article class="card reveal" data-delay="{i*80}"><span class="ico">{I[icon]}</span>'
        f'<h3>{t(title, lang)}</h3><p>{t(text, lang)}</p></article>'
        for i, (icon, title, text) in enumerate(A["mvv"]))
    ceo = "\n      ".join(f'<p>{t(p, lang)}</p>' for p in A["ceo"])
    values_html = chip_list(lang, VALUES)
    nat_html = chip_list(lang, NATIONALITIES)
    equip_html = chip_list(lang, EQUIPMENT)
    training_html = "\n".join(
        f'      <div class="tile reveal" data-delay="{(i%3)*80}"><span class="ico">{I[icon]}</span>'
        f'<div><h4>{t(title, lang)}</h4></div></div>'
        for i, (icon, title) in enumerate(TRAINING))
    uniform_html = "\n".join(
        f'      <div class="uniform reveal" data-delay="{i*70}">'
        f'<div class="uniform-photos">'
        f'<img src="/assets/img/photos/uniforms/{key}-front.jpg" alt="{t(title, lang)}" loading="lazy">'
        f'<img src="/assets/img/photos/uniforms/{key}-back.jpg" alt="{t(title, lang)}" loading="lazy">'
        f'</div><h4>{t(title, lang)}</h4></div>'
        for i, (key, title) in enumerate(UNIFORMS))
    cert_items_html = "\n      ".join(f'<p>{t(c, lang)}</p>' for c in CERTIFICATIONS)
    faqs = []
    for i, (q, a) in enumerate(A["faq"]):
        ans = t(a, lang).replace("{ADDR}", t(ADDRESS_1L, lang)).replace("{PHONE}", PHONE)
        faqs.append(f'''      <div class="acc{" is-open" if i == 0 else ""} reveal">
        <button class="acc-btn" type="button">{t(q, lang)}<span class="pm">{I["plus"]}</span></button>
        <div class="acc-panel"><div class="inner">{ans}</div></div>
      </div>''')

    FAQ_HTML = "\n".join(faqs)
    body = banner(lang, t(A["banner_h"], lang), t(A["banner_p"], lang), t(A["crumb"], lang)) + f'''
<section class="section">
  <div class="wrap">
    <div class="split">
      <div class="split-visual reveal">
        <div class="visual-frame">{ABOUT_SVG}</div>
        <div class="visual-badge"><b dir="ltr">{t(A["badge"][0], lang)}</b><span>{t(A["badge"][1], lang)}</span></div>
      </div>
      <div class="reveal" data-delay="120">
        <p class="eyebrow">{t(A["story_eyebrow"], lang)}</p>
        <h2>{t(A["story_h2"], lang)}</h2>
        {story}
        <div class="btn-row" style="margin-top:26px">
          <a class="btn btn-dark" href="{link(lang, "contact.html")}">{t(UI["talk"], lang)} {I["arrow"]}</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="grid grid-3">
{mvv}
    </div>
    <div class="sec-head center reveal" style="margin-top:56px">
      <p class="eyebrow">{t(A["values_eyebrow"], lang)}</p>
      <h2>{t(A["values_h2"], lang)}</h2>
    </div>
    <div class="chips center">
{values_html}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(A["commit_eyebrow"], lang)}</p>
      <h2>{t(A["commit_h2"], lang)}</h2>
      <p>{t(A["commit_lead"], lang)}</p>
    </div>
    <div class="grid grid-2">
{tiles(lang, A["commit_tiles"], cols=2)}
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(A["nat_eyebrow"], lang)}</p>
      <h2>{t(A["nat_h2"], lang)}</h2>
      <p>{t(A["nat_lead"], lang)}</p>
    </div>
    <div class="chips center">
{nat_html}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(A["train_eyebrow"], lang)}</p>
      <h2>{t(A["train_h2"], lang)}</h2>
      <p>{t(A["train_lead"], lang)}</p>
    </div>
    <div class="grid grid-3">
{training_html}
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(A["equip_eyebrow"], lang)}</p>
      <h2>{t(A["equip_h2"], lang)}</h2>
      <p>{t(A["equip_lead"], lang)}</p>
    </div>
    <div class="chips center">
{equip_html}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(A["uniform_eyebrow"], lang)}</p>
      <h2>{t(A["uniform_h2"], lang)}</h2>
      <p>{t(A["uniform_lead"], lang)}</p>
    </div>
    <div class="uniform-gallery">
{uniform_html}
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(A["cert_eyebrow"], lang)}</p>
      <h2>{t(A["cert_h2"], lang)}</h2>
      {cert_items_html}
    </div>
    {logo_panel("assets/img/photos/certifications.jpg", CERT_ALT, lang)}
  </div>
</section>

<section class="section section--dark">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(A["ceo_eyebrow"], lang)}</p>
      <h2>{t(A["ceo_h2"], lang)}</h2>
    </div>
    <blockquote class="quote reveal">
      {ceo}
      <p class="quote-line">{t(A["ceo_line"], lang)}</p>
      <p>{t(A["ceo_thanks"], lang)}</p>
      <footer class="quote-by">{t(A["ceo_by"], lang)}</footer>
    </blockquote>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(A["clients_eyebrow"], lang)}</p>
      <h2>{t(A["clients_h2"], lang)}</h2>
      <p>{t(A["clients_lead"], lang)}</p>
    </div>
    {logo_panel("assets/img/photos/clients-logos.jpg", CLIENTS_ALT, lang)}
    <div class="center" style="margin-top:44px">
      <a class="btn btn-dark" href="{link(lang, "clients.html")}">{t(A["clients_btn"], lang)} {I["arrow"]}</a>
    </div>
  </div>
</section>

{stats_block(lang)}

<section class="section">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(A["faq_eyebrow"], lang)}</p>
      <h2>{t(A["faq_h2"], lang)}</h2>
    </div>
    <div style="max-width:840px;margin:0 auto">
{FAQ_HTML}
    </div>
  </div>
</section>

{cta(lang)}
'''
    page(lang, "about.html", t(A["title"], lang), t(A["desc"], lang), body)

def build_services(lang):
    S = SERVICES_PAGE
    sections = []
    for i, s in enumerate(SERVICES):
        alt = " section--alt" if i % 2 else ""
        flip = " split--flip" if i % 2 else ""
        pts = "\n".join(
            f'          <li><span class="ico">{I["check"]}</span><span>{t(p, lang)}</span></li>'
            for p in s["points"])
        sections.append(f'''
<section class="section{alt}" id="{s["anchor"]}">
  <div class="wrap">
    <div class="split{flip}">
      <div class="reveal">
        <p class="eyebrow">{t(S["service_label"], lang)} {i+1:02d}</p>
        <h2>{t(s["name"], lang)}</h2>
        <p class="lead">{t(s["intro"], lang)}</p>
        <ul class="check-list">
{pts}
        </ul>
        <div class="btn-row">
          <a class="btn btn-dark" href="{link(lang, "contact.html")}?service={s["anchor"]}">{t(UI["req_quote"], lang)} {I["arrow"]}</a>
        </div>
      </div>
      <div class="split-visual reveal" data-delay="120">
        <div class="visual-frame"><div style="color:#fff;width:160px;max-width:60%">{I[s["icon"]]}</div></div>
      </div>
    </div>
  </div>
</section>''')

    body = banner(lang, t(S["banner_h"], lang), t(S["banner_p"], lang), t(S["crumb"], lang)) + f'''
<section class="section">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(S["over_eyebrow"], lang)}</p>
      <h2>{t(S["over_h2"], lang)}</h2>
      <p>{t(S["over_lead"], lang)}</p>
    </div>
    <div class="grid grid-3">
{service_cards(lang)}
    </div>
  </div>
</section>
{"".join(sections)}

<section class="section section--alt">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(S["people_eyebrow"], lang)}</p>
      <h2>{t(S["people_h2"], lang)}</h2>
      <p>{t(S["people_lead"], lang)}</p>
    </div>
    <div class="grid grid-3">
{tiles(lang, S["people_tiles"])}
    </div>
  </div>
</section>

{cta(lang, S["cta"])}
'''
    page(lang, "services.html", t(S["title"], lang), t(S["desc"], lang), body)

def build_clients(lang):
    CL = CLIENTS_PAGE
    body = banner(lang, t(CL["banner_h"], lang), t(CL["banner_p"], lang), t(CL["crumb"], lang)) + f'''
<section class="section">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(CL["eyebrow"], lang)}</p>
      <h2>{t(CL["h2"], lang)}</h2>
      <p>{t(CL["lead"], lang)}</p>
    </div>
    {logo_panel("assets/img/photos/clients-logos.jpg", CLIENTS_ALT, lang)}
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(CL["list_eyebrow"], lang)}</p>
      <h2>{t(CL["list_h2"], lang)}</h2>
    </div>
    <div class="chips center">
{chip_list(lang, CLIENTS)}
    </div>
  </div>
</section>

{cta(lang, CL["cta"])}
'''
    page(lang, "clients.html", t(CL["title"], lang), t(CL["desc"], lang), body)

def build_partners(lang):
    P = PARTNERS_PAGE
    join_p = (t(P["join_p"], lang)
              .replace("{EMAIL}", f'<a href="mailto:{EMAIL}" dir="ltr">{EMAIL}</a>')
              .replace("{PHONE}", f'<span dir="ltr">{PHONE}</span>'))
    body = banner(lang, t(P["banner_h"], lang), t(P["banner_p"], lang), t(P["crumb"], lang)) + f'''
<section class="section">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(P["eyebrow"], lang)}</p>
      <h2>{t(P["h2"], lang)}</h2>
      <p>{t(P["lead"], lang)}</p>
    </div>
    {logo_panel("assets/img/photos/partners-logos.png", PARTNERS_ALT, lang)}
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="eyebrow">{t(P["why_eyebrow"], lang)}</p>
      <h2>{t(P["why_h2"], lang)}</h2>
    </div>
    <div class="grid grid-3">
{tiles(lang, P["tiles"])}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="split">
      <div class="reveal">
        <p class="eyebrow">{t(P["join_eyebrow"], lang)}</p>
        <h2>{t(P["join_h2"], lang)}</h2>
        <p class="lead">{t(P["join_lead"], lang)}</p>
        <p>{join_p}</p>
        <div class="btn-row">
          <a class="btn btn-dark" href="{link(lang, "contact.html")}">{t(P["join_btn"], lang)} {I["arrow"]}</a>
        </div>
      </div>
      <div class="split-visual reveal" data-delay="120">
        <div class="visual-frame"><div style="color:#fff;width:160px;max-width:55%">{I["link"]}</div></div>
      </div>
    </div>
  </div>
</section>

{cta(lang)}
'''
    page(lang, "partners.html", t(P["title"], lang), t(P["desc"], lang), body)

def build_contact(lang):
    C = CONTACT
    F = C["fields"]
    card_values = [
        f'<p>{t(ADDRESS_BR, lang)}</p>',
        f'<a href="tel:{PHONE_HREF}" dir="ltr">{PHONE}</a>',
        (f'<a href="mailto:{EMAIL}" dir="ltr">{EMAIL}</a>'
         f'<small class="info-note">{t(FOOTER["email_general"], lang)}</small>'
         f'<a href="mailto:{EMAIL_SALES}" dir="ltr">{EMAIL_SALES}</a>'
         f'<small class="info-note">{t(FOOTER["email_sales"], lang)}</small>'),
    ]
    cards = []
    for i, ((icon, title, sub), value) in enumerate(zip(C["cards"], card_values)):
        extra = (f'<p style="color:var(--muted);font-size:.86rem">{t(sub, lang)}</p>') if sub else ""
        cards.append(f'''      <div class="info-card reveal" data-delay="{i*80}">
        <span class="ico">{I[icon]}</span>
        <div><h4>{t(title, lang)}</h4>{value}{extra}</div>
      </div>''')
    options = "\n".join(f'              <option value="{v}">{t(o, lang)}</option>' for v, o in C["options"])
    note = (t(F["note"], lang)
            .replace("{PRIVACY}", f'<a href="{link(lang, "privacy-policy.html")}">{t(FOOTER["privacy"], lang)}</a>')
            .replace("{PHONE}", f'<span dir="ltr">{PHONE}</span>'))
    # Lets a "Request a Quote" link on the services page (contact.html?service=<anchor>)
    # land here with the right inquiry type pre-selected and the message field
    # pre-filled, instead of the visitor arriving at a blank general enquiry.
    service_names = json.dumps(
        {s["anchor"]: html.unescape(t(s["name"], lang)) for s in SERVICES},
        ensure_ascii=False)

    body = banner(lang, t(C["banner_h"], lang), t(C["banner_p"], lang), t(C["crumb"], lang)) + f'''
<section class="section">
  <div class="wrap">
    <div class="grid grid-3" style="margin-bottom:64px">
{chr(10).join(cards)}
    </div>

    <div class="contact-grid">
      <div class="reveal">
        <p class="eyebrow">{t(C["form_eyebrow"], lang)}</p>
        <h2>{t(C["form_h2"], lang)}</h2>
        <p>{t(C["form_lead"], lang)}</p>

        <div class="map-embed" style="margin-top:32px">
          <a class="pin" href="{MAPS_URL}" target="_blank" rel="noopener noreferrer" aria-label="{t(UI["map_label"], lang)}">
            {I["pin"]}
            <h4>{t(COMPANY, lang)}</h4>
            <p>{t(ADDRESS_1L, lang)}</p>
          </a>
        </div>

        <ul class="check-list" style="margin-top:32px">
          <li><span class="ico">{I["check"]}</span><span><b>{t(C["office_hours"], lang)}</b><span>{t(HOURS, lang)}</span></span></li>
          <li><span class="ico">{I["check"]}</span><span><b>{t(C["emergency"], lang)}</b><span>{t(C["emergency_v"], lang)}</span></span></li>
        </ul>
      </div>

      <div class="form-card reveal" data-delay="120">
        <form data-contact-form novalidate data-sent-message="{t(C["sent"], lang)}"
              data-endpoint="{CONTACT_ENDPOINT}" data-lang="{lang}"
              data-sending-message="{t(C["sending"], lang)}" data-error-message="{t(C["send_failed"], lang)}"
              data-service-names='{service_names}' data-quote-prefill="{t(C["quote_prefill"], lang)}">
          <!-- Honeypot: hidden from people, tempting to bots. A filled-in
               value marks the submission as spam, server-side. -->
          <div class="visually-hidden" aria-hidden="true">
            <label for="website">{t(C["honeypot"], lang)}</label>
            <input type="text" id="website" name="website" tabindex="-1" autocomplete="off">
          </div>
          <div class="form-status" role="status" aria-live="polite"></div>

          <div class="grid grid-2" style="gap:0 20px">
            <div class="field">
              <label for="name">{t(F["name"], lang)} <span class="req">*</span></label>
              <input type="text" id="name" name="name" placeholder="{t(F["name_ph"], lang)}" required>
              <span class="err">{t(F["req"], lang)}</span>
            </div>
            <div class="field">
              <label for="company">{t(F["company"], lang)}</label>
              <input type="text" id="company" name="company" placeholder="{t(F["company_ph"], lang)}">
              <span class="err"></span>
            </div>
            <div class="field">
              <label for="email">{t(F["email"], lang)} <span class="req">*</span></label>
              <input type="email" id="email" name="email" placeholder="you@example.com" dir="ltr" required>
              <span class="err">{t(F["bad_email"], lang)}</span>
            </div>
            <div class="field">
              <label for="phone">{t(F["phone"], lang)} <span class="req">*</span></label>
              <input type="tel" id="phone" name="phone" placeholder="+965 0000 0000" dir="ltr" required>
              <span class="err">{t(F["bad_phone"], lang)}</span>
            </div>
          </div>

          <div class="field">
            <label for="service">{t(F["service"], lang)} <span class="req">*</span></label>
            <select id="service" name="service" required>
              <option value="">{t(F["select"], lang)}</option>
{options}
            </select>
            <span class="err">{t(F["choose"], lang)}</span>
          </div>

          <div class="field">
            <label for="message">{t(F["message"], lang)} <span class="req">*</span></label>
            <textarea id="message" name="message" placeholder="{t(F["message_ph"], lang)}" required></textarea>
            <span class="err">{t(F["req"], lang)}</span>
          </div>

          <button class="btn btn-primary" type="submit" style="width:100%">{t(F["submit"], lang)} {I["arrow"]}</button>
          <p class="form-note">{note}</p>
        </form>
      </div>
    </div>
  </div>
</section>

{cta(lang, C["cta"])}
'''
    page(lang, "contact.html", t(C["title"], lang), t(C["desc"], lang), body)

def build_privacy(lang):
    P = PRIVACY
    out = [f'<span class="updated">{t(P["updated"], lang)}</span>',
           f'<p class="lead">{t(P["intro"], lang).replace("{COMPANY}", t(COMPANY, lang))}</p>']
    for heading, blocks in P["sections"]:
        out.append(f'<h2>{t(heading, lang)}</h2>')
        for kind, payload in blocks:
            if kind == "p":
                out.append(f'<p>{t(payload, lang)}</p>')
            else:
                items = "\n        ".join(f'<li>{t(i, lang)}</li>' for i in payload)
                out.append(f'<ul>\n        {items}\n      </ul>')
    out.append(f'<h2>{t(P["contact_h"], lang)}</h2>')
    out.append(f'<p>{t(P["contact_p"], lang)}</p>')
    out.append('<ul>\n        '
               f'<li><b>{t(COMPANY, lang)}</b></li>\n        '
               f'<li>{t(ADDRESS_1L, lang)}</li>\n        '
               f'<li>{t(P["tel_label"], lang)} <a href="tel:{PHONE_HREF}" dir="ltr">{PHONE}</a></li>\n        '
               f'<li>{t(P["email_label"], lang)} <a href="mailto:{EMAIL}" dir="ltr">{EMAIL}</a></li>\n      </ul>')
    rich = "\n      ".join(out)

    body = banner(lang, t(P["banner_h"], lang), t(P["banner_p"], lang), t(P["crumb"], lang)) + f'''
<section class="section">
  <div class="wrap">
    <div class="rich reveal">
      {rich}
    </div>
  </div>
</section>
'''
    page(lang, "privacy-policy.html", t(P["title"], lang), t(P["desc"], lang), body)

def build_404(lang):
    N = NOTFOUND
    body = f'''
<section class="section" style="padding:120px 0">
  <div class="wrap center">
    <p class="eyebrow" style="justify-content:center">{t(N["eyebrow"], lang)}</p>
    <h1 style="margin-bottom:18px">{t(N["h1"], lang)}</h1>
    <p class="lead" style="max-width:560px;margin:0 auto 32px">{t(N["lead"], lang)}</p>
    <div class="btn-row center">
      <a class="btn btn-primary" href="{link(lang, "index.html")}">{t(N["back"], lang)} {I["arrow"]}</a>
      <a class="btn btn-dark" href="{link(lang, "contact.html")}">{t(N["contact"], lang)}</a>
    </div>
  </div>
</section>
'''
    page(lang, "404.html", t(N["title"], lang), t(N["desc"], lang), body)

# ============================================================ write
SITEMAP_PRIORITY = {
    "index.html": "1.0", "services.html": "0.9", "about.html": "0.8",
    "contact.html": "0.8", "partners.html": "0.6", "clients.html": "0.6",
    "privacy-policy.html": "0.3",
}

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
        build_about(lang)
        build_services(lang)
        build_clients(lang)
        build_partners(lang)
        build_contact(lang)
        build_privacy(lang)
        build_404(lang)

    for (lang, fname), html in PAGES.items():
        out_path = out_file_for(lang, fname)
        full = os.path.join(OUT, out_path)
        os.makedirs(os.path.dirname(full) or OUT, exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(html)
        print("wrote", out_path, len(html), "bytes")

    # Retire the flat ".html" URLs this migration replaces, and add the /home/
    # alias, without breaking anyone already pointed at the old address.
    redirects = 0
    for lang in LANGS:
        for fname in ROUTES:
            if fname == "index.html":
                continue  # no flat URL to retire: index.html *is* the file behind "/"
            old_path = fname if lang == "en" else f"ar/{fname}"
            write_redirect(old_path, canonical(lang, fname), lang)
            redirects += 1
        home_stub = "home/index.html" if lang == "en" else "ar/home/index.html"
        write_redirect(home_stub, canonical(lang, "index.html"), lang)
        redirects += 1
    print("wrote", redirects, "redirect stubs (retired .html URLs + /home alias)")

    print("wrote sitemap.xml with", write_sitemap(), "urls")
    synced = sync_backend_prompt()
    print("backend prompt:", ", ".join(synced) if synced else "already in sync")
