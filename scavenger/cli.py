"""Command line entry point.

    python -m scavenger.cli --regions melbourne,craigieburn --limit 40
"""
from __future__ import annotations

import argparse
import logging

from .config import NICHES, REGIONS
from .pipeline import run


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Melbourne no-website lead scavenger")
    ap.add_argument("--regions", help="comma-separated suburb slugs")
    ap.add_argument("--niches", help="comma-separated niche slugs")
    ap.add_argument("--limit", type=int, default=60,
                    help="max leads to verify+enrich (controls credit spend)")
    ap.add_argument("--min-score", type=int, default=25)
    ap.add_argument("--outdir", default="data/leads")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(message)s",
    )

    regions = args.regions.split(",") if args.regions else REGIONS
    niches = ([n for n in NICHES if n["slug"] in args.niches.split(",")]
              if args.niches else NICHES)
    if not niches:
        ap.error("no matching niches; see scavenger/config.py")

    result = run(niches=niches, regions=regions, outdir=args.outdir,
                 max_enrich=args.limit, min_score=args.min_score)

    print(f"\nQualified leads: {len(result['qualified'])}")
    for name, path in result["paths"].items():
        print(f"  {name:10s} {path}")
    print("\nTop 10:")
    for lead in result["qualified"][:10]:
        print(f"  [{lead.score:3d}] {lead.business_name:38s} "
              f"{lead.owner_name or '-':22s} {lead.phone or '-'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
