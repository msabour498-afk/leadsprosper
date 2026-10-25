#!/usr/bin/env python3
"""Build every page of leadsprosper.com from one place.

Run:  python3 build.py
Edit the SITE settings below (phone, address, form, analytics), run the
script again, and every page updates. Output files are written next to this
script, at the top level of the repo.
"""
import hashlib
import html
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def version(name):
    """Short content hash so browsers fetch the new file after every change."""
    with open(os.path.join(ROOT, name), "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


CSS_V = version("styles.css")
JS_V = version("site.js")

# ---------------------------------------------------------------- settings
SITE = {
    "name": "Leads Prosper",
    "url": "https://leadsprosper.com",
    "email": "support@leadsprosper.com",
    # Add when ready, e.g. "+1 312 555 0100". Leave None to hide.
    "phone": None,
    # Add when ready, e.g. {"street": "...", "city": "Chicago", "region": "IL", "zip": "606xx"}
    "address": None,
    "main_city": "Chicago",
    "areas": ["Chicago", "New York City"],
    # Analytics. Paste IDs as strings, e.g. "GTM-ABC1234" / "G-XXXXXXX".
    "gtm_id": None,
    "ga4_id": None,
    # Forms. provider: "hubspot", "formspree", or None (opens the visitor's email app).
    "form": {
        "provider": "hubspot",
        "hubspotPortalId": "247730807",
        "hubspotFormId": "09784c96-ee3b-4b4e-98f8-384163513f64",
        "hubspotRegion": "na2",   # na1/na2 use api.hsforms.com; eu1 uses api-eu1
        "formspreeEndpoint": "",  # e.g. "https://formspree.io/f/xxxxxxx"
    },
    "year": 2026,
}

SERVICES = [
    ("google-ads", "Google Ads"),
    ("facebook-ads", "Facebook Ads"),
    ("chatgpt-ads", "ChatGPT Ads"),
]
INDUSTRIES = [
    ("b2b", "B2B companies"),
    ("b2c", "B2C companies"),
]

e = html.escape


def url(slug):
    return "/" if slug == "" else "/" + slug


def abs_url(slug):
    return SITE["url"] + url(slug)


# ---------------------------------------------------------------- shared pieces
LOGO_SVG = (
    '<svg class="logo-mark" viewBox="0 0 32 32" aria-hidden="true" focusable="false">'
    '<rect width="32" height="32" rx="6" fill="#13233f"/>'
    '<path d="M7 22 L13 16 L18 19 L25 10" fill="none" stroke="#fff" stroke-width="3" '
    'stroke-linecap="round" stroke-linejoin="round"/>'
    '<circle cx="25" cy="10" r="2.6" fill="#3fbf95"/></svg>'
)
CARET = ('<svg class="caret" viewBox="0 0 10 6" aria-hidden="true" focusable="false">'
         '<path d="M1 1l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>')
ICON_MAIL = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3 6h18v12H3z M3 7l9 6 9-6" '
             'fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>')
ICON_PHONE = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6.6 3h3l1.5 4.5-2 1.3a11 11 0 0 0 '
              '6.1 6.1l1.3-2 4.5 1.5v3a2 2 0 0 1-2.2 2A17 17 0 0 1 4.6 5.2 2 2 0 0 1 6.6 3z" fill="none" '
              'stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>')
ICON_TEXT = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 5h16v11H9l-5 4z" fill="none" '
             'stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>')


def tel_href(prefix):
    digits = "".join(c for c in SITE["phone"] if c.isdigit() or c == "+")
    return f"{prefix}:{digits}"


def header(current):
    def menu(key, label, items, all_slug, all_label):
        links = "".join(
            f'<li><a href="{url(s)}"{" aria-current=\"page\"" if s == current else ""}>{e(n)}</a></li>'
            for s, n in items
        )
        links += (f'<li class="sub-all"><a href="{url(all_slug)}"'
                  f'{" aria-current=\"page\"" if all_slug == current else ""}>{e(all_label)}</a></li>')
        return (f'<li class="has-menu"><button type="button" class="menu-toggle" aria-expanded="false" '
                f'aria-controls="menu-{key}">{label}{CARET}</button>'
                f'<ul class="submenu" id="menu-{key}">{links}</ul></li>')

    audit_cur = ' aria-current="page"' if current == "free-audit" else ""
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap bar">
    <a class="logo" href="/">{LOGO_SVG}<span>Leads Prosper</span></a>
    <nav class="nav" aria-label="Main">
      <div class="nav-panel" id="nav-panel">
        <ul class="nav-list">
          {menu("services", "Services", [(s, n) for s, n in SERVICES], "services", "All services")}
          {menu("industries", "Industries", INDUSTRIES, "industries", "All industries")}
          <li><a class="nav-link" href="/free-audit"{audit_cur}>Free audit</a></li>
        </ul>
      </div>
    </nav>
    <a class="btn btn-small header-cta" href="/contact">Contact</a>
    <button type="button" class="nav-toggle" aria-expanded="false" aria-controls="nav-panel">Menu</button>
  </div>
