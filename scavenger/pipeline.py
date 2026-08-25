"""End-to-end scavenging run."""
from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from . import dedupe as dedupe_mod
from . import enrich as enrich_mod
from . import score as score_mod
from . import verify as verify_mod
from .config import NICHES, REGIONS
from .export import write_callsheet, write_csv, write_jsonl
from .firecrawl_client import Firecrawl
from .sources import hotfrog

log = logging.getLogger("scavenger")


def run(
    niches: list[dict] | None = None,
    regions: list[str] | None = None,
    outdir: str | Path = "data/leads",
    max_enrich: int = 60,
    min_score: int = 25,
    api_key: str | None = None,
) -> dict:
    """Discover -> dedupe -> verify -> enrich -> score -> export."""
    niches = niches or NICHES
    regions = regions or REGIONS
    fc = Firecrawl(api_key=api_key)

    # -- 1. discover --------------------------------------------------------
    candidates: list = []
    for region in regions:
        for niche in niches:
            try:
                found = hotfrog.discover(fc, region, niche)
                log.info("discover %s/%s -> %d", region, niche["slug"], len(found))
                candidates.append(found)
            except Exception as exc:  # noqa: BLE001
                log.warning("discover %s/%s failed: %s", region, niche["slug"], exc)
    leads = [l for batch in candidates for l in batch]
    log.info("raw candidates: %d", len(leads))

    # -- 2. dedupe + drop resold numbers -----------------------------------
    score_mod.flag_shared_phones(leads)
    leads = dedupe_mod.dedupe(leads)
    log.info("after dedupe: %d", len(leads))

    # Anything already advertising a website on the search page is out now,
    # before we spend enrichment credits on it.
    leads = [l for l in leads if not (l.website_url and verify_mod.is_own_website(l.website_url))]

    # Work the most promising first so a capped run spends its budget well.
    leads.sort(key=lambda l: (-l.ticket_value, bool(l.flags)))

    # -- 3. verify website status ------------------------------------------
    for lead in leads[:max_enrich]:
        if not lead.source_url or "hotfrog" not in lead.source_url:
            continue
        try:
            verify_mod.verify_from_detail(lead, hotfrog.fetch_detail(fc, lead.source_url))
        except Exception as exc:  # noqa: BLE001
            log.warning("verify %s failed: %s", lead.business_name, exc)
        if lead.has_website is False:
            try:
                results = fc.search(
                    f'"{lead.business_name}" {lead.suburb or "Melbourne"} VIC', limit=6
                )
                verify_mod.verify_from_search(lead, results)
            except Exception as exc:  # noqa: BLE001
                log.warning("search %s failed: %s", lead.business_name, exc)

    # -- 4. enrich owners (only for those still lacking a website) ----------
    for lead in leads[:max_enrich]:
        if lead.has_website is False:
            enrich_mod.enrich(fc, lead)

    # -- 5. score and export ------------------------------------------------
    for lead in leads:
        score_mod.score(lead)

    # A lead with no confirmed active ABN is a dead listing, not a prospect.
    qualified = [
        l for l in leads
        if l.score >= min_score
        and l.has_website is False
        and not any(f.startswith("no_abn_match") for f in l.flags)
    ]
    qualified.sort(key=lambda l: -l.score)

    outdir = Path(outdir)
    stamp = date.today().isoformat()
    paths = {
        "csv": write_csv(qualified, outdir / f"melbourne-leads-{stamp}.csv"),
        "jsonl": write_jsonl(leads, outdir / f"all-candidates-{stamp}.jsonl"),
        "callsheet": write_callsheet(qualified, outdir / f"call-sheet-{stamp}.md"),
    }
    log.info("qualified: %d/%d", len(qualified), len(leads))
    return {"qualified": qualified, "all": leads, "paths": paths}
