#!/usr/bin/env python3
"""Scrape every US Mantality Health clinic into mantality.json.

Source (all public pages on mantalityhealth.com):
  1. https://mantalityhealth.com/locations/  - the locator page. Its Next.js
     flight payload (self.__next_f.push) holds one object per clinic:
     {"slug", "name", "addressLine1", "addressLine2": "City, ST 12345", "phone", ...}
  2. https://mantalityhealth.com/sitemap.xml - per-clinic pages
     /locations/<slug>/, used to catch clinics missing from the locator.
  3. https://mantalityhealth.com/locations/<slug>/ - each clinic page carries a
     schema.org "MedicalClinic" JSON-LD block (street, city, state, ZIP,
     country, phone). This is the preferred source for each row; the locator
     payload is the fallback.

Non-US clinics and ones marked "coming soon" / not yet open are skipped.
Standard library only (Python 3.9+). Run from the repo root:
    python3 pipeline/chains/mantality.py
"""

import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE = "https://mantalityhealth.com"
LOCATIONS_URL = BASE + "/locations/"
SITEMAP_URL = BASE + "/sitemap.xml"
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mantality.json")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
MIN_INTERVAL = 0.6  # seconds between requests (< 2 req/s)
MAX_CONSECUTIVE_ERRORS = 3

US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
    "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA",
    "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "PR",
}
NOT_OPEN_RE = re.compile(r"coming\s+soon|opening\s+soon|now\s+opening|temporarily\s+closed", re.I)
SLUG_RE = re.compile(r"/locations/([a-z0-9-]+)/?(?=[\"'<#?]|$)")


class Fetcher:
    """Polite GET helper: throttled, and aborts after repeated failures."""

    def __init__(self):
        self.last = 0.0
        self.errors = 0

    def get(self, url):
        wait = MIN_INTERVAL - (time.time() - self.last)
        if wait > 0:
            time.sleep(wait)
        self.last = time.time()
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8", errors="replace")
            self.errors = 0
            return body
        except (urllib.error.URLError, OSError) as exc:
            self.errors += 1
            print("  ! fetch failed %s: %s" % (url, exc), file=sys.stderr)
            if self.errors >= MAX_CONSECUTIVE_ERRORS:
                sys.exit("Stopping: %d consecutive fetch errors." % self.errors)
            return None


def flight_text(page):
    """Concatenate the Next.js RSC flight payload chunks of a page."""
    out = []
    for chunk in re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', page, re.S):
        try:
            out.append(json.loads('"' + chunk + '"'))
        except ValueError:
            pass
    return "".join(out)


def locator_entries(page):
    """Clinic objects ({"slug": ..., "addressLine1": ...}) from the locator payload."""
    text = flight_text(page)
    decoder = json.JSONDecoder()
    found = {}
    for m in re.finditer(r'\{"slug":"([a-z0-9-]+)"', text):
        try:
            obj, _ = decoder.raw_decode(text, m.start())
        except ValueError:
            continue
        if isinstance(obj, dict) and "addressLine1" in obj:
            found.setdefault(obj["slug"], obj)
    return found


def location_slugs(text):
    return {s for s in SLUG_RE.findall(text)}


def jsonld_clinic(page):
    """The MedicalClinic / LocalBusiness JSON-LD object on a clinic page, if any."""
    wanted = {"MedicalClinic", "LocalBusiness", "MedicalBusiness", "Physician", "HealthAndBeautyBusiness"}
    for raw in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', page, re.S):
        try:
            data = json.loads(html.unescape(raw.strip()))
        except ValueError:
            continue
        items = data if isinstance(data, list) else data.get("@graph", [data])
        for item in items:
            if not isinstance(item, dict):
                continue
            types = item.get("@type")
            types = set(types) if isinstance(types, list) else {types}
            if types & wanted and isinstance(item.get("address"), dict):
                return item
    return None


def fmt_phone(raw):
    if not raw:
        return None
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        return raw.strip() or None
    return "(%s) %s-%s" % (digits[:3], digits[3:6], digits[6:])


def parse_city_line(line):
    """'West Des Moines, IA 50266' -> ('West Des Moines', 'IA', '50266')."""
    m = re.match(r"\s*(.+?),\s*([A-Za-z]{2})\.?\s+(\d{5})(?:-\d{4})?\s*$", line or "")
    if m:
        return m.group(1).strip(), m.group(2).upper(), m.group(3)
    m = re.match(r"\s*(.+?),\s*([A-Za-z]{2})\.?\s*$", line or "")
    if m:
        return m.group(1).strip(), m.group(2).upper(), None
    return None, None, None


