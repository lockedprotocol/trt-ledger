"""XO agent: builds the daily executive briefing and schedules it for 8:00 AM US Eastern.

Deterministic on purpose: every line is read from a live source (the site, GitHub, data.json,
Buttondown). No LLM writes into the briefing, so it can't invent a number.

Env (all optional except the email ones; a missing source shows as "not connected"):
  RESEND_API_KEY, BRIEFING_TO, BRIEFING_FROM   email delivery (Resend, scheduled send)
  GITHUB_TOKEN, GITHUB_REPOSITORY              workflow + Pages certificate status
  BUTTONDOWN_API_KEY                           subscriber count
  HC_PING_URL                                  healthchecks.io dead-man's switch
  --dry-run                                    print the briefing, send nothing
"""
import datetime as dt, json, os, re, ssl, sys, urllib.error, urllib.request
from pathlib import Path
from string import Template
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
ET = ZoneInfo("America/New_York")
SITE = "trtledger.com"
WORKFLOWS = {"check-prices.yml": "Weekly price check", "refresh-directory.yml": "Monthly directory refresh",
             "morning-briefing.yml": "Morning briefing"}


def http(url, headers=None, data=None, method=None, timeout=20):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "trt-ledger-ops", **(headers or {})},
                                 method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
        return r.status, (json.loads(body) if body[:1] in (b"{", b"[") else body)


def probe(url):
    try:
        return f"✅ {http(url)[0]}"
    except urllib.error.HTTPError as e:
        return f"❌ HTTP {e.code}"
    except (ssl.SSLError, urllib.error.URLError) as e:
        reason = getattr(e, "reason", e)
        return f"❌ {'certificate error' if 'CERTIFICATE' in str(reason).upper() else reason}"
    except Exception as e:
        return f"❌ {type(e).__name__}"


def github(path):
    token, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY", "trtledger/trt-ledger")
    if not token:
        return None
    return http(f"https://api.github.com/repos/{repo}{path}",
                {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})[1]


def collect():
    f, decisions = {}, []
    now = dt.datetime.now(ET)

    # Site
    f["https"], f["http"] = probe(f"https://{SITE}"), probe(f"http://{SITE}")
    try:
        pages = github("/pages")
        cert = (pages or {}).get("https_certificate", {}).get("state")
        f["cert"] = cert or "not connected"
        if pages and not pages.get("https_enforced") and cert == "approved":
            decisions.append("HTTPS certificate is issued — turn on **Enforce HTTPS** (repo → Settings → Pages).")
    except Exception as e:
        f["cert"] = f"unknown ({type(e).__name__})"
    if not f["https"].startswith("✅"):
        decisions.append("Hold the Reddit launch: https://trtledger.com doesn't load yet.")

    # Data (Operations agent output)
    data = json.loads((ROOT / "data.json").read_text())
    clinics = data["clinics"]
    f["clinic_count"], f["data_updated"] = len(clinics), data.get("updated", "?")
    cutoff = (now.date() - dt.timedelta(days=14)).isoformat()
    stale = [c["name"] for c in clinics if c.get("checked", "") < cutoff]
    f["stale"] = ", ".join(stale) if stale else "none ✅"
    report = (ROOT / "checker/last-report.md").read_text()
    nums = dict(re.findall(r"^- (.+?): (\d+)$", report, re.M))
    f["last_check_summary"] = (f"{nums.get('Sources confirmed', '?')} confirmed, "
                               f"{nums.get('Price changes', '?')} changed, "
                               f"{nums.get('Held for review (jump over 50%)', '?')} held")
    if int(nums.get("Held for review (jump over 50%)", 0)):
        decisions.append("A price jump over 50% is **held** — confirm it in checker/last-report.md.")
    if int(nums.get("Couldn't read", 0)):
        decisions.append("A price rule broke and self-repair failed — see checker/last-report.md.")
    blocked = re.findall(r"^- \*\*(.+?)\*\* — last confirmed", report, re.M)
    if blocked and now.weekday() == 0:
        decisions.append(f"Monday hand-check (sites block bots): {', '.join(blocked)}.")

    # Automation health
    rows = []
    for wf, name in WORKFLOWS.items():
        try:
            runs = (github(f"/actions/workflows/{wf}/runs?per_page=1") or {}).get("workflow_runs", [])
        except Exception:
            runs = []
        if not runs:
            rows.append(f"| {name} | — | not connected |")
            continue
        r = runs[0]
        ok = r.get("conclusion") == "success"
        rows.append(f"| {name} | {r['created_at'][:10]} | {'✅' if ok else '❌ ' + str(r.get('conclusion') or r['status'])} |")
        if r.get("conclusion") == "failure" and wf != "morning-briefing.yml":
            decisions.append(f"**{name}** failed on {r['created_at'][:10]}: {r['html_url']}")
    f["jobs"] = "\n".join(rows)

    # Audience (Marketing agent output)
    key = os.environ.get("BUTTONDOWN_API_KEY")
    try:
        f["subscribers"] = http("https://api.buttondown.com/v1/subscribers?type=regular",
                                {"Authorization": f"Token {key}"})[1].get("count", "?") if key else "not connected"
    except Exception as e:
        f["subscribers"] = f"unknown ({type(e).__name__})"
    f["search"] = "not connected (Search Console API)"
    f["traffic"] = cloudflare_visits(now.date())
    f["drafts"] = post_drafts(data, now.date())
    if f["drafts"].startswith("1."):
        decisions.append("Post drafts are ready below — click to post the ones you approve.")

    f["decisions"] = "\n".join(f"{i}. {d}" for i, d in enumerate(decisions, 1)) or "None — the machine is running. ✅"
    f["verdict"] = "🟢 All clear" if not decisions else f"🟡 {len(decisions)} item(s) need you"
    f["date"], f["generated"] = now.strftime("%a %b %-d, %Y"), now.strftime("%Y-%m-%d %H:%M %Z")
    return f


