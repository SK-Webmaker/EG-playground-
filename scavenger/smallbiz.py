"""Broad small-business mode: any Melbourne small business with no website.

Differs from the high-ticket trade pipeline in what it filters. At this breadth
the directory noise is different -- national franchises, tech-support spam and
multi-listing resellers all show up -- so those get their own filters.
"""
from __future__ import annotations

import re

# National brands / franchises: they have a corporate site, and the local
# operator cannot buy one anyway.
FRANCHISE = re.compile(
    r"\b(jim'?s|aussie pooch|mitre\s?10|victa|hire a hubby|poolwerx|bakers delight|"
    r"snap print|kwik kopy|battery world|repco|midas|ultra ?tune|kmart|bunnings|"
    r"chemist warehouse|7-eleven|dominos|subway)\b", re.I)

# Offshore "customer support" spam that infests directory listings.
SPAM = re.compile(
    r"\b(canon|hp|epson|brother|norton|mcafee|gmail|yahoo|outlook)\b.*\b"
    r"(support|customer care|helpline|customer service|setup)\b", re.I)

# Anyone already selling websites is a competitor, not a prospect.
COMPETITOR = re.compile(r"\b(website|web design|seo|digital marketing)\b", re.I)

# Generic "<service> <suburb>" SEO shells.
GENERIC = re.compile(
    r"^(best|cheap|cheaper|affordable|local|professional|expert)\b|"
    r"\b(melbourne|victoria|vic)\s*$", re.I)

# A business named after a person is owner-operated: ask for them by name.
PERSON_NAME = re.compile(
    r"^[A-Z][a-z]+'s\b|"                       # Howard's, Deb's, Perfect Pete's
    r"^[A-Z][a-z]+\s+[A-Z][a-z]+\s+(Hair|Salon|Lawn|Mowing|Motors|Painters)|"
    r"\b(&|and)\s+Sons?\b|"                    # Steve + Sons
    r"\bFamily\b")                             # Harris Family Butchers

PO_BOX = re.compile(r"\bP\.?O\.?\s*Box\b", re.I)
# A street address means a real shopfront rather than a serving-area listing.
STREET = re.compile(r"\d+\s*[a-zA-Z]?[/-]?\s*\w+|\bShop\b|\bUnit\b|\bFactory\b", re.I)


def classify(name: str, address: str | None) -> list[str]:
    """Return disqualifying reasons, empty if the lead is worth calling."""
    reasons = []
    if FRANCHISE.search(name):
        reasons.append("franchise")
    if SPAM.search(name):
        reasons.append("offshore_spam")
    if COMPETITOR.search(name):
        reasons.append("competitor")
    if GENERIC.search(name.strip()):
        reasons.append("generic_seo_name")
    if address and PO_BOX.search(address) :
        reasons.append("po_box_only")
    return reasons


def quality(name: str, phone: str | None, address: str | None) -> tuple[int, list[str]]:
    """Score 0-100 for "worth a cold call", plus the signals behind it."""
    score, signals = 0, []

    if phone and phone.startswith("+614"):
        score += 25; signals.append("direct_mobile")
    elif phone:
        score += 15; signals.append("landline")

    if address and STREET.search(address) and not PO_BOX.search(address):
        score += 25; signals.append("street_premises")
    elif address:
        score += 5; signals.append("serving_area_only")

    if PERSON_NAME.search(name):
        score += 25; signals.append("owner_named_business")

    # A short, specific, non-keyword name reads like a real local business.
    words = re.findall(r"[A-Za-z]+", name)
    if 1 < len(words) <= 4 and not GENERIC.search(name):
        score += 15; signals.append("specific_name")

    # Trading-name suffixes signal a registered, established operator.
    if re.search(r"\b(pty|ltd|co\.|& co)\b", name, re.I):
        score += 10; signals.append("registered_entity")

    return min(score, 100), signals
