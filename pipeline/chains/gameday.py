#!/usr/bin/env python3
"""Scrape every US Gameday Men's Health clinic into gameday.json.

Source: the public JSON feed behind the chain's location finder.
https://gamedaymenshealth.com/location-finder embeds an iframe from
location-finder.gamedaymenshealth.com, and that app loads every clinic from

    https://interface-api.gamedaymenshealth.com/finder/entities?country=US

which returns {"data": [{"id", "name", "locationFinderName", "mainPhone",
"url", "address", "city", "state", "stateCode", "zip", "countryCode",
"comingSoon", ...}], "total": N}.

Rows kept: countryCode "US", a street address, and no "comingSoon" flag (the
locator hides flagged rows the same way). Brand placeholder rows with no
address and Canadian clinics are dropped. If a row has a street address but
no ZIP (or state), the clinic's own page (its "url") is fetched and the
schema.org PostalAddress JSON-LD / on-page address line is used instead.

Standard library only (Python 3.9+). Run from the repo root:
    python3 pipeline/chains/gameday.py
"""

import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API_URL = "https://interface-api.gamedaymenshealth.com/finder/entities?country=US"
FINDER_ORIGIN = "https://location-finder.gamedaymenshealth.com"
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gameday.json")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
MIN_INTERVAL = 0.6  # seconds between requests (< 2 req/s)
MAX_CONSECUTIVE_ERRORS = 3
MIN_EXPECTED_ROWS = 50  # refuse to overwrite the output with a suspiciously small result

STATE_CODES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
    "Washington DC": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY",
    "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
    "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
    "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
    "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI",
    "Wyoming": "WY", "Puerto Rico": "PR",
}
US_STATES = set(STATE_CODES.values())


class Fetcher:
    """Polite GET helper: throttled, and aborts after repeated failures."""

    def __init__(self):
        self.last = 0.0
        self.errors = 0

    def get(self, url, headers=None):
        wait = MIN_INTERVAL - (time.time() - self.last)
        if wait > 0:
            time.sleep(wait)
        self.last = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8", "replace")
        except (urllib.error.URLError, OSError) as exc:
            self.errors += 1
            print(f"  ! {url}: {exc}", file=sys.stderr)
            if self.errors >= MAX_CONSECUTIVE_ERRORS:
                sys.exit(f"Stopping: {self.errors} consecutive request errors.")
            return None
        self.errors = 0
        return body


def clean(text):
    """Collapse whitespace, straighten quotes, and normalise dashes."""
    if text is None:
        return ""
    text = html.unescape(str(text)).replace("’", "'").replace("‘", "'")
    text = text.replace("—", "-").replace("–", "-")
    return re.sub(r"\s+", " ", text).strip()


def clean_street(text):
    """Return the street line, e.g. 'Ridgedale Office Center, 13911 Ridgedale Dr'
    becomes '13911 Ridgedale Dr, Ridgedale Office Center' so it starts with the street."""
    s = clean(text)
    s = re.sub(r"\s*,\s*(,\s*)+", ", ", s).strip(" ,")
    s = re.sub(r"\b(Suite|Ste\.?|Unit)\s*:\s*", r"\1 ", s, flags=re.I)
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if len(parts) > 1 and not re.search(r"\d", parts[0]) and re.match(r"\d", parts[1]):
        parts = parts[1:] + parts[:1]
    return ", ".join(parts)


def norm_zip(value):
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) in (5, 9):
        return digits[:5]
    if len(digits) in (3, 4):  # leading zeros lost (e.g. New England ZIPs stored as numbers)
        return digits.zfill(5)
    return None


def norm_state(code, name):
    code = clean(code).upper()
    if code in US_STATES:
        return code
    return STATE_CODES.get(clean(name).title())


def fmt_phone(*candidates):
    for value in candidates:
        digits = re.sub(r"\D", "", str(value or ""))
        if len(digits) == 11 and digits.startswith("1"):
            digits = digits[1:]
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return None


def pick_name(entity, state):
    """The feed has two name fields and each is sometimes the sloppier one
    ("Annapolis, MD", "... Braintree Massachusetts TRT & ED Clinic"). Prefer the
    one that reads "Gameday Men's Health <place>, ST"; on a tie use "name"."""
    def score(name):
        return (2 if name.lower().startswith("gameday men's health") else 0) + \
               (1 if re.search(r",\s*%s\b" % re.escape(state), name) else 0)
    names = [clean(entity.get(k)) for k in ("name", "locationFinderName")]
    names = [n for n in names if n] or ["Gameday Men's Health"]
    best = max(names, key=score)  # max() keeps the first ("name") on ties
    best = re.sub(r"(?<=[a-z])\s+(%s)$" % re.escape(state), r", \1", best)  # "Hanover MA"
    return re.sub(r"^GameDay\b", "Gameday", best)


