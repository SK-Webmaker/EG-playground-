"""Local trader-association directories -- a free, high-quality discovery source.

Melbourne shopping strips run their own trader association sites. They beat the
big directories on every axis that matters here:

  * curated and current -- membership is paid/maintained, so dead businesses drop
    off, unlike Hotfrog where listings rot for years
  * real shopfronts with a street address and a landline
  * small unprotected sites, so they are reachable by plain HTTP at no API cost
  * the listing shows the trader's own website when they have one, which makes
    "no website" an observation rather than an inference

Parsed generically: strip scripts, flatten to text lines, then read the
name/category/address/phone block and look for an external link.
"""
from __future__ import annotations

import hashlib
import html
import os
import pathlib
import re
import subprocess
from dataclasses import dataclass, field

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")

AU_PHONE = re.compile(r"\(0\d\)\s?\d{4}\s?\d{4}|\b0[2-8]\s?\d{4}\s?\d{4}\b|\b04\d{2}\s?\d{3}\s?\d{3}\b")
ADDRESS = re.compile(r"\d+[A-Za-z]?[/\-]?\s?[\w' ]+(?:St|Street|Rd|Road|Ave|Avenue|Pde|Parade|"
                     r"Cres|Court|Ct|Dr|Drive|Hwy|Highway|Place|Pl|Lane|Ln|Arcade|Mall)\b[^,]*,?"
                     r"[^,]*VIC\s*\d{4}", re.I)

# Hosts that are the association's own or infrastructure, not a trader's website.
def infra_hosts(site_host: str) -> set[str]:
    return {site_host, "gmpg.org", "w3.org", "fonts.googleapis.com", "fonts.gstatic.com",
            "google.com", "googletagmanager.com", "gstatic.com", "jquery.com",
            "wordpress.org", "elementor.com", "cdn.jsdelivr.net", "schema.org"}

SOCIAL_HOSTS = {"facebook.com", "instagram.com", "linkedin.com", "twitter.com",
                "x.com", "tiktok.com", "youtube.com"}


CACHE = pathlib.Path(os.getenv("SCAVENGER_CACHE", "data/raw/pages"))


def fetch(url: str, timeout: int = 25) -> str:
    """GET with an on-disk cache. These are small community sites -- fetch once."""
    CACHE.mkdir(parents=True, exist_ok=True)
    key = CACHE / (hashlib.sha1(url.encode()).hexdigest() + ".html")
    if key.exists():
        return key.read_text(encoding="utf-8", errors="ignore")
    try:
        r = subprocess.run(
            ["curl", "-sSL", "--compressed", "--max-time", str(timeout),
             "-H", f"User-Agent: {UA}", "-H", "Accept-Language: en-AU,en;q=0.9", url],
            capture_output=True, timeout=timeout + 10)
        body = r.stdout.decode("utf-8", "ignore")
        if body:
            key.write_text(body, encoding="utf-8")
        return body
    except Exception:
        return ""


def text_lines(page: str) -> list[str]:
    body = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", page, flags=re.S)
    txt = html.unescape(re.sub(r"<[^>]+>", "\n", body))
    return [l.strip() for l in txt.split("\n") if l.strip()]


def hosts_in(page: str) -> set[str]:
    out = set()
    for u in re.findall(r'href="(https?://[^"]+)"', page):
        m = re.match(r"https?://([^/]+)", u)
        if m:
            out.add(re.sub(r"^www\.", "", m.group(1).lower()))
    return out


def social_urls(page: str) -> list[str]:
    """Full social profile URLs with a real handle in the path."""
    found = []
    for u in re.findall(r'href="(https?://[^"]+)"', page):
        m = re.match(r'https?://(?:www\.|m\.)?([^/]+)(/[^"?#]*)?', u)
        if not m:
            continue
        host, path = m.group(1).lower(), (m.group(2) or "").strip("/")
        if host not in SOCIAL_HOSTS or not path:
            continue
        # a bare share/intent link is not a profile
        if path.split("/")[0] in {"sharer", "share", "intent", "dialog", "plugins"}:
            continue
        if u not in found:
            found.append(u.split("?")[0])
    return found


def sitewide_socials(pages: list[str], threshold: float = 0.3) -> set[str]:
    """The association's own socials appear on every page -- not a trader's."""
    from collections import Counter
    c: Counter = Counter()
    for pg in pages:
        c.update(set(social_urls(pg)))
    cut = max(2, int(len(pages) * threshold))
    return {u for u, n in c.items() if n >= cut}


@dataclass
class Trader:
    name: str
    category: str | None = None
    description: str | None = None
    address: str | None = None
    phone: str | None = None
    website: str | None = None
    socials: list[str] = field(default_factory=list)
    source_url: str = ""
    strip: str = ""


def sitewide_hosts(pages: list[str], threshold: float = 0.3) -> set[str]:
    """Hosts linked from most pages are footer/infrastructure, not trader sites.

    Self-calibrating per directory: Oakleigh's footer credits its web developer
    (anthonyzayler.com) on all 138 pages, which would otherwise be misread as
    every trader's website.
    """
    from collections import Counter
    counts: Counter = Counter()
    for pg in pages:
        counts.update(hosts_in(pg))
    cut = max(2, int(len(pages) * threshold))
    return {h for h, n in counts.items() if n >= cut}


def parse_trader(url: str, page: str, site_host: str, nav: set[str],
                 extra_infra: set[str] | None = None,
                 skip_socials: set[str] | None = None) -> Trader | None:
    lines = [l for l in text_lines(page) if l not in nav and len(l) < 300]
    if not lines:
        return None
    # The <title> carries the trader name before the site suffix.
    m = re.search(r"<title>([^<]+)</title>", page)
    name = re.split(r"\s+[-|–]\s+", html.unescape(m.group(1)))[0].strip() if m else None
    if not name:
        return None

    t = Trader(name=name, source_url=url)
    try:
        i = next(idx for idx, l in enumerate(lines) if l.strip() == name)
        block = lines[i + 1:i + 12]
    except StopIteration:
        block = lines[:12]

    for line in block:
        if not t.phone and (p := AU_PHONE.search(line)):
            t.phone = p.group(0)
        elif not t.address and (a := ADDRESS.search(line)):
            t.address = a.group(0)
        elif not t.category and len(line) < 40 and "‣" not in line and not AU_PHONE.search(line):
            t.category = line
        elif not t.description and len(line) > 40:
            t.description = line

    infra = infra_hosts(site_host) | (extra_infra or set())
    for h in hosts_in(page):
        if h in infra or h.endswith(".gov.au"):
            continue
        if h in SOCIAL_HOSTS or any(h.endswith("." + s) for s in SOCIAL_HOSTS):
            continue                      # handled as full URLs below
        if not t.website:
            t.website = h

    t.socials = [u for u in social_urls(page) if u not in (skip_socials or set())]
    return t
