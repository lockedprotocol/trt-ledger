# TRT Ledger — one-time setup

After these steps the site runs itself: it checks prices weekly, refreshes the clinic
directory monthly, repairs its own price rules when a clinic redesigns its page,
emails subscribers when prices change, and republishes automatically. Total setup: about 30 minutes.

## 1. Put the site on GitHub (free)

1. Create a **public** repository named `trt-ledger` and upload this folder to it.
   (Claude can do this for you with the GitHub account you're signed into.)
2. In the repository: **Settings → Actions → General → Workflow permissions →
   "Read and write permissions" → Save.** This lets the weekly jobs save new prices.
3. **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `(root)` → Save.**
   The site goes live at `https://<your-username>.github.io/trt-ledger/` within a few minutes,
   and republishes itself every time a job saves new data.
4. **Settings → Secrets and variables → Actions → Variables → New variable** → name `SITE_URL`,
   value = your site's address. Alert emails link here. Change it when your own domain is live.

## 2. Use your own domain (trtledger.com)

1. Buy `trtledger.com` (Cloudflare or Namecheap, about $10/year).
2. At the domain company, add these DNS records:
   - `A` records for `@` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `CNAME` record for `www` → `<your-username>.github.io`
3. **Settings → Pages → Custom domain** → enter `trtledger.com` → Save → tick **Enforce HTTPS** once it's offered.
4. Update the `SITE_URL` variable to `https://trtledger.com`.

## 3. Price-drop emails (Buttondown, free to start)

1. Create an account at buttondown.com.
2. Put your Buttondown username in `data.json` as `"buttondownUsername": "yourname"`,
   then run `python3 checker/check_prices.py --build`. The signup form on the site goes live.
3. Copy your API key (Buttondown **Settings → API**) into the repository:
   **Settings → Secrets and variables → Actions → New repository secret** → name `BUTTONDOWN_API_KEY`.

## 4. Automatic repairs (optional, a few cents a month)

When a clinic redesigns its pricing page, the weekly check asks Claude to find the price
again and writes a new rule. It only accepts the result after checking it against the page.

1. Create an API key at console.anthropic.com and set a low monthly spend limit there (e.g. $5).
2. Add it as a repository secret named `ANTHROPIC_API_KEY`.

Without this key, a broken rule just shows up in the weekly report for you to fix.

## 5. Start the jobs

In the repository's **Actions** tab, open each workflow and click **Run workflow** once:
- **Weekly price check** — then runs every Monday.
- **Monthly clinic directory refresh** — then runs on the 2nd of each month.

## What runs by itself

| Job | When | What it does |
|---|---|---|
| Weekly price check | Mondays | Re-reads every clinic's own pricing page, updates the site, emails subscribers about changes, repairs broken rules |
| Monthly directory refresh | 2nd of each month | Re-pulls ~14,000 clinics from the federal NPI registry and chain location lists |
| Stale-price flags | Always | Any price not re-confirmed for 3 weeks is labelled on the site automatically |
| Safety stops | Always | Price jumps over 50% are held for you; a directory that shrinks over 20% isn't published; a chain list that suddenly halves keeps last month's locations; a site that's down is retried next week |

## What still needs you (about 15 minutes a month)

GitHub emails you when a run fails, which the weekly check does on purpose when a price rule is
broken or a price jumped more than 50%. Each run writes `checker/last-report.md`; look at it once a month too:
- **"Check by hand"** — TRT Nation and PeterMD block automated visits. Look at their pricing pages;
  if a price changed, edit `data.json`, set that clinic's `checked` date to today, and run
  `python3 checker/check_prices.py --build`.
- **"Held for review"** — a price moved more than 50%. Confirm it on the clinic's site, then edit `data.json`.
- **"Couldn't read"** — a rule broke and couldn't be repaired automatically.

GitHub pauses scheduled jobs in repositories with no activity for 60 days. The weekly job
commits its report every week, which keeps them running.