def cloudflare_visits(today):
    """Visits and page views for the last 7 days from Cloudflare Web Analytics (GraphQL API)."""
    token, acct, tag = (os.environ.get(k) for k in ("CF_API_TOKEN", "CF_ACCOUNT_ID", "CF_SITE_TAG"))
    if not (token and acct and tag):
        return "not connected (Cloudflare Web Analytics)"
    token = "".join(ch for ch in token if ch.isascii() and not ch.isspace())   # pasted tokens can carry invisible characters
    q = """query($a:String!,$t:String!,$from:Date!,$to:Date!){viewer{accounts(filter:{accountTag:$a}){
      rumPageloadEventsAdaptiveGroups(limit:1,filter:{siteTag:$t,date_geq:$from,date_leq:$to}){count sum{visits}}}}}"""
    v = {"a": acct, "t": tag, "from": str(today - dt.timedelta(days=7)), "to": str(today - dt.timedelta(days=1))}
    try:
        res = http("https://api.cloudflare.com/client/v4/graphql",
                   {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                   json.dumps({"query": q, "variables": v}).encode(), "POST")[1]
        groups = res["data"]["viewer"]["accounts"][0]["rumPageloadEventsAdaptiveGroups"]
        if not groups:
            return "**0** visits"
        return f"**{groups[0]['sum']['visits']}** visits · {groups[0]['count']} page views"
    except urllib.error.HTTPError as e:
        return f"error (Cloudflare HTTP {e.code}: check CF_API_TOKEN has Account Analytics: Read)"
    except Exception as e:
        return f"unknown ({type(e).__name__})"


def post_drafts(data, today):
    """CMO drafts, built only from data.json facts. You approve by clicking; nothing posts on its own."""
    from urllib.parse import quote
    site = f"https://{SITE}"
    week_ago = str(today - dt.timedelta(days=7))
    posts = []
    for c in data.get("recentChanges", []):
        if c.get("date", "") >= week_ago and c.get("old") and c.get("new"):
            verb = "dropped" if c["new"] < c["old"] else "raised"
            what = {"monthly": "monthly TRT price", "intakeFee": "intake fee", "labFee": "lab fee"}.get(c.get("field"), "TRT price")
            posts.append(f"{c['name']} {verb} its {what} from ${c['old']:,} to ${c['new']:,} "
                         f"(source: {c.get('url', '')}). Compare every online clinic's true first-year cost: {site}")
    if today.weekday() == 1:   # Tuesday: one evergreen post
        n = len(data["clinics"])
        posts.append(f"The advertised TRT price usually leaves out labs, meds or intake fees. I add them up for "
                     f"{n} online clinics, re-checked weekly, every price linked to its source: {site}")
    if not posts:
        return "None today."
    return "\n".join(f"{i}. {p}\n   → [Post on X](https://x.com/intent/post?text={quote(p)})"
                     for i, p in enumerate(posts, 1))


def send_at(text, subject, when):
    """Resend scheduled send: GitHub cron is often 5–30 min late, so the job runs early and Resend delivers at 8:00."""
    key = os.environ["RESEND_API_KEY"]
    late = dt.datetime.now(ET) >= when
    payload = {"from": os.environ.get("BRIEFING_FROM", "TRT Ledger <onboarding@resend.dev>"),
               "to": [os.environ["BRIEFING_TO"]], "subject": subject + (" (late)" if late else ""), "text": text}
    if not late:
        payload["scheduled_at"] = when.isoformat()
    return http("https://api.resend.com/emails", {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json.dumps(payload).encode(), "POST")[1]


def ping(suffix=""):
    url = os.environ.get("HC_PING_URL")
    if url:
        try:
            http(url + suffix, timeout=10)
        except Exception:
            pass


def main():
    dry = "--dry-run" in sys.argv
    try:
        f = collect()
        text = Template((ROOT / "ops/briefing_template.md").read_text()).safe_substitute(f)
        if dry:
            print(text)
            return
        today = dt.datetime.now(ET).date()
        (ROOT / "ops/briefings").mkdir(exist_ok=True)
        (ROOT / f"ops/briefings/{today}.md").write_text(text)   # archive; the daily commit also keeps cron alive
        when = dt.datetime.combine(today, dt.time(8, 0), ET)   # 8:00 AM Eastern (EST now, EDT in summer)
        if os.environ.get("RESEND_API_KEY") and os.environ.get("BRIEFING_TO"):
            print("Resend:", send_at(text, f"TRT Ledger briefing — {f['verdict']}", when))
        else:
            print("Email not connected yet (RESEND_API_KEY / BRIEFING_TO); briefing archived only.\n\n" + text)
        ping()   # dead-man's switch: healthchecks.io alerts you if this ping doesn't arrive
    except Exception:
        ping("/fail")
        raise


if __name__ == "__main__":
    main()
