#!/usr/bin/env python3
"""Build the state and city pages search engines index (trtledger.com/trt/...).

Inputs:  data.json (online clinics, chains), clinics/*.json (in-person directory)
Writes:  trt/index.html                      every state
         trt/<state>/index.html              online options + in-person clinics by city
         trt/<state>/<city>/index.html       cities with a TRT or hormone clinic, or 8+ listings
         sitemap.xml, robots.txt
         index.html                          the "Browse by state" links (between markers)
Every number on a page is computed from the same data the main site uses, with the same
first-year cost formula and default assumptions, so the pages and the site always agree.
Usage: python3 pipeline/build_pages.py        (SITE_URL env sets canonical URLs)
"""
import datetime as dt
import html
import json
import math
import os
import re
import shutil
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "trt"
SITE = os.environ.get("SITE_URL", "https://trtledger.com").rstrip("/")
NEARBY_MILES = 30
ASSUME = {"medCost": 40, "labCost": 150, "labsPerYear": 4}   # the site's default assumptions
NAMES = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
         "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia",
         "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
         "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts",
         "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
         "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
         "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
         "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
         "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
         "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"}
CAT_ORDER = ["trt", "hormone", "urology", "endocrinology"]
CAT_HEAD = {"trt": "TRT and men's health clinics", "hormone": "Hormone clinics",
            "urology": "Urologists", "endocrinology": "Endocrinologists"}
CAT_SHORT = {"trt": "TRT / men's clinic", "hormone": "Hormone clinic", "urology": "Urology", "endocrinology": "Endocrinology"}
e = html.escape


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def usd(n):
    return f"${round(n):,}"


def fmt_date(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def miles(a, b):
    t = math.pi / 180
    x = math.sin((b[0] - a[0]) * t / 2) ** 2 + math.cos(a[0] * t) * math.cos(b[0] * t) * math.sin((b[1] - a[1]) * t / 2) ** 2
    return 7917.6 * math.asin(math.sqrt(x))


# ---- the same rules the site uses (assets/app.js: servesState, yearOne) ----
def serves(c, st):
    s = c.get("states") or ""
    if re.search(r"not listed", s, re.I):
        return None
    if re.search(r"all except", s, re.I):
        return st not in re.split(r"except", s, flags=re.I)[1]
    return st in re.split(r",\s*", s)


def year_one(c):
    if c.get("clinicYear1Estimate"):
        return c["clinicYear1Estimate"], False
    total, est = (c.get("monthly") or 0) * 12 + (c.get("intakeFee") or 0), False
    if not c.get("medsIncluded"):
        total, est = total + ASSUME["medCost"] * 12, True
    if c.get("labsIncluded") is False:
        total += c.get("labFee") or ASSUME["labCost"] * ASSUME["labsPerYear"]
        est = est or not c.get("labFee")
    if c.get("labsIncluded") is None:
        total, est = total + ASSUME["labCost"] * ASSUME["labsPerYear"], True
    return total, est


def is_trt(c):
    return not (len(c["forms"]) == 1 and c["forms"][0] == "enclomiphene")


# ---- page shell ----
THEME_HEAD = ("<script>try{const t=localStorage.getItem('trtTheme');if(t)document.documentElement.dataset.theme=t}catch(e){}</script>")
THEME_BTN_JS = ("<script>document.getElementById('themeBtn').addEventListener('click',()=>{const r=document.documentElement;"
                "const dark=r.dataset.theme?r.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;"
                "r.dataset.theme=dark?'light':'dark';try{localStorage.setItem('trtTheme',r.dataset.theme)}catch(e){}});</script>")
LOGO = ('<svg viewBox="0 0 28 28" aria-hidden="true"><rect width="28" height="28" rx="8" fill="var(--accent)"/>'
        '<path d="M8 9.5h12M8 14h12M8 18.5h7" stroke="var(--accent-ink)" stroke-width="2.2" stroke-linecap="round"/></svg>'
        '<span>TRT<em>Ledger</em></span>')


def page(path, title, desc, crumbs, body, updated, jsonld):
    depth = len(Path(path).parts) - 1
    root = "../" * depth
    url = f"{SITE}/{Path(path).parent.as_posix()}/".replace("/./", "/")
    crumb_html = " <span aria-hidden=\"true\">›</span> ".join(
        f'<a href="{root}{href}">{e(name)}</a>' if href is not None else f"<span>{e(name)}</span>" for name, href in crumbs)
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": name,
         "item": (f"{SITE}/{href}".rstrip("/") + "/") if href is not None else url}
        for i, (name, href) in enumerate(crumbs)]}] + jsonld
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">
{THEME_HEAD}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{root}assets/site.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="wrap topbar">
    <a class="logo" href="{root}" aria-label="TRT Ledger home">{LOGO}</a>
    <nav class="nav" aria-label="Sections">
      <a href="{root}#find">Find clinics</a>
      <a href="{root}#overpaying">Am I overpaying?</a>
      <a href="{root}#labs">Lab tests</a>
      <a href="{root}trt/">Browse by state</a>
      <a href="{root}#alerts">Price alerts</a>
    </nav>
    <button type="button" class="icon-btn" id="themeBtn" aria-label="Switch color theme">
      <svg class="sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/></svg>
      <svg class="moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>
    </button>
  </div>
