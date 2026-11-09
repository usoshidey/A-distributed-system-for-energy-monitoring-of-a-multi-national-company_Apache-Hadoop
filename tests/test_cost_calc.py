"""
Test Multi-Currency Tariff and Cost Calculation Logic.
"""

from backend.services.cost_service import calculate_cost, calculate_multinational_expenditure, get_active_tariffs


def test_tariff_retrieval():
    tariffs = get_active_tariffs()
    assert "India" in tariffs
    assert tariffs["India"]["rate"] == 8.00
    assert tariffs["India"]["currency"] == "INR"

    assert "USA" in tariffs
    assert tariffs["USA"]["rate"] == 0.15
    assert tariffs["USA"]["currency"] == "USD"

    assert "Germany" in tariffs
    assert tariffs["Germany"]["rate"] == 0.30
    assert tariffs["Germany"]["currency"] == "EUR"

    assert "Japan" in tariffs
    assert tariffs["Japan"]["rate"] == 30.00
    assert tariffs["Japan"]["currency"] == "JPY"


def test_single_country_cost_calc():
    # 1000 kWh in India at 8 INR = 8,000 INR
    res_in = calculate_cost("India", 1000.0)
    assert res_in["local_cost"] == 8000.0
    assert "₹" in res_in["local_cost_formatted"]

    # 1000 kWh in USA at 0.15 USD = 150 USD
    res_us = calculate_cost("USA", 1000.0)
    assert res_us["local_cost"] == 150.0
    assert "$" in res_us["local_cost_formatted"]


def test_multinational_consolidated_expenditure():
    sample_consumption = {
        "India": 10000.0,
        "USA": 15000.0,
        "Germany": 8000.0,
        "Japan": 12000.0
    }
    exp = calculate_multinational_expenditure(sample_consumption)
    assert exp["global_kwh_total"] == 45000.0
    assert exp["global_expenditure_usd"] > 0
    assert len(exp["country_breakdown"]) == 4

