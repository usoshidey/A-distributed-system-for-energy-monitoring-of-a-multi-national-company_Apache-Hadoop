"""
Report Generation and Export Service.
Generates tabular data, CSV streams/files, and summary analytics for specified filters.
"""

import os
import io
import csv
from datetime import datetime
from sqlalchemy import func, and_
from backend.database import SessionLocal
from backend.models import Country, Branch, EnergyReading, ElectricityTariff

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")


def generate_consumption_report(country=None, branch_name=None, start_date=None, end_date=None, limit=1000):
    """
    Query energy readings matching filters and return summary + tabular records.
    """
    db = SessionLocal()
    os.makedirs(REPORTS_DIR, exist_ok=True)

    try:
        query = db.query(EnergyReading).join(Branch, EnergyReading.branch_id == Branch.id) \
                                      .join(Country, Branch.country_id == Country.id)

        filters = []
        if country and country != "All":
            filters.append(Country.name == country)
        if branch_name and branch_name != "All":
            filters.append(Branch.name == branch_name)
        if start_date:
            try:
                s_dt = datetime.strptime(start_date, "%Y-%m-%d")
                filters.append(EnergyReading.timestamp >= s_dt)
            except ValueError:
                pass
        if end_date:
            try:
                e_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
                filters.append(EnergyReading.timestamp <= e_dt)
            except ValueError:
                pass

        if filters:
            query = query.filter(and_(*filters))

        total_matching = query.count()
        readings = query.order_by(EnergyReading.timestamp.desc()).limit(limit).all()

        # Aggregations
        kwh_list = [r.energy_kwh for r in readings]
        total_kwh = sum(kwh_list) if kwh_list else 0.0
        avg_kwh = total_kwh / len(kwh_list) if kwh_list else 0.0
        max_kwh = max(kwh_list) if kwh_list else 0.0
        min_kwh = min(kwh_list) if kwh_list else 0.0

        rows = []
        for r in readings:
            rows.append({
                "reading_id": r.reading_id,
                "meter_code": r.meter_rel.meter_code if r.meter_rel else "",
                "branch_name": r.branch_rel.name if r.branch_rel else "",
                "country": r.branch_rel.country_rel.name if r.branch_rel and r.branch_rel.country_rel else "",
                "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "energy_kwh": round(r.energy_kwh, 2),
                "voltage": round(r.voltage, 2),
                "current": round(r.current, 2),
                "power_factor": round(r.power_factor, 2)
            })

        summary = {
            "filters": {
                "country": country or "All",
                "branch": branch_name or "All",
                "start_date": start_date or "Earliest",
                "end_date": end_date or "Latest"
            },
            "total_records_matched": total_matching,
            "records_returned": len(rows),
            "total_consumption_kwh": round(total_kwh, 2),
            "average_consumption_kwh": round(avg_kwh, 2),
            "max_consumption_kwh": round(max_kwh, 2),
            "min_consumption_kwh": round(min_kwh, 2),
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }

        return {"summary": summary, "data": rows}
    finally:
        db.close()


def export_report_csv(country=None, branch_name=None, start_date=None, end_date=None):
    """
    Generate CSV string buffer ready for streaming or saving.
    """
    result = generate_consumption_report(country, branch_name, start_date, end_date, limit=15000)
    data = result["data"]

    output = io.StringIO()
    fieldnames = [
        "reading_id",
        "meter_code",
        "branch_name",
        "country",
        "timestamp",
        "energy_kwh",
        "voltage",
        "current",
        "power_factor"
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

    csv_content = output.getvalue()
    output.close()
    return csv_content

