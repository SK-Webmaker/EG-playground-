"""Export leads to CSV and a human-readable call sheet."""
from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

CSV_COLUMNS = [
    "score", "business_name", "niche_label", "ticket_value",
    "owner_name", "owner_confidence", "owner_source",
    "phone", "email", "suburb", "postcode", "address",
    "abn", "entity_type", "gst_registered", "trading_years",
    "has_website", "website_evidence", "social_only",
    "source", "source_url", "flags",
]


def write_csv(leads: list, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for lead in sorted(leads, key=lambda l: -l.score):
            row = lead.to_dict()
            row["flags"] = "; ".join(row.get("flags") or [])
            writer.writerow(row)
    return path


def write_jsonl(leads: list, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for lead in sorted(leads, key=lambda l: -l.score):
            fh.write(lead.to_json() + "\n")
    return path


def write_callsheet(leads: list, path: str | Path, top: int = 40) -> Path:
    """Markdown call sheet -- ordered so the best call is the first line."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ranked = sorted(leads, key=lambda l: -l.score)[:top]
    lines = [
        f"# Melbourne no-website lead call sheet",
        f"_Generated {date.today().isoformat()} — {len(ranked)} qualified leads_",
        "",
        "| # | Score | Business | Niche | Owner | Confidence | Phone | Suburb | Typical job |",
        "|---|-------|----------|-------|-------|-----------|-------|--------|-------------|",
    ]
    for i, l in enumerate(ranked, 1):
        lines.append(
            f"| {i} | {l.score} | {l.business_name} | {l.niche_label} | "
            f"{l.owner_name or '—'} | {l.owner_confidence} | {l.phone or '—'} | "
            f"{l.suburb or '—'} | ${l.ticket_value:,} |"
        )
    lines += ["", "## Evidence", ""]
    for i, l in enumerate(ranked, 1):
        lines += [
            f"**{i}. {l.business_name}**",
            f"- Owner: {l.owner_name or 'not identified'} "
            f"({l.owner_source or 'no source'})",
            f"- ABN: {l.abn or '—'} · {l.entity_type or '—'} · "
            f"GST: {'yes' if l.gst_registered else 'no'} · "
            f"trading {l.trading_years or '?'} yrs",
            f"- Website: {l.website_evidence or 'unverified'}",
            f"- Flags: {', '.join(l.flags) or 'none'}",
            "",
        ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
