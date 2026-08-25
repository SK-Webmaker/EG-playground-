"""ABN Lookup over plain HTTP -- no API credits.

Same role as sources/abn.py but fetched with curl instead of Firecrawl, because
credits are the scarce resource. ABN Lookup is a public government register and
serves plain server-rendered HTML, so it parses cleanly with regex.

What it gives us, all of which decides whether a lead is worth a call:
  owner name (sole traders), liveness (active ABN), GST (turnover > $75k),
  and years trading.
"""
from __future__ import annotations

import html
import re
import urllib.parse
from dataclasses import dataclass, field
from datetime import date

from .traders import fetch

SEARCH = "https://abr.business.gov.au/Search/ResultsActive?SearchText={q}"
VIEW = "https://abr.business.gov.au/ABN/View?abn={abn}"

PERSON = re.compile(r"^([A-Z][A-Za-z'\-]+),\s*([A-Z][A-Za-z'\-\s]+)$")
FAMILY_TRUST = re.compile(r"(?:the\s+)?(?:trustee\s+for\s+)?(?:the\s+)?"
                          r"([A-Z][A-Za-z'\-]+)\s+FAMILY\s+TRUST", re.I)
MONTHS = {m: i + 1 for i, m in enumerate(
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])}

STOP = {"the","and","pty","ltd","for","trustee","co","services","service",
        "melbourne","vic","victoria","australia","cafe","shop","store"}


def _text(page: str) -> str:
    body = re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body)))


def _tokens(s: str) -> set[str]:
    return {t for t in re.findall(r"[a-z]+", s.lower()) if len(t) > 2 and t not in STOP}


@dataclass
class AbnRecord:
    abn: str | None = None
    entity_name: str | None = None
    entity_type: str | None = None
    owner_name: str | None = None
    owner_confidence: str = "none"
    gst: bool = False
    active_from: str | None = None
    years: float | None = None
    postcode: str | None = None
    match: float = 0.0
    notes: list[str] = field(default_factory=list)


def search(name: str) -> list[tuple[str, str, str]]:
    """(abn, listed_name, location) rows from the active-ABN results table."""
    page = fetch(SEARCH.format(q=urllib.parse.quote_plus(name)))
    if not page:
        return []
    rows = []
    # Each row: <a href="...ABN/View?abn=NNN">NN NNN NNN NNN</a> ... name ... postcode STATE
    for m in re.finditer(
            r'ABN/View\?abn=(\d+)"[^>]*>.*?</a>(.*?)(?=<tr|</table)', page, re.S):
        abn, rest = m.group(1), _text(m.group(2))
        loc = ""
        if (lm := re.search(r"\b(\d{4})\s+(ACT|NSW|NT|QLD|SA|TAS|VIC|WA)\b", rest)):
            loc = lm.group(0)
            rest = rest[:lm.start()]
        listed = re.sub(r"\b(Active|Entity Name|Business Name|Trading Name|Other Name)\b",
                        " ", rest).strip(" |")
        rows.append((abn, listed.strip(), loc))
    return rows


def fetch_record(abn: str) -> AbnRecord:
    page = fetch(VIEW.format(abn=re.sub(r"\D", "", abn)))
    r = AbnRecord(abn=abn)
    if not page:
        r.notes.append("fetch_failed")
        return r
    t = _text(page)
    if (m := re.search(r"Entity name:\s*(.+?)\s*ABN status:", t)):
        r.entity_name = m.group(1).strip()
    if (m := re.search(r"Entity type:\s*(.+?)\s*(?:Goods|Main business|ABN last)", t)):
        r.entity_type = m.group(1).strip()
    if (m := re.search(r"ABN status:\s*Active from (\d{1,2} \w{3} \d{4})", t)):
        r.active_from = m.group(1)
        d = re.match(r"(\d{1,2}) (\w{3}) (\d{4})", m.group(1))
        if d and d.group(2)[:3].title() in MONTHS:
            start = date(int(d.group(3)), MONTHS[d.group(2)[:3].title()], int(d.group(1)))
            r.years = round((date.today() - start).days / 365.25, 1)
    r.gst = bool(re.search(r"Goods & Services Tax \(GST\):\s*Registered from", t))
    if (m := re.search(r"Main business location:\s*(\w{2,3})\s*(\d{4})", t)):
        r.postcode = m.group(2)

    en = r.entity_name or ""
    if PERSON.match(en):
        g = PERSON.match(en)
        r.owner_name = f"{g.group(2).strip().title()} {g.group(1).strip().title()}"
        r.owner_confidence = "confirmed"
    elif (fm := FAMILY_TRUST.search(en)):
        if fm.group(1).lower() not in {"the", "family", "trust"}:
            r.owner_name = f"{fm.group(1).title()} family"
            r.owner_confidence = "inferred"
    return r


def enrich(name: str, postcode: str | None = None, min_match: float = 0.55) -> AbnRecord:
    """Best-effort ABN match for a trading name; blank record when unsure."""
    rows = search(name)
    if not rows:
        return AbnRecord(notes=["no_abn_rows"])
    want = _tokens(name)
    best, best_s = None, 0.0
    for abn, listed, loc in rows:
        lt = _tokens(listed)
        if not want or not lt:
            continue
        s = len(want & lt) / len(want)
        if "VIC" in loc:
            s += 0.15
        elif loc:
            s -= 0.35
        if postcode and postcode in loc:
            s += 0.2
        if s > best_s:
            best, best_s = abn, s
    if not best or best_s < min_match:
        return AbnRecord(match=round(best_s, 2), notes=["no_confident_match"])
    rec = fetch_record(best)
    rec.match = round(best_s, 2)
    return rec