</header>"""


def floating_button():
    if SITE["phone"]:
        return (f'<div class="float-group">'
                f'<a class="float-contact" href="{tel_href("sms")}">{ICON_TEXT}<span>Text us</span></a>'
                f'<a class="float-contact" href="{tel_href("tel")}">{ICON_PHONE}<span>Call us</span></a></div>')
    return (f'<a class="float-contact" href="mailto:{SITE["email"]}">{ICON_MAIL}'
            f'<span>Email us</span></a>')


def footer():
    svc = "".join(f'<li><a href="{url(s)}">{e(n)}</a></li>' for s, n in SERVICES)
    ind = "".join(f'<li><a href="{url(s)}">{e(n)}</a></li>' for s, n in INDUSTRIES)
    contact = f'<li><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></li>'
    if SITE["phone"]:
        contact += f'<li><a href="{tel_href("tel")}">{e(SITE["phone"])}</a></li>'
    if SITE["address"]:
        a = SITE["address"]
        contact += f'<li>{e(a["street"])}<br>{e(a["city"])}, {e(a["region"])} {e(a["zip"])}</li>'
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-about">
        <a class="logo" href="/">{LOGO_SVG}<span>Leads Prosper</span></a>
        <p>Paid ads that bring in leads. Based in Chicago, working with businesses in New York and other major metros.</p>
      </div>
      <div><h2>Services</h2><ul>{svc}<li><a href="/services">All services</a></li></ul></div>
      <div><h2>Industries</h2><ul>{ind}<li><a href="/industries">All industries</a></li></ul></div>
      <div><h2>Contact</h2><ul>{contact}<li><a href="/free-audit">Free account audit</a></li><li><a href="/contact">Contact page</a></li></ul></div>
    </div>
    <p class="legal">&copy; {SITE["year"]} Leads Prosper. Serving Chicago, New York City, and other major US metros.</p>
  </div>
</footer>"""


def cta_band(heading="Start with a free audit", text=None):
    text = text or ("Send us access to your ad account, or tell us where you're starting from. "
                    "We'll show you where the budget is going and what we'd change.")
    return f"""<section class="cta-band">
  <div class="wrap">
    <h2>{e(heading)}</h2>
    <p>{e(text)}</p>
    <div class="actions"><a class="btn" href="/free-audit">Get my free audit</a></div>
  </div>
</section>"""


def business_schema():
    data = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "@id": SITE["url"] + "/#business",
        "name": SITE["name"],
        "url": SITE["url"] + "/",
        "email": SITE["email"],
        "logo": SITE["url"] + "/favicon.svg",
        "image": SITE["url"] + "/og.png",
        "description": "Lead generation agency running Google Ads, Facebook Ads, and ChatGPT Ads.",
        "areaServed": [{"@type": "City", "name": "Chicago"}, {"@type": "City", "name": "New York"}],
        "knowsAbout": ["Google Ads", "Facebook Ads", "Instagram Ads", "ChatGPT Ads", "Lead generation"],
    }
    if SITE["phone"]:
        data["telephone"] = SITE["phone"]
    if SITE["address"]:
        a = SITE["address"]
        data["address"] = {"@type": "PostalAddress", "streetAddress": a["street"], "addressLocality": a["city"],
                           "addressRegion": a["region"], "postalCode": a["zip"], "addressCountry": "US"}
    return data


def service_schema(slug, name, description):
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": name + " management",
        "serviceType": name,
        "description": description,
        "url": abs_url(slug),
        "provider": {"@id": SITE["url"] + "/#business"},
        "areaServed": [{"@type": "City", "name": "Chicago"}, {"@type": "City", "name": "New York"}],
    }


def analytics_head():
    out = ""
    if SITE["gtm_id"]:
        g = SITE["gtm_id"]
        out += ("<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});"
                "var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;"
                "j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);"
                f"}})(window,document,'script','dataLayer','{g}');</script>\n")
    elif SITE["ga4_id"]:
        g = SITE["ga4_id"]
        out += (f'<script async src="https://www.googletagmanager.com/gtag/js?id={g}"></script>\n'
                "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
                f"gtag('js',new Date());gtag('config','{g}');</script>\n")
    return out


def analytics_body():
    if SITE["gtm_id"]:
        return (f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={SITE["gtm_id"]}" '
                'height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n')
    return ""


