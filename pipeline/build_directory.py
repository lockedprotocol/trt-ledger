#!/usr/bin/env python3
"""Build the nationwide in-person clinic directory the site searches by ZIP.

Inputs:
  pipeline/raw/registry.json   from fetch_registry.py (NPI registry)
  pipeline/chains/*.json       from the per-chain scrapers (pipeline/chains/*.py)
  geo/zip3/*.json              from build_geo.py (ZIP -> lat/lon)
Writes:
  clinics/<zip3>.json          locations whose ZIP starts with those 3 digits
  clinics/index.json           counts + bounding box per shard, so the browser only
                               downloads shards near the visitor
Each location is one street address; doctors at the same address are grouped.
Categories: trt (TRT / men's health clinic), hormone (hormone clinic), urology, endocrinology.
"""
import datetime as dt
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "geo"
OUT = ROOT / "clinics"

URO, ENDO = "208800000X", "207RE0101X"
TRT_RE = re.compile(r"\b(testosterone|low[- ]?t|trt|andrology|gameday men|ageless men|nu ?male|mantality)\b"
                    r"|\bmen'?s (health|clinic|wellness|medical|vitality|center)"
                    r"|\bmale (medical|clinic|health|vitality|wellness)", re.I)
# Businesses whose names happen to contain "TRT" or "hormone" but aren't clinics
NOT_CLINIC_RE = re.compile(r"\b(logistics|sober|home health|home care|training|academy|transport\w*|trucking|freight|"
                           r"staffing|construction|consulting|insurance|sports medicine academy)\b", re.I)
HORMONE_RE = re.compile(r"\b(hormones?|bhrt)\b", re.I)
WOMEN_RE = re.compile(r"\b(women|woman|womens|her|she|ladies|female|feminine|menopaus\w*|fertility|ob ?gyn|obstetric\w*|gyn\w*|midwi\w*|pediatric\w*)\b", re.I)
# Name matches whose main taxonomy isn't a place you'd go for treatment
NON_CLINICAL = ("3336", "291U", "332B", "3416", "1041", "101Y", "133", "2084P0800X", "103T", "1223", "1835")
PRIORITY = {"trt": 0, "hormone": 1, "urology": 2, "endocrinology": 3}
CHAIN_BRANDS = {"gameday": re.compile(r"gameday", re.I), "ageless": re.compile(r"ageless", re.I),
                "low-t-center": re.compile(r"\blow[- ]?t\b", re.I), "numale": re.compile(r"\bnu ?male\b", re.I),
                "mantality": re.compile(r"mantality", re.I)}
SMALL = {"llc", "pllc", "pc", "pa", "p.a.", "p.c.", "lp", "llp", "inc", "md", "do", "np", "pa-c", "usa", "trt", "ii", "iii", "iv",
         "dba", "faap", "facs", "facp", "aprn", "fnp", "fnp-c"}
UPPER = {"llc", "pllc", "pc", "pa", "lp", "llp", "md", "do", "np", "pa-c", "usa", "trt", "ii", "iii", "iv", "dba", "facs", "facp",
         "aprn", "fnp", "fnp-c", "bhrt", "hrt", "ne", "nw", "se", "sw"}


def tidy(s):
    """REGISTRY UPPERCASE -> Title Case, keeping suffixes like LLC and MD."""
    words = []
    for w in (s or "").split():
        lw = w.lower().strip(",.")
        if lw in UPPER:
            words.append(w.upper())
        else:
            words.append("-".join(p[:1].upper() + p[1:].lower() for p in w.split("-")))
    out = " ".join(words)
    return re.sub(r"\bMen'S\b", "Men's", re.sub(r"\bMens\b", "Men's", out))


STREET_WORDS = {"STREET": "ST", "AVENUE": "AVE", "AV": "AVE", "DRIVE": "DR", "ROAD": "RD", "BOULEVARD": "BLVD",
                "PARKWAY": "PKWY", "HIGHWAY": "HWY", "LANE": "LN", "COURT": "CT", "PLACE": "PL", "CIRCLE": "CIR",
                "SQUARE": "SQ", "TERRACE": "TER", "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W",
                "NORTHWEST": "NW", "NORTHEAST": "NE", "SOUTHWEST": "SW", "SOUTHEAST": "SE"}


def street_key(line, zip5):
    s = re.sub(r"[^A-Z0-9 ]", " ", (line or "").upper())
    s = re.split(r"\b(STE|SUITE|UNIT|BLDG|BUILDING|FL|FLOOR|RM|ROOM|APT)\b", s)[0]
    s = " ".join(STREET_WORDS.get(w, w) for w in s.split())   # "College Drive" == "College Dr"
    return f"{s}|{zip5}"


def load_geo():
    zips = {}
    for f in (GEO / "zip3").glob("*.json"):
        zips.update(json.loads(f.read_text()))
    return zips, json.loads((GEO / "zip3-centroids.json").read_text())


