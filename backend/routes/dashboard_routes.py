"""
Dashboard Routes: Consolidates metrics, KPIs, Chart.js time-series and alert streams.
"""

from flask import Blueprint, jsonify
from sqlalchemy import func, desc, text
from backend.database import SessionLocal
from backend.models import Country, Branch, EnergyReading, EnergyAlert
from backend.services.cost_service import calculate_cost, calculate_multinational_expenditure
from backend.services.hadoop_service import get_hadoop_status
from backend.services.hive_service import get_hive_status

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("", methods=["GET"])
def get_dashboard_data():
    db = SessionLocal()
    try:
        # 1. High-level counts
        total_countries = db.query(Country).count()
        total_branches = db.query(Branch).count()
        total_readings = db.query(EnergyReading).count()

        # 2. Total global consumption & breakdown by country
        country_agg = db.query(
            Country.name.label("country"),
            Country.currency_symbol.label("symbol"),
            Country.currency_code.label("curr_code"),
            func.sum(EnergyReading.energy_kwh).label("total_kwh"),
            func.avg(EnergyReading.energy_kwh).label("avg_kwh")
        ).join(Branch, Branch.country_id == Country.id) \
         .join(EnergyReading, EnergyReading.branch_id == Branch.id) \
         .group_by(Country.name, Country.currency_symbol, Country.currency_code) \
         .order_by(desc("total_kwh")).all()

        country_consumption_map = {r.country: float(r.total_kwh or 0) for r in country_agg}
        expenditure_calc = calculate_multinational_expenditure(country_consumption_map, db_session=db)

        highest_country = country_agg[0].country if country_agg else "N/A"
        highest_country_kwh = round(float(country_agg[0].total_kwh), 2) if country_agg else 0.0

        # 3. Branch-wise consumption
        branch_agg = db.query(
            Branch.name.label("branch"),
            Branch.branch_type.label("branch_type"),
            Country.name.label("country"),
            func.sum(EnergyReading.energy_kwh).label("total_kwh"),
            func.avg(EnergyReading.energy_kwh).label("avg_kwh")
        ).join(Country, Branch.country_id == Country.id) \
         .join(EnergyReading, EnergyReading.branch_id == Branch.id) \
         .group_by(Branch.name, Branch.branch_type, Country.name) \
         .order_by(desc("total_kwh")).all()

        highest_branch = branch_agg[0].branch if branch_agg else "N/A"

        # 4. Daily consumption trend (last 30 days chronologically)
        daily_sql = text("""
            SELECT
                strftime('%Y-%m-%d', timestamp) AS r_date,
                SUM(energy_kwh) AS total_kwh,
                AVG(energy_kwh) AS avg_kwh
            FROM energy_readings
            GROUP BY strftime('%Y-%m-%d', timestamp)
            ORDER BY r_date ASC
        """)
        daily_rows = db.execute(daily_sql).fetchall()
        daily_chart = {
            "labels": [r[0] for r in daily_rows],
            "values": [round(float(r[1] or 0), 2) for r in daily_rows],
            "averages": [round(float(r[2] or 0), 2) for r in daily_rows]
        }

        # 5. Monthly consumption trend
        monthly_sql = text("""
            SELECT
                strftime('%Y-%m', timestamp) AS r_month,
                SUM(energy_kwh) AS total_kwh
            FROM energy_readings
            GROUP BY strftime('%Y-%m', timestamp)
            ORDER BY r_month ASC
        """)
        monthly_rows = db.execute(monthly_sql).fetchall()
        monthly_chart = {
            "labels": [r[0] for r in monthly_rows],
            "values": [round(float(r[1] or 0), 2) for r in monthly_rows]
        }

        # 6. Country comparison chart (Bar) & Pie chart (Distribution)
        country_chart = {
            "labels": [r.country for r in country_agg],
            "values": [round(float(r.total_kwh or 0), 2) for r in country_agg],
            "averages": [round(float(r.avg_kwh or 0), 2) for r in country_agg]
        }

        # 7. Branch comparison chart (Bar)
        branch_chart = {
            "labels": [r.branch for r in branch_agg],
            "values": [round(float(r.total_kwh or 0), 2) for r in branch_agg],
            "types": [r.branch_type for r in branch_agg]
        }

        # 8. Recent Energy Readings (Latest 10)
        recent_readings = db.query(EnergyReading) \
            .order_by(EnergyReading.timestamp.desc()) \
            .limit(10).all()

        # 9. Abnormal Consumption Alerts (Latest 8 pending alerts)
        recent_alerts = db.query(EnergyAlert) \
            .order_by(EnergyAlert.timestamp.desc()) \
            .limit(8).all()

        pending_alerts_count = db.query(EnergyAlert).filter_by(status="Pending").count()

        # 10. Engine Status
        hadoop_stat = get_hadoop_status()
        hive_stat = get_hive_status()

        return jsonify({
            "kpi": {
                "total_consumption_kwh": expenditure_calc["global_kwh_total"],
                "total_consumption_formatted": f"{expenditure_calc['global_kwh_total']:,.2f} kWh",
                "total_expenditure_usd": expenditure_calc["global_expenditure_usd"],
                "total_expenditure_formatted": expenditure_calc["global_expenditure_formatted"],
                "total_countries": total_countries,
                "total_branches": total_branches,
                "total_readings": total_readings,
                "highest_consuming_country": highest_country,
                "highest_country_kwh": highest_country_kwh,
                "highest_consuming_branch": highest_branch,
                "pending_alerts_count": pending_alerts_count
            },
            "charts": {
                "daily": daily_chart,
                "monthly": monthly_chart,
                "country": country_chart,
                "branch": branch_chart,
                "distribution_pie": country_chart
            },
            "expenditure_breakdown": expenditure_calc["country_breakdown"],
            "recent_readings": [r.to_dict() for r in recent_readings],
            "recent_alerts": [a.to_dict() for a in recent_alerts],
            "bigdata_status": {
                "hadoop": hadoop_stat,
                "hive": hive_stat
            }
        })
    finally:
        db.close()