def zip_from_page(page, street):
    """Last resort: find '<street> ... ST 12345' in the clinic page text."""
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", page)))
    idx = text.find(street)
    if idx < 0:
        return None
    m = re.search(r"\b[A-Z]{2}\s+(\d{5})\b", text[idx: idx + 200])
    return m.group(1) if m else None


def build_row(slug, entry, page):
    """Merge clinic-page JSON-LD (preferred) with the locator entry (fallback)."""
    entry = entry or {}
    clinic = jsonld_clinic(page) if page else None
    addr = (clinic or {}).get("address") or {}

    city, state, zipcode = parse_city_line(entry.get("addressLine2", ""))
    street = (addr.get("streetAddress") or entry.get("addressLine1") or "").strip()
    city = (addr.get("addressLocality") or city or "").strip()
    state = (addr.get("addressRegion") or state or "").strip().upper()
    zipcode = (str(addr.get("postalCode") or "") or zipcode or "").strip()[:5]
    country = (addr.get("addressCountry") or "US")
    if isinstance(country, dict):
        country = country.get("name") or country.get("addressCountry") or "US"
    country = str(country).strip().upper()

    if not re.fullmatch(r"\d{5}", zipcode or "") and page and street:
        zipcode = zip_from_page(page, street) or zipcode

    name = (clinic or {}).get("name") or ("Mantality Health " + entry["name"] if entry.get("name") else None)
    status_blob = " ".join(str(v) for v in (entry.get("name"), entry.get("status"),
                                            entry.get("comingSoon"), (clinic or {}).get("name")) if v)
    return {
        "chain": "mantality",
        "name": (name or "Mantality Health %s, %s" % (city, state)).strip(),
        "address": street,
        "city": city,
        "state": state,
        "zip": zipcode,
        "phone": fmt_phone((clinic or {}).get("telephone") or entry.get("phone")),
        "url": (clinic or {}).get("url") or "%s/locations/%s/" % (BASE, slug),
        "_country": country,
        "_not_open": bool(NOT_OPEN_RE.search(status_blob)) or entry.get("comingSoon") is True,
    }


def main():
    fetcher = Fetcher()

    print("Fetching locator page", LOCATIONS_URL)
    locator = fetcher.get(LOCATIONS_URL)
    if not locator:
        sys.exit("Could not load the locations page.")
    entries = locator_entries(locator)
    slugs = set(entries) | location_slugs(locator)

    print("Fetching sitemap", SITEMAP_URL)
    sitemap = fetcher.get(SITEMAP_URL)
    if sitemap:
        slugs |= {s for s in re.findall(r"<loc>%s/locations/([a-z0-9-]+)/</loc>" % re.escape(BASE), sitemap)}
    print("  %d clinics in locator payload, %d slugs total" % (len(entries), len(slugs)))

    rows, skipped = [], []
    for slug in sorted(slugs):
        page = fetcher.get("%s/locations/%s/" % (BASE, slug))
        if page is None and slug not in entries:
            skipped.append((slug, "page unavailable, not in locator"))
            continue
        row = build_row(slug, entries.get(slug), page)
        if row["_not_open"]:
            skipped.append((slug, "not open yet"))
            continue
        if row["_country"] not in ("US", "USA", "UNITED STATES") or row["state"] not in US_STATES:
            skipped.append((slug, "non-US (%s, %s)" % (row["_country"], row["state"])))
            continue
        if not row["address"] or not row["city"]:
            skipped.append((slug, "no street address"))
            continue
        rows.append({k: v for k, v in row.items() if not k.startswith("_")})

    # De-duplicate on normalized street + ZIP.
    seen, unique = set(), []
    for r in rows:
        key = (re.sub(r"[^a-z0-9]", "", r["address"].lower()), r["zip"])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    unique.sort(key=lambda r: (r["state"], r["city"], r["address"]))

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(unique, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print("Wrote %d US locations to %s" % (len(unique), OUT_PATH))
    for slug, why in skipped:
        print("  skipped %s: %s" % (slug, why))
    missing = [r["url"] for r in unique if not re.fullmatch(r"\d{5}", r["zip"] or "")]
    if missing:
        print("  WARNING missing ZIP:", ", ".join(missing))


if __name__ == "__main__":
    main()
