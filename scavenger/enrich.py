"""Owner enrichment via ABN Lookup.

Does double duty:
  1. OWNER IDENTITY -- for a sole trader the ABN entity name is the owner's legal
     name, which is the whole point of the exercise.
  2. LIVENESS -- Hotfrog carries dead listings for years. An active ABN is a
     harder freshness test than a review date, so a candidate with no active ABN
     match is dropped rather than sold as a lead.
"""
from __future__ import annotations

import re

from .sources import abn as abn_src

STOPWORDS = {"pty", "ltd", "the", "trustee", "for", "and", "&", "services",
             "service", "group", "co", "melbourne", "vic", "victoria"}


def _tokens(name: str) -> set[str]:
    return {t for t in re.findall(r"[a-z]+", name.lower())
            if len(t) > 2 and t not in STOPWORDS}


def match_score(business_name: str, candidate_name: str, location: str | None) -> float:
    """How confidently does an ABN row correspond to this business?"""
    a, b = _tokens(business_name), _tokens(candidate_name)
    if not a or not b:
        return 0.0
    overlap = len(a & b) / len(a)
    if location and re.search(r"\bVIC\b", location, re.I):
        overlap += 0.15          # Victorian record for a Melbourne business
    elif location:
        overlap -= 0.35          # interstate: probably a different business
    return overlap


def enrich(fc, lead, min_match: float = 0.6) -> None:
    """Resolve ABN, owner name and trading facts onto the lead in place."""
    try:
        matches = abn_src.search(fc, lead.business_name)
    except Exception as exc:  # noqa: BLE001 - enrichment must never kill a run
        lead.flags.append(f"abn_lookup_failed:{type(exc).__name__}")
        return

    if not matches:
        lead.flags.append("no_abn_match")
        return

    best, best_score = None, 0.0
    for row in matches:
        s = match_score(lead.business_name, row.get("name") or "", row.get("location"))
        if s > best_score:
            best, best_score = row, s

    if not best or best_score < min_match:
        # No confident registry match -> likely a dead or renamed listing.
        lead.flags.append(f"no_abn_match(best={best_score:.2f})")
        return

    lead.abn = re.sub(r"\D", "", best.get("abn") or "") or None
    if not lead.abn:
        return

    try:
        detail = abn_src.fetch(fc, lead.abn)
    except Exception as exc:  # noqa: BLE001
        lead.flags.append(f"abn_detail_failed:{type(exc).__name__}")
        return

    entity_name = (detail.get("entity_name") or "").strip()
    lead.entity_type = detail.get("entity_type")
    lead.abn_active_from = detail.get("active_from")
    lead.trading_years = abn_src.trading_years(detail.get("active_from"))
    gst = (detail.get("gst_registered") or "").strip().lower()
    lead.gst_registered = bool(gst) and "not registered" not in gst

    if abn_src.looks_like_person(entity_name):
        # Sole trader: the registered entity IS the human. Confirmed.
        lead.owner_name = abn_src.format_owner(entity_name)
        lead.owner_source = f"ABN Lookup {lead.abn} (entity name, sole trader)"
        lead.owner_confidence = "confirmed"
    elif (trust_surname := abn_src.family_surname(entity_name)):
        # Family trust: the register names the family that owns the business.
        # Strong enough to ask for them by surname on the phone.
        lead.owner_name = f"{trust_surname} family"
        lead.owner_source = f"ABN Lookup {lead.abn} (entity: {entity_name})"
        lead.owner_confidence = "inferred"
        lead.flags.append("owner_via_family_trust")
    elif entity_name:
        # Company: registry names the company, not a director. ASIC has the
        # directors but only behind a paid extract, so at best we infer from a
        # family surname in the trading name.
        lead.flags.append("company_owner_needs_asic")
        surname = _surname_from_trading_name(lead.business_name)
        if surname and not lead.owner_name:
            lead.owner_name = f"(likely) {surname} family"
            lead.owner_source = f"inferred from trading name; company {entity_name}"
            lead.owner_confidence = "inferred"


def _surname_from_trading_name(name: str) -> str | None:
    """'Traynor Roofing' -> 'Traynor'. Only the leading proper noun."""
    trade_words = {
        "roofing", "concreting", "concrete", "landscaping", "excavations",
        "excavation", "plumbing", "building", "builders", "carpentry", "paving",
        "fencing", "decking", "joinery", "cabinets", "cabinet", "makers",
        "renovations", "restumping", "reblocking", "underpinning", "demolition",
        "solar", "electrical", "tiling", "scaffolding", "constructions",
        "construction", "metal", "services", "group", "pty", "ltd",
    }
    for word in re.findall(r"[A-Z][a-z]{2,}", name):
        if word.lower() not in trade_words:
            return word
    return None
