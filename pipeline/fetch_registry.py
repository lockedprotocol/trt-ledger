#!/usr/bin/env python3
"""Pull providers who commonly treat low testosterone from the federal NPI registry.

Source: CMS NPPES NPI Registry API (https://npiregistry.cms.hhs.gov/api-page), public data.
What we pull:
  - Urologists and endocrinologists (individuals and organizations), by state
  - Organizations whose name says they do TRT / men's health / hormones (keyword search)
The API returns at most 1,200 results per query (200 per page, skip <= 1000), so any
query that hits the cap is split by 3-digit ZIP prefix.

Writes pipeline/raw/registry.json (one record per NPI). Responses are cached in
pipeline/raw/npi-cache/ for a day so a re-run after a failure is fast.
Usage: python3 pipeline/fetch_registry.py [--fresh]
"""
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "pipeline" / "raw"
CACHE = RAW / "npi-cache"
API = "https://npiregistry.cms.hhs.gov/api/"
STATES = ["AL","AK","AZ","AR","CA","CO","CT","DE","DC","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA",
          "MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX",
          "UT","VT","VA","WA","WV","WI","WY"]
SPECIALTIES = ["Urology", "Endocrinology, Diabetes & Metabolism"]
NAME_PATTERNS = ["*men's health*", "*mens health*", "*men's clinic*", "*mens clinic*", "*men's wellness*", "*mens wellness*",
                 "*male medical*", "*male clinic*", "*male health*", "*male vitality*", "*low t*", "*low-t*", "*testosterone*",
                 "*trt*", "*hormone*", "*bhrt*", "*andrology*", "gameday*", "*ageless men*", "*numale*", "*nu male*", "*mantality*"]
PAGE, MAX_SKIP = 200, 1000
FRESH = "--fresh" in sys.argv


def call(params):
    """One API page, cached on disk for 24h."""
    params = {"version": "2.1", "limit": PAGE, **params}
    key = hashlib.sha1(json.dumps(params, sort_keys=True).encode()).hexdigest()
    f = CACHE / f"{key}.json"
    if not FRESH and f.exists() and time.time() - f.stat().st_mtime < 86400:
        return json.loads(f.read_text())
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = json.loads(r.read())
            break
        except Exception as e:  # network blips and 5xx: back off and retry
            if attempt == 4:
                raise RuntimeError(f"{url}: {e}")
            time.sleep(2 ** attempt)
    if "Errors" in data:
        raise RuntimeError(f"{url}: {data['Errors']}")
    f.write_text(json.dumps(data))
    return data


def query_all(params):
    """All pages for a query. Returns (results, capped)."""
    out = []
    for skip in range(0, MAX_SKIP + 1, PAGE):
        res = call({**params, "skip": skip}).get("results", [])
        out += res
        if len(res) < PAGE:
            return out, False
    return out, True


def query_split(params, zip3s):
    """Run a query; if it hits the API cap, re-run it per 3-digit ZIP prefix."""
    res, capped = query_all(params)
    if not capped:
        return res
    out = []
    for z3 in zip3s:
        sub, sub_capped = query_all({**params, "postal_code": z3 + "*"})
        if sub_capped:
            print(f"  ! still capped: {params} zip {z3}*", file=sys.stderr)
        out += sub
    return out


def jobs(zip3_by_state):
    for spec in SPECIALTIES:
        for st in STATES:
            for etype in ("NPI-1", "NPI-2"):
                yield ("specialty", spec), {"taxonomy_description": spec, "state": st, "enumeration_type": etype,
                                            "address_purpose": "LOCATION"}, zip3_by_state.get(st, [])
    for pat in NAME_PATTERNS:
        yield ("name", pat), {"organization_name": pat, "enumeration_type": "NPI-2"}, None


def run_job(job, zip3_by_state):
    tag, params, zip3s = job
    if zip3s is None:  # nationwide name search: split by state when capped
        res, capped = query_all(params)
        if capped:
            res = []
            for st in STATES:
                res += query_split({**params, "state": st, "address_purpose": "LOCATION"}, zip3_by_state.get(st, []))
    else:
        res = query_split(params, zip3s)
    return tag, res


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    # ZIP prefixes per state come from the ZIP lookup built by build_geo.py + the site's ZIP3->state table
    zip3_by_state = json.loads((ROOT / "pipeline" / "zip3_states.json").read_text())
    records, t0 = {}, time.time()
    all_jobs = list(jobs(zip3_by_state))
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i, (tag, res) in enumerate(pool.map(lambda j: run_job(j, zip3_by_state), all_jobs), 1):
            for r in res:
                rec = records.setdefault(r["number"], {"raw": r, "found_by": []})
                if list(tag) not in rec["found_by"]:
                    rec["found_by"].append(list(tag))
            if i % 25 == 0 or i == len(all_jobs):
                print(f"{i}/{len(all_jobs)} queries, {len(records)} providers, {time.time()-t0:.0f}s")
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / "registry.json").write_text(json.dumps(list(records.values())))
    print(f"Wrote {len(records)} providers to pipeline/raw/registry.json")


if __name__ == "__main__":
    main()
