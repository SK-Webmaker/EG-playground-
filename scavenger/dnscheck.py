"""Free website detection by resolving the domains a business would plausibly own.

Firecrawl search costs credits; DNS is free and unlimited. It is used as a
*positive* detector only: a resolving name-derived domain is strong evidence the
business has a website, while a non-resolving one is weaker evidence it does not
(they may use an unrelated domain).

Precision is the whole game -- a false "has website" silently drops a good lead.
So candidates must be multi-word concatenations of the business name, never a
single generic word: "wise.com" and "chief.com" resolve to unrelated companies
and would wrongly kill Hair Wise Salon and Hair & beauty Chief.
"""
from __future__ import annotations

import re
import socket
from concurrent.futures import ThreadPoolExecutor

socket.setdefaulttimeout(4)

DROP = {"the", "and", "of", "pty", "ltd", "co", "for", "trustee"}
# Trailing words owners routinely omit from their domain.
TRAILING = {"company", "services", "service", "group", "australia", "melbourne",
            "vic", "victoria", "shop", "store", "centre", "center", "co"}
TLDS = (".com.au", ".com", ".net.au", ".au")


def candidates(name: str) -> list[str]:
    words = [w.lower() for w in re.findall(r"[A-Za-z]+", name) if w.lower() not in DROP]
    if len(words) < 2:
        return []                      # single-word names are too collision-prone
    out = []
    full = "".join(words)
    out.append(full)
    trimmed = words[:]
    while len(trimmed) > 2 and trimmed[-1] in TRAILING:
        trimmed.pop()
        out.append("".join(trimmed))
    # NOTE: deliberately no "first two words" variant. It generates generic
    # industry domains owned by others -- harrisfamily.com and hairbeauty.com.au
    # both resolve, and would wrongly disqualify Harris Family Butchers and
    # Hair & beauty Chief, which are verified website-free.
    # >=10 chars keeps us clear of generic two-word collisions
    return [s for s in dict.fromkeys(out) if len(s) >= 10]


def resolves(domain: str) -> bool:
    try:
        socket.gethostbyname(domain)
        return True
    except Exception:
        return False


def owns_domain(domain: str, name: str) -> bool:
    """Confirm the resolved site actually belongs to this business.

    A parked or unrelated domain can match the name pattern, so fetch it and
    require a distinctive word from the business name to appear in the page.
    """
    from .traders import fetch
    page = fetch("https://" + domain, timeout=12) or fetch("http://" + domain, timeout=12)
    if not page:
        # Unreachable but resolving and name-shaped: assume it is theirs. Erring
        # toward "has website" costs a lead; erring the other way costs a wasted
        # call, which is the more expensive mistake for the person dialling.
        return True
    low = page.lower()
    if any(k in low for k in ("domain is for sale", "buy this domain",
                              "parked free", "godaddy.com/domainsearch")):
        return False
    words = [w.lower() for w in re.findall(r"[A-Za-z]{4,}", name) if w.lower() not in DROP]
    distinctive = [w for w in words if w not in TRAILING]
    return any(w in low for w in distinctive)


def find_site(name: str, confirm: bool = True) -> str | None:
    for stem in candidates(name):
        for tld in TLDS:
            d = stem + tld
            if resolves(d) and (not confirm or owns_domain(d, name)):
                return d
    return None


def bulk(names: list[str], workers: int = 24) -> dict[str, str | None]:
    with ThreadPoolExecutor(workers) as ex:
        return dict(zip(names, ex.map(find_site, names)))
