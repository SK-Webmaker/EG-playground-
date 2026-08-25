"""Filter, score and export the broad small-business harvest."""
from __future__ import annotations
import json, pathlib, sys
from collections import Counter
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from scavenger.models import normalise_phone
from scavenger.smallbiz import classify, quality
from scavenger.config import in_melbourne

# Spot-check verification run live on 2026-08-25 via targeted web search.
# "clear" = no own domain found, only aggregators/social. "site" = own domain found.
VERIFIED = {
 "Ngoc Dzung Hair Salon":     ("clear", "Yelp/WhitePages/YellowPages only; Yelp updated Aug 2026"),
 "Harris Family Butchers":    ("clear", "Facebook 'Harris Family Meats' only; 40 years in Mackie Rd"),
 "Zina's Unisex Salon":       ("clear", "Yelp/cybo/hairsalons.com.au listings only"),
 "Maurice Albert Salon":      ("clear", "Facebook 601 likes + Instagram + centre directory; 'Award Winning Hairdresser Since 1977'"),
 "Limnos Butchers":           ("clear", "Instagram + Oakleigh Traders directory + Facebook; no domain"),
 "La Serra Hairdressers":     ("clear", "no web presence found at all"),
 "Jorge Viota Hairdressers":  ("clear", "no web presence found at all"),
 "Munro Mechanic Repairs":    ("clear", "no web presence found at all"),
 "V J Electrics":             ("clear", "no web presence found at all"),
 "Andrew Roy Lawn Mowing Company": ("site", "andrewroylawnmowing.com.au"),
}

src = json.load(open("data/harvest-2026-08-25.json"))
rows = []
for cell in src["cells"]:
    for n, p, a, s, pc in cell["b"]:
        rows.append({"name": n, "phone_raw": p, "phone": normalise_phone(p),
                     "address": a, "suburb": s, "postcode": pc,
                     "category": cell["cat"], "search_suburb": cell["suburb"]})

# Resold / multi-listing phone numbers -> one operator behind many listings.
phone_counts = Counter(r["phone"] for r in rows if r["phone"])

seen, out = set(), []
for r in rows:
    reasons = classify(r["name"], r["address"])
    if r["phone"] and phone_counts[r["phone"]] > 1:
        reasons.append(f"shared_phone_x{phone_counts[r['phone']]}")
    if not r["phone"]:
        reasons.append("no_phone")
    if r["postcode"] and not in_melbourne(r["postcode"]):
        reasons.append("outside_melbourne")

    key = r["phone"] or r["name"].lower()
    if key in seen:
        reasons.append("duplicate")
    seen.add(key)

    status, note = VERIFIED.get(r["name"], (None, None))
    r["website_status"] = status or "unverified"
    r["website_note"] = note or "not yet checked - verify before calling"
    if status == "site":
        reasons.append("HAS_WEBSITE")

    r["score"], r["signals"] = quality(r["name"], r["phone"], r["address"])
    if status == "clear":
        r["score"] = min(100, r["score"] + 15)
        r["signals"].append("website_verified_clear")
    r["reasons"] = reasons
    r["qualified"] = not reasons
    out.append(r)

qual = sorted([r for r in out if r["qualified"]], key=lambda r: -r["score"])
rej = [r for r in out if not r["qualified"]]

import csv
p = pathlib.Path("data/leads/melbourne-smallbiz-2026-08-25.csv")
p.parent.mkdir(parents=True, exist_ok=True)
cols = ["score","name","category","phone","address","suburb","postcode","website_status","website_note","signals","search_suburb"]
with p.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for r in qual:
        w.writerow({**r, "signals": "; ".join(r["signals"])})

json.dump({"qualified": qual, "rejected": rej}, open("data/leads/smallbiz-full.json","w"), indent=1)

print(f"harvested {len(out)} | qualified {len(qual)} | rejected {len(rej)}\n")
print("rejection reasons:")
for reason, c in Counter(x.split('_x')[0] for r in rej for x in r["reasons"]).most_common():
    print(f"  {c:3d}  {reason}")
print(f"\ncategory spread of qualified:")
for cat, c in Counter(r["category"] for r in qual).most_common():
    print(f"  {c:3d}  {cat}")
print(f"\nverified clear: {sum(1 for r in qual if r['website_status']=='clear')}"
      f" | unverified: {sum(1 for r in qual if r['website_status']=='unverified')}")
print(f"\ntop 25:")
for r in qual[:25]:
    print(f"  [{r['score']:3d}] {r['name'][:36]:36s} {r['phone'] or '-':15s} {(r['suburb'] or '-')[:14]:14s} {r['category']}")
print(f"\nCSV: {p}")
