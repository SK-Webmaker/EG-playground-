"""Deduplication -- directories repeat the same operator many times over."""
from __future__ import annotations


def dedupe(leads: list) -> list:
    """Collapse by phone (or name+postcode), keeping the richest record."""
    best: dict[str, object] = {}
    for lead in leads:
        existing = best.get(lead.key)
        if existing is None or _richness(lead) > _richness(existing):
            if existing is not None:
                _merge(lead, existing)
            best[lead.key] = lead
    return list(best.values())


def _richness(lead) -> int:
    return sum([
        bool(lead.owner_name) * 4,
        bool(lead.abn) * 3,
        bool(lead.phone) * 2,
        bool(lead.email) * 2,
        bool(lead.address) * 1,
        bool(lead.postcode) * 1,
    ])


def _merge(keep, drop) -> None:
    """Carry across any field the winner is missing."""
    for field in ("address", "suburb", "postcode", "email", "owner_name",
                  "owner_source", "abn", "entity_type", "social_only"):
        if not getattr(keep, field, None) and getattr(drop, field, None):
            setattr(keep, field, getattr(drop, field))
    for flag in getattr(drop, "flags", []):
        if flag not in keep.flags:
            keep.flags.append(flag)
