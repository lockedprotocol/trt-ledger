#!/usr/bin/env python3
"""Scrape US clinic locations for NuMale Medical Center (now VidaVital Medical).

numale.com now 301-redirects to vidavitalmedical.com: NuMale rebranded as
VidaVital Medical. The location list lives in plain HTML at

    https://www.vidavitalmedical.com/locations/

with one <article class="loc"> card per clinic (city, address, phone, link).
Each clinic page (e.g. /omaha/) also has a JSON-LD "MedicalClinic" block, used
only to fill in a missing ZIP, street or phone. If the cards cannot be found
(layout change), the script falls back to the clinic pages listed in
/sitemap.xml and reads their JSON-LD instead.

Writes numale.json (next to this file): a JSON array of
{"chain", "name", "address", "city", "state", "zip", "phone", "url"}.

Python 3.9+, standard library only. Fetches politely (>= 0.6 s between
requests) and stops after repeated errors or a bot-protection response.
"""

import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

CHAIN = "numale"
BASE = "https://www.vidavitalmedical.com"  # numale.com 301-redirects here
BRAND = "VidaVital Medical"
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "numale.json")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
MIN_INTERVAL = 0.6  # seconds between requests (< 2 req/s)
MAX_CONSECUTIVE_ERRORS = 3
TIMEOUT = 40

US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
    "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
    "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
    "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
    "WV", "WI", "WY", "PR",
}
NOT_OPEN_RE = re.compile(r"coming\s+soon|opening\s+soon|now\s+opening|temporarily\s+closed", re.I)


class BlockedError(RuntimeError):
    pass


class Fetcher:
    """Rate-limited GET with a small retry budget and an error circuit breaker."""

    def __init__(self) -> None:
        self._last = 0.0
        self._consecutive_errors = 0

    def get(self, url: str, retries: int = 2) -> Optional[str]:
        for attempt in range(retries + 1):
            wait = MIN_INTERVAL - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
            req = urllib.request.Request(url, headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            })
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                    body = resp.read().decode("utf-8", "replace")
                    self._consecutive_errors = 0
                    return body
            except urllib.error.HTTPError as e:
                if e.code in (403, 429) or (e.code == 503 and "cloudflare" in str(e.headers.get("server", "")).lower()):
                    raise BlockedError("HTTP %d from %s (rate limit / bot protection)" % (e.code, url))
                if e.code == 404:
                    print("  404 %s" % url, file=sys.stderr)
                    return None
                err = "HTTP %d" % e.code
            except (urllib.error.URLError, OSError) as e:
                err = str(e)
            self._consecutive_errors += 1
            print("  error fetching %s: %s (attempt %d)" % (url, err, attempt + 1), file=sys.stderr)
            if self._consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                raise RuntimeError("stopping after %d consecutive errors" % self._consecutive_errors)
            time.sleep(2 * (attempt + 1))
        return None


