"""
Farmer Subsidy & Schemes module.
Contains a reference list of major Central & Telangana state government
farmer welfare schemes, plus a simple rule-based eligibility checker.

NOTE: Scheme details (benefit amounts, criteria) reflect commonly published
scheme guidelines at a summary level for academic/demo purposes. Encourage
users to verify latest details on official portals before applying.
"""

SCHEMES = [
    {
        "id": "pm_kisan",
        "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "level": "Central",
        "description": "Direct income support of Rs. 6,000/year (in 3 installments of Rs. 2,000) to eligible farmer families.",
        "benefit": "Rs. 6,000 per year (direct bank transfer)",
        "eligibility": {
            "max_land_acres": None,   # small & marginal originally, now broadly applicable with exclusions
            "category": None,
            "min_land_acres": 0
        },
        "official_link": "https://pmkisan.gov.in"
    },
    {
        "id": "rythu_bandhu",
        "name": "Rythu Bandhu Scheme",
        "level": "Telangana State",
        "description": "Investment support scheme providing per-acre financial assistance to Telangana farmers per crop season.",
        "benefit": "Rs. 5,000/acre/season (Rabi & Kharif)",
        "eligibility": {
            "max_land_acres": None,
            "category": None,
            "state_only": "Telangana"
        },
        "official_link": "https://rythubandhu.telangana.gov.in"
    },
    {
        "id": "rythu_bima",
        "name": "Rythu Bima (Farmer Life Insurance)",
        "level": "Telangana State",
        "description": "Life insurance coverage scheme for Telangana farmers/farm family in case of death of the farmer (natural or accidental).",
        "benefit": "Rs. 5,00,000 life insurance cover",
        "eligibility": {
            "max_land_acres": None,
            "category": None,
            "state_only": "Telangana",
            "age_range": (18, 59)
        },
        "official_link": "https://tsdex.telangana.gov.in"
    },
    {
        "id": "pmfby",
        "name": "PMFBY (Pradhan Mantri Fasal Bima Yojana)",
        "level": "Central",
        "description": "Crop insurance scheme covering yield losses due to natural calamities, pests & diseases.",
        "benefit": "Insurance payout on crop loss; low premium (2% Kharif, 1.5% Rabi)",
        "eligibility": {
            "max_land_acres": None,
            "category": None
        },
        "official_link": "https://pmfby.gov.in"
    },
    {
        "id": "kcc",
        "name": "Kisan Credit Card (KCC)",
        "level": "Central",
        "description": "Provides farmers with affordable credit for crop production, post-harvest expenses, and allied activities.",
        "benefit": "Short-term credit up to Rs. 3 lakh at subsidized interest (~4% with timely repayment)",
        "eligibility": {
            "max_land_acres": None,
            "category": None
        },
        "official_link": "https://www.myscheme.gov.in/schemes/kcc"
    },
    {
        "id": "soil_health_card",
        "name": "Soil Health Card Scheme",
        "level": "Central",
        "description": "Provides farmers with soil nutrient status reports and fertilizer/nutrient recommendations for their land.",
        "benefit": "Free soil testing report every 2 years",
        "eligibility": {
            "max_land_acres": None,
            "category": None
        },
        "official_link": "https://soilhealth.dac.gov.in"
    },
    {
        "id": "pmksy",
        "name": "PMKSY (Pradhan Mantri Krishi Sinchayee Yojana)",
        "level": "Central",
        "description": "Irrigation scheme promoting micro-irrigation (drip/sprinkler) for water-use efficiency, subsidy on equipment.",
        "benefit": "Subsidy up to 55%-80% on drip/sprinkler irrigation equipment cost",
        "eligibility": {
            "max_land_acres": None,
            "category": None
        },
        "official_link": "https://pmksy.gov.in"
    },
    {
        "id": "mif_telangana",
        "name": "Telangana Micro Irrigation Subsidy",
        "level": "Telangana State",
        "description": "State-level subsidy for drip/sprinkler irrigation systems to promote water conservation.",
        "benefit": "Up to 90% subsidy for SC/ST farmers, 80% for others (Telangana Horticulture Dept.)",
        "eligibility": {
            "max_land_acres": None,
            "category": None,
            "state_only": "Telangana"
        },
        "official_link": "https://horticulture.telangana.gov.in"
    },
    {
        "id": "nfsm",
        "name": "National Food Security Mission (NFSM) Input Subsidy",
        "level": "Central",
        "description": "Subsidy on seeds, farm implements & inputs to increase productivity of rice, wheat, pulses & coarse cereals.",
        "benefit": "Subsidy on certified seeds & farm machinery (varies by input)",
        "eligibility": {
            "max_land_acres": None,
            "category": None
        },
        "official_link": "https://www.nfsm.gov.in"
    },
    {
        "id": "sc_st_subplan",
        "name": "SC/ST Sub-Plan Agricultural Assistance (Telangana)",
        "level": "Telangana State",
        "description": "Special financial assistance & input subsidy for SC/ST category farmers under state sub-plan schemes.",
        "benefit": "Additional subsidy (10-15% higher than general category) on inputs & equipment",
        "eligibility": {
            "max_land_acres": None,
            "category": ["SC", "ST"],
            "state_only": "Telangana"
        },
        "official_link": "https://tswreis.telangana.gov.in"
    },
]


def check_eligibility(land_holding_acres, category, state, age=None):
    """
    Simple rule-based eligibility checker.
    Returns list of schemes the farmer is likely eligible for, with a reason.
    """
    eligible = []
    for scheme in SCHEMES:
        elig = scheme["eligibility"]
        reasons = []
        is_eligible = True

        if elig.get("state_only") and state and elig["state_only"].lower() != state.lower():
            is_eligible = False

        if elig.get("category") and category and category not in elig["category"]:
            is_eligible = False

        if elig.get("max_land_acres") is not None and land_holding_acres is not None:
            if land_holding_acres > elig["max_land_acres"]:
                is_eligible = False

        if elig.get("age_range") and age is not None:
            lo, hi = elig["age_range"]
            if not (lo <= age <= hi):
                is_eligible = False

        if is_eligible:
            eligible.append(scheme)

    return eligible


def get_all_schemes():
    return SCHEMES


def get_scheme_by_id(scheme_id):
    for s in SCHEMES:
        if s["id"] == scheme_id:
            return s
    return None
