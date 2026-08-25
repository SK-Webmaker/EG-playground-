"""Outreach templates.

Deliberately built around what the register tells us. A sole trader gets their
own name; a family trust gets the family surname; a company gets neither and is
approached by business name.

Compliance is not optional here -- see COMPLIANCE.md. In short: unsolicited
commercial email to an Australian business needs consent or the inferred-consent
carve-out plus accurate sender details and a working unsubscribe (Spam Act 2003),
and cold *calls* must be washed against the Do Not Call Register.
"""
from __future__ import annotations


def greeting(lead) -> str:
    if lead.owner_confidence == "confirmed" and lead.owner_name:
        return f"Hi {lead.owner_name.split()[0]},"
    if lead.owner_name and "family" in lead.owner_name:
        return f"Hi {lead.owner_name.split()[0]},"
    return "Hi there,"


def call_opener(lead) -> str:
    """What to actually say when they pick up."""
    who = (lead.owner_name.split()[0]
           if lead.owner_name and lead.owner_confidence == "confirmed" else None)
    ask = f"is that {who}?" if who else f"is the owner of {lead.business_name} about?"
    return (
        f"Hi, {ask} I'm calling because I noticed {lead.business_name} comes up in "
        f"{lead.suburb or 'Melbourne'} directories but doesn't have a website — "
        f"so when someone searches for a {lead.niche_label.lower()} and finds you, "
        f"there's nothing for them to look at. On jobs around "
        f"${lead.ticket_value:,}, one job a year covers the site several times over. "
        f"Have you got two minutes?"
    )


def email_subject(lead) -> str:
    return f"{lead.business_name} — no website showing up in {lead.suburb or 'Melbourne'}"


def email_body(lead, sender: str, unsubscribe_url: str) -> str:
    proof = (
        f"You're listed on {lead.source} and registered with an active ABN"
        + (f" ({lead.abn})" if lead.abn else "")
        + ", but I couldn't find a website anywhere."
    )
    social = (
        f" You've got a presence on {lead.social_only.split('/')[2]}, which is a "
        f"start — but you don't own it and it won't show up when someone searches."
        if lead.social_only else ""
    )
    return f"""{greeting(lead)}

{proof}{social}

For a {lead.niche_label.lower()} business where a typical job runs around
${lead.ticket_value:,}, that's the gap I'd like to close — a simple site that
shows your work, your service area and a way to call you.

Worth a quick chat? Reply here or call me any time.

{sender}

---
You received this because {lead.business_name} is publicly listed as a
{lead.niche_label.lower()} business in {lead.suburb or 'Melbourne'}.
Unsubscribe: {unsubscribe_url}
"""
