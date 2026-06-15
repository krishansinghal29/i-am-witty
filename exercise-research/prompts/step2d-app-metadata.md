# Step 2d — App Metadata Enrichment Subagent Prompt

> Template. Replace `{BATCH_NAME}` and `{APP_BATCH}` per run.

---

You are gathering the maximum available **company / product metadata** for each app
in your batch. These are apps for communication/speaking/dating/comedy training.

Apps in your batch ({BATCH_NAME}) — read this file for names + URLs:
`/Users/krishansinghal/i-am-witty/exercise-research/output/step2/app-metadata/batches/{BATCH_NAME}.jsonl`

## For each app, find as much as you can of:
- Founding/launch date (company founded vs app first released — capture both if they differ)
- Founder(s) and current CEO
- Headquarters / country
- Funding: total raised, individual rounds (stage, amount, date, lead investors), last known valuation; or "bootstrapped"/"no known funding"
- Revenue estimate (ARR/annual), and basis for the estimate
- Downloads / installs estimate, and MAU/DAU if available
- Employee/team size
- Pricing (free, freemium tiers, subscription price, one-time)
- Platforms (iOS, Android, web)
- Ownership/acquisition status (independent, acquired by X, shut down, etc.)
- Parent company / studio if part of one

## Where to look
Crunchbase, PitchBook snippets, Tracxn, company About/Press pages, TechCrunch and
other funding-announcement coverage, LinkedIn company pages, App Store / Google Play
listings (release date, rating count as a downloads proxy), Sensor Tower / data.ai /
AppMagic public estimates, SimilarWeb, product blogs, founder interviews/podcasts,
Wellfound (AngelList). Triangulate; many of these are small private apps where
figures are estimates — that's fine, just label them.

Be explicit about confidence: every numeric field gets a `confidence` of
`confirmed` (from a primary/official source) or `estimate` (third-party/inferred),
and cite where it came from.

## Output
Write to:
`/Users/krishansinghal/i-am-witty/exercise-research/output/step2/app-metadata/{BATCH_NAME}.jsonl`

One JSON object per app:
```json
{
  "provider": "App name (exactly as in the batch file)",
  "company": "legal/company name if different",
  "url": "primary URL",
  "founded": "year/date company founded, or ''",
  "launched": "app first-release date, or ''",
  "founders": ["names"],
  "ceo": "current CEO/lead, or ''",
  "hq": "city, country",
  "funding_total": "e.g. '$4.2M' or 'bootstrapped' or 'unknown'",
  "funding_rounds": [{"stage": "Seed", "amount": "$2M", "date": "2021-05", "investors": ["..."]}],
  "last_valuation": "or ''",
  "revenue_estimate": "e.g. '~$3M ARR' or 'unknown'",
  "downloads_estimate": "e.g. '500K+ installs' or 'unknown'",
  "users_estimate": "MAU/DAU if known, or ''",
  "employees": "e.g. '11-50' or number or ''",
  "pricing": "concise pricing summary",
  "platforms": ["iOS","Android","web"],
  "ownership": "independent | acquired by X (date) | shut down | subsidiary of X",
  "confidence_notes": "which fields are confirmed vs estimated, and key caveats",
  "source_urls": ["urls used"]
}
```
Write incrementally; validate every line is JSON. Use `unknown`/`''` for anything
you genuinely cannot find — do not fabricate figures.

## Final report
Report: apps covered, how many had funding data found, the best-documented and the
most opaque app in the batch, and any notable findings (big raises, acquisitions,
shutdowns).
