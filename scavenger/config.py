"""Targeting configuration: which niches, where, and what a good lead looks like."""
from __future__ import annotations

# ---------------------------------------------------------------------------
# High-ticket niches. `ticket` is the typical AUD job value used for scoring --
# the whole premise is that one recovered job pays for a website many times over,
# which is the argument you make on the call.
# ---------------------------------------------------------------------------
NICHES: list[dict] = [
    {"slug": "home-extensions",     "ticket": 250_000, "label": "Home extensions / builders"},
    {"slug": "swimming-pools",      "ticket": 90_000,  "label": "Pool construction"},
    {"slug": "landscaping",         "ticket": 45_000,  "label": "Landscaping & outdoor construction"},
    {"slug": "kitchen-renovations", "ticket": 35_000,  "label": "Kitchen renovation"},
    {"slug": "bathroom-renovations","ticket": 28_000,  "label": "Bathroom renovation"},
    {"slug": "excavation",          "ticket": 30_000,  "label": "Excavation & earthmoving"},
    {"slug": "underpinning",        "ticket": 35_000,  "label": "Underpinning & restumping"},
    {"slug": "cabinet-makers",      "ticket": 25_000,  "label": "Custom joinery & cabinetmaking"},
    {"slug": "roofing",             "ticket": 22_000,  "label": "Roofing & re-roofing"},
    {"slug": "solar-energy",        "ticket": 15_000,  "label": "Solar & battery installation"},
    {"slug": "concreting",          "ticket": 18_000,  "label": "Concreting & driveways"},
    {"slug": "demolition",          "ticket": 25_000,  "label": "Demolition"},
    {"slug": "fencing",             "ticket": 12_000,  "label": "Fencing & gates"},
    {"slug": "decking",             "ticket": 15_000,  "label": "Decking & pergolas"},
    {"slug": "paving",              "ticket": 14_000,  "label": "Paving & stonework"},
    {"slug": "stonemasons",         "ticket": 20_000,  "label": "Stonemasonry"},
    {"slug": "waterproofing",       "ticket": 12_000,  "label": "Waterproofing"},
    {"slug": "scaffolding",         "ticket": 20_000,  "label": "Scaffolding hire"},
    {"slug": "air-conditioning",    "ticket": 12_000,  "label": "HVAC / split systems"},
    {"slug": "commercial-cleaning", "ticket": 36_000,  "label": "Commercial cleaning (annual contract)"},
]

# Melbourne metro coverage. Growth corridors first -- that is where owner-operator
# trades cluster and where the no-website rate is highest.
REGIONS: list[str] = [
    "melbourne", "craigieburn", "epping", "thomastown", "reservoir", "preston",
    "coburg", "sunshine", "footscray", "werribee", "hoppers-crossing", "tarneit",
    "point-cook", "melton", "caroline-springs", "dandenong", "springvale",
    "cranbourne", "pakenham", "berwick", "frankston", "mordialloc", "cheltenham",
    "ringwood", "bayswater", "box-hill", "glen-waverley", "clayton", "oakleigh",
    "bundoora", "greensborough", "eltham", "sunbury", "essendon", "brunswick",
]

# ---------------------------------------------------------------------------
# Owner-operator detection.
# ---------------------------------------------------------------------------

# A business named after a person is overwhelmingly owner-operated, and the ABN
# entity name will usually hand you the owner directly.
SURNAME_PATTERNS = [
    r"^[A-Z]\.?\s?[A-Z]?\.?\s?[A-Z]?\.?\s+[A-Z][a-z]{2,}",   # "A A Ibrahim ...", "F & R Spiteri ..."
    r"\b[A-Z][a-z]+(?:'s)\b",                                  # "Paul's Landscaping"
    r"^[A-Z][a-z]{2,}\s+(?:&|and)\s+Sons?\b",                  # "Rossi & Sons"
]

# Generic "<service> <suburb>" names are usually SEO shells or lead-gen resellers,
# not a business with an owner to sell to.
GENERIC_NAME_TOKENS = {
    "melbourne", "victoria", "vic", "australia", "wide", "best", "cheap",
    "cheaper", "affordable", "local", "pro", "expert", "experts", "services",
    "directory", "group", "solutions", "co", "company",
}

# Directory-listed phone numbers reused across many "businesses" mean a lead-gen
# reseller, not an operator. Anything at or above this count is dropped.
SHARED_PHONE_DROP_THRESHOLD = 2

# ---------------------------------------------------------------------------
# Scoring weights (see score.py)
# ---------------------------------------------------------------------------
WEIGHTS = {
    "ticket": 30,           # normalised job value
    "owner_identified": 25, # we have a human name to ask for
    "direct_mobile": 15,    # mobile reaches the owner, not a receptionist
    "sole_trader": 10,      # decision maker is one person -- short sales cycle
    "gst_registered": 10,   # GST implies >$75k turnover: they can afford it
    "trading_years": 10,    # established, not a startup with no cash
}

# Melbourne metro postcode range (3000-3210 inner/metro, 3335-3810 outer growth).
def in_melbourne(postcode: str | None) -> bool:
    if not postcode or not postcode.isdigit():
        return False
    pc = int(postcode)
    return 3000 <= pc <= 3210 or 3335 <= pc <= 3810
