"""Website verification -- the make-or-break check.

A directory listing with no website link proves nothing (Hotfrog hides the field
on search pages). A lead is only sold as "no website" once we have positive
evidence, in this order:

  1. Detail page on the source directory -- shows the website if one exists.
  2. Targeted web search for the business name + suburb.

Anything we can't positively clear stays `has_website=None` and is quarantined
out of the callable list, because pitching a web design service to someone who
already has a website is the fastest way to burn the lead.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

# Aggregator / social domains are NOT the business's own website.
NON_SITE_DOMAINS = {
    "hotfrog.com.au", "yellowpages.com.au", "truelocal.com.au", "localsearch.com.au",
    "startlocal.com.au", "aussieweb.com.au", "yelp.com", "yelp.com.au",
    "facebook.com", "m.facebook.com", "instagram.com", "linkedin.com",
    "twitter.com", "x.com", "tiktok.com", "youtube.com", "pinterest.com",
    "google.com", "goo.gl", "maps.google.com", "business.site",
    "hipages.com.au", "oneflare.com.au", "serviceseeking.com.au", "airtasker.com",
    "wordpress.com", "wix.com", "squarespace.com", "gumtree.com.au",
    "abr.business.gov.au", "asic.gov.au", "centralindex.com", "here.com",
}

SOCIAL_DOMAINS = {"facebook.com", "m.facebook.com", "instagram.com", "linkedin.com"}

# Free-hosting subdomains mean "no real web presence" for our purposes, but the
# owner clearly wanted one -- that is a warm lead, not a cold one.
FREE_HOST_SUFFIXES = (".wixsite.com", ".business.site", ".wordpress.com",
                      ".blogspot.com", ".weebly.com", ".godaddysites.com")


def domain_of(url: str | None) -> str | None:
    if not url:
        return None
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return None
    return host[4:] if host.startswith("www.") else host or None


def is_own_website(url: str | None) -> bool:
    """True only for a domain the business plausibly controls."""
    host = domain_of(url)
    if not host:
        return False
    if host in NON_SITE_DOMAINS:
        return False
    if any(host.endswith(s) for s in FREE_HOST_SUFFIXES):
        return False
    return "." in host


def is_social(url: str | None) -> bool:
    return domain_of(url) in SOCIAL_DOMAINS


def _name_tokens(name: str) -> set[str]:
    stop = {"the", "and", "pty", "ltd", "co", "services", "service", "group",
            "melbourne", "vic", "victoria", "australia"}
    return {t for t in re.findall(r"[a-z]+", name.lower()) if len(t) > 2 and t not in stop}


def domain_matches_business(url: str, business_name: str) -> bool:
    """Does this domain actually belong to THIS business, not a competitor?"""
    host = domain_of(url)
    if not host:
        return False
    stem = re.sub(r"[^a-z]", "", host.split(".")[0])
    tokens = _name_tokens(business_name)
    if not tokens:
        return False
    # Require a distinctive token of the name to appear in the domain stem.
    return any(t in stem for t in tokens if len(t) > 3)


def verify_from_detail(lead, detail: dict) -> None:
    """Apply a directory detail-page result to the lead. Authoritative when positive."""
    url = (detail or {}).get("website_url")
    if url and is_own_website(url):
        lead.has_website = True
        lead.website_url = url
        lead.website_evidence = f"listed on source detail page: {url}"
        return
    if url and is_social(url):
        lead.social_only = url
    if (detail or {}).get("email") and not lead.email:
        lead.email = detail["email"]
    if (detail or {}).get("contact_person") and not lead.owner_name:
        lead.owner_name = detail["contact_person"]
        lead.owner_source = "directory listing contact"
        lead.owner_confidence = "inferred"
    # No website on the detail page -> candidate confirmed, pending search sweep.
    lead.has_website = False
    lead.website_evidence = "no website field on source detail page"


def verify_from_search(lead, results: list[dict]) -> None:
    """Second pass: a web search that finds an owned domain overrides a False."""
    for r in results or []:
        url = r.get("url") or ""
        if is_social(url) and not lead.social_only:
            lead.social_only = url
        if is_own_website(url) and domain_matches_business(url, lead.business_name):
            lead.has_website = True
            lead.website_url = url
            lead.website_evidence = f"found via web search: {url}"
            return
    if lead.has_website is False:
        lead.website_evidence = (
            (lead.website_evidence or "") + "; no matching domain in web search"
        )