def registry_entries():
    for rec in json.loads((ROOT / "pipeline" / "raw" / "registry.json").read_text()):
        r = rec["raw"]
        loc = next((a for a in r.get("addresses", []) if a.get("address_purpose") == "LOCATION"), None)
        if not loc or loc.get("country_code") != "US":
            continue
        primary = next((t for t in r.get("taxonomies", []) if t.get("primary")), (r.get("taxonomies") or [{}])[0])
        code, codes = primary.get("code", ""), {t.get("code") for t in r.get("taxonomies", [])}
        b, is_org = r.get("basic", {}), r.get("enumeration_type") == "NPI-2"
        name = b.get("organization_name", "") if is_org else " ".join(
            x for x in [b.get("first_name"), b.get("last_name")] if x)
        cats = set()
        if any(t == "specialty" for t, _ in rec["found_by"]):
            if code == URO or (is_org and URO in codes and re.search(r"urolog", name, re.I)):
                cats.add("urology")
            if code == ENDO or (is_org and ENDO in codes and re.search(r"endocrin", name, re.I)):
                cats.add("endocrinology")
        if is_org and not code.startswith(NON_CLINICAL) and not NOT_CLINIC_RE.search(name):
            if TRT_RE.search(name):
                cats.add("trt")
            elif HORMONE_RE.search(name) and not WOMEN_RE.search(name):
                cats.add("hormone")
        if not cats:
            continue
        yield {
            "npi": r["number"], "org": is_org, "name": name,
            "credential": ", ".join(x for x in re.split(r"[\s,;/]+", (b.get("credential") or "").replace(".", "")) if x),
            "cats": cats, "addr": loc.get("address_1", ""), "city": loc.get("city", ""), "st": loc.get("state", ""),
            "zip": (loc.get("postal_code") or "")[:5], "phone": loc.get("telephone_number"),
        }


def update_chain_counts():
    """Refresh each chain's per-state location counts in data.json from its scraped list."""
    data_path = ROOT / "data.json"
    data = json.loads(data_path.read_text())
    # The monthly job lists the scrapers that succeeded this run; a list kept from last month
    # keeps its old "checked" date. Run by hand (no list), the file's date is used.
    fresh_file = ROOT / "pipeline" / "chains" / "fresh.txt"
    fresh = set(fresh_file.read_text().split()) if fresh_file.exists() else None
    for chain in data.get("inPerson", []):
        f = ROOT / "pipeline" / "chains" / f"{chain['id']}.json"
        try:
            rows = json.loads(f.read_text()) if f.exists() else []
        except ValueError:
            rows = []
        if not rows:
            continue  # no scraper (or it failed): keep the hand-entered counts
        chain["locations"] = dict(sorted(Counter(r["state"] for r in rows if r.get("state")).items()))
        chain["statesReported"], chain["everywhere"] = [], False
        if fresh is None:
            chain["checked"] = dt.date.fromtimestamp(f.stat().st_mtime).isoformat()
        elif chain["id"] in fresh:
            chain["checked"] = dt.date.today().isoformat()
        chain["notes"] = f"{len(rows)} U.S. clinics in {len(chain['locations'])} states"
    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    (ROOT / "data.js").write_text("// Generated from data.json by checker/check_prices.py — edit data.json, not this file.\n"
                                  "window.TRT_DATA = " + json.dumps(data, indent=2, ensure_ascii=False) + ";\n")