def page(slug, title, description, body, schemas=(), noindex=False, current=None):
    canonical = abs_url(slug)
    cfg = {"email": SITE["email"], "form": SITE["form"]}
    schema_tags = "".join(
        f'<script type="application/ld+json">{json.dumps(s, separators=(",", ":"))}</script>\n'
        for s in [business_schema(), *schemas]
    )
    robots = '<meta name="robots" content="noindex">\n' if noindex else ""
    canon = "" if noindex else f'<link rel="canonical" href="{canonical}">\n'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
{robots}{canon}<meta property="og:type" content="website">
<meta property="og:site_name" content="Leads Prosper">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE["url"]}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#13233f">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400;600;700;800&display=swap">
<link rel="stylesheet" href="/styles.css?v={CSS_V}">
<script>window.dataLayer=window.dataLayer||[];window.LP_CONFIG={json.dumps(cfg)};</script>
{analytics_head()}{schema_tags}</head>
<body>
{analytics_body()}{header(current if current is not None else slug)}
<main id="main">
{body}
</main>
{footer()}
{floating_button()}
<script src="/site.js?v={JS_V}" defer></script>
</body>
</html>
"""


def crumbs(*trail):
    parts = ['<a href="/">Home</a>']
    for slug, name in trail[:-1]:
        parts.append(f'<a href="{url(slug)}">{e(name)}</a>')
    parts.append(f'<span aria-current="page">{e(trail[-1][1])}</span>')
    return f'<nav class="crumbs" aria-label="Breadcrumb">{" / ".join(parts)}</nav>'


def checks(items):
    return '<ul class="checks">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


# ---------------------------------------------------------------- pages
PAGES = {}

# Home -------------------------------------------------------------------
PAGES["index.html"] = page(
    "", "Lead Generation Agency in Chicago | Google & Facebook Ads | Leads Prosper",
    "Leads Prosper is a Chicago lead generation agency running Google Ads, Facebook Ads, and ChatGPT Ads "
    "for businesses in Chicago, NYC, and other metros. Get a free account audit.",
    f"""<section class="hero">
  <div class="wrap">
    <h1>Ads that bring in leads</h1>
    <p class="lead">We run Google Ads, Facebook Ads, and ChatGPT Ads for businesses in Chicago, New York, and other
    major metros. We judge the work by calls, form fills, and customers, not by clicks.</p>
    <div class="actions">
      <a class="btn" href="/free-audit">Get a free account audit</a>
      <a class="btn btn-ghost" href="/services">See services</a>
    </div>
  </div>
</section>
<section class="section tint" aria-labelledby="path-h">
  <div class="wrap">
    <div class="section-head">
      <h2 id="path-h">Where leads get lost</h2>
      <p>Every lead moves through the same five steps. Most wasted budget comes from one weak step, not the whole account.
      We find that step first.</p>
    </div>
    <ol class="path">
      <li><strong>Ad shown</strong><span>To the right people, in the right area, for the right searches.</span></li>
      <li><strong>Click</strong><span>An ad worth clicking, matched to what the person wanted.</span></li>
      <li><strong>Visit</strong><span>A page that loads fast and answers their question.</span></li>
      <li><strong>Lead</strong><span>A call or form that's easy to complete and gets tracked.</span></li>
      <li><strong>Customer</strong><span>Fast follow-up, and results sent back to the ad platform.</span></li>
    </ol>
  </div>
</section>
<section class="section" aria-labelledby="svc-h">
  <div class="wrap">
    <div class="section-head"><h2 id="svc-h">What we run</h2></div>
    <div class="rows">
      <div class="row"><h3>Google Ads</h3><p>Search, Performance Max, and YouTube campaigns that catch people already looking for what you sell.</p><a class="more" href="/google-ads">Google Ads</a></div>
      <div class="row"><h3>Facebook Ads</h3><p>Facebook and Instagram campaigns that reach the right people before they start searching.</p><a class="more" href="/facebook-ads">Facebook Ads</a></div>
      <div class="row"><h3>ChatGPT Ads</h3><p>A new channel. We help you test it with a small budget and compare it against what already works.</p><a class="more" href="/chatgpt-ads">ChatGPT Ads</a></div>
    </div>
  </div>
</section>
<section class="section" aria-labelledby="how-h">
  <div class="wrap">
    <div class="section-head"><h2 id="how-h">How we start</h2></div>
    <ol class="steps">
      <li><strong>Free audit</strong>We review your ad accounts and tracking, or your plans if you're not running ads yet.</li>
      <li><strong>Plan</strong>We agree on what a good lead is, what it's worth to you, and the budget to test with.</li>
      <li><strong>Launch or fix</strong>We rebuild what's broken and launch what's missing, starting with tracking.</li>
      <li><strong>Report</strong>You see leads and cost per lead, in plain numbers you can check yourself.</li>
    </ol>
  </div>
