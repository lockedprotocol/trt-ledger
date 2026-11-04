#!/usr/bin/env python3
"""Weekly TRT Ledger price checker.

Reads data.json, re-reads every watched price from its source page, records changes,
rebuilds data.js for the site, writes checker/last-report.md and (optionally) emails
subscribers through Buttondown.

Usage:
  python3 checker/check_prices.py            # check, update data, send alert if configured
  python3 checker/check_prices.py --dry-run  # check only; change nothing, send nothing
  python3 checker/check_prices.py --build    # just rebuild data.js after editing data.json

Env:
  BUTTONDOWN_API_KEY  if set, price changes are emailed to subscribers
  SITE_URL            link used in alert emails (default https://trtledger.com)

Exit code is 1 when a watched price couldn't be read (the page probably changed),
so a scheduled run shows up as failed and you get notified to fix that rule.
"""
import datetime as dt
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import self_heal

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data.json"
SITE_JS = ROOT / "data.js"
REPORT = ROOT / "checker" / "last-report.md"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
MAX_AUTO_CHANGE = 0.5   # a jump bigger than 50% is held for review instead of published
KEEP_CHANGES = 30       # how many recent changes the site shows


def page_text(url, cache={}):
    """Fetch a page with curl (handles redirects and modern TLS).
    Returns (text, state): state is "ok", "blocked" (the site refuses automated visitors;
    we never try to get around that) or "unreachable" (timeout, DNS, 5xx: try again next week)."""
    if url not in cache:
        for attempt in range(2):
            proc = subprocess.run(
                ["curl", "-sL", "--max-time", "30", "-A", UA, "-w", "\n%{http_code}", url],
                capture_output=True, text=True, errors="ignore",
            )
            raw, _, status = proc.stdout.rpartition("\n")
            if status in ("403", "429") or re.search(r"Just a moment\.\.\.|Attention Required! \| Cloudflare", raw):
                cache[url] = (None, "blocked")
                break
            if proc.returncode != 0 or status == "000" or status.startswith("5"):
                cache[url] = (None, "unreachable")
                time.sleep(5)
                continue
            raw = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", " ", raw)
            cache[url] = (re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))), "ok")
            break
    return cache[url]


def read_value(rule, text):
    found = []
    for m in re.findall(rule["pattern"], text):
        try:
            found.append(float((m if isinstance(m, str) else m[0]).replace(",", "")))
        except ValueError:
            continue   # e.g. "49.99." — skip anything that isn't a clean number
    if not found:
        return None
    pick = rule.get("pick", "first")
    value = max(found) if pick == "max" else min(found) if pick == "min" else found[0]
    return round(value * rule.get("multiply", 1), 2)


def current_value(item, field):
    if field == "total":  # lab rows store price + fees separately
        return round(item["price"] + item["fees"], 2)
    return item.get(field)


def apply_value(item, field, value):
    if field == "total":
        item["price"] = round(value - item["fees"], 2)
    else:
        item[field] = int(value) if float(value).is_integer() else value


def check(data, today):
    changes, held, failures, blocked, healed, unreachable, ok = [], [], [], [], [], [], 0
    items = [(c, c["name"], c["sourceUrl"]) for c in data["clinics"]]
    items += [(l, f'{l["vendor"]} — {l["test"]}', l["sourceUrl"]) for l in data["labs"]]
    for item, name, url in items:
        rules = item.get("watch")
        if not rules:
            continue
        try:
            text, state = page_text(url)
            if state == "blocked":
                blocked.append({"name": name, "url": url, "since": item.get("checked")})
                continue
            if state == "unreachable":
                unreachable.append({"name": name, "url": url})
                continue
            item_ok = True
            for rule in rules:
                new = read_value(rule, text)
                old = current_value(item, rule["field"])
                note, new_pattern = "", None
                if new is None and old is not None:
                    # The page changed: ask Claude for the price and a new rule (checked before use)
                    new, new_pattern, note = self_heal.heal(text, name, label(rule["field"]), old, rule, read_value)
                if new is None:
                    failures.append({"name": name, "field": rule["field"], "url": url, "note": note})
                    item_ok = False
                    continue
                change = {"date": today, "name": name, "field": rule["field"], "old": old, "new": new, "url": url}
                if old and abs(new - old) / old > MAX_AUTO_CHANGE:
                    # A big jump: keep the old price and the old rule until a person confirms it
                    if new_pattern:
                        change["proposed_pattern"] = new_pattern
                    held.append(change)
                    item_ok = False
                    continue
                if new_pattern:   # only now is the repaired rule saved
                    rule["pattern"], rule["healed"] = new_pattern, today
                    rule.pop("pick", None)
                    healed.append({"name": name, "field": rule["field"], "url": url, "note": note})
                if old is None or abs(new - old) >= 0.005:
                    changes.append((item, rule["field"], change))
            if item_ok:
                item["checked"] = today
                ok += 1
        except Exception as e:   # one broken page or rule must never stop the weekly run
            failures.append({"name": name, "field": "page", "url": url, "note": f"{e.__class__.__name__}: {e}"})
    return changes, held, failures, blocked, healed, unreachable, ok


def money(v):
    return "—" if v is None else f"${v:,.2f}".replace(".00", "")


def label(field):
    return {"monthly": "monthly price", "intakeFee": "intake fee", "prepaid": "prepaid total",
            "clinicYear1Estimate": "year-1 estimate", "total": "total price", "ongoingMonthly": "average after year one"}.get(field, field)