def main():
    zips, centroids = load_geo()
    places = defaultdict(lambda: {"orgs": [], "docs": [], "cats": set(), "npis": [], "chain": None, "url": None})
    for e in registry_entries():
        p = places[street_key(e["addr"], e["zip"])]
        p["cats"] |= e["cats"]
        p["npis"].append(e["npi"])
        p.update({k: p.get(k) or e[k] for k in ("addr", "city", "st", "zip", "phone")})
        (p["orgs"] if e["org"] else p["docs"]).append(e)

    chain_rows = 0
    for f in sorted((ROOT / "pipeline" / "chains").glob("*.json")):
        try:
            rows = json.loads(f.read_text())
        except ValueError:
            print(f"  ! skipping unreadable {f.name}", file=sys.stderr)
            continue
        for c in rows:
            if not (c.get("zip") and c.get("state")):
                continue
            chain_rows += 1
            p = places[street_key(c.get("address"), c["zip"][:5])]
            p["cats"].add("trt")
            p["chain"], p["url"], p["chain_name"] = c["chain"], c.get("url"), c.get("name")
            for k_src, k in (("address", "addr"), ("city", "city"), ("state", "st"), ("zip", "zip"), ("phone", "phone")):
                p[k] = p.get(k) or c.get(k_src)

    # The same chain clinic often appears twice: once from the chain's own locator and once as a
    # registry organization whose address is written differently ("Hwy" vs "Highway"). Fold
    # same-ZIP registry entries named after the chain into the chain's entry.
    by_zip = defaultdict(list)
    for key, p in places.items():
        by_zip[key.split("|")[1]].append(key)
    merged = 0
    for key, p in list(places.items()):
        brand = CHAIN_BRANDS.get(p.get("chain"))
        if not brand:
            continue
        for other in by_zip[key.split("|")[1]]:
            q = places.get(other)
            if other == key or not q or q.get("chain") or not any(brand.search(o["name"]) for o in q["orgs"]):
                continue
            p["orgs"] += q["orgs"]; p["docs"] += q["docs"]; p["npis"] += q["npis"]; p["cats"] |= q["cats"]
            p["phone"] = p.get("phone") or q.get("phone")
            del places[other]
            merged += 1

    # Different addresses in one ZIP that share a phone number are one practice listed twice
    # (e.g. a group's two buildings); show them once so counts mean practices, not records.
    by_phone, phone_merged = {}, 0
    for key in sorted(places, key=lambda k: (not places[k].get("chain"), not places[k]["orgs"])):
        p = places[key]
        digits = re.sub(r"\D", "", p.get("phone") or "")[-10:]
        if len(digits) < 10:
            continue
        pk = (key.split("|")[1], digits)
        if pk not in by_phone:
            by_phone[pk] = key
            continue
        q = places[by_phone[pk]]
        q["orgs"] += p["orgs"]; q["docs"] += p["docs"]; q["npis"] += p["npis"]; q["cats"] |= p["cats"]
        del places[key]
        phone_merged += 1

    # A ZIP code from another state means the record's address is wrong; leave it out
    zip3_state = {z: st for st, zs in json.loads((ROOT / "pipeline" / "zip3_states.json").read_text()).items() for z in zs}
    wrong_state = 0
    for key in list(places):
        p = places[key]
        zst = zip3_state.get((p.get("zip") or "")[:3])
        if zst and p.get("st") and zst != p["st"]:
            del places[key]
            wrong_state += 1

    shards, missing_geo, counts = defaultdict(list), 0, Counter()
    for p in places.values():
        z = (p.get("zip") or "")[:5]
        ll = zips.get(z) or centroids.get(z[:3])
        if not ll:
            missing_geo += 1
            continue
        cats = sorted(p["cats"], key=PRIORITY.get)
        orgs = sorted(p["orgs"], key=lambda o: min(PRIORITY[c] for c in o["cats"]))
        docs = sorted({f"{tidy(d['name'])}{', ' + d['credential'] if d['credential'] else ''}" for d in p["docs"]})
        if p.get("chain_name"):
            name = p["chain_name"]
        elif orgs:
            name = tidy(orgs[0]["name"])
        elif len(docs) == 1:
            name = docs[0]
        else:
            name = f"{docs[0]} + {len(docs) - 1} more"
        for c in cats:
            counts[c] += 1
        shards[z[:3]].append({k: v for k, v in {
            "name": name, "cats": cats, "addr": tidy(p.get("addr")), "city": tidy(p.get("city")), "st": p.get("st"),
            "zip": z, "phone": p.get("phone"), "lat": ll[0], "lon": ll[1], "docs": docs[:6], "ndocs": len(docs),
            "chain": p.get("chain"), "url": p.get("url"), "npi": p["npis"][:3],
        }.items() if v not in (None, [], "")})

    # Unattended monthly runs: refuse to publish a directory that shrank a lot (a source broke)
    total_new = sum(len(r) for r in shards.values())
    old_index = OUT / "index.json"
    if old_index.exists() and "--force" not in sys.argv:
        old = json.loads(old_index.read_text())
        total_old, trt_old = old.get("total", 0), old.get("counts", {}).get("trt", 0)
        if total_new < 0.8 * total_old:
            sys.exit(f"Refusing to publish: {total_new} locations vs {total_old} last time. Check the sources, "
                     "or re-run with --force if the drop is real.")
        if counts["trt"] < 0.8 * trt_old:
            sys.exit(f"Refusing to publish: {counts['trt']} TRT clinics vs {trt_old} last time. A chain list or "
                     "name search probably broke; re-run with --force if the drop is real.")

    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    index = {}
    for z3, rows in sorted(shards.items()):
        rows.sort(key=lambda r: (PRIORITY[r["cats"][0]], r["name"]))
        (OUT / f"{z3}.json").write_text(json.dumps(rows, separators=(",", ":"), ensure_ascii=False))
        lats, lons = [r["lat"] for r in rows], [r["lon"] for r in rows]
        index[z3] = [len(rows), min(lats), min(lons), max(lats), max(lons)]
    total = sum(v[0] for v in index.values())
    (OUT / "index.json").write_text(json.dumps({
        "updated": dt.date.today().isoformat(), "total": total, "counts": counts, "shards": index}, separators=(",", ":")))
    update_chain_counts()
    print(f"{total} locations in {len(index)} shards ({chain_rows} chain rows, {merged} duplicates folded into chains, "
          f"{phone_merged} same-phone duplicates merged, {wrong_state} wrong-state records dropped); "
          f"by category: {dict(counts)}; "
          f"dropped {missing_geo} with no ZIP location")


if __name__ == "__main__":
    main()
