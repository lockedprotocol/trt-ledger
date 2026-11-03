#!/usr/bin/env python3
"""Scrape all US Low T Center clinic locations.

Source: https://lowtcenter.com/locations/
  The locator page embeds every clinic as an inline JS array
  (`var locationData = [...]`) with name, address, city, state, zipcode,
  phone_number, coming_soon and url fields. That single page is the data source.
  https://lowtcenter.com/locations-sitemap.xml is read only to swap the
  page's stale/redirecting clinic URLs (e.g. /locations/alliance-4/) for their
  canonical form. If a clinic has a street address but no ZIP, its own page is
  fetched to look for one.

Output: pipeline/chains/low-t-center.json (next to this script), a JSON array of
  {"chain", "name", "address", "city", "state", "zip", "phone", "url"}.

Python 3.9+, standard library only. Run from anywhere:
  python3 pipeline/chains/low-t-center.py
"""

import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

CHAIN = "low-t-center"
BASE = "https://lowtcenter.com"
LOCATOR_URL = BASE + "/locations/"
SITEMAP_URL = BASE + "/locations-sitemap.xml"
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), CHAIN + ".json")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
MIN_INTERVAL = 1.0  # seconds between requests (well under 2 req/s)
MAX_ERRORS = 3      # stop fetching after this many failed requests

US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
    "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA",
    "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "PR",
}


class Fetcher:
    """Rate-limited GET with a small error budget."""

    def __init__(self):
        self.last = 0.0
        self.errors = 0

    def get(self, url):
        if self.errors >= MAX_ERRORS:
            raise RuntimeError("too many failed requests; stopping")
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
                return resp.read().decode("utf-8", "replace")
        except (urllib.error.URLError, OSError) as exc:
            self.errors += 1
            print("WARN fetch failed %s: %s" % (url, exc), file=sys.stderr)
            return None


def clean(value):
    """Unescape HTML entities and collapse whitespace; '' for None."""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", html.unescape(str(value))).strip()


def extract_location_data(page):
    """Return the list assigned to `locationData` in the locator page's inline JS."""
    m = re.search(r"\b(?:var|let|const)\s+locationData\s*=\s*;?\s*(?=\[)", page)
    if not m:
        raise RuntimeError("locationData array not found on %s" % LOCATOR_URL)
    data, _ = json.JSONDecoder().raw_decode(page, m.end())
    if not isinstance(data, list):
        raise RuntimeError("locationData is not a list")
    return data


def slug_of(url):
    return urllib.parse.urlparse(url).path.rstrip("/").split("/")[-1].lower()


def base_slug(slug):
    """'alliance-4' -> 'alliance', 'synergenx-burr-ridge-2' -> 'synergenx-burr-ridge'."""
    return re.sub(r"-\d+$", "", slug)


def load_canonical_urls(fetcher):
    """Map clinic slug (and its de-suffixed form) -> canonical URL from the sitemap."""
    xml = fetcher.get(SITEMAP_URL)
    if not xml:
        return {}
    canon = {}
    for loc in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml):
        if "/locations/" not in loc or re.search(r"\.(jpe?g|png|webp|gif|svg)$", loc, re.I):
            continue
        slug = slug_of(loc)
        canon.setdefault(slug, loc)
        canon.setdefault(base_slug(slug), loc)
    return canon


def normalize_url(raw, name, canon):
    """Absolute URL for a clinic, preferring the sitemap's canonical form."""
    raw = clean(raw)
    if not raw:
        url = None
    elif re.match(r"https?://", raw):
        url = raw
    elif raw.startswith("/"):
        url = BASE + raw
    else:  # bare slug such as "murfreesboro"
        url = LOCATOR_URL + raw.strip("/") + "/"
    if url and url.startswith(BASE):
        slug = slug_of(url)
        hit = canon.get(slug) or canon.get(base_slug(slug))
        if hit:
            return hit
        return url if url.endswith("/") else url + "/"
    # Off-site or missing URL: try the clinic name as a slug ("SynergenX Prosper").
    guess = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return canon.get(guess) or url


def zip_from_page(fetcher, url, street, state):
    """Look for '<STATE> <ZIP>' on the clinic's own page, near its street address."""
    if not url or not url.startswith(BASE):
        return None
    page = fetcher.get(url)
    if not page:
        return None
    text = clean(re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<(script|style)\b.*?</\1>", " ", page)))
    pattern = r"\b%s\s+(\d{5})(?:-\d{4})?\b" % re.escape(state)
    number = street.split(" ")[0] if street else ""
    if number:
        idx = text.find(number)
        if idx >= 0:
            m = re.search(pattern, text[idx: idx + 300])
            if m:
                return m.group(1)
    m = re.search(pattern, text)
    return m.group(1) if m else None


def short_name(raw):
    """'Low T Center Alliance | Hormone Health & TRT Clinic' -> 'Low T Center Alliance'."""
    return clean(raw).split(" | ")[0].strip()


def main():
    fetcher = Fetcher()
    page = fetcher.get(LOCATOR_URL)
    if not page:
        sys.exit("could not fetch %s" % LOCATOR_URL)
    raw_locations = extract_location_data(page)
    canon = load_canonical_urls(fetcher)

    rows, seen = [], set()
    skipped = {"coming_soon": 0, "non_us": 0, "no_zip": 0, "duplicate": 0}
    for loc in raw_locations:
        name = short_name(loc.get("name"))
        if loc.get("coming_soon") or "coming soon" in name.lower():
            skipped["coming_soon"] += 1
            continue
        state = clean(loc.get("state")).upper()
        if state not in US_STATES:
            skipped["non_us"] += 1
            print("INFO skip non-US: %s (%s)" % (name, state), file=sys.stderr)
            continue
        street = ", ".join(p for p in (clean(loc.get("address_part_one")),
                                       clean(loc.get("address_part_two"))) if p)
        city = clean(loc.get("city"))
        url = normalize_url(loc.get("url"), name, canon)
        zm = re.match(r"^(\d{5})(?:-\d{4})?$", clean(loc.get("zipcode")))
        zipcode = zm.group(1) if zm else None
        if not zipcode and street:
            zipcode = zip_from_page(fetcher, url, street, state)
        if not zipcode:
            skipped["no_zip"] += 1
            print("WARN skip, no ZIP: %s" % name, file=sys.stderr)
            continue
        phone = clean(loc.get("phone_number")) or None

        key = (re.sub(r"[^a-z0-9]", "", street.lower()), zipcode)
        if key in seen:
            skipped["duplicate"] += 1
            continue
        seen.add(key)

        rows.append({
            "chain": CHAIN,
            "name": name,
            "address": street,
            "city": city,
            "state": state,
            "zip": zipcode,
            "phone": phone,
            "url": url,
        })

    rows.sort(key=lambda r: (r["state"], r["city"], r["name"]))
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("%d source entries -> %d US locations written to %s (skipped: %s)"
          % (len(raw_locations), len(rows), OUT_PATH, skipped))


if __name__ == "__main__":
    main()
