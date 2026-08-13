"""
Crop Profit Calculator module.
Simple financial estimate: (expected yield x market price) - total investment
"""

# Typical yield per acre (quintals) - representative averages for demo
TYPICAL_YIELD_PER_ACRE = {
    "rice": 22, "maize": 20, "cotton": 8, "chilli": 10, "turmeric": 18,
    "soybean": 10, "groundnut": 8, "wheat": 15, "sugarcane": 350,
    "pigeonpeas": 6, "chickpea": 8, "blackgram": 5, "mungbean": 5,
    "jute": 12, "coffee": 4, "banana": 150, "mango": 60, "papaya": 200,
    "coconut": 80, "grapes": 90, "pomegranate": 50, "orange": 60,
    "apple": 70, "watermelon": 120, "muskmelon": 100, "lentil": 6,
    "mothbeans": 4, "kidneybeans": 6,
}


def calculate_profit(crop, land_acres, investment_per_acre, market_price_per_quintal, custom_yield=None):
    crop = crop.lower()
    yield_per_acre = custom_yield if custom_yield else TYPICAL_YIELD_PER_ACRE.get(crop, 10)

    total_yield_quintals = yield_per_acre * land_acres
    total_investment = investment_per_acre * land_acres
    total_revenue = total_yield_quintals * market_price_per_quintal
    net_profit = total_revenue - total_investment
    roi_pct = (net_profit / total_investment * 100) if total_investment > 0 else 0

    return {
        "crop": crop.capitalize(),
        "land_acres": land_acres,
        "yield_per_acre_quintals": yield_per_acre,
        "total_yield_quintals": round(total_yield_quintals, 1),
        "total_investment": round(total_investment),
        "total_revenue": round(total_revenue),
        "net_profit": round(net_profit),
        "roi_pct": round(roi_pct, 1),
        "is_profitable": net_profit > 0
    }
