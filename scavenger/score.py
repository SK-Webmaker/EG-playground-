"""Lead scoring and junk filtering."""
from __future__ import annotations

import re
from collections import Counter

from .config import (GENERIC_NAME_TOKENS, SHARED_PHONE_DROP_THRESHOLD,
                     SURNAME_PATTERNS, WEIGHTS, in_melbourne)
from .models import is_mobile

MAX_TICKET = 250_000


def looks_owner_operated(name: str) -> bool:
    return any(re.search(p, name) for p in SURNAME_PATTERNS)


def looks_generic(name: str) -> bool:
    """'Bathroom Renovations Kew' -- an SEO shell, not a business with an owner."""
    tokens = [t.lower() for t in re.findall(r"[A-Za-z]+", name)]
    if not tokens:
        return True
    generic = sum(1 for t in tokens if t in GENERIC_NAME_TOKENS)
    return generic >= max(1, len(tokens) - 2) and not looks_owner_operated(name)


def flag_shared_phones(leads: list) -> None:
    """Mark numbers reused across listings -- lead-gen resellers, not operators."""
    counts = Counter(l.phone for l in leads if l.phone)
    for lead in leads:
        if lead.phone and counts[lead.phone] >= SHARED_PHONE_DROP_THRESHOLD:
            lead.flags.append(f"shared_phone_x{counts[lead.phone]}")


def score(lead) -> int:
    b: dict[str, int] = {}

    b["ticket"] = int(WEIGHTS["ticket"] * min(lead.ticket_value, MAX_TICKET) / MAX_TICKET)

    if lead.owner_name:
        b["owner_identified"] = (
            WEIGHTS["owner_identified"] if lead.owner_confidence == "confirmed"
            else WEIGHTS["owner_identified"] // 2
        )

    if is_mobile(lead.owner_phone or lead.phone):
        b["direct_mobile"] = WEIGHTS["direct_mobile"]

    if (lead.entity_type or "").lower().startswith("individual"):
        b["sole_trader"] = WEIGHTS["sole_trader"]

    if lead.gst_registered:
        b["gst_registered"] = WEIGHTS["gst_registered"]

    if lead.trading_years:
        # 3+ years established earns full marks; newer scales down.
        b["trading_years"] = int(WEIGHTS["trading_years"] * min(lead.trading_years, 3) / 3)

    total = sum(b.values())

    # --- penalties ---------------------------------------------------------
    if lead.has_website is True:
        total = 0
        lead.flags.append("HAS_WEBSITE_disqualified")
    elif lead.has_website is None:
        total = int(total * 0.5)
        lead.flags.append("website_unverified")
    if any(f.startswith("shared_phone") for f in lead.flags):
        total = int(total * 0.2)
    if looks_generic(lead.business_name):
        total = int(total * 0.4)
        lead.flags.append("generic_name")
    if not lead.phone and not lead.email:
        total = int(total * 0.3)
        lead.flags.append("no_contact")
    if lead.postcode and not in_melbourne(lead.postcode):
        total = int(total * 0.3)
        lead.flags.append("outside_melbourne")
    if lead.social_only and lead.has_website is False:
        total += 5  # wants a presence, has no site -- an easier conversation
        lead.flags.append("social_only")

    lead.score_breakdown = b
    lead.score = max(0, min(100, total))
    return lead.score
