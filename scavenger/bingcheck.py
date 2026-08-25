"""Free website + social verification via Bing HTML search.

Firecrawl costs credits per call; this path costs nothing, so it is what the
qualification pass runs on. Bing is used rather than Google because Google
serves a consent/minimal page to a plain curl while Bing returns a full,
parseable result set.

For each business we want three things:
  1. Does it own a website?  -> disqualifies the lead
  2. Does it have socials?   -> a warm lead: they believe in being online
  3. Is it actually active?   -> follower counts and "updated <date>" in snippets
"""
from __future__ import annotations

import gzip
import html
import re
import subprocess
import urllib.parse
from dataclasses import dataclass, field

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")

# Aggregators, socials and directories are not the business's own website.
NOT_OWN = {
    "hotfrog.com.au","yellowpages.com.au","truelocal.com.au","localsearch.com.au",
    "startlocal.com.au","aussieweb.com.au","yelp.com","yelp.com.au","m.yelp.com",
    "whitepages.com.au","whereis.com","cybo.com","biashara.cybo.com","sjn.com",
    "australianplanet.com","zipleaf.com","info-clipper.com","moovitapp.com",
    "facebook.com","m.facebook.com","instagram.com","linkedin.com","au.linkedin.com",
    "twitter.com","x.com","tiktok.com","youtube.com","pinterest.com","au.pinterest.com",
    "google.com","maps.google.com","business.site","bing.com","microsoft.com",
    "hipages.com.au","oneflare.com.au","serviceseeking.com.au","airtasker.com",
    "gumtree.com.au","abr.business.gov.au","asic.gov.au","glassdoor.com",
    "tripadvisor.com","tripadvisor.com.au","zomato.com","fresha.com","gettimely.com",
    "squareup.com","bookings.gettimely.com","hairsalons.com.au","oakleightraders.com.au",
    "wikipedia.org","indeed.com","seek.com.au","instagram.com","threads.net",
    "yellow.com.au","dnb.com","opengovau.com","abnlookup.com.au","hotdoc.com.au",
    "secondpage.com.au","childcarecentre.com.au","localsearch.com","cylex.com.au",
    "cylex-australia.com","brownbook.net","ausbizdirectory.com","pagesjaunes.com",
}
SOCIAL = {"facebook.com","m.facebook.com","instagram.com","linkedin.com",
          "au.linkedin.com","tiktok.com","youtube.com"}
FREE_HOST = (".wixsite.com",".business.site",".wordpress.com",".blogspot.com",
             ".weebly.com",".godaddysites.com",".square.site",".myshopify.com")

STOP = {"the","and","of","co","pty","ltd","services","service","group","salon",
        "melbourne","vic","victoria","australia","shop","centre","center"}

# "601 likes", "1.2K followers", "Updated August 2026", "4.8 (37)"
RE_LIKES = re.compile(r"([\d,\.]+\s*[KkMm]?)\s*(?:likes|followers|people follow)", re.I)
RE_UPDATED = re.compile(r"updated\s+([A-Z][a-z]+\s+20\d\d)", re.I)
RE_REVIEWS = re.compile(r"(\d+)\s*(?:reviews|ratings)", re.I)
RE_ESTAB = re.compile(r"\b(?:since|est\.?|established)\s+(19\d\d|20[0-2]\d)\b", re.I)


def _fetch(url: str, timeout: int = 30) -> str:
    """curl through the session proxy; returns '' on failure rather than raising."""
    try:
        out = subprocess.run(
            ["curl","-sS","--compressed","--max-time",str(timeout),
             "-H",f"User-Agent: {UA}",
             "-H","Accept: text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
             "-H","Accept-Language: en-AU,en;q=0.9", url],
            capture_output=True, timeout=timeout+10)
        return out.stdout.decode("utf-8","ignore")
    except Exception:
        return ""


def host_of(url: str) -> str:
    try:
        h = (urllib.parse.urlparse(url).hostname or "").lower()
    except ValueError:
        return ""
    return h[4:] if h.startswith("www.") else h


def tokens(name: str) -> set[str]:
    return {t for t in re.findall(r"[a-z]+", name.lower())
            if len(t) > 2 and t not in STOP}


def domain_matches(url: str, name: str) -> bool:
    """Guard against crediting a competitor's domain to this business."""
    stem = re.sub(r"[^a-z]", "", host_of(url).split(".")[0])
    toks = tokens(name)
    return any(t in stem for t in toks if len(t) > 3) if toks else False


@dataclass
class Check:
    name: str
    website: str | None = None
    socials: list[str] = field(default_factory=list)
    followers: int | None = None
    last_seen: str | None = None
    reviews: int | None = None
    established: str | None = None
    directory_hits: int = 0
    raw_hits: int = 0
    notes: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        if self.website:
            return "has_website"
        if self.raw_hits == 0:
            return "no_trace"          # nothing online at all -- may be defunct
        return "clear"


def _num(s: str) -> int:
    s = s.strip().replace(",", "")
    mult = 1
    if s[-1:].lower() == "k": mult, s = 1_000, s[:-1]
    elif s[-1:].lower() == "m": mult, s = 1_000_000, s[:-1]
    try:
        return int(float(s) * mult)
    except ValueError:
        return 0


def check(name: str, suburb: str | None = None, extra: str = "") -> Check:
    q = f'"{name}" {suburb or ""} {extra}'.strip()
    url = "https://www.bing.com/search?" + urllib.parse.urlencode(
        {"q": q, "count": "20", "setmkt": "en-AU"})
    page = _fetch(url)
    c = Check(name=name)
    if not page:
        c.notes.append("fetch_failed")
        return c

    # Bing wraps organic result links in <a href="http..."> inside <h2>.
    links = re.findall(r'<h2><a[^>]+href="(https?://[^"]+)"', page)
    if not links:
        links = re.findall(r'href="(https?://[^"]+)"[^>]*class="[^"]*tilk', page)
    text = html.unescape(re.sub(r"<[^>]+>", " ", page))
    c.raw_hits = len(links)

    for link in links:
        h = host_of(link)
        if not h or h.endswith("bing.com") or h.endswith("microsoft.com"):
            continue
        if h in SOCIAL:
            if link not in c.socials:
                c.socials.append(link)
            continue
        if h in NOT_OWN or any(h.endswith(f) for f in FREE_HOST):
            c.directory_hits += 1
            continue
        if domain_matches(link, name):
            c.website = c.website or link
        else:
            c.directory_hits += 1

    if (m := RE_LIKES.search(text)):   c.followers = _num(m.group(1))
    if (m := RE_UPDATED.search(text)): c.last_seen = m.group(1)
    if (m := RE_REVIEWS.search(text)): c.reviews = int(m.group(1))
    if (m := RE_ESTAB.search(text)):   c.established = m.group(1)
    return c
