#!/usr/bin/env python3
"""Build the ZIP -> latitude/longitude lookup the site uses for distance search.

Source: U.S. Census Bureau Gazetteer, ZIP Code Tabulation Areas (public domain).
Writes:
  geo/zip3/<first 3 digits>.json   {"78701": [30.27, -97.74], ...}  (loaded on demand)
  geo/zip3-centroids.json          {"787": [30.4, -97.8], ...}       (fallback for ZIPs that
                                                                      aren't ZCTAs, e.g. PO boxes)
Usage: python3 pipeline/build_geo.py [path/to/Gaz_zcta_national.txt]
"""
import io
import json
import sys
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_zcta_national.zip"


def load_rows(path=None):
    if path:
        text = Path(path).read_text()
    else:
        with urllib.request.urlopen(URL, timeout=120) as r:
            z = zipfile.ZipFile(io.BytesIO(r.read()))
        text = z.read(z.namelist()[0]).decode("utf-8")
    lines = text.splitlines()
    head = [h.strip() for h in lines[0].split("\t")]
    i_zip, i_lat, i_lon = head.index("GEOID"), head.index("INTPTLAT"), head.index("INTPTLONG")
    for line in lines[1:]:
        cols = [c.strip() for c in line.split("\t")]
        if len(cols) > i_lon and cols[i_zip]:
            yield cols[i_zip], float(cols[i_lat]), float(cols[i_lon])


def main():
    shards = defaultdict(dict)
    for z, lat, lon in load_rows(sys.argv[1] if len(sys.argv) > 1 else None):
        shards[z[:3]][z] = [round(lat, 4), round(lon, 4)]

    out = ROOT / "geo" / "zip3"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.json"):
        old.unlink()
    centroids = {}
    for z3, zips in sorted(shards.items()):
        (out / f"{z3}.json").write_text(json.dumps(zips, separators=(",", ":")))
        pts = list(zips.values())
        centroids[z3] = [round(sum(p[0] for p in pts) / len(pts), 3), round(sum(p[1] for p in pts) / len(pts), 3)]
    (ROOT / "geo" / "zip3-centroids.json").write_text(json.dumps(centroids, separators=(",", ":")))
    print(f"{sum(len(s) for s in shards.values())} ZIPs in {len(shards)} shards")


if __name__ == "__main__":
    main()