</header>
<main id="main" class="dir-page">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb">{crumb_html}</nav>
{body}
  </div>
</main>
<footer class="foot">
  <div class="wrap foot-grid">
    <div>
      <a class="logo" href="{root}">{LOGO}</a>
      <p>An independent price guide. Clinics can't pay to be listed or ranked.</p>
    </div>
    <div>
      <h3>How we get our data</h3>
      <ul>
        <li>Online clinic prices are read from each clinic's own website every week.</li>
        <li>In-person clinics come from the federal <a href="https://npiregistry.cms.hhs.gov/" target="_blank" rel="noopener">NPI registry</a> and clinic chains' own location lists, refreshed monthly.</li>
      </ul>
      <p class="note">Page updated {fmt_date(updated)}.</p>
    </div>
    <div>
      <h3>Important</h3>
      <p>TRT Ledger is not medical advice and is not a pharmacy or clinic. Prices change; confirm with the provider before you pay. Testosterone is a prescription medication — talk to a licensed clinician.</p>
    </div>
  </div>
</footer>
{THEME_BTN_JS}
</body>
</html>
"""


def write(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


# ---- wording helpers ----
def plural(n, one, many=None):
    return f"{n:,} {one if n == 1 else (many or one + 's')}"


def mix_sentence(counts):
    """'5 TRT or men's health clinics, 1 hormone clinic and 24 urology practices' (zero counts left out)."""
    parts = [plural(counts[c], *w) for c, w in (
        ("trt", ("TRT or men's health clinic", "TRT or men's health clinics")),
        ("hormone", ("hormone clinic",)),
        ("urology", ("urology practice",)),
        ("endocrinology", ("endocrinology practice",))) if counts[c]]
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


# ---- city grouping: one page per real city, whatever the spelling ----
ABBREV = [(r"\bst\.?\s", "saint "), (r"\bste\.?\s", "sainte "), (r"\bft\.?\s", "fort "), (r"\bmt\.?\s", "mount "),
          (r"\bpt\.?\s", "port "), (r"\btwp\b\.?", "township"), (r"\bhts\b\.?", "heights"), (r"\bjct\b\.?", "junction")]
ALIASES = {("NY", "new york city"): "new york", ("NY", "manhattan"): "new york", ("TX", "sugarland"): "sugar land"}


def city_key(city, st):
    k = city.lower().strip()
    k = re.sub(r"[,\s]+(" + st.lower() + r"|d\.?c\.?)$", "", k)        # "Boston, Ma", "Washington Dc"
    for pat, rep in ABBREV:
        k = re.sub(pat, rep, k + " ").strip()
    k = re.sub(r"[^a-z0-9 ]", "", k)
    k = re.sub(r"\s+", " ", k).strip()
    return ALIASES.get((st, k), k)


