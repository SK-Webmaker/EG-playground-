"""Turn the verified run JSON into the CSV / JSONL / call-sheet deliverables.

Runs the real scoring and export code over the live-verified records, so the
exports you ship are produced by the same code path as a scheduled run.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from scavenger.export import write_callsheet, write_csv, write_jsonl
from scavenger.models import Lead
from scavenger.score import flag_shared_phones, score

SRC = pathlib.Path("data/verified-2026-08-25.json")
OUT = pathlib.Path("data/leads")

def main() -> int:
    payload = json.loads(SRC.read_text())
    leads = []
    for row in payload["leads"]:
        flags = row.pop("flags", [])
        lead = Lead(**{k: v for k, v in row.items() if k in Lead.__dataclass_fields__})
        lead.flags = list(flags)
        leads.append(lead)

    flag_shared_phones(leads)
    for lead in leads:
        score(lead)
    leads.sort(key=lambda l: -l.score)

    stamp = payload["run_date"]
    paths = {
        "csv": write_csv(leads, OUT / f"melbourne-leads-{stamp}.csv"),
        "jsonl": write_jsonl(leads, OUT / f"melbourne-leads-{stamp}.jsonl"),
        "callsheet": write_callsheet(leads, OUT / f"call-sheet-{stamp}.md"),
    }
    for name, path in paths.items():
        print(f"{name:10s} {path}")
    print()
    for l in leads:
        print(f"[{l.score:3d}] {l.business_name:44s} {l.owner_name or '-':22s} "
              f"{l.phone or '-':15s} {l.owner_confidence}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
