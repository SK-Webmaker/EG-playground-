"""Core data model for a scavenged lead."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field, asdict


def normalise_phone(raw: str | None) -> str | None:
    """Australian numbers to E.164. '03 9548 3115' -> '+61395483115'."""
    if not raw:
        return None
    digits = re.sub(r"[^\d+]", "", raw)
    if digits.startswith("+61"):
        return digits
    if digits.startswith("61") and len(digits) >= 11:
        return "+" + digits
    # 13 / 1300 / 1800 national numbers carry no leading 0 to strip.
    if digits.startswith(("1300", "1800", "13")) and len(digits) in (6, 10):
        return "+61" + digits
    if digits.startswith("0") and len(digits) == 10:
        return "+61" + digits[1:]
    if len(digits) == 8:  # local landline without area code -- assume Melbourne
        return "+613" + digits
    return digits or None


def is_mobile(e164: str | None) -> bool:
    return bool(e164 and e164.startswith("+614"))


@dataclass
class Lead:
    # --- identity -----------------------------------------------------------
    business_name: str
    niche: str
    niche_label: str = ""
    ticket_value: int = 0

    # --- location -----------------------------------------------------------
    address: str | None = None
    suburb: str | None = None
    postcode: str | None = None

    # --- business contact ---------------------------------------------------
    phone: str | None = None
    phone_raw: str | None = None
    email: str | None = None

    # --- owner (the point of the exercise) ----------------------------------
    owner_name: str | None = None
    owner_source: str | None = None       # provenance -- always recorded
    owner_confidence: str = "none"        # none | inferred | confirmed
    owner_phone: str | None = None
    owner_email: str | None = None

    # --- registry facts -----------------------------------------------------
    abn: str | None = None
    entity_type: str | None = None
    gst_registered: bool = False
    abn_active_from: str | None = None
    trading_years: float | None = None

    # --- website status -----------------------------------------------------
    has_website: bool | None = None       # None = unverified
    website_url: str | None = None
    website_evidence: str | None = None
    social_only: str | None = None        # facebook/instagram page if that's all they have

    # --- provenance & scoring ----------------------------------------------
    source: str = ""
    source_url: str | None = None
    score: int = 0
    score_breakdown: dict = field(default_factory=dict)
    flags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.phone_raw and not self.phone:
            self.phone = normalise_phone(self.phone_raw)

    @property
    def key(self) -> str:
        """Dedupe key: phone if we have one, else name+postcode."""
        basis = self.phone or f"{self.business_name.lower().strip()}|{self.postcode or ''}"
        return hashlib.sha1(basis.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)
