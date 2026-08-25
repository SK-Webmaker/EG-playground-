"""ABN Lookup (Australian Business Register) -- the owner-identification source.

This is the piece that turns a business listing into a named human. ABN Lookup is
a public government register. For an Individual/Sole Trader the `Entity name` IS
the owner's legal name, rendered "SURNAME, GIVEN NAMES".

Worked example (verified live):
    HUME CONCRETING MELBOURNE -> ABN 11 584 809 528
    Entity name: MEHMET, HAKAN | Individual/Sole Trader | VIC 3064

For companies the entity name is the company, not a person -- those are marked
`inferred` at best, and directors require a paid ASIC extract (see enrich.py).
"""
from __future__ import annotations

import re
from datetime import date

SEARCH_URL = "https://abr.business.gov.au/Search/ResultsActive?SearchText={query}"
VIEW_URL = "https://abr.business.gov.au/ABN/View?abn={abn}"

SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "matches": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "abn": {"type": "string"},
                    "name": {"type": "string"},
                    "name_type": {"type": ["string", "null"]},
                    "location": {"type": ["string", "null"]},
                },
            },
        }
    },
}

SEARCH_PROMPT = (
    "Extract the search results table. For each row: abn (digits only), name, "
    "name_type (Entity Name / Business Name / Trading Name) and location "
    "(postcode and state)."
)

DETAIL_SCHEMA = {
    "type": "object",
    "properties": {
        "entity_name": {"type": ["string", "null"]},
        "entity_type": {"type": ["string", "null"]},
        "abn_status": {"type": ["string", "null"]},
        "active_from": {"type": ["string", "null"]},
        "gst_registered": {"type": ["string", "null"]},
        "location": {"type": ["string", "null"]},
        "business_names": {"type": "array", "items": {"type": "string"}},
    },
}

DETAIL_PROMPT = (
    "Extract the ABN record: entity_name, entity_type, abn_status, active_from "
    "(the date the ABN became active), gst_registered (the GST line, or null if "
    "not registered), location, and all registered business/trading names."
)

# "MEHMET, HAKAN" -> ("MEHMET", "HAKAN")
PERSON_NAME = re.compile(r"^([A-Z][A-Za-z'\-]+),\s*([A-Z][A-Za-z'\-\s]+)$")

# Small trades very often trade through a discretionary family trust, and the
# trust is named after the family. Verified live: Banat Cabinet Makers is run by
# "THE CIRKA FAMILY TRUST" -- so you can ask for Mr/Ms Cirka by name.
FAMILY_TRUST = re.compile(
    r"(?:the\s+)?(?:trustee\s+for\s+)?(?:the\s+)?([A-Z][A-Za-z'\-]+)\s+FAMILY\s+TRUST",
    re.I,
)

TRUST_STOPWORDS = {"the", "family", "trust", "trustee", "for", "superannuation", "super"}


def family_surname(entity_name: str | None) -> str | None:
    """'THE CIRKA FAMILY TRUST' -> 'Cirka'."""
    if not entity_name:
        return None
    m = FAMILY_TRUST.search(entity_name)
    if not m:
        return None
    surname = m.group(1)
    if surname.lower() in TRUST_STOPWORDS:
        return None
    return surname.title()


def looks_like_person(entity_name: str | None) -> bool:
    return bool(entity_name and PERSON_NAME.match(entity_name.strip()))


def format_owner(entity_name: str) -> str:
    """'MEHMET, HAKAN' -> 'Hakan Mehmet'."""
    m = PERSON_NAME.match(entity_name.strip())
    if not m:
        return entity_name.title()
    surname, given = m.group(1), m.group(2)
    return f"{given.strip().title()} {surname.strip().title()}"


def trading_years(active_from: str | None) -> float | None:
    """'01 Jul 2005' -> years as a float."""
    if not active_from:
        return None
    m = re.search(r"(\d{1,2})\s+([A-Za-z]{3})\w*\s+(\d{4})", active_from)
    if not m:
        return None
    months = {mn: i + 1 for i, mn in enumerate(
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}
    try:
        start = date(int(m.group(3)), months[m.group(2).title()], int(m.group(1)))
    except (KeyError, ValueError):
        return None
    return round((date.today() - start).days / 365.25, 1)


def search(fc, business_name: str) -> list[dict]:
    from urllib.parse import quote_plus
    url = SEARCH_URL.format(query=quote_plus(business_name))
    return (fc.scrape_json(url, SEARCH_PROMPT, SEARCH_SCHEMA) or {}).get("matches", []) or []


def fetch(fc, abn: str) -> dict:
    digits = re.sub(r"\D", "", abn)
    return fc.scrape_json(VIEW_URL.format(abn=digits), DETAIL_PROMPT, DETAIL_SCHEMA) or {}