def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def fmt_phone(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        return raw.strip() or None
    return "(%s) %s-%s" % (digits[:3], digits[3:6], digits[6:])


def norm_street(s: str) -> str:
    s = re.sub(r"\bSTE\b", "Ste", s)
    s = re.sub(r",?\s*(Suite|Ste\.?)\s+", " Ste ", s)
    return re.sub(r"\s+", " ", s).strip(" ,")


def parse_cards(page: str, base: str) -> List[Dict]:
    """Parse <article class="loc"> cards from the /locations/ page."""
    out = []
    for art in re.findall(r'<article[^>]*class="[^"]*\bloc\b[^"]*"[^>]*>(.*?)</article>', page, re.S):
        text = clean(art)
        if NOT_OPEN_RE.search(text):
            print("  skipping not-yet-open card: %s" % text[:80], file=sys.stderr)
            continue
        h3 = re.search(r"<h3[^>]*>(.*?)</h3>", art, re.S)
        heading = clean(h3.group(1)) if h3 else ""
        addr = re.search(r"<address[^>]*>(.*?)</address>", art, re.S)
        lines = [clean(x) for x in re.split(r"<br\s*/?>", addr.group(1))] if addr else []
        lines = [x for x in lines if x]
        street, city, state, zipc = None, None, None, None
        if lines:
            m = re.match(r"^(.*?),\s*([A-Z]{2})\s*(\d{5})?(?:-\d{4})?$", lines[-1])
            if m:
                city, state, zipc = m.group(1).strip(), m.group(2), m.group(3)
                street = " ".join(lines[:-1]) or None
            else:
                street = " ".join(lines)
        if not (city and state):
            m = re.match(r"^(.*?),\s*([A-Z]{2})$", heading)
            if m:
                city, state = city or m.group(1).strip(), state or m.group(2)
        tel = re.search(r'href="tel:([^"]+)"', art)
        link = re.search(r'<a[^>]+href="([^"]+)"[^>]*>\s*View Clinic', art) or \
            re.search(r'<a[^>]+href="(/[^"#?]+/)"', art)
        out.append({
            "street": norm_street(street) if street else None,
            "city": city, "state": state, "zip": zipc,
            "phone": fmt_phone(tel.group(1)) if tel else None,
            "url": urljoin(base + "/", link.group(1)) if link else None,
        })
    return out


def clinic_jsonld(page: str) -> Optional[Dict]:
    """Return the per-clinic MedicalClinic JSON-LD node (the one with an address)."""
    for block in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', page, re.S):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        nodes = data if isinstance(data, list) else data.get("@graph", [data])
        for n in nodes:
            if not isinstance(n, dict):
                continue
            types = n.get("@type")
            types = types if isinstance(types, list) else [types]
            if any(t in ("MedicalClinic", "LocalBusiness", "MedicalBusiness") for t in types) \
                    and isinstance(n.get("address"), dict) and "#clinic" in str(n.get("@id", "")):
                return n
    return None


def from_jsonld(n: Dict, url: str) -> Dict:
    a = n["address"]
    zipm = re.match(r"\d{5}", str(a.get("postalCode", "")))
    return {
        "name": clean(n.get("name", "")) or None,
        "street": norm_street(clean(a.get("streetAddress", ""))) or None,
        "city": clean(a.get("addressLocality", "")) or None,
        "state": clean(a.get("addressRegion", "")).upper() or None,
        "zip": zipm.group(0) if zipm else None,
        "country": clean(a.get("addressCountry", "")) or "US",
        "phone": fmt_phone(n.get("telephone")),
        "url": n.get("url") or url,
    }


def sitemap_clinic_pages(fetcher: Fetcher, base: str) -> List[str]:
    """Clinic pages = top-level /<slug>/ that have a /<slug>/testosterone-replacement-therapy/ child."""
    xml = fetcher.get(base + "/sitemap.xml") or ""
    paths = [urlparse(u).path for u in re.findall(r"<loc>\s*(.*?)\s*</loc>", xml)]
    slugs = {p.split("/")[1] for p in paths if re.match(r"^/[^/]+/testosterone-replacement-therapy/$", p)}
    return [base + "/" + s + "/" for s in sorted(slugs)]


def main() -> int:
    fetcher = Fetcher()
    base = BASE
    print("source: %s/locations/" % base, file=sys.stderr)

    page = fetcher.get(base + "/locations/")
    if page is None:
        print("could not fetch locations page", file=sys.stderr)
        return 1
    cards = parse_cards(page, base)
    print("  %d location cards on /locations/" % len(cards), file=sys.stderr)

    if not cards:  # layout changed: fall back to clinic pages from the sitemap
        for url in sitemap_clinic_pages(fetcher, base):
            p = fetcher.get(url)
            n = clinic_jsonld(p) if p else None
            if n:
                cards.append(from_jsonld(n, url))
        print("  %d clinics via sitemap + JSON-LD fallback" % len(cards), file=sys.stderr)

    rows, seen = [], set()
    for c in cards:
        # Fill gaps (ZIP, street, phone, state) from the clinic page's JSON-LD.
        if c.get("url") and not all(c.get(k) for k in ("street", "city", "state", "zip", "phone")):
            p = fetcher.get(c["url"])
            n = clinic_jsonld(p) if p else None
            if n:
                j = from_jsonld(n, c["url"])
                for k in ("street", "city", "state", "zip", "phone", "name", "country"):
                    if not c.get(k) and j.get(k):
                        c[k] = j[k]
                if not c.get("zip"):  # last resort: "City, ST 12345" in the page's <address>
                    m = re.search(r"%s,?\s*%s\s+(\d{5})" % (re.escape(c.get("city") or ""), c.get("state") or ""), clean(p))
                    if m:
                        c["zip"] = m.group(1)
        if (c.get("country") or "US").upper() not in ("US", "USA", "UNITED STATES"):
            continue
        if c.get("state") not in US_STATES:
            print("  skipping non-US / unparsed: %r" % c, file=sys.stderr)
            continue
        key = (re.sub(r"\W", "", (c.get("street") or "").lower()), c.get("zip"), c["city"].lower())
        if key in seen:
            continue
        seen.add(key)
        rows.append({
            "chain": CHAIN,
            "name": c.get("name") or "%s %s" % (BRAND, c["city"]),
            "address": c.get("street"),
            "city": c["city"],
            "state": c["state"],
            "zip": c.get("zip"),
            "phone": c.get("phone"),
            "url": c.get("url"),
        })

    rows.sort(key=lambda r: (r["state"], r["city"], r["address"] or ""))
    with open(OUT_PATH, "w") as f:
        json.dump(rows, f, indent=2)
        f.write("\n")
    missing = [r["name"] for r in rows if not (r["zip"] and r["state"] and r["address"])]
    print("wrote %d locations to %s (%d missing street/zip/state)" % (len(rows), OUT_PATH, len(missing)), file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BlockedError as e:
        print("BLOCKED: %s" % e, file=sys.stderr)
        sys.exit(2)
    except RuntimeError as e:
        print("FAILED: %s" % e, file=sys.stderr)
        sys.exit(1)