</section>
<section class="section tint" aria-labelledby="who-h">
  <div class="wrap">
    <div class="section-head"><h2 id="who-h">Who we work with</h2></div>
    <div class="split">
      <div>
        <h3>B2B companies</h3>
        <p>Software, professional services, manufacturing, and other businesses with longer sales cycles,
        where one good lead matters more than a hundred cheap ones.</p>
        <a class="more" href="/b2b">B2B lead generation</a>
      </div>
      <div>
        <h3>B2C companies</h3>
        <p>Home services, legal, health, real estate, and other local businesses that need the phone to ring
        this week.</p>
        <a class="more" href="/b2c">B2C lead generation</a>
      </div>
    </div>
  </div>
</section>
{cta_band()}""",
)

# Services overview ---------------------------------------------------------
PAGES["services.html"] = page(
    "services", "Paid Ads Services in Chicago & NYC | Google, Facebook, ChatGPT Ads | Leads Prosper",
    "Google Ads, Facebook Ads, and ChatGPT Ads management for lead generation in Chicago, New York City, "
    "and other metros. Start with a free account audit.",
    f"""<section class="page-hero">
  <div class="wrap">
    {crumbs(("services", "Services"))}
    <h1>Our services</h1>
    <p class="lead">Three ad channels, one goal: more qualified leads for the money you spend. We set up tracking first,
    so every channel is judged the same way.</p>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="rows">
      <div class="row"><h3>Google Ads</h3><p>Search, Performance Max, and YouTube. Best when people already search for what you offer.</p><a class="more" href="/google-ads">Google Ads</a></div>
      <div class="row"><h3>Facebook Ads</h3><p>Facebook and Instagram, with lead forms or your own site. Best for reaching people before they search.</p><a class="more" href="/facebook-ads">Facebook Ads</a></div>
      <div class="row"><h3>ChatGPT Ads</h3><p>Ads shown in ChatGPT. Early, and worth a measured test for some businesses.</p><a class="more" href="/chatgpt-ads">ChatGPT Ads</a></div>
    </div>
  </div>
</section>
<section class="section tint">
  <div class="wrap">
    <div class="section-head"><h2>Included with every channel</h2></div>
    <div class="cols">
      <div><h3>Conversion tracking</h3><p>Calls, forms, and bookings recorded correctly in each platform and in Google Analytics.</p></div>
      <div><h3>Landing page review</h3><p>Clear notes on what to change so more visitors become leads.</p></div>
      <div><h3>Lead quality feedback</h3><p>Sending results from your CRM back to the platforms, so they find more leads like your best ones.</p></div>
      <div><h3>Plain reporting</h3><p>Leads, cost per lead, and what we changed. No vanity metrics.</p></div>
    </div>
  </div>
</section>
{cta_band()}""",
    schemas=[service_schema("services", "Paid advertising", "Google Ads, Facebook Ads, and ChatGPT Ads management for lead generation.")],
)


def service_page(slug, name, title, description, intro, handles, audit, fit, faqs):
    faq_html = "".join(f"<details><summary>{e(q)}</summary><p>{a}</p></details>" for q, a in faqs)
    return page(
        slug, title, description,
        f"""<section class="page-hero">
  <div class="wrap">
    {crumbs(("services", "Services"), (slug, name))}
    <h1>{e(name)}</h1>
    <p class="lead">{intro}</p>
    <div class="actions"><a class="btn" href="/free-audit">Get a free {e(name)} audit</a></div>
  </div>
</section>
<section class="section">
  <div class="wrap split">
    <div><h2>What we handle</h2>{checks(handles)}</div>
    <div><h2>What the audit checks</h2>{checks(audit)}</div>
  </div>
</section>
<section class="section tint">
  <div class="wrap">
    <div class="section-head"><h2>A good fit if</h2></div>
    {checks(fit)}
  </div>
</section>
<section class="section faq">
  <div class="wrap measure">
    <h2>Common questions</h2>
    {faq_html}
  </div>
