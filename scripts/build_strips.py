"""Qualify shopping-strip traders into callable no-website leads."""
from __future__ import annotations
import concurrent.futures as cf, csv, json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from scavenger.abnfree import enrich
from scavenger.models import normalise_phone

# Chains, banks, government and franchises: no local owner to sell to.
EXCLUDE = re.compile(
    r"\b(anz|nab|westpac|commonwealth bank|bendigo bank|bank of|beyond bank|"
    r"just cuts|zambrero|subway|mcdonald|kfc|domino|7-eleven|coles|woolworths|aldi|"
    r"chemist warehouse|priceline|australia post|telstra|optus|vodafone|"
    r"specsavers|opsm|bakers delight|brumby|donut king|boost juice|gloria jean|"
    r"jim's|mitre 10|bunnings|repco|midas|ultra tune|centrelink|medicare|"
    r"mp\b|member for|city of |council|library|police|salvation army|"
    r"red cross|vinnies|op shop|community centre|apm employment|asg\b|"
    r"foodworks|iga|nandos|grill'd|guzman)", re.I)

rows = json.load(open("data/strips-raw.json"))
cands = []
for t in rows:
    if t.get("website") or not t.get("phone"):
        continue
    if EXCLUDE.search(t["name"]):
        continue
    t["phone_e164"] = normalise_phone(t["phone"])
    pc = None
    if t.get("address") and (m := re.search(r"VIC\s*(\d{4})", t["address"], re.I)):
        pc = m.group(1)
    t["postcode"] = pc
    cands.append(t)
print(f"no-website + phone + not a chain: {len(cands)}")

def go(t):
    try:
        r = enrich(t["name"], t["postcode"])
    except Exception as e:
        return t, None
    return t, r

out = []
with cf.ThreadPoolExecutor(6) as ex:
    for t, r in ex.map(go, cands):
        if r:
            t.update(abn=r.abn, entity_type=r.entity_type, owner_name=r.owner_name,
                     owner_confidence=r.owner_confidence, gst=r.gst,
                     trading_years=r.years, abn_match=r.match)
        out.append(t)

def score(t):
    s, sig = 0, []
    if t.get("abn"):
        s += 20; sig.append("active_abn")
    else:
        sig.append("abn_unconfirmed")
    if t.get("owner_name"):
        s += 20; sig.append(f"owner_{t['owner_confidence']}")
    if t.get("gst"):
        s += 15; sig.append("gst_registered")
    y = t.get("trading_years") or 0
    if y >= 10: s += 15; sig.append(f"{y}yrs_established")
    elif y >= 3: s += 8; sig.append(f"{y}yrs")
    if t.get("socials"):
        s += 15; sig.append(f"{len(t['socials'])}_social_profiles")
    if t.get("address"):
        s += 10; sig.append("street_premises")
    if (t.get("phone_e164") or "").startswith("+614"):
        s += 5; sig.append("mobile")
    t["score"] = min(s, 100); t["signals"] = sig
    return t

out = [score(t) for t in out]
out.sort(key=lambda t: -t["score"])
json.dump(out, open("data/leads/strips-qualified.json", "w"), indent=1, ensure_ascii=False)

cols = ["score","name","category","phone","address","strip","owner_name","owner_confidence",
        "abn","entity_type","gst","trading_years","socials","signals","source_url"]
p = pathlib.Path("data/leads/melbourne-strip-leads-2026-08-25.csv")
with p.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader()
    for t in out:
        w.writerow({**t, "socials": " | ".join(t.get("socials") or []),
                    "signals": "; ".join(t.get("signals") or [])})

print(f"qualified {len(out)} -> {p}")
print(f"  with owner name : {sum(1 for t in out if t.get('owner_name'))}")
print(f"  GST registered  : {sum(1 for t in out if t.get('gst'))}")
print(f"  has socials     : {sum(1 for t in out if t.get('socials'))}")
print(f"  active ABN      : {sum(1 for t in out if t.get('abn'))}\n")
for t in out[:30]:
    print(f"  [{t['score']:3d}] {t['name'][:30]:30s} {t['phone']:16s} "
          f"{(t.get('owner_name') or '-')[:18]:18s} {'GST' if t.get('gst') else '   '} "
          f"{str(t.get('trading_years') or '-'):>5}y {len(t.get('socials') or [])}s")