def edit_distance(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def median_point(rows):
    lats, lons = sorted(r["lat"] for r in rows), sorted(r["lon"] for r in rows)
    return lats[len(lats) // 2], lons[len(lons) // 2]


def group_cities(rows_by_state):
    cities = {}
    for st, rs in rows_by_state.items():
        groups = defaultdict(list)
        for r in rs:
            if r.get("city"):
                groups[city_key(r["city"], st)].append(r)
        # Fold small misspelled groups ("Astin", "El Pas") into a big same-state city close by
        keys = sorted(groups, key=lambda k: -len(groups[k]))
        for k in keys[::-1]:
            if len(groups.get(k, [])) > 2:
                continue
            for big in keys:
                if big == k or big not in groups or len(groups[big]) < 3:
                    continue
                if (edit_distance(k.replace(" ", ""), big.replace(" ", "")) <= 2 and min(len(k), len(big)) >= 5
                        and miles(median_point(groups[k]), median_point(groups[big])) < 15):
                    groups[big] += groups.pop(k)
                    break
        for k, crs in groups.items():
            if not k:
                continue
            center = median_point(crs)
            # A record whose ZIP puts it far from the rest of its city has a wrong address; keep it off the page
            crs = [r for r in crs if miles(center, (r["lat"], r["lon"])) < 40]
            if not crs:
                continue
            name = Counter(r["city"] for r in crs if not re.search(r"\b(St|Ft|Mt|Pt)\b\.?", r["city"])).most_common(1)
            name = name[0][0] if name else Counter(r["city"] for r in crs).most_common(1)[0][0]
            name = re.sub(r"[,\s]+(" + st + r"|Dc|D\.c\.)$", "", name, flags=re.I)
            counts = Counter(r["cats"][0] for r in crs)
            cities[(st, slug(k))] = {"st": st, "slug": slug(k), "name": name, "rows": crs, "center": median_point(crs),
                                     "counts": counts, "focus": counts["trt"] + counts["hormone"]}
    return cities


# ---- page sections ----
def online_rows(st, data):
    rows = []
    for c in data["clinics"]:
        if not is_trt(c):
            continue
        s = serves(c, st)
        if s is False:
            continue
        cost, est = year_one(c)
        rows.append((0 if s else 1, cost, c, s, est))
    rows.sort(key=lambda r: (r[0], r[1]))
    return rows


def compare_link(root, st, anchor="find"):
    return f"{root}?state={st}#{anchor}"


def online_table(st, data, root):
    rows = online_rows(st, data)
    if not rows:
        return ""
    yn = lambda v, y, n: y if v is True else n if v is False else "Not stated"
    trs = []
    for _, cost, c, s, est in rows:
        tags = "".join([
            "" if s else '<span class="tag warn">Check state</span>',
            "" if c.get("verified") else '<span class="tag warn">Unverified price</span>',
            '<span class="tag model">Estimate</span>' if est else ""])
        monthly = usd(c["monthly"]) + "/mo" if c.get("monthly") else e(c.get("monthlyLabel") or "—")
        trs.append(f"""<tr><th scope="row"><a href="{e(c['url'])}" target="_blank" rel="noopener nofollow">{e(c['name'])}</a> {tags}</th>
        <td class="num">{usd(cost)}</td><td>{monthly}</td><td>{yn(c.get('labsIncluded'), 'Included', 'Extra')}</td>
        <td>{yn(c.get('medsIncluded'), 'Included', 'Extra')}</td><td>{e(c['commitment'])}</td></tr>""")
    return f"""
    <section class="dir-section" aria-labelledby="online">
      <h2 id="online">Online TRT clinics that serve {e(NAMES[st])}</h2>
      <p class="sub">{online_lead(st, rows)}</p>
      <div class="panel tablewrap">
        <table class="dir-table">
          <thead><tr><th scope="col">Clinic</th><th scope="col">Est. first year</th><th scope="col">Price</th><th scope="col">Labs</th><th scope="col">Medication</th><th scope="col">Contract</th></tr></thead>
          <tbody>{''.join(trs)}</tbody>
        </table>
      </div>
      <p class="note">First-year estimates include startup fees. Where a clinic doesn't publish a cost we assume ${ASSUME['medCost']}/month for medication and ${ASSUME['labCost']} lab panels {ASSUME['labsPerYear']} times a year ("Estimate").
        Prices checked {fmt_date(data['updated'])}. <a href="{compare_link(root, st)}">Compare them in detail</a> or <a href="{compare_link(root, st, 'overpaying')}">check if you're overpaying</a>.</p>
    </section>"""


def online_lead(st, rows):
    conf = [r for r in rows if r[0] == 0]
    name = NAMES[st]
    if len(conf) == 1:
        lead = f"{e(conf[0][2]['name'])} is the only online clinic that confirms it treats patients in {name}; its first-year cost is about <b>{usd(conf[0][1])}</b>."
    elif conf:
        lead = f"{len(conf)} online clinics confirm they treat patients in {name}; the lowest first-year cost is about <b>{usd(conf[0][1])}</b> at {e(conf[0][2]['name'])}."
    else:
        lead = f"No online clinic we track confirms it treats patients in {name}."
    unsure = len(rows) - len(conf)
    if unsure:
        lead += f" {plural(unsure, 'more clinic', 'more clinics')} don't publish which states they serve." if unsure > 1 else " 1 more clinic doesn't publish which states it serves."
    return lead


def online_summary(st, data, root):
    """City pages: a short pointer to the state's full table instead of repeating it."""
    rows = online_rows(st, data)
    conf = [r for r in rows if r[0] == 0][:3]
    if not rows:
        return ""
    items = "".join(f'<li><b>{e(c["name"])}</b> — about {usd(cost)} in the first year'
                    f'{" (estimate)" if est else ""}</li>' for _, cost, c, s, est in conf)
    return f"""
    <section class="dir-section" aria-labelledby="online">
      <h2 id="online">Online TRT in {e(NAMES[st])}</h2>
      <p class="sub">{online_lead(st, rows)}</p>
      {f'<ul class="chainlist">{items}</ul>' if items else ''}
      <p class="note"><a href="../#online">See all {plural(len(rows), 'online clinic')} for {e(NAMES[st])}</a> ·
        <a href="{compare_link(root, st)}">compare them in detail</a> · prices checked {fmt_date(data['updated'])}.</p>
    </section>"""


def clinic_li(r, chains):
    where = ", ".join(x for x in [r.get("addr"), r.get("city"), f"{r['st']} {r['zip']}"] if x)
    maps = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote_plus(f"{r['name']}, {where}")
    phone = r.get("phone")
    tel = f' · <a href="tel:+1{re.sub(r"[^0-9]", "", phone)[-10:]}">{e(phone)}</a>' if phone else ""
    site = f' · <a href="{e(r["url"])}" target="_blank" rel="noopener nofollow">Website</a>' if r.get("url") else ""
    docs = ""
    if r.get("ndocs", 0) > 1:
        docs = f'<div class="row">{r["ndocs"]} providers: {e(", ".join(r["docs"][:3]))}{", …" if r["ndocs"] > 3 else ""}</div>'
    elif r.get("ndocs") == 1 and r["docs"][0] != r["name"]:
        docs = f'<div class="row">{e(r["docs"][0])}</div>'
    chain = chains.get(r.get("chain"))
    price = (f'<div class="row"><b>Pricing:</b> {e(chain["pricing"])}</div>'
             if chain and not chain["pricing"].startswith("Not published") else "")
    tags = " ".join(f'<span class="tag {"trt" if c == "trt" else "model"}">{CAT_SHORT[c]}</span>' for c in r["cats"])
    return (f'<li class="near"><div><b>{e(r["name"])}</b> {tags}</div>'
            f'<div class="row">{e(where)}{tel} · <a href="{e(maps)}" target="_blank" rel="noopener">Map</a>{site}</div>{docs}{price}</li>')


def grouped_clinics(rows, chains):
    out = []
    for cat in CAT_ORDER:
        group = sorted((r for r in rows if r["cats"][0] == cat), key=lambda r: r["name"])
        if group:
            out.append(f'<h3 class="subhead">{CAT_HEAD[cat]} <span class="count">{len(group)}</span></h3>'
                       f'<ol class="nearlist panel">{"".join(clinic_li(r, chains) for r in group)}</ol>')
    return "".join(out)


def faq_block(items):
    body = "".join(f"<details class=\"faq\"><summary>{e(q)}</summary><p>{a}</p></details>" for q, a in items)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re.sub(r"<[^>]+>", "", a))}}
        for q, a in items]}
    return f'<section class="dir-section" aria-labelledby="faq"><h2 id="faq">Common questions</h2>{body}</section>', ld