def write_report(today, changes, held, failures, blocked, healed, unreachable, ok, dry):
    lines = [f"# Price check — {today}{' (dry run)' if dry else ''}", "",
             f"- Sources confirmed: {ok}", f"- Price changes: {len(changes)}",
             f"- Held for review (jump over {int(MAX_AUTO_CHANGE*100)}%): {len(held)}",
             f"- Rules repaired automatically: {len(healed)}",
             f"- Couldn't read: {len(failures)}", f"- Site blocks automated checks: {len(blocked)}",
             f"- Site was down (retried next week): {len(unreachable)}", ""]
    if changes:
        lines += ["## Changes published", ""] + [
            f"- **{c['name']}** {label(c['field'])}: {money(c['old'])} → {money(c['new'])} ([source]({c['url']}))"
            for _, _, c in changes] + [""]
    if held:
        lines += ["## Held for review — confirm by hand, then edit data.json", ""] + [
            f"- **{c['name']}** {label(c['field'])}: {money(c['old'])} → {money(c['new'])} ([source]({c['url']}))"
            + (f" — proposed new rule: `{c['proposed_pattern']}`" if c.get("proposed_pattern") else "")
            for c in held] + [""]
    if healed:
        lines += ["## Repaired automatically — the page changed and Claude found the price again", ""] + [
            f"- **{h['name']}** {label(h['field'])}: {h['note']} ([page]({h['url']}))" for h in healed] + [""]
    if failures:
        lines += ["## Couldn't read — the page changed; update the `watch` pattern in data.json", ""] + [
            f"- **{f['name']}** {label(f['field'])} ([page]({f['url']})){' — ' + f['note'] if f.get('note') else ''}"
            for f in failures] + [""]
    if unreachable:
        lines += ["## Site was down — nothing to do, it's retried next week", ""] + [
            f"- **{u['name']}** ([page]({u['url']}))" for u in unreachable] + [""]
    if blocked:
        lines += ["## Check by hand — these sites block automated visits", ""] + [
            f"- **{b['name']}** — last confirmed {b['since']} ([page]({b['url']})). If the price changed, edit data.json, "
            "set `checked` to today, and run `python3 checker/check_prices.py --build`." for b in blocked] + [""]
    REPORT.write_text("\n".join(lines))
    return "\n".join(lines)


def send_alert(changes, site_url, sponsor=None):
    key = os.environ.get("BUTTONDOWN_API_KEY")
    if not key or not changes:
        return "skipped (no API key or no changes)"
    drops = [c for _, _, c in changes if c["old"] and c["new"] < c["old"]]
    subject = (f"TRT price drop: {drops[0]['name']} now {money(drops[0]['new'])}"
               if len(drops) == 1 else f"{len(changes)} TRT price changes this week")
    body = "\n".join(
        [f"Here's what changed on [TRT Ledger]({site_url}) this week:", ""]
        + [f"- **{c['name']}** {label(c['field'])}: ~~{money(c['old'])}~~ **{money(c['new'])}** "
           f"([source]({c['url']}))" for _, _, c in changes]
        + ["", f"[Compare every clinic's true first-year cost →]({site_url}#compare)", "",
           "_Prices are read from each clinic's own site. Not medical advice._"]
        # Optional paid sponsor line, set in data.json as {"sponsor": {"name": ..., "text": ..., "url": ...}}.
        # Always labeled and kept apart from the price data.
        + (["", "---", f"**Sponsor:** [{sponsor['name']}]({sponsor['url']}) — {sponsor['text']}",
            "_Sponsors never affect prices or rankings on TRT Ledger._"] if sponsor and sponsor.get("url") else []))
    req = urllib.request.Request(
        "https://api.buttondown.com/v1/emails",
        data=json.dumps({"subject": subject, "body": body, "status": "about_to_send"}).encode(),
        headers={"Authorization": f"Token {key}", "Content-Type": "application/json",
                 # Buttondown asks for this once per key before allowing immediate sends
                 "X-Buttondown-Live-Dangerously": "true"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return f"sent (HTTP {r.status})"


def build_site_data(data):
    SITE_JS.write_text("// Generated from data.json by checker/check_prices.py — edit data.json, not this file.\n"
                       "window.TRT_DATA = " + json.dumps(data, indent=2, ensure_ascii=False) + ";\n")


def main():
    if "--build" in sys.argv:  # after editing data.json by hand
        build_site_data(json.loads(DATA.read_text()))
        print("Rebuilt data.js")
        return
    dry = "--dry-run" in sys.argv
    today = dt.date.today().isoformat()
    data = json.loads(DATA.read_text())
    changes, held, failures, blocked, healed, unreachable, ok = check(data, today)

    if not dry:
        for item, field, change in changes:
            apply_value(item, field, change["new"])
        data["recentChanges"] = ([c for _, _, c in changes] + data.get("recentChanges", []))[:KEEP_CHANGES]
        if ok:   # "prices last checked" only moves when at least one price was confirmed
            data["updated"] = today
        DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        build_site_data(data)

    print(write_report(today, changes, held, failures, blocked, healed, unreachable, ok, dry))
    if not dry:
        print("Email alert:", send_alert(changes, os.environ.get("SITE_URL", "https://trtledger.com"), data.get("sponsor")))
    # A red run makes GitHub email the owner: broken rules and held price jumps need a person
    sys.exit(1 if failures or held else 0)


if __name__ == "__main__":
    main()