</section>
{cta_band()}""",
        schemas=[service_schema(slug, name, description)],
    )


PAGES["google-ads.html"] = service_page(
    "google-ads", "Google Ads",
    "Google Ads Agency in Chicago | PPC Management for Leads | Leads Prosper",
    "Chicago Google Ads agency managing Search, Performance Max, and YouTube campaigns for lead generation "
    "in Chicago, NYC, and other metros. Get a free Google Ads audit.",
    "Google Ads puts you in front of people at the moment they search for what you sell. We build and run campaigns "
    "for businesses in Chicago, New York, and other metros, and measure them by leads, not clicks.",
    ["Search campaigns built around the terms your buyers actually use",
     "Performance Max and YouTube, when they fit your goals",
     "Negative keywords and search term reviews to cut wasted spend",
     "Call, form, and booking tracking with Google Ads and GA4",
     "Location targeting set to the areas you actually serve",
     "Sending closed deals from your CRM back to Google"],
    ["Whether conversions are tracked, and tracked only once",
     "Search terms that spend money without producing leads",
     "Location settings that show ads outside your service area",
     "Bidding strategies that don't match how much data you have",
     "Ads and landing pages that don't match the search",
     "Budget split across campaigns versus where leads come from"],
    ["People search for your service on Google",
     "You're spending on Google Ads but can't tell which leads came from it",
     "You want an outside review before raising your budget",
     "You serve Chicago, New York, or another large metro and need tight location targeting"],
    [("Do I need to give you access to my account for the audit?",
      "It gives the most useful audit. You can add us as a read-only user in Google Ads, and remove us any time. If you'd rather not, we can review what you share by screen or export."),
     ("Do you work with businesses outside Chicago?",
      "Yes. Chicago is home base, and we also work with businesses in New York City and other major US metros."),
     ("Will I own my Google Ads account?",
      "You should always own your ad account and its data. We work inside your account as a user you control.")],
)

PAGES["facebook-ads.html"] = service_page(
    "facebook-ads", "Facebook Ads",
    "Facebook Ads Agency in Chicago | Meta Lead Generation | Leads Prosper",
    "Chicago Facebook Ads agency running Facebook and Instagram lead generation campaigns for businesses in "
    "Chicago, NYC, and other metros. Get a free Facebook Ads audit.",
    "Facebook and Instagram reach people before they start searching. We build Meta campaigns that turn that "
    "attention into calls and form fills for businesses in Chicago, New York, and other metros.",
    ["Facebook and Instagram campaigns built for leads, not likes",
     "Instant lead forms or your own landing pages, whichever fits",
     "Meta Pixel and Conversions API setup",
     "Audience building from your customer lists and site visitors",
     "Ad creative tests, with clear notes on what's working",
     "Special Ad Category setup for housing, employment, credit, and financial offers"],
    ["Whether the Pixel and Conversions API record leads correctly",
     "Campaign objectives that optimize for the wrong result",
     "Lead forms that bring in fake or low-quality contacts",
     "Audiences that overlap and compete with each other",
     "Ad fatigue: the same ads shown too many times",
     "How fast new leads get a response"],
    ["Your customers use Facebook or Instagram (most do)",
     "You get leads from Meta but too many are low quality",
     "You have a clear offer that works well with visuals",
     "You want leads beyond the people already searching on Google"],
    [("Are Facebook leads lower quality than Google leads?",
      "They can be, mostly because the person wasn't searching yet. Form questions, follow-up speed, and sending lead quality back to Meta make a large difference."),
     ("Do you handle Instagram too?",
      "Yes. Facebook and Instagram ads run from the same Meta Ads Manager, and we manage both."),
     ("What's a Special Ad Category?",
      "Meta requires ads for housing, employment, credit, and some financial products to use restricted targeting. We set these up correctly so ads aren't rejected.")],
)

PAGES["chatgpt-ads.html"] = service_page(
    "chatgpt-ads", "ChatGPT Ads",
    "ChatGPT Ads Agency in Chicago | Advertising on ChatGPT | Leads Prosper",
    "Chicago agency helping businesses in Chicago, NYC, and other metros test ChatGPT Ads: account setup, "
    "tracking, ads, and honest cost-per-lead comparisons. Free audit.",
    "OpenAI now sells ads in ChatGPT. It's a young channel, so we treat it as a test: small budget, clean tracking, "
    "and a straight comparison against your Google and Facebook results.",
    ["Deciding whether ChatGPT Ads make sense for your business yet",
     "Ads Manager setup, budgets, and bids",
     "Conversion tracking with OpenAI's pixel and Conversions API",
     "Writing and testing ads",
     "Comparing cost per lead against your other channels",
     "Scaling up only if the numbers hold"],
    ["Whether your offer is something people research in ChatGPT",
     "What you already pay per lead on Google and Meta, as a baseline",
     "Whether your site and tracking are ready for a new channel",
     "A sensible test budget and what result would justify more"],
    ["You already run Google or Facebook Ads and know your cost per lead",
     "Your buyers research before they buy",
     "You're comfortable testing a new channel with a set budget",
     "You want to learn the channel before your competitors do"],
    [("Can any business run ChatGPT Ads?",
      "OpenAI is opening its self-serve Ads Manager gradually, and also sells through partners. Part of our job is getting you set up through whichever route is available."),
     ("How are ChatGPT Ads priced?",
      "OpenAI offers bidding by cost per thousand views (CPM) and by cost per click (CPC)."),
     ("Do advertisers see what people type into ChatGPT?",
      "No. OpenAI says advertisers get aggregated results, not individual conversations, and that ads are kept separate from ChatGPT's answers.")],
)

# Industries -----------------------------------------------------------------
B2B_LIST = [
    ("Software and SaaS", "Demo requests and trial sign-ups from the right size of company, not students and job seekers.",
     "B2B software, apps, IT platforms"),
    ("Professional services", "High-value consultations, where one new client covers months of ad spend.",
     "Law firms serving businesses, accounting, consulting, engineering"),
    ("Manufacturing and industrial", "Quote requests from buyers and engineers searching for specific parts and capabilities.",
     "Contract manufacturers, machine shops, suppliers, distributors"),
    ("IT and managed services", "Local businesses looking for support, security, and cloud help.",
     "MSPs, cybersecurity, IT consulting"),
    ("Commercial services", "Facility managers and owners requesting bids.",
     "Commercial cleaning, construction, HVAC, security, staffing"),
]
B2C_LIST = [
    ("Home services", "Calls from homeowners in your service area, often the same day.",
     "HVAC, plumbing, roofing, remodeling, landscaping, pest control"),
    ("Legal", "Consultation requests for practice areas with high case values.",
     "Personal injury, family law, criminal defense, immigration, estate planning"),
    ("Health and wellness", "Booked appointments from patients nearby.",
     "Dental, med spas, chiropractic, physical therapy, clinics"),
    ("Real estate and mortgage", "Buyer, seller, and refinance leads, set up within Meta's housing and credit ad rules.",
     "Agents, brokerages, lenders, property managers"),
    ("Automotive", "Service appointments and sales inquiries from local drivers.",
     "Dealers, repair shops, detailing, auto glass"),
    ("Fitness and local studios", "Trial sign-ups and first visits from people close enough to come regularly.",
     "Gyms, yoga and pilates studios, martial arts, personal training"),
]


def industry_rows(items):
    return "".join(
        f'<div class="industry"><h3>{e(n)}</h3><div><p>{e(d)}</p><p class="examples">Includes: {e(x)}</p></div></div>'
        for n, d, x in items
    )


PAGES["industries.html"] = page(
    "industries", "Industries We Serve | B2B & B2C Lead Generation in Chicago | Leads Prosper",
    "Lead generation for B2B and B2C businesses in Chicago, NYC, and other metros: software, professional "
    "services, home services, legal, health, and more.",
    f"""<section class="page-hero">
  <div class="wrap">
    {crumbs(("industries", "Industries"))}
    <h1>Industries we serve</h1>
    <p class="lead">Business buyers and household buyers behave differently, so we run their ads differently.</p>
  </div>
