"""Scrape Melbourne shopping-strip trader directories (free, no API credits).

Each strip site is described by its index URL and the URL shape of a trader page.
Everything else is generic: fetch index -> collect detail links -> fetch detail
pages -> detect site-wide footer hosts -> parse each trader.
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from scavenger.traders import (fetch, parse_trader, sitewide_hosts,  # noqa: E402
                               sitewide_socials)

STRIPS = [
    {"name": "Oakleigh (Eaton Mall / Portman St)", "host": "oakleightraders.com.au",
     "index": ["https://oakleightraders.com.au/traders/"],
     "detail": r'href="(https://oakleightraders\.com\.au/trader/[^"]+)"'},
    {"name": "Balaclava / St Kilda East (Carlisle St)", "host": "carlislestreet.com.au",
     "index": ["https://www.carlislestreet.com.au/"],
     "detail": r'href="[^"]*?(/directory/[a-z0-9\-]{3,}/)"',
     "base": "https://carlislestreet.com.au"},
    {"name": "South Melbourne Market", "host": "southmelbournemarket.com.au",
     "index": ["https://www.southmelbournemarket.com.au/traders/"],
     "detail": r'href="[^"]*?(/traders/[a-z0-9\-]{3,}/)"',
     "base": "https://www.southmelbournemarket.com.au"},
    {"name": "Prahran Market", "host": "prahranmarket.com.au",
     "index": ["https://prahranmarket.com.au/traders/"],
     "detail": r'href="[^"]*?(/trader/[a-z0-9\-]{3,}/)"',
     "base": "https://www.prahranmarket.com.au"},
    {"name": "Chapel St (Prahran / Windsor / South Yarra)", "host": "chapelstreet.com.au",
     "index": [f"https://chapelstreet.com.au/businesses/{c}/" for c in
               ("bar","coffee","entertainment","food-beverage","health-wellbeing",
                "retail","services","community")],
     "detail": r'href="[^"]*?(/business/[a-z0-9\-]{3,}/)"',
     "base": "https://chapelstreet.com.au"},
    {"name": "Dandenong Market", "host": "dandenongmarket.com.au",
     "index": ["https://www.dandenongmarket.com.au/traders/"],
     "detail": r'href="[^"]*?(/traders/[a-z0-9\-]{3,}/)"',
     "base": "https://www.dandenongmarket.com.au"},
]

# Boilerplate that appears on every page of these sites.
NAV = {
 'Home','Traders','Dining','Fashion','Beauty','Health','Lifestyle','Services','About',
 'About Oakleigh','Getting to Oakleigh','What’s On','Contact','Contact Us','List your Business',
 'Instagram','Facebook','Skip to content','View Trader »','More Oakleigh Traders','Website',
 '* All images provided by listed trader.','Join Our','Newsletter','First Name','Last  Name',
 'Email','Subscribe','‣','Directory','Industries','Keywords','Search','Menu','Back',
 'What’s On','Visit','Shop','Eat','News','Events','Read More','View More','Share',
 'Opening Hours','Location','Follow us','Sign up','Subscribe to our newsletter',
}


def collect(strip: dict) -> list[str]:
    links: set[str] = set()
    for idx_url in strip["index"]:
        page = fetch(idx_url)
        if not page:
            continue
        for m in re.findall(strip["detail"], page):
            links.add(m if m.startswith("http") else strip.get("base", "") + m)
    return sorted(links)


def run(strip: dict, workers: int = 12) -> list:
    links = collect(strip)
    if not links:
        print(f"  !! no detail links for {strip['name']}")
        return []
    with cf.ThreadPoolExecutor(workers) as ex:
        pages = list(ex.map(fetch, links))
    pairs = [(u, p) for u, p in zip(links, pages) if p and len(p) > 500]
    infra = sitewide_hosts([p for _, p in pairs])
    own_socials = sitewide_socials([p for _, p in pairs])
    out = []
    for u, p in pairs:
        t = parse_trader(u, p, strip["host"], NAV, infra, own_socials)
        if t and t.name:
            t.strip = strip["name"]
            out.append(t)
    print(f"  {strip['name']}: {len(links)} links -> {len(out)} parsed "
          f"({sum(1 for t in out if not t.website)} no website)")
    return out


if __name__ == "__main__":
    allt = []
    for s in STRIPS:
        print(f"scraping {s['host']} ...")
        allt += run(s)
    pathlib.Path("data").mkdir(exist_ok=True)
    json.dump([t.__dict__ for t in allt],
              open("data/strips-raw.json", "w"), indent=1, ensure_ascii=False)
    print(f"\ntotal {len(allt)} traders -> data/strips-raw.json")
