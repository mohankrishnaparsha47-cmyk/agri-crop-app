"""
Mandi / Market Price Checker module.
Provides current market (mandi) prices for crops across major Telangana
markets. Uses a bundled sample dataset for offline demo.

TO GO LIVE with real-time prices:
Data.gov.in provides a free "Agmarknet" API (Variety-wise Daily Market Prices).
1. Register free at https://data.gov.in/user/register and get an API key.
2. Replace `get_market_prices()` below with a requests.get() call to:
   https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
   (search "Agmarknet" on data.gov.in for the latest resource ID)
3. Cache results (e.g. refresh every 6 hours) to avoid hitting rate limits.
"""

import random
from datetime import datetime, timedelta

MARKETS = [
    "Warangal Mandi", "Nizamabad Mandi", "Karimnagar Mandi",
    "Khammam Mandi", "Hyderabad (Bowenpally) Mandi", "Adilabad Mandi",
    "Mahbubnagar Mandi", "Nalgonda Mandi"
]

# Base price per quintal (Rs.) - representative ranges for demo
CROP_BASE_PRICE = {
    "rice": (1900, 2400),
    "maize": (1700, 2100),
    "cotton": (6200, 7500),
    "chilli": (12000, 22000),
    "turmeric": (7500, 9500),
    "soybean": (4200, 4800),
    "groundnut": (5500, 6500),
    "wheat": (2100, 2400),
    "sugarcane": (300, 380),
    "pigeonpeas": (6500, 7800),
    "chickpea": (5000, 5800),
    "blackgram": (7000, 8200),
    "mungbean": (7200, 8500),
    "jute": (4500, 5200),
    "coffee": (25000, 32000),
    "banana": (1200, 1800),
    "mango": (2500, 4500),
    "papaya": (800, 1400),
    "coconut": (2200, 3200),
    "grapes": (4000, 6500),
    "pomegranate": (5500, 9000),
    "orange": (2000, 3200),
    "apple": (6000, 9500),
    "watermelon": (600, 1200),
    "muskmelon": (900, 1500),
    "lentil": (6500, 7500),
    "mothbeans": (5500, 6200),
    "kidneybeans": (7500, 8800),
}


def get_market_prices(crop):
    """Returns simulated current mandi prices for a crop across markets."""
    crop = crop.lower()
    if crop not in CROP_BASE_PRICE:
        return []

    lo, hi = CROP_BASE_PRICE[crop]
    today = datetime.now()
    results = []
    for market in MARKETS:
        price = round(random.uniform(lo, hi), 0)
        # small trend simulation
        change_pct = round(random.uniform(-4, 5), 1)
        results.append({
            "market": market,
            "crop": crop.capitalize(),
            "price_per_quintal": int(price),
            "change_pct": change_pct,
            "date": today.strftime("%d-%b-%Y")
        })
    results.sort(key=lambda x: -x["price_per_quintal"])
    return results


def get_price_trend(crop, days=7):
    """Simulated price trend over the last N days for charting."""
    crop = crop.lower()
    if crop not in CROP_BASE_PRICE:
        return []
    lo, hi = CROP_BASE_PRICE[crop]
    base = (lo + hi) / 2
    trend = []
    today = datetime.now()
    price = base
    for i in range(days, 0, -1):
        date = today - timedelta(days=i)
        price = max(lo, min(hi, price + random.uniform(-80, 80)))
        trend.append({"date": date.strftime("%d-%b"), "price": round(price)})
    return trend


def get_all_crops():
    return sorted(CROP_BASE_PRICE.keys())