</section>
<section class="section">
  <div class="wrap split">
    <div>
      <h2>B2B companies</h2>
      <p>Longer sales cycles, several decision makers, and leads that need qualifying. We focus on lead quality and
      send closed deals back to the ad platforms.</p>
      <ul class="tags">{"".join(f"<li>{e(n)}</li>" for n, _, _ in B2B_LIST)}</ul>
      <p style="margin-top:1.25rem"><a class="more" href="/b2b">B2B lead generation</a></p>
    </div>
    <div>
      <h2>B2C companies</h2>
      <p>Fast decisions, local searches, and phones that need to ring. We focus on calls, booked appointments,
      and response speed.</p>
      <ul class="tags">{"".join(f"<li>{e(n)}</li>" for n, _, _ in B2C_LIST)}</ul>
      <p style="margin-top:1.25rem"><a class="more" href="/b2c">B2C lead generation</a></p>
    </div>
  </div>
</section>
{cta_band()}""",
)

PAGES["b2b.html"] = page(
    "b2b", "B2B Lead Generation Agency in Chicago | Google & Facebook Ads | Leads Prosper",
    "B2B lead generation in Chicago, NYC, and other metros with Google Ads, Facebook Ads, and ChatGPT Ads. "
    "Qualified demo and quote requests. Free account audit.",
    f"""<section class="page-hero">
  <div class="wrap">
    {crumbs(("industries", "Industries"), ("b2b", "B2B"))}
    <h1>B2B lead generation</h1>
    <p class="lead">For companies that sell to other businesses. We aim for fewer, better leads: real companies,
    real decision makers, and deals you can trace back to the ad that started them.</p>
    <div class="actions"><a class="btn" href="/free-audit">Get a free account audit</a></div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>Main B2B industries</h2></div>
    {industry_rows(B2B_LIST)}
  </div>
</section>
<section class="section tint">
  <div class="wrap">
    <div class="section-head"><h2>How B2B ads differ</h2></div>
    <div class="cols">
      <div><h3>Quality over volume</h3><p>Form questions and targeting that screen out students, job seekers, and companies too small to buy.</p></div>
      <div><h3>Closed-loop tracking</h3><p>Results from your CRM sent back to Google and Meta, so they optimize for deals, not form fills.</p></div>
      <div><h3>Longer cycles</h3><p>Remarketing that stays in front of buyers during a sales process that can take months.</p></div>
    </div>
  </div>