def cost_answer(st, rows, chains_here):
    conf = [r for r in rows if r[0] == 0]
    parts = []
    if conf:
        parts.append(f"Online clinics that confirm they serve {NAMES[st]} start at about {usd(conf[0][1])} for the first year "
                     f"({e(conf[0][2]['name'])}), including startup fees.")
    elif rows:
        parts.append(f"Online clinics that may serve {NAMES[st]} (they don't publish their states) start at about "
                     f"{usd(rows[0][1])} for the first year ({e(rows[0][2]['name'])}), including startup fees.")
    for ch in chains_here:
        if not ch["pricing"].startswith("Not published"):
            parts.append(f"In person, {e(ch['name'])} lists {e(ch['pricing'])}.")
    if not parts:
        parts.append("Most in-person clinics don't publish prices, so call and ask before your first visit.")
    parts.append("Insurance may cover part of the cost when low testosterone is diagnosed; cash-pay clinics usually don't bill insurance.")
    return " ".join(parts)


def online_answer(st, rows):
    conf = [r for r in rows if r[0] == 0]
    if len(conf) == 1:
        return f"Yes. {e(conf[0][2]['name'])} confirms it treats patients in {NAMES[st]}."
    if conf:
        return (f"Yes. {e(conf[0][2]['name'])} and {plural(len(conf) - 1, 'other online clinic')} confirm they treat "
                f"patients in {NAMES[st]}.")
    return f"Some online clinics may serve {NAMES[st]} but don't publish their states; confirm with them before you sign up."


