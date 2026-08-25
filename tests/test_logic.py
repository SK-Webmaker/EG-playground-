"""Unit tests over the real page data observed during development."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from scavenger.models import Lead, normalise_phone, is_mobile
from scavenger.sources import abn
from scavenger import verify, score, dedupe, enrich

def test_phone_normalisation():
    assert normalise_phone("03 9548 3115") == "+61395483115"
    assert normalise_phone("0406 985 226") == "+61406985226"
    assert normalise_phone("1300 768 533") == "+611300768533"
    assert is_mobile(normalise_phone("0406 985 226"))
    assert not is_mobile(normalise_phone("03 9548 3115"))

def test_abn_person_parsing():
    # Verified live: ABN 11 584 809 528 / HUME CONCRETING MELBOURNE
    assert abn.looks_like_person("MEHMET, HAKAN")
    assert abn.format_owner("MEHMET, HAKAN") == "Hakan Mehmet"
    # Companies are not people
    assert not abn.looks_like_person("Traynor Roofing Pty Ltd")
    assert not abn.looks_like_person("CONCRETING MELBOURNE PTY LTD")
    assert abn.trading_years("01 Jul 2005") > 19

def test_website_classification():
    # koncept Concreting really does have a site -> disqualify
    assert verify.is_own_website("http://www.concreting.koncept.net.au/")
    # Aggregators and socials are not the business's own website
    assert not verify.is_own_website("https://www.hotfrog.com.au/company/123")
    assert not verify.is_own_website("https://www.facebook.com/somebiz")
    assert not verify.is_own_website("https://mybiz.wixsite.com/home")
    assert verify.is_social("https://www.facebook.com/somebiz")

def test_domain_must_match_business():
    assert verify.domain_matches_business("http://banatcabinets.com.au", "Banat Cabinet Makers")
    # A competitor's domain must not disqualify our lead
    assert not verify.domain_matches_business("http://someoneelse.com.au", "Banat Cabinet Makers")

def test_generic_name_detection():
    # Real SEO shells seen on Hotfrog
    assert score.looks_generic("Concreting Melbourne")
    assert score.looks_generic("Melbourne Wide Bathroom Renovation")
    # Real owner-operators must survive
    assert not score.looks_generic("Banat Cabinet Makers")
    assert not score.looks_generic("A A Ibrahim Cabinet Makers")
    assert score.looks_owner_operated("A A Ibrahim Cabinet Makers")
    assert score.looks_owner_operated("Paul's Landscaping Melbourne")

def test_shared_phone_flagging():
    # 0466 344 447 appeared on 4 fake suburb listings
    leads = [Lead(business_name=f"Bathroom Renovations {s}", niche="bathroom-renovations",
                  phone_raw="0466 344 447") for s in ("Kew", "Brighton", "Camberwell")]
    score.flag_shared_phones(leads)
    assert all(any(f.startswith("shared_phone") for f in l.flags) for l in leads)

def test_website_disqualifies_lead():
    l = Lead(business_name="Banat Cabinet Makers", niche="cabinet-makers",
             ticket_value=25_000, phone_raw="03 9464 2883")
    l.has_website = True
    assert score.score(l) == 0
    assert "HAS_WEBSITE_disqualified" in l.flags

def test_confirmed_owner_scores_above_unidentified():
    base = dict(business_name="Banat Cabinet Makers", niche="cabinet-makers",
                ticket_value=25_000, phone_raw="0412 000 111")
    known = Lead(**base); known.has_website = False
    known.owner_name = "Hakan Mehmet"; known.owner_confidence = "confirmed"
    known.entity_type = "Individual/Sole Trader"; known.gst_registered = True
    known.trading_years = 10.0
    unknown = Lead(**base); unknown.has_website = False
    assert score.score(known) > score.score(unknown)

def test_unverified_website_is_penalised():
    base = dict(business_name="Miffy Excavations", niche="excavation", ticket_value=30_000,
                phone_raw="03 9370 3513")
    clear = Lead(**base); clear.has_website = False
    unknown = Lead(**base); unknown.has_website = None
    assert score.score(clear) > score.score(unknown)
    assert "website_unverified" in unknown.flags

def test_dedupe_merges_richer_record():
    a = Lead(business_name="Ascot Excavations", niche="excavation", phone_raw="0418 584 283")
    b = Lead(business_name="Ascot Excavations", niche="excavation", phone_raw="0418 584 283",
             address="89 Fenton St", postcode="3032", owner_name="Someone", abn="123")
    out = dedupe.dedupe([a, b])
    assert len(out) == 1 and out[0].owner_name == "Someone"

def test_abn_match_scoring_rejects_interstate():
    vic = enrich.match_score("Banat Cabinet Makers", "BANAT CABINETS", "3074 VIC")
    nsw = enrich.match_score("Banat Cabinet Makers", "BANAT CABINETS", "2000 NSW")
    assert vic > nsw
    # The stale Spiteri case: unrelated names must not match
    assert enrich.match_score("F & R Spiteri Concreting", "S MORRIS CONCRETING PTY LTD", "4560 QLD") < 0.6

def test_surname_inference_skips_trade_words():
    assert enrich._surname_from_trading_name("Traynor Roofing") == "Traynor"
    assert enrich._surname_from_trading_name("Saluni Metal Roofing") == "Saluni"

def test_family_trust_surname():
    # Verified live: Banat Cabinet Makers trades under THE CIRKA FAMILY TRUST
    assert abn.family_surname("THE CIRKA FAMILY TRUST") == "Cirka"
    assert abn.family_surname("The Trustee for the Nguyen Family Trust") == "Nguyen"
    # Must not yield a junk "surname"
    assert abn.family_surname("SUPA REBLOCKING AND UNDERPINNING (VIC) PTY LTD") is None
    assert abn.family_surname("THE FAMILY TRUST") is None


if __name__ == "__main__":
    fns = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    failed = 0
    for name, fn in fns:
        try:
            fn(); print(f"  PASS {name}")
        except AssertionError as e:
            failed += 1; print(f"  FAIL {name}: {e}")
        except Exception as e:
            failed += 1; print(f"  ERR  {name}: {type(e).__name__}: {e}")
    print(f"\n{len(fns)-failed}/{len(fns)} passed")
    raise SystemExit(1 if failed else 0)
