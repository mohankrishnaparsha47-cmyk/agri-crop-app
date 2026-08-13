"""
Simple i18n module for English <-> Telugu toggle.
Usage in templates: {{ t('dashboard') }}
Usage in app.py: from translations import t, set_language
"""

from flask import session

TRANSLATIONS = {
    "app_name": {"en": "Smart Farmer Assistant", "te": "స్మార్ట్ ఫార్మర్ అసిస్టెంట్"},
    "tagline": {"en": "Better Information, Better Farming, Better Tomorrow",
                "te": "మంచి సమాచారం, మంచి వ్యవసాయం, మంచి భవిష్యత్తు"},
    "dashboard": {"en": "Dashboard", "te": "డాష్‌బోర్డ్"},
    "home": {"en": "Home", "te": "హోమ్"},
    "crop_suggestions": {"en": "Crop Suggestions", "te": "పంట సూచనలు"},
    "weather_updates": {"en": "Weather Updates", "te": "వాతావరణ సమాచారం"},
    "fertilizer_recommendations": {"en": "Fertilizer Recommendations", "te": "ఎరువుల సిఫార్సులు"},
    "irrigation_alerts": {"en": "Irrigation Alerts", "te": "నీటి తడి హెచ్చరికలు"},
    "field_records": {"en": "Field Records", "te": "పొల రికార్డులు"},
    "schemes": {"en": "Farmer Subsidy & Schemes", "te": "రైతు రాయితీలు & పథకాలు"},
    "market_prices": {"en": "Market Prices", "te": "మార్కెట్ ధరలు"},
    "pest_detection": {"en": "Pest & Disease Detection", "te": "పురుగు మరియు వ్యాధి గుర్తింపు"},
    "profit_calculator": {"en": "Profit Calculator", "te": "లాభం కాలిక్యులేటర్"},
    "soil_info": {"en": "Soil Information", "te": "నేల సమాచారం"},
    "my_applications": {"en": "My Applications", "te": "నా అప్లికేషన్లు"},
    "login": {"en": "Login", "te": "లాగిన్"},
    "register": {"en": "Register", "te": "నమోదు"},
    "logout": {"en": "Logout", "te": "లాగ్అవుట్"},
    "phone_number": {"en": "Phone Number", "te": "ఫోన్ నంబర్"},
    "password": {"en": "Password", "te": "పాస్‌వర్డ్"},
    "submit": {"en": "Submit", "te": "సమర్పించు"},
    "good_morning": {"en": "Good Morning", "te": "శుభోదయం"},
    "productive_today": {"en": "Let's make today productive.", "te": "ఈరోజును ఫలవంతంగా చేసుకుందాం."},
    "benefits": {"en": "Benefits", "te": "ప్రయోజనాలు"},
    "improves_yield": {"en": "Improves Crop Yield", "te": "పంట దిగుబడి పెంచుతుంది"},
    "saves_water": {"en": "Saves Water and Time", "te": "నీరు మరియు సమయం ఆదా చేస్తుంది"},
    "reduces_costs": {"en": "Reduces Costs", "te": "ఖర్చులు తగ్గిస్తుంది"},
    "supports_farming": {"en": "Supports Smart Farming", "te": "స్మార్ట్ వ్యవసాయానికి తోడ్పడుతుంది"},
    "recommended_crop": {"en": "Recommended Crop", "te": "సిఫార్సు చేసిన పంట"},
    "get_suggestion": {"en": "Get Crop Suggestion", "te": "పంట సూచన పొందండి"},
    "select_crop": {"en": "Select Crop", "te": "పంటను ఎంచుకోండి"},
    "select_soil": {"en": "Select Soil Type", "te": "నేల రకాన్ని ఎంచుకోండి"},
    "apply_now": {"en": "Apply Now", "te": "ఇప్పుడు దరఖాస్తు చేయండి"},
    "check_eligibility": {"en": "Check My Eligibility", "te": "నా అర్హతను తనిఖీ చేయండి"},
    "add_record": {"en": "Add Record", "te": "రికార్డు జోడించండి"},
    "new": {"en": "NEW", "te": "కొత్తది"},
}


def t(key):
    """Translate a key based on current session language (default English)."""
    lang = session.get("lang", "en")
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang, entry.get("en", key))


def set_language(lang_code):
    if lang_code in ("en", "te"):
        session["lang"] = lang_code


def current_language():
    return session.get("lang", "en")
