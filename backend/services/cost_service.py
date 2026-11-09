"""
Energy Cost and Tariff Calculation Service.
Calculates country-level and global consolidated electricity expenditure based on
country-specific tariffs and currency exchange normalization.
"""

from backend.database import SessionLocal
from backend.models import Country, ElectricityTariff

# Illustrative base tariffs if database records are unavailable
DEFAULT_TARIFFS = {
    "India": {"rate": 8.00, "currency": "INR", "symbol": "₹", "usd_rate": 0.012},
    "USA": {"rate": 0.15, "currency": "USD", "symbol": "$", "usd_rate": 1.0},
    "Germany": {"rate": 0.30, "currency": "EUR", "symbol": "€", "usd_rate": 1.08},
    "Japan": {"rate": 30.00, "currency": "JPY", "symbol": "¥", "usd_rate": 0.0067}
}


def get_active_tariffs(db_session=None):
    """Fetch active tariffs for all countries from database."""
    close_at_end = False
    if db_session is None:
        db_session = SessionLocal()
        close_at_end = True

    tariffs = {}
    try:
        countries = db_session.query(Country).all()
        for c in countries:
            active_t = next((t for t in c.tariffs if t.is_active), None) if c.tariffs else None
            rate = active_t.tariff_rate if active_t else DEFAULT_TARIFFS.get(c.name, {}).get("rate", 0.20)
            tariffs[c.name] = {
                "country_id": c.id,
                "country_name": c.name,
                "rate": rate,
                "currency": c.currency_code,
                "symbol": c.currency_symbol,
                "usd_rate": c.usd_exchange_rate,
                "note": "Illustrative sample tariff for academic benchmarking"
            }
        return tariffs
    finally:
        if close_at_end:
            db_session.close()


def calculate_cost(country_name, energy_kwh, db_session=None):
    """
    Calculate expenditure for a given country and consumption.
    Returns local cost and normalized USD cost.
    """
    tariffs = get_active_tariffs(db_session=db_session)
    info = tariffs.get(country_name, DEFAULT_TARIFFS.get(country_name, {
        "rate": 0.20, "currency": "USD", "symbol": "$", "usd_rate": 1.0
    }))

    local_cost = round(energy_kwh * info["rate"], 2)
    usd_cost = round(local_cost * info.get("usd_rate", 1.0), 2)

    return {
        "country": country_name,
        "energy_kwh": round(energy_kwh, 2),
        "tariff_rate": info["rate"],
        "currency_code": info["currency"],
        "currency_symbol": info["symbol"],
        "local_cost": local_cost,
        "local_cost_formatted": f"{info['symbol']} {local_cost:,.2f}",
        "usd_equivalent": usd_cost,
        "usd_formatted": f"$ {usd_cost:,.2f}",
        "is_illustrative": True
    }


def calculate_multinational_expenditure(country_consumption_map, db_session=None):
    """
    Given a dict of {country_name: total_kwh}, calculates per-country expenditure
    and global combined USD total.
    """
    tariffs = get_active_tariffs(db_session=db_session)
    country_breakdown = []
    global_usd_total = 0.0
    global_kwh_total = 0.0

    for country, kwh in country_consumption_map.items():
        cost_info = calculate_cost(country, kwh)
        country_breakdown.append(cost_info)
        global_usd_total += cost_info["usd_equivalent"]
        global_kwh_total += kwh

    return {
        "global_kwh_total": round(global_kwh_total, 2),
        "global_expenditure_usd": round(global_usd_total, 2),
        "global_expenditure_formatted": f"$ {global_usd_total:,.2f}",
        "country_breakdown": country_breakdown,
        "tariff_notice": "Notice: Electricity tariffs are illustrative and represent national industrial averages."
    }
