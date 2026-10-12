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


def opener(row: dict, sender: str) -> str:
    hi = f"Hi {first_name(row)}" if first_name(row) else "Hi"
    return (f"{hi}, it's {sender}. I noticed {row['name']} doesn't have a website, "
            f"so people searching for you online find nothing to look at. I build "
            f"simple sites for local businesses - happy to send a free mock-up? "
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
            "suburb", "abn", "trading_years", "socials", "message"]
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for l in leads:
            w.writerow({**l, "message": opener(l, args.sender)})

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
        "Personalised per lead in the CSV `message` column. Base text:", "",
        f"> {opener({'name': '<Business>', 'owner_confidence': 'none', 'owner_name': ''}, args.sender)}",
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