</section>
{cta_band()}""",
)

PAGES["b2c.html"] = page(
    "b2c", "B2C Lead Generation Agency in Chicago | Local Google & Facebook Ads | Leads Prosper",
    "B2C lead generation in Chicago, NYC, and other metros: calls and booked appointments for home services, "
    "legal, health, real estate, and more. Free account audit.",
    f"""<section class="page-hero">
  <div class="wrap">
    {crumbs(("industries", "Industries"), ("b2c", "B2C"))}
    <h1>B2C lead generation</h1>
    <p class="lead">For businesses that sell to people and households. We focus on calls, form fills, and
    booked appointments from people in the area you serve.</p>
    <div class="actions"><a class="btn" href="/free-audit">Get a free account audit</a></div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>Main B2C industries</h2></div>
    {industry_rows(B2C_LIST)}
  </div>
</section>
<section class="section tint">
  <div class="wrap">
    <div class="section-head"><h2>How B2C ads differ</h2></div>
    <div class="cols">
      <div><h3>Calls count</h3><p>Phone calls tracked as leads, including which ad and keyword produced them.</p></div>
      <div><h3>Tight locations</h3><p>Ads shown only where you work, from a single Chicago neighborhood to all five NYC boroughs.</p></div>
      <div><h3>Speed to lead</h3><p>People contact several businesses. We help you set up fast replies so you're the first to answer.</p></div>
    </div>
  </div>
</section>
{cta_band()}""",
)

# Forms ----------------------------------------------------------------------


def text_field(name, label, kind="text", required=False, autocomplete="", hint=""):
    req = f' data-required="{name}"' if required else ""
    opt = "" if required else ' <span class="opt">(optional)</span>'
    ac = f' autocomplete="{autocomplete}"' if autocomplete else ""
    err = {"name": "Enter your full name.", "email": "Enter a valid email address.",
           "website": "Enter your website, like example.com.", "message": "Tell us a little about what you need."}.get(name, "This field is required.")
    return (f'<div class="field"{req}><label for="f-{name}">{label}{opt}</label>'
            f'<input id="f-{name}" name="{name}" type="{kind}"{ac}{hint} aria-describedby="e-{name}">'
            f'<p class="error" id="e-{name}">{err}</p></div>')


def honeypot():
    return ('<div class="hp" aria-hidden="true"><label for="f-fax">Leave this empty</label>'
            '<input id="f-fax" name="company_fax" type="text" tabindex="-1" autocomplete="off"></div>')


AUDIT_FORM = f"""<form class="form" data-lead-form="audit" novalidate>
  {text_field("name", "Full name", required=True, autocomplete="name")}
  {text_field("email", "Work email", "email", required=True, autocomplete="email")}
  {text_field("phone", "Phone", "tel", autocomplete="tel")}
  <div class="field" data-required="website"><label for="f-website">Website</label>
    <input id="f-website" name="website" type="text" inputmode="url" autocomplete="url" placeholder="example.com" aria-describedby="e-website">
    <span hidden data-extra="Website" data-name="website"></span>
    <p class="error" id="e-website">Enter your website, like example.com.</p></div>
  <div class="field" data-required="accounts"><fieldset aria-describedby="e-accounts">
    <legend>Which accounts should we audit?</legend>
    <span hidden data-extra="Accounts to audit" data-name="accounts"></span>
    <div class="choices">
      <label class="choice"><input type="checkbox" name="accounts" value="Google Ads"> Google Ads</label>
      <label class="choice"><input type="checkbox" name="accounts" value="Facebook/Instagram Ads"> Facebook / Instagram</label>
      <label class="choice"><input type="checkbox" name="accounts" value="ChatGPT Ads"> ChatGPT Ads</label>
      <label class="choice"><input type="checkbox" name="accounts" value="Not running ads yet"> Not running ads yet</label>
    </div></fieldset>
    <p class="error" id="e-accounts">Pick at least one.</p></div>
  <div class="field"><label for="f-spend">Monthly ad spend <span class="opt">(optional)</span></label>
    <span hidden data-extra="Monthly ad spend" data-name="spend"></span>
    <select id="f-spend" name="spend">
      <option value="">Choose one</option>
      <option>Not spending yet</option>
      <option>Under $2,000</option>
      <option>$2,000 to $10,000</option>
      <option>$10,000 to $50,000</option>
      <option>Over $50,000</option>
    </select></div>
  <div class="field"><fieldset><legend>Who are your customers? <span class="opt">(optional)</span></legend>
    <span hidden data-extra="Customers" data-name="customers"></span>
    <div class="choices">
      <label class="choice"><input type="radio" name="customers" value="Businesses (B2B)"> Businesses (B2B)</label>
      <label class="choice"><input type="radio" name="customers" value="Consumers (B2C)"> Consumers (B2C)</label>
      <label class="choice"><input type="radio" name="customers" value="Both"> Both</label>
    </div></fieldset></div>
  <div class="field"><label for="f-message">Anything we should know? <span class="opt">(optional)</span></label>
    <textarea id="f-message" name="message" placeholder="Goals, problems, the city you serve"></textarea></div>
  {honeypot()}
  <button class="btn" type="submit">Request my free audit</button>
  <p class="form-status" role="alert" aria-live="polite"></p>
  <p class="form-note">We only use your details to reply to you.</p>
