# Backdraft Grants: working guide for collaborators

This file is the shared source of truth for everyone working on this repo: Joseph, Hayes, Joseph's Perplexity Computer task and Hayes's Claude. Update it when a fact changes.

## What it is
Backdraft Grants (https://backdraftgrants.com) helps volunteer and combination fire departments write FEMA grant narratives.
- Free tool: pick your department and get draft narratives for AFG, SAFER and Fire Prevention and Safety (FP&S). The drafts are prefilled from public data (the USFA National Fire Department Registry and Census population and poverty data). Facts only the chief knows stay as red blanks, because the tool never invents facts in a federal application.
- Paid plans, taken as reservations at no charge for now:
  - $249: finished narratives.
  - $795: full FEMA GO prep. We are added as Grant Writer, enter every section, and the chief (the AOR) signs and submits.
- Free state fire grant deadline pages for all 50 states (public/states/*.html), for search traffic.
- The next FEMA AFG round is expected in 2027. The FY2025 window ran May 19 to June 22, 2026.
- Run by Joseph Gahagan, 1390 Chain Bridge Rd #10140, McLean, VA 22101. Not affiliated with FEMA.

## Goal and status
- Goal: 25 or more real people who reserve a plan. Payment collection starts only after that, and Joseph sets up payouts himself.
- Real reservations so far: 0. Most recorded traffic is the owner testing.
- The main bottleneck is that no outreach has been sent yet.

## Rules (non-negotiable)
- Legal only, under US federal and Virginia law. No deception, fake reviews, testimonials or social proof, invented scarcity, impersonation, or collecting data against a site's terms.
- Real evidence only. Never invent numbers or results. If something can't be tested, call it "untested".
- Free tiers only. No ad spend and no paid signups without Joseph's approval.
- Email goes only to business contacts with a relevant reason, and it must follow CAN-SPAM: a truthful subject, the real identity and address above, and a working opt-out. No bulk blasts, purchased lists, calls or texts.
- Send from hello@backdraftgrants.com only. Never send from wagl, COMPÁS, HedgePick or Yondr addresses, and keep those businesses completely separate.
- Do not put secrets in this repo. That includes the admin key, contact lists and outreach data. The repo is public.

## Architecture
- public/: the static site. public/index.html holds the homepage and the free tool, all inline; it is about 780 lines.
  - The state deadline data is the `var G=[...]` array in index.html.
  - public/version.txt holds the version number; open pages reload themselves when it changes.
- server.py: a small Flask app on port 5001 with SQLite (data.db, which is not in git). Endpoints:
  - POST /api/event: tracks events such as view and reserve_click.
  - POST /api/reserve: saves a reservation.
  - GET /api/stats: needs the X-Admin-Key header. The key is private; ask Joseph.
  - The department search API.
- On the live site, the API is reached at https://backdraftgrants.com/port/5001/api/...
- Hosting: the app is published through Joseph's Perplexity Computer at backdraft.pplx.app. The old afgdrafts.pplx.app forwards to the domain.
- Domain: backdraftgrants.com is registered at Porkbun and its DNS is on Cloudflare (free plan). The Cloudflare Worker "backdraft-grants" (cloudflare/worker.js) proxies backdraft.pplx.app so the address bar keeps showing backdraftgrants.com.
- Email: hello@backdraftgrants.com is a Google Workspace alias. MX, SPF, DKIM and DMARC are all set.
- tools/: the build scripts.
  - build_states.py regenerates public/states/*.html and the sitemap from the G array.
  - build_data.py builds the department and economic data from the files in data/.
- research/: the sourced state program research.

## How changes go live
Only Joseph's Perplexity task can deploy, because the hosting belongs to his Perplexity account.
1. Work on a branch and open a pull request to `main`. Never force-push and never rewrite history.
2. Before merging, make sure that:
   - public/version.txt and the matching `var V='...'` in index.html are bumped to the same new number;
   - `python3 tools/build_states.py` has been run if the G array changed;
   - every inline script passes `node --check`. A broken script once disabled the whole tool.
3. Merge into main. Each morning at 9:00 ET, the Perplexity daily cycle pulls main, deploys any work that isn't live yet and logs it. To deploy sooner, ask Joseph.
4. Check https://backdraftgrants.com/version.txt to confirm the change is live.

The Perplexity daily cycle also edits main every day; it re-verifies state deadlines and commits the results. Always pull before you start, and keep pull requests small to avoid conflicts.

## Open items
- 25 personalized outreach drafts are waiting, unsent. Joseph sends them himself from hello@backdraftgrants.com.
- The $795 tier needs a FEMA GO Grant Writer login. Joseph creates it; see STOP_CHECKLIST.md.
- Payout setup, such as a Stripe Payment Link, is Joseph's job. Nobody else handles bank details.
- The Gmail send-as display name reads "BackDraft Grants". The brand is "Backdraft Grants".
- A free trial of Porkbun's hosted inbox ends 2026-12-09. Do not activate it; mail runs through Google.

## Legal pages (added Nov 24, 2026, branch legal-pages)
- Source text lives in `tools/legal/privacy.html` and `tools/legal/terms.html` (body fragments with TITLE/DESC comments). Edit those, never the generated files.
- `python3 tools/build_states.py` now also writes `public/privacy.html`, `public/terms.html`, adds them to `sitemap.xml`, and puts the shared footer (Privacy, Terms, Grant disclaimer, hello@backdraftgrants.com) on all 50 state pages.
- The homepage footer and the reservation acknowledgment line (`#ack`) are in `public/index.html`. Reservations record `[terms 2026-11-24]` at the start of the note. If the Terms change materially, update that date tag and the "Last updated" line together.
- The Privacy Policy describes actual practices (no cookies, no IP stored by the app, drafts stay in the browser, Google Fonts loaded). If you add analytics, cookies, payments, AI processing of customer data or new vendors, update the policy in the same PR.
- Not yet decided by the owner: refund terms for paid plans, checkbox vs text acknowledgment, liability cap amount, venue. Paid-service refund terms must be approved before any payment collection.

## Admin & Outreach Pipeline dashboard (added Nov 27, 2026)
- Live at `https://backdraftgrants.com/admin.html` (marked `noindex, nofollow`, locked behind `X-Admin-Key` from `admin_key.txt`).
- Shows live non-QA site visitors, reserve clicks, real vs test reservations, and the outreach pipeline table (`Emailed`, `Called`, `Outcome`, `Notes`, non-emergency HQ phone, draft link, Add Department, CSV export).
- Backed by `pipeline` table in SQLite `data.db` (`GET/POST /api/pipeline`, `PATCH/DELETE /api/pipeline/<id>`).
- Contact lists and customer records remain out of the public git repo (`outreach/`, `data.db`, `admin_key.txt` are gitignored).
