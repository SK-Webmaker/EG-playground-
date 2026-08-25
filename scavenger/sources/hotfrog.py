"""Hotfrog AU directory source.

Hotfrog is the primary discovery surface: it indexes small operators who never
built a site, and its search pages are reliably scrapeable.

IMPORTANT: a Hotfrog *search* page omits the website field even when the business
has one (verified against koncept Concreting, which shows a website on its detail
page but not in the list). Absence of a website here is therefore a CANDIDATE
signal only -- verify.py has the final say.
"""
from __future__ import annotations

from ..models import Lead

BASE = "https://www.hotfrog.com.au"

LISTING_SCHEMA = {
    "type": "object",
    "properties": {
        "businesses": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "phone": {"type": ["string", "null"]},
                    "address": {"type": ["string", "null"]},
                    "suburb": {"type": ["string", "null"]},
                    "postcode": {"type": ["string", "null"]},
                    "profile_url": {"type": ["string", "null"]},
                    "description": {"type": ["string", "null"]},
                    "website_url": {"type": ["string", "null"]},
                },
            },
        }
    },
}

LISTING_PROMPT = (
    "Extract every business listing on this page. For each: name, phone, full "
    "address, suburb, postcode, the hotfrog profile URL, short description, and "
    "website_url (the external business website if one is shown, otherwise null). "
    "Do not invent websites."
)

DETAIL_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "phone": {"type": ["string", "null"]},
        "website_url": {"type": ["string", "null"]},
        "email": {"type": ["string", "null"]},
        "contact_person": {"type": ["string", "null"]},
        "address": {"type": ["string", "null"]},
        "description": {"type": ["string", "null"]},
    },
}

DETAIL_PROMPT = (
    "Extract this business profile. website_url must be the external business "
    "website if the page shows one, otherwise null -- never a hotfrog.com.au URL. "
    "contact_person is a named individual (owner/manager) if the page names one, "
    "otherwise null. Do not guess."
)


def search_url(region: str, niche_slug: str) -> str:
    return f"{BASE}/search/vic-{region}/{niche_slug}"


def discover(fc, region: str, niche: dict) -> list[Lead]:
    """Return candidate leads for one region x niche cell."""
    url = search_url(region, niche["slug"])
    payload = fc.scrape_json(url, LISTING_PROMPT, LISTING_SCHEMA)
    leads: list[Lead] = []
    for row in payload.get("businesses", []) or []:
        name = (row.get("name") or "").strip()
        if not name:
            continue
        leads.append(
            Lead(
                business_name=name,
                niche=niche["slug"],
                niche_label=niche["label"],
                ticket_value=niche["ticket"],
                address=row.get("address"),
                suburb=row.get("suburb"),
                postcode=row.get("postcode"),
                phone_raw=row.get("phone"),
                website_url=row.get("website_url"),
                source="hotfrog",
                source_url=row.get("profile_url") or url,
            )
        )
    return leads


def fetch_detail(fc, profile_url: str) -> dict:
    """Detail page -- authoritative on whether a website exists."""
    return fc.scrape_json(profile_url, DETAIL_PROMPT, DETAIL_SCHEMA)