LABS_ANSWER = ("Clinics generally require recent blood tests showing low testosterone before they prescribe. "
               "You can order your own lab tests without a doctor visit in most states.")


def city_has_page(c, state_total):
    if c["focus"] >= 1 and len(c["rows"]) >= 2:
        return len(c["rows"]) < 0.9 * state_total or state_total < 20
    return len(c["rows"]) >= 8 and len(c["rows"]) < 0.9 * state_total


def main():
    data = json.loads((ROOT / "data.json").read_text())
    chains = {c["id"]: c for c in data.get("inPerson", [])}
    rows = []
    for f in (ROOT / "clinics").glob("[0-9]*.json"):
        rows += json.loads(f.read_text())
    rows = [r for r in rows if r.get("st") in NAMES]
    today = data["updated"]

    by_state = defaultdict(list)
    for r in rows:
        by_state[r["st"]].append(r)
    cities = group_cities(by_state)
    for c in cities.values():
        c["page"] = city_has_page(c, len(by_state[c["st"]]))

    if OUT.exists():
        shutil.rmtree(OUT)
    sitemap = [f"{SITE}/", f"{SITE}/trt/"]
    city_pages = [c for c in cities.values() if c["page"]]

    # ---- city pages ----
    for c in city_pages:
        st, name, crs, counts = c["st"], c["name"], c["rows"], c["counts"]
        path = f"trt/{slug(NAMES[st])}/{c['slug']}/index.html"
        root = "../../../"
        rows_online = online_rows(st, data)
        near = sorted(((miles(c["center"], o["center"]), o) for o in city_pages if o is not c), key=lambda x: x[0])
        near = [(d, o) for d, o in near if d < NEARBY_MILES][:10]
        near_html = ("<section class=\"dir-section\" aria-labelledby=\"nearby\"><h2 id=\"nearby\">Nearby cities</h2><ul class=\"citylist\">"
                     + "".join(f'<li><a href="../../{slug(NAMES[o["st"]])}/{o["slug"]}/">{e(o["name"])}, {o["st"]}</a> '
                               f'<span class="note">{round(d)} mi · {plural(len(o["rows"]), "listing")}</span></li>' for d, o in near)
                     + "</ul></section>") if near else ""
        chains_here = [ch for ch in chains.values() if any(r.get("chain") == ch["id"] for r in crs)]
        summary = f"{plural(len(crs), 'clinic listing')} in {name}: {mix_sentence(counts)}."
        focus = (f" {c['focus']} of them {'focuses' if c['focus'] == 1 else 'focus'} on testosterone or hormones." if c["focus"] else
                 " None are dedicated TRT clinics; some urologists and endocrinologists prescribe testosterone, so call and ask.")
        faq, faq_ld = faq_block([
            (f"How much does TRT cost in {name}?", cost_answer(st, rows_online, chains_here)),
            (f"Where can I get TRT in {name}, {st}?",
             e(summary) + " Urologists and endocrinologists can prescribe testosterone, but not all of them offer TRT — call and ask."),
            (f"Can I get TRT online in {NAMES[st]}?", online_answer(st, rows_online)),
            ("Do I need blood work before starting TRT?", LABS_ANSWER),
        ])
        conf = [r for r in rows_online if r[0] == 0]
        title = f"TRT Clinics & Doctors in {name}, {st}"
        desc = (f"{plural(len(crs), 'TRT, hormone, urology and endocrinology listing')} in {name}, {NAMES[st]}"
                + (f", plus online TRT from about {usd(conf[0][1])} for the first year." if conf else ".")
                + " Addresses, phone numbers and sourced prices.")
        body = f"""
    <header class="dir-head">
      <h1>TRT clinics and doctors in {e(name)}, {st}</h1>
      <p class="lede">{e(summary)}{e(focus)}</p>
      <div class="dir-cta"><a class="cta-btn" href="{compare_link(root, st, 'overpaying')}">Am I overpaying?</a><a class="btn-secondary" href="{compare_link(root, st)}">Compare online clinics</a></div>
    </header>
    <section class="dir-section" aria-labelledby="inperson">
      <h2 id="inperson">In-person clinics in {e(name)}</h2>
      <p class="sub">From the federal NPI registry and clinic chains' own location lists. Not every urologist or endocrinologist offers TRT — call and ask.</p>
      {grouped_clinics(crs, chains)}
    </section>
    {online_summary(st, data, root)}
    {near_html}
    {faq}"""
        write(path, page(path, title, desc, [("TRT Ledger", ""), ("Browse by state", "trt/"),
                                             (NAMES[st], f"trt/{slug(NAMES[st])}/"), (name, None)], body, today, [faq_ld]))
        sitemap.append(f"{SITE}/trt/{slug(NAMES[st])}/{c['slug']}/")

    # ---- state pages ----
    state_total = {}
    for st in sorted(NAMES):
        rs = by_state.get(st, [])
        path = f"trt/{slug(NAMES[st])}/index.html"
        root = "../../"
        counts = Counter(r["cats"][0] for r in rs)
        rows_online = online_rows(st, data)
        st_cities = sorted((c for c in cities.values() if c["st"] == st), key=lambda c: -len(c["rows"]))
        with_page = [c for c in st_cities if c["page"]]
        others = [c for c in st_cities if not c["page"]]
        city_html = ("<ul class=\"citylist cols\">" + "".join(
            f'<li><a href="{c["slug"]}/">{e(c["name"])}</a> <span class="note">{len(c["rows"])}</span></li>' for c in with_page) + "</ul>"
                     if with_page else "")
        if others:
            names_ = sorted(others, key=lambda c: c["name"])
            city_html += (f'<p class="note">{"Also " if with_page else ""}{plural(len(others), "other town")} with fewer listings'
                          f'{" (" + ", ".join(e(c["name"]) for c in names_[:60]) + ("…" if len(names_) > 60 else "") + ")"}. '
                          f'<a href="{compare_link(root, st)}">Search by ZIP code</a> to see them.</p>')
        trt_rows = sorted((r for r in rs if r["cats"][0] in ("trt", "hormone")), key=lambda r: (r.get("city", ""), r["name"]))
        trt_html = (f'<ol class="nearlist panel">{"".join(clinic_li(r, chains) for r in trt_rows)}</ol>' if trt_rows
                    else f'<p class="note">No dedicated TRT or hormone clinics are listed in {NAMES[st]} yet. Online clinics (above) serve the state, '
                         f'and some of the urologists and endocrinologists on the city pages prescribe testosterone — call and ask.</p>')
        chains_here = [ch for ch in chains.values() if ch["locations"].get(st)]
        chain_items = []
        for ch in chains_here:
            listed = sum(1 for r in rs if r.get("chain") == ch["id"])
            n = ch["locations"][st]
            note = "" if listed >= n else f" (from the chain's own list; {plural(listed, 'is', 'are')} in our directory below)" if listed else " (from the chain's own list; not yet in our directory below)"
            chain_items.append(
                f'<li><b>{e(ch["name"])}</b> — {plural(n, "location")} in {NAMES[st]}{note}'
                + (f' · {e(ch["pricing"])}' if not ch["pricing"].startswith("Not published") else "")
                + f' · <a href="{e(ch["locatorUrl"])}" target="_blank" rel="noopener nofollow">Locations</a></li>')
        summary = (f"{plural(len(rs), 'clinic listing')} across {plural(len(st_cities), 'city', 'cities')}: {mix_sentence(counts)}."
                   if rs else f"No in-person clinics are listed in {NAMES[st]} yet.")
        state_total[st] = len(rs)
        faq, faq_ld = faq_block([
            (f"How much does TRT cost in {NAMES[st]}?", cost_answer(st, rows_online, chains_here)),
            (f"Can I get TRT online in {NAMES[st]}?", online_answer(st, rows_online)),
            ("Do I need blood work before starting TRT?", LABS_ANSWER),
        ])
        conf = [r for r in rows_online if r[0] == 0]
        title = f"TRT Clinics in {NAMES[st]}: Online Prices & Local Clinics"
        desc = (f"Online TRT clinics that serve {NAMES[st]}"
                + (f" from about {usd(conf[0][1])} for the first year" if conf else "")
                + f", and {plural(len(rs), 'in-person TRT, hormone, urology and endocrinology listing')} by city. Sourced prices.")
        body = f"""
    <header class="dir-head">
      <h1>TRT in {e(NAMES[st])}</h1>
      <p class="lede">{e(summary)}</p>
      <div class="dir-cta"><a class="cta-btn" href="{compare_link(root, st)}">Find clinics near my ZIP</a><a class="btn-secondary" href="{compare_link(root, st, 'overpaying')}">Am I overpaying?</a></div>
    </header>
    {online_table(st, data, root)}
    <section class="dir-section" aria-labelledby="cities">
      <h2 id="cities">Clinics by city</h2>
      {city_html or f'<p class="note">No in-person clinics are listed in {NAMES[st]} yet.</p>'}
    </section>
    {'<section class="dir-section" aria-labelledby="chains"><h2 id="chains">Clinic chains in ' + e(NAMES[st]) + '</h2><ul class="chainlist">' + "".join(chain_items) + '</ul></section>' if chain_items else ''}
    <section class="dir-section" aria-labelledby="dedicated">
      <h2 id="dedicated">TRT and hormone clinics in {e(NAMES[st])}</h2>
      {trt_html}
    </section>
    {faq}"""
        write(path, page(path, title, desc, [("TRT Ledger", ""), ("Browse by state", "trt/"), (NAMES[st], None)],
                         body, today, [faq_ld]))
        sitemap.append(f"{SITE}/trt/{slug(NAMES[st])}/")

    # ---- all-states index ----
    links = "".join(f'<li><a href="{slug(NAMES[st])}/">{e(NAMES[st])}</a> <span class="note">{state_total[st]:,}</span></li>'
                    for st in sorted(NAMES, key=lambda s: NAMES[s]))
    body = f"""
    <header class="dir-head">
      <h1>TRT clinics by state</h1>
      <p class="lede">Online TRT clinics that serve each state, with true first-year costs, and {plural(len(rows), 'in-person TRT, hormone, urology and endocrinology listing')}
        in {plural(len(cities), 'city', 'cities')} across the 50 states and DC, with a guide for {plural(len(city_pages), 'city', 'cities')}.</p>
    </header>
    <section class="dir-section"><ul class="citylist cols">{links}</ul></section>"""
    write("trt/index.html", page("trt/index.html", "TRT Clinics by State: Prices & Locations | TRT Ledger",
                                 "Find TRT clinics in every U.S. state: online clinics with sourced first-year costs and in-person clinics by city.",
                                 [("TRT Ledger", ""), ("Browse by state", None)], body, today, []))

    # ---- sitemap, robots, homepage links ----
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>{e(u)}</loc><lastmod>{today}</lastmod></url>\n" for u in sitemap) + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    index = (ROOT / "index.html").read_text()
    block = ("<!-- states:start -->\n" + "".join(
        f'          <li><a href="trt/{slug(NAMES[st])}/">{e(NAMES[st])}</a></li>\n' for st in sorted(NAMES, key=lambda s: NAMES[s]))
        + "          <!-- states:end -->")
    index = re.sub(r"<!-- states:start -->.*?<!-- states:end -->", lambda m: block, index, flags=re.S)
    (ROOT / "index.html").write_text(index)
    print(f"Wrote {len(city_pages)} city pages, {len(NAMES)} state pages, sitemap with {len(sitemap)} URLs")


if __name__ == "__main__":
    main()
