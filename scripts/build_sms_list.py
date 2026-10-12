"""Cut the master list down to leads you can text: Australian mobiles only.

Landlines can't receive SMS or WhatsApp, so they stay on the call sheet. Each
mobile lead gets a fresh zero-credit DNS website re-check (the master list ages)
and a ready-to-send opener that carries sender ID and an opt-out, as the Spam Act
requires of commercial SMS -- see COMPLIANCE.md.

    python3 scripts/build_sms_list.py --sender "Sam, Example Web Co"
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from scavenger.dnscheck import find_site

MASTER = pathlib.Path("data/leads/melbourne-master-leads-2026-08-25.csv")
# Verified in the first (high-ticket) run but never merged into the master list.
EXTRA = pathlib.Path("data/leads/melbourne-leads-2026-08-25.csv")
OUT = pathlib.Path("data/leads")


def mobile(phone: str | None) -> str | None:
    """Return the number as 04xx xxx xxx if it is an Australian mobile."""
    d = re.sub(r"\D", "", phone or "")
    if d.startswith("61"):
        d = "0" + d[2:]
    if len(d) == 10 and d.startswith("04"):
        return f"{d[:4]} {d[4:7]} {d[7:]}"
    return None


def first_name(row: dict) -> str | None:
    if row["owner_confidence"] == "confirmed" and row["owner_name"]:
        return row["owner_name"].split()[0]
    return None


# What the site would put in front of a customer, keyed on words in the category.
SHOWCASE = [
    (("dry clean", "jewel", "shoe", "frame"), "what you offer, your hours and directions"),
    (("cafe", "food", "espresso", "bar", "lounge", "thai", "rolls", "eggs", "mart", "kitchen"),
     "your menu, opening hours and directions"),
    (("lawn", "garden", "mowing", "clean", "handyman", "restump", "underpin", "electric",
      "panel", "mechanic", "joinery", "cabinet", "doors"), "photos of your work and a quote request form"),
    (("dog", "groom", "nail", "beauty", "hair", "salon"), "your services, prices and online bookings"),
]
DEFAULT_SHOWCASE = "what you do, your hours and a click-to-call button"


def showcase(row: dict) -> str:
    text = f"{row.get('category', '')} {row['name']}".lower()
    for keys, phrase in SHOWCASE:
        if any(k in text for k in keys):
            return phrase
    return DEFAULT_SHOWCASE


def opener(row: dict, sender: str) -> str:
    hi = f"Hi {first_name(row)}" if first_name(row) else "Hi"
    return (f"{hi}, it's {sender}. I noticed {row['name']} doesn't have a website. "
            f"We build websites for local businesses - yours could show {showcase(row)}. "
            f"Happy to mock one up free, no obligation. Keen to see it? "
            f"Reply STOP to opt out.")


def follow_up(row: dict, sender: str) -> str:
    hi = f"Hi {first_name(row)}" if first_name(row) else "Hi"
    return (f"{hi}, {sender} again - just following up on the free website mock-up "
            f"for {row['name']}. Happy to send it over, no strings attached. "
            f"Reply STOP to opt out.")


def load() -> list[dict]:
    rows = list(csv.DictReader(MASTER.open()))
    for r in csv.DictReader(EXTRA.open()):
        rows.append({
            "score": r["score"], "name": r["business_name"], "category": r["niche_label"],
            "phone": r["phone"], "suburb": r["suburb"], "owner_name": r["owner_name"],
            "owner_confidence": r["owner_confidence"], "abn": r["abn"],
            "trading_years": r.get("trading_years", ""), "socials": "",
            "website_note": r.get("website_evidence", ""), "source": r.get("source", ""),
        })
    seen, out = set(), []
    for r in rows:
        m = mobile(r["phone"])
        if m and m not in seen:
            seen.add(m)
            out.append({**r, "mobile": m})
    return out


EXAMPLE = {"name": "Peninsula Dog Grooming", "category": "Dog grooming",
           "owner_confidence": "confirmed", "owner_name": "Donna Kariofilis"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sender", default="[your name, business]")
    args = ap.parse_args()

    leads = load()
    with cf.ThreadPoolExecutor(12) as ex:
        sites = dict(zip((l["name"] for l in leads), ex.map(find_site, (l["name"] for l in leads))))
    dropped = [(l["name"], sites[l["name"]]) for l in leads if sites[l["name"]]]
    leads = [l for l in leads if not sites[l["name"]]]
    leads.sort(key=lambda l: -int(l["score"] or 0))

    stamp = dt.date.today().isoformat()
    csv_path = OUT / f"sms-list-{stamp}.csv"
    cols = ["score", "name", "mobile", "owner_name", "owner_confidence", "category",
            "suburb", "abn", "trading_years", "socials", "message", "follow_up"]
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for l in leads:
            w.writerow({**l, "message": opener(l, args.sender),
                        "follow_up": follow_up(l, args.sender)})

    md_path = OUT / f"sms-list-{stamp}.md"
    lines = [
        "# Melbourne no-website leads — mobiles to message",
        f"_Generated {stamp} — {len(leads)} mobiles; website re-checked by DNS today_",
        "",
        "| # | Score | Business | Owner | Mobile | Category | Area |",
        "|---|-------|----------|-------|--------|----------|------|",
    ]
    for i, l in enumerate(leads, 1):
        owner = l["owner_name"] if l["owner_confidence"] != "none" and l["owner_name"] else "—"
        if l["owner_confidence"] == "inferred":
            owner += " (inferred)"
        lines.append(f"| {i} | {l['score']} | {l['name']} | {owner} | {l['mobile']} | "
                     f"{l['category']} | {l['suburb'] or '—'} |")
    lines += [
        "", "## Message", "",
        "Personalised per lead in the CSV `message` column (first name where the "
        "owner is confirmed; the middle line changes with the type of business). Example:", "",
        f"> {opener(EXAMPLE, args.sender)}",
        "", "## Follow-up (3-4 days later, once only, if no reply)", "",
        f"> {follow_up(EXAMPLE, args.sender)}",
        "", "## When they reply", "",
        "- **\"Yes / sure / send it\"** — \"Great! What's the best email to send it to? "
        "I'll have it to you within 48 hours.\" Then build the mock-up from their "
        "Facebook/Instagram photos and directory listing.",
        "- **\"How much?\"** — \"Depends what you need, but most local business sites "
        "are a one-off build plus a small monthly fee for hosting and updates. Let me "
        "send the mock-up first so you can see if it's worth it.\"",
        "- **\"Not interested\"** — \"No worries at all, thanks for letting me know. "
        "All the best with the business.\" Don't message again.",
        "- **STOP** — remove them from the list straight away.",
        "", "## Before sending", "",
        "- Commercial SMS falls under the **Spam Act 2003**: identify yourself and "
        "keep the opt-out; honour STOP within 5 business days.",
        "- Send one-to-one from your own phone, not as a bulk blast.",
        "- Owner names come from ABN Lookup — personal information, don't republish.",
    ]
    if dropped:
        lines += ["", "## Dropped today (website now resolves)", ""]
        lines += [f"- {n} — {s}" for n, s in dropped]
    md_path.write_text("\n".join(lines) + "\n")

    print(f"{len(leads)} mobiles -> {csv_path}, {md_path}")
    for n, s in dropped:
        print(f"  dropped {n}: {s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
