# Melbourne no-website lead scavenger

Finds Melbourne businesses in **high-ticket niches that have no website**, and
traces the **actual owner** behind each one — not just the switchboard number.

Built on the connectors already attached to this workspace: **Firecrawl** for
discovery and verification, **Render** for scheduled runs, **Resend** for
outreach.

```bash
pip install -r requirements.txt
cp .env.example .env          # add your FIRECRAWL_API_KEY
python -m scavenger.cli --regions melbourne,craigieburn --limit 40 --verbose
```

## How it works

```
Hotfrog directory  ──►  candidates (name, phone, suburb, no website shown)
        │
        ├─ shared-phone filter ──► drop lead-gen resellers reusing one number
        ├─ generic-name filter ──► drop "<Service> <Suburb>" SEO shells
        │
        ▼
website verification  ──►  directory detail page, then targeted web search
        │                  a lead is only sold as "no website" on evidence
        ▼
ABN Lookup  ──►  owner identity  +  liveness  +  GST  +  years trading
        │
        ▼
score ──► CSV · JSONL · markdown call sheet
```

### Finding the owner, not the business

Three paths, in descending confidence — every one recorded in `owner_source`:

| Registered as | What the register gives you | Confidence |
|---|---|---|
| Individual / Sole Trader | The owner's legal name outright — `LAMPROU, JAMES` → **James Lamprou** | `confirmed` |
| Discretionary family trust | The family surname — `THE CIRKA FAMILY TRUST` → **Cirka family** | `inferred` |
| Pty Ltd company | Company only; directors need a paid ASIC extract | `none` |

For a sole trader the listed mobile *is* the owner's direct line — which is why
`direct_mobile` carries weight in the score.

### Why verification is not optional

Hotfrog **hides the website field on search pages** even when the business has
one. Treating "no website link" as proof produces false leads. Live example:
*Saluni Metal Roofing* showed no website, has a confirmed sole-trader owner and
GST registration — and turned out to run `salunimetalroofing.com`. Verification
caught it before it reached the call sheet.

### Why the ABN check doubles as a freshness test

Directory listings go stale for years. An **active ABN is a harder liveness
signal than a review date**, and it costs nothing extra because the same lookup
identifies the owner. *F & R Spiteri Concreting*, *Donisi Concreting* and
*Ascot Excavations* were all dropped this way.

## Scoring

`score.py`, out of 100 — ticket value (30), owner identified (25), direct mobile
(15), sole trader (10), GST registered (10), years trading (10).

GST registration matters commercially: it implies turnover above $75k, so the
business can actually afford the work.

Penalties: a confirmed website zeroes the lead; unverified halves it; a shared
phone cuts it to 20%; a generic name to 40%.

## Layout

| Path | |
|---|---|
| `scavenger/config.py` | niches, ticket values, regions, weights |
| `scavenger/sources/` | `hotfrog.py` discovery · `abn.py` owner + liveness |
| `scavenger/verify.py` | website evidence rules |
| `scavenger/enrich.py` | ABN matching and owner resolution |
| `scavenger/score.py` | scoring and junk filtering |
| `outreach/templates.py` | call opener + compliant email |
| `render.yaml` | weekly Render cron job |
| `COMPLIANCE.md` | **read before contacting anyone** |
| `data/leads/` | CSV · JSONL · call sheet |

## Tuning

Edit `NICHES` and `REGIONS` in `scavenger/config.py`. `--limit` caps how many
leads get verified and enriched, which is what controls Firecrawl spend.
Responses are cached under `SCAVENGER_CACHE`, so re-runs cost nothing.

## Tests

```bash
python3 tests/test_logic.py
```

13 tests over the real page shapes observed while building — phone
normalisation, ABN person/trust parsing, website classification, shared-phone
detection, dedupe and scoring.

## Before you call or email

Read `COMPLIANCE.md`. Cold calls must be washed against the **Do Not Call
Register**; email must satisfy the **Spam Act 2003** (accurate sender, working
unsubscribe); owner names from ABN Lookup are personal information under the
**Privacy Act 1988** and should not be resold or republished.

## Known limits

- Company directors need a paid ASIC extract; the pipeline flags
  `company_owner_needs_asic` rather than guessing.
- Personal email addresses are generally not public. The pipeline collects
  published business email only and does not attempt to guess or harvest
  private addresses.
- Hotfrog is the only discovery source wired up. Localsearch and Google Business
  Profiles would raise volume; Yellow Pages rejects parameterised search URLs.
- **Semrush is connected to this workspace but disabled in chat.** Enabling it
  would allow domain-level verification as a cross-check on the search sweep.