</form>"""

CONTACT_FORM = f"""<form class="form" data-lead-form="contact" novalidate>
  {text_field("name", "Full name", required=True, autocomplete="name")}
  {text_field("email", "Email", "email", required=True, autocomplete="email")}
  {text_field("phone", "Phone", "tel", autocomplete="tel")}
  <div class="field" data-required="message"><label for="f-message">How can we help?</label>
    <textarea id="f-message" name="message" aria-describedby="e-message"></textarea>
    <p class="error" id="e-message">Tell us a little about what you need.</p></div>
  {honeypot()}
  <button class="btn" type="submit">Send message</button>
  <p class="form-status" role="alert" aria-live="polite"></p>
</form>"""

PAGES["free-audit.html"] = page(
    "free-audit", "Free Google Ads & Facebook Ads Audit in Chicago | Leads Prosper",
    "Request a free Google Ads, Facebook Ads, or ChatGPT Ads account audit from Leads Prosper, a lead generation "
    "agency serving Chicago, NYC, and other metros.",
    f"""<section class="page-hero">
  <div class="wrap">
    {crumbs(("free-audit", "Free audit"))}
    <h1>Free account audit</h1>
    <p class="lead">Tell us about your ad accounts. We'll review them and show you where the budget is going,
    what's leaking, and what we'd change first.</p>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap form-wrap">
    {AUDIT_FORM}
    <div class="aside">
      <h2>What you get</h2>
      {checks(["A review of tracking: are leads counted correctly?",
               "Where spend goes versus where leads come from",
               "Wasted spend: search terms, audiences, and locations",
               "Landing page notes",
               "A short, prioritized list of fixes"])}
      <h2 style="margin-top:2rem">Not running ads yet?</h2>
      <p>Pick "Not running ads yet" and tell us what you sell and where. We'll suggest which channel to start with
      and a sensible test budget.</p>
      <p>Prefer email? Write to <a href="mailto:{SITE["email"]}">{SITE["email"]}</a>.</p>
    </div>
  </div>
</section>""",
    schemas=[service_schema("free-audit", "Ad account audit", "Free review of Google Ads, Facebook Ads, and ChatGPT Ads accounts.")],
)

PAGES["contact.html"] = page(
    "contact", "Contact Leads Prosper | Chicago Lead Generation Agency",
    "Contact Leads Prosper, a Chicago lead generation agency running Google Ads, Facebook Ads, and ChatGPT Ads "
    "for businesses in Chicago, NYC, and other metros.",
    f"""<section class="page-hero">
  <div class="wrap">
    {crumbs(("contact", "Contact"))}
    <h1>Contact us</h1>
    <p class="lead">Questions about ads, an existing account, or working together. Send a message and we'll reply by email.</p>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap form-wrap">
    {CONTACT_FORM}
    <div class="aside">
      <h2>Email</h2>
      <p><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></p>
      {f'<h2>Phone</h2><p><a href="{tel_href("tel")}">{e(SITE["phone"])}</a></p>' if SITE["phone"] else ""}
      <h2>Areas we serve</h2>
      <p>Chicago is home base. We also work with businesses in New York City and other major US metros.</p>
      <h2>Want an audit instead?</h2>
      <p><a href="/free-audit">Request a free account audit</a></p>
    </div>
  </div>
</section>""",
)

PAGES["404.html"] = page(
    "404", "Page not found | Leads Prosper",
    "The page you were looking for isn't here.",
    """<section class="notfound">
  <div class="wrap measure">
    <h1>Page not found</h1>
    <p class="lead">That page doesn't exist or has moved. Try one of these instead.</p>
    <ul>
      <li><a href="/">Home</a></li>
      <li><a href="/services">Services</a></li>
      <li><a href="/industries">Industries</a></li>
      <li><a href="/free-audit">Free account audit</a></li>
      <li><a href="/contact">Contact</a></li>
    </ul>
  </div>
</section>""",
    noindex=True, current="",
)

FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#13233f"/>'
           '<path d="M7 22 L13 16 L18 19 L25 10" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" '
           'stroke-linejoin="round"/><circle cx="25" cy="10" r="2.6" fill="#3fbf95"/></svg>\n')


def main():
    for name, content in PAGES.items():
        with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
            f.write(content)
    slugs = [n[:-5] for n in PAGES if n != "404.html"]
    slugs = ["" if s == "index" else s for s in slugs]
    items = "".join(f"  <url><loc>{abs_url(s)}</loc></url>\n" for s in slugs)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + items + "</urlset>\n")
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE['url']}/sitemap.xml\n")
    with open(os.path.join(ROOT, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(FAVICON)
    print(f"Built {len(PAGES)} pages, sitemap.xml, robots.txt, favicon.svg")


if __name__ == "__main__":
    main()