def street_number(text):
    m = re.match(r"\s*([A-Z]?\d+[A-Z0-9]*)", text or "", re.I)
    return m.group(1).upper() if m else None


def address_from_page(fetcher, url, street):
    """Read (city, state, zip) for this clinic from its own page, or None."""
    page = fetcher.get(url)
    if not page:
        return None
    want = street_number(street)
    # 1. schema.org PostalAddress blocks (the page also carries the HQ address, so match the number).
    for block in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', page, re.S):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
            elif isinstance(node, dict):
                if node.get("@type") == "PostalAddress":
                    zip5 = norm_zip(node.get("postalCode"))
                    if zip5 and street_number(node.get("streetAddress")) == want:
                        return clean(node.get("addressLocality")), clean(node.get("addressRegion")).upper(), zip5
                stack.extend(node.values())
    # 2. The visible address line: "<street>, <City>, ST 12345".
    text = html.unescape(re.sub(r"<[^>]+>", "\n", page))
    for line in text.split("\n"):
        line = clean(line)
        m = re.match(r"(.+),\s*([A-Za-z .'-]+),\s*([A-Z]{2})\s+(\d{5})(?:-\d{4})?$", line)
        if m and street_number(m.group(1)) == want:
            return m.group(2).strip(), m.group(3), m.group(4)
    return None


def main():
    fetcher = Fetcher()
    body = None
    for attempt in range(MAX_CONSECUTIVE_ERRORS):
        body = fetcher.get(API_URL, {
            "Accept": "application/json",
            "Origin": FINDER_ORIGIN,
            "Referer": FINDER_ORIGIN + "/",
        })
        if body:
            break
        time.sleep(2 * (attempt + 1))
    if not body:
        sys.exit("Could not fetch the location feed.")
    try:
        entities = json.loads(body)["data"]
    except (ValueError, KeyError, TypeError) as exc:
        sys.exit(f"Unexpected response from {API_URL}: {exc}")
    print(f"{len(entities)} entities from {API_URL}")

    rows, seen_ids, seen_keys = [], set(), set()
    skipped = {"non_us": 0, "coming_soon": 0, "no_address": 0, "duplicate": 0, "no_zip_or_state": 0}
    for e in entities:
        if not isinstance(e, dict):
            continue
        if (e.get("countryCode") or "").upper() != "US":
            skipped["non_us"] += 1
            continue
        if e.get("comingSoon"):
            skipped["coming_soon"] += 1
            continue
        street = clean_street(e.get("address"))
        if not street:
            skipped["no_address"] += 1
            continue

        url = clean(e.get("url")) or None
        if url and not url.startswith("http"):
            url = "https://gamedaymenshealth.com/" + url.lstrip("/")
        city = clean(e.get("city"))
        state = norm_state(e.get("stateCode"), e.get("state"))
        zip5 = norm_zip(e.get("zip"))
        if (not zip5 or not state or not city) and url:
            found = address_from_page(fetcher, url, street)
            if found:
                city = city or found[0]
                state = state or (found[1] if found[1] in US_STATES else None)
                zip5 = zip5 or found[2]
        if not (zip5 and state):
            skipped["no_zip_or_state"] += 1
            print(f"  ? no ZIP/state for {e.get('id')} {street!r}", file=sys.stderr)
            continue

        key = (re.sub(r"[^A-Z0-9]", "", street.upper().split(",")[0]), zip5)
        eid = e.get("id")
        if (eid and eid in seen_ids) or key in seen_keys:
            skipped["duplicate"] += 1
            continue
        seen_ids.add(eid)
        seen_keys.add(key)

        rows.append({
            "chain": "gameday",
            "name": pick_name(e, state),
            "address": street,
            "city": city,
            "state": state,
            "zip": zip5,
            "phone": fmt_phone(e.get("mainPhone"), e.get("mainPhoneDisp")),
            "url": url,
        })

    rows.sort(key=lambda r: (r["state"], r["city"], r["name"]))
    print(f"{len(rows)} US locations kept; skipped {skipped}")
    if len(rows) < MIN_EXPECTED_ROWS:
        sys.exit(f"Only {len(rows)} rows - not overwriting {OUT_PATH}.")
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
