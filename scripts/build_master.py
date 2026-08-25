"""Merge strip + directory leads into one qualified master call list."""
from __future__ import annotations
import concurrent.futures as cf, csv, json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from scavenger.abnfree import enrich
from scavenger.dnscheck import find_site
from scavenger.models import normalise_phone

MASTER = []

# --- 1. shopping-strip traders (website status observed on the listing) ------
for t in json.load(open("data/leads/strips-qualified.json")):
    MASTER.append({
        "name": t["name"], "phone": t.get("phone"), "phone_e164": t.get("phone_e164"),
        "address": t.get("address"), "suburb": t.get("strip"), "category": t.get("category"),
        "socials": t.get("socials") or [], "abn": t.get("abn"),
        "entity_type": t.get("entity_type"), "owner_name": t.get("owner_name"),
        "owner_confidence": t.get("owner_confidence") or "none", "gst": bool(t.get("gst")),
        "trading_years": t.get("trading_years"), "source": "trader association",
        "source_url": t.get("source_url"),
        "website_status": "clear", "website_note": "no website linked on trader-association listing",
    })

# --- 2. directory leads: still need a website check --------------------------
d = json.load(open("data/leads/smallbiz-full.json"))["qualified"]
names = [r["name"] for r in d]
print(f"DNS-checking {len(names)} directory leads ...")
with cf.ThreadPoolExecutor(12) as ex:
    sites = dict(zip(names, ex.map(find_site, names)))
kept = 0
for r in d:
    site = sites.get(r["name"])
    if site:
        continue                                   # has a website -> drop
    if r.get("website_status") == "clear":
        note = r.get("website_note")
    else:
        note = "no name-derived domain resolves (DNS check)"
    MASTER.append({
        "name": r["name"], "phone": r.get("phone_raw"), "phone_e164": r.get("phone"),
        "address": r.get("address"), "suburb": r.get("suburb"), "category": r.get("category"),
        "socials": [], "abn": None, "entity_type": None, "owner_name": None,
        "owner_confidence": "none", "gst": False, "trading_years": None,
        "source": "hotfrog directory", "source_url": None,
        "website_status": "clear", "website_note": note,
    })
    kept += 1
print(f"  kept {kept}, dropped {len(d)-kept} with a resolving website")

# --- 3. ABN enrich anything still missing it --------------------------------
todo = [m for m in MASTER if not m["abn"]]
print(f"ABN-enriching {len(todo)} ...")
def go(m):
    pc = None
    if m.get("address") and (x := re.search(r"VIC\s*(\d{4})", m["address"], re.I)):
        pc = x.group(1)
    try:
        return m, enrich(m["name"], pc)
    except Exception:
        return m, None
with cf.ThreadPoolExecutor(6) as ex:
    for m, r in ex.map(go, todo):
        if r and r.abn:
            m.update(abn=r.abn, entity_type=r.entity_type, owner_name=r.owner_name,
                     owner_confidence=r.owner_confidence, gst=r.gst,
                     trading_years=r.years)

# --- 3b. dedupe across sources ----------------------------------------------
# The same business can appear in both a trader association and a directory
# (Limnos Butchers did). Merge on phone, keeping the richer record.
def richness(m):
    return (bool(m["owner_name"]) * 4 + bool(m["abn"]) * 3 + len(m["socials"]) * 2
            + bool(m["address"]) + bool(m.get("trading_years")))

by_phone: dict = {}
for m in MASTER:
    key = m["phone_e164"] or m["name"].lower().strip()
    prev = by_phone.get(key)
    if prev is None:
        by_phone[key] = m
        continue
    keep, drop = (m, prev) if richness(m) > richness(prev) else (prev, m)
    for f in ("address", "suburb", "category", "owner_name", "abn", "entity_type",
              "trading_years", "source_url"):
        if not keep.get(f) and drop.get(f):
            keep[f] = drop[f]
    keep["gst"] = keep["gst"] or drop["gst"]
    keep["socials"] = list(dict.fromkeys(keep["socials"] + drop["socials"]))
    if keep["owner_confidence"] == "none":
        keep["owner_confidence"] = drop["owner_confidence"]
    by_phone[key] = keep
before = len(MASTER)
MASTER = list(by_phone.values())
print(f"deduped {before} -> {len(MASTER)}")

# --- 4. score ---------------------------------------------------------------
def score(m):
    s, sig = 0, []
    if m["abn"]:            s += 20; sig.append("active_abn")
    if m["owner_name"]:     s += 20; sig.append("owner_" + m["owner_confidence"])
    if m["gst"]:            s += 15; sig.append("gst_registered")
    y = m.get("trading_years") or 0
    if y >= 10:  s += 15; sig.append(f"{y}y_established")
    elif y >= 3: s += 8;  sig.append(f"{y}y")
    if m["socials"]:        s += 15; sig.append(f"{len(m['socials'])}_socials")
    if m["address"]:        s += 10; sig.append("street_premises")
    if (m["phone_e164"] or "").startswith("+614"): s += 5; sig.append("mobile")
    if m["source"] == "trader association": s += 5; sig.append("curated_source")
    m["score"] = min(s, 100); m["signals"] = sig
    return m

MASTER = sorted((score(m) for m in MASTER), key=lambda m: -m["score"])
pathlib.Path("data/leads").mkdir(parents=True, exist_ok=True)
json.dump(MASTER, open("data/leads/master.json", "w"), indent=1, ensure_ascii=False)

cols = ["score","name","category","phone","address","suburb","owner_name","owner_confidence",
        "abn","entity_type","gst","trading_years","socials","website_note","source","signals"]
p = pathlib.Path("data/leads/melbourne-master-leads-2026-08-25.csv")
with p.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader()
    for m in MASTER:
        w.writerow({**m, "socials": " | ".join(m["socials"]), "signals": "; ".join(m["signals"])})

print(f"\nMASTER {len(MASTER)} leads -> {p}")
print(f"  owner named   : {sum(1 for m in MASTER if m['owner_name'])}")
print(f"  GST registered: {sum(1 for m in MASTER if m['gst'])}")
print(f"  active ABN    : {sum(1 for m in MASTER if m['abn'])}")
print(f"  has socials   : {sum(1 for m in MASTER if m['socials'])}")
print(f"  10y+ trading  : {sum(1 for m in MASTER if (m.get('trading_years') or 0)>=10)}")
