# Compliance notes — read before you contact anyone

This tool collects information from **public sources only**: business directory
listings and the Australian Business Register. It does not attempt to obtain
private, non-published personal contact details, and it should not be modified
to do so.

## Cold calling — Do Not Call Register
Before calling any number in the export, wash the list against the
**Do Not Call Register** (donotcall.gov.au). Numbers published purely as
business contact points are generally callable for business-to-business
purposes, but the safe process is to check, and to keep the wash records.
Penalties under the *Do Not Call Register Act 2006* are per-call.

## Email — Spam Act 2003
Unsolicited commercial email to a business needs either consent or the
inferred-consent position that applies where a work address is
**conspicuously published** and not marked "no unsolicited emails", and the
message is relevant to that person's role. Every message must:
- identify you accurately, with real contact details, and
- carry a working unsubscribe honoured within 5 business days.

`outreach/templates.py` includes both. Do not strip them.

## Privacy Act 1988
Owner names taken from ABN Lookup are personal information even though the
register is public. Handle accordingly:
- use it only for the business purpose it was collected for,
- don't republish or resell the enriched list,
- honour any request to be removed, and
- delete `data/leads/` exports you are no longer working.

Sole trader ABN records are personal data about an individual. Treat the
`owner_name` column with more care than the business phone number.

## Source terms
Directory sites have terms of use that may restrict automated access. The
pipeline is rate-limited and caches responses so a re-run costs no extra
requests. Keep it that way; do not raise `qps` to hammer a source.
