"""
Country Routes: Country metadata, aggregated energy metrics, branch relations.
"""

from flask import Blueprint, jsonify
from sqlalchemy import func, desc
from backend.database import SessionLocal
from backend.models import Country, Branch, EnergyReading
from backend.services.cost_service import calculate_cost

country_bp = Blueprint("countries", __name__, url_prefix="/api/countries")


@country_bp.route("", methods=["GET"])
def get_countries():
    db = SessionLocal()
    try:
        countries = db.query(Country).all()
        result = []
        for c in countries:
            # Aggregate metrics for this country
            stats = db.query(
                func.count(EnergyReading.id).label("readings"),
                func.sum(EnergyReading.energy_kwh).label("total_kwh"),
                func.avg(EnergyReading.energy_kwh).label("avg_kwh")
            ).join(Branch, EnergyReading.branch_id == Branch.id) \
             .filter(Branch.country_id == c.id).first()

            total_kwh = float(stats.total_kwh or 0.0)
            avg_kwh = float(stats.avg_kwh or 0.0)
            cost_info = calculate_cost(c.name, total_kwh, db_session=db)

            c_dict = c.to_dict()
            branches_list = [b.to_dict() for b in c.branches] if c.branches else []
            c_dict.update({
                "total_readings": stats.readings or 0,
                "total_kwh": round(total_kwh, 2),
                "avg_kwh": round(avg_kwh, 2),
                "local_expenditure": cost_info["local_cost"],
                "local_expenditure_formatted": cost_info["local_cost_formatted"],
                "usd_equivalent": cost_info["usd_equivalent"],
                "usd_formatted": cost_info["usd_formatted"],
                "branches": branches_list
            })
            result.append(c_dict)

        return jsonify({"countries": result})
    finally:
        db.close()


@country_bp.route("/<int:country_id>", methods=["GET"])
def get_country_detail(country_id):
    db = SessionLocal()
    try:
        c = db.query(Country).filter_by(id=country_id).first()
        if not c:
            return jsonify({"error": "Country not found"}), 404

        stats = db.query(
            func.count(EnergyReading.id).label("readings"),
            func.sum(EnergyReading.energy_kwh).label("total_kwh"),
            func.avg(EnergyReading.energy_kwh).label("avg_kwh")
        ).join(Branch, EnergyReading.branch_id == Branch.id) \
         .filter(Branch.country_id == c.id).first()

        total_kwh = float(stats.total_kwh or 0.0)
        cost_info = calculate_cost(c.name, total_kwh, db_session=db)

        c_dict = c.to_dict()
        branches_list = [b.to_dict() for b in c.branches] if c.branches else []
        c_dict.update({
            "total_readings": stats.readings or 0,
            "total_kwh": round(total_kwh, 2),
            "avg_kwh": round(float(stats.avg_kwh or 0.0), 2),
            "local_expenditure": cost_info["local_cost"],
            "local_expenditure_formatted": cost_info["local_cost_formatted"],
            "usd_equivalent": cost_info["usd_equivalent"],
            "branches": branches_list
        })
        return jsonify({"country": c_dict})
    finally:
        db.close()
