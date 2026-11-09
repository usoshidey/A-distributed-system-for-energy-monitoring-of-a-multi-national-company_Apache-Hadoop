"""
Branch Routes: Branch-level details, smart meter registries, and baseline consumption statistics.
"""

from flask import Blueprint, jsonify
from sqlalchemy import func
from backend.database import SessionLocal
from backend.models import Branch, Country, EnergyMeter, EnergyReading

branch_bp = Blueprint("branches", __name__, url_prefix="/api/branches")


@branch_bp.route("", methods=["GET"])
def get_branches():
    db = SessionLocal()
    try:
        branches = db.query(Branch).all()
        result = []
        for b in branches:
            stats = db.query(
                func.count(EnergyReading.id).label("readings"),
                func.sum(EnergyReading.energy_kwh).label("total_kwh"),
                func.avg(EnergyReading.energy_kwh).label("avg_kwh"),
                func.max(EnergyReading.energy_kwh).label("peak_kwh")
            ).filter(EnergyReading.branch_id == b.id).first()

            meters = db.query(EnergyMeter).filter_by(branch_id=b.id).all()

            b_dict = b.to_dict()
            b_dict.update({
                "readings_count": stats.readings or 0,
                "total_kwh": round(float(stats.total_kwh or 0), 2),
                "avg_kwh": round(float(stats.avg_kwh or 0), 2),
                "peak_kwh": round(float(stats.peak_kwh or 0), 2),
                "meters": [m.to_dict() for m in meters]
            })
            result.append(b_dict)

        return jsonify({"branches": result})
    finally:
        db.close()


@branch_bp.route("/<int:branch_id>", methods=["GET"])
def get_branch_detail(branch_id):
    db = SessionLocal()
    try:
        b = db.query(Branch).filter_by(id=branch_id).first()
        if not b:
            return jsonify({"error": "Branch not found"}), 404

        stats = db.query(
            func.count(EnergyReading.id).label("readings"),
            func.sum(EnergyReading.energy_kwh).label("total_kwh"),
            func.avg(EnergyReading.energy_kwh).label("avg_kwh"),
            func.max(EnergyReading.energy_kwh).label("peak_kwh"),
            func.avg(EnergyReading.voltage).label("avg_voltage"),
            func.avg(EnergyReading.power_factor).label("avg_pf")
        ).filter(EnergyReading.branch_id == b.id).first()

        meters = db.query(EnergyMeter).filter_by(branch_id=b.id).all()
        recent_readings = db.query(EnergyReading).filter_by(branch_id=b.id) \
                            .order_by(EnergyReading.timestamp.desc()).limit(15).all()

        b_dict = b.to_dict()
        b_dict.update({
            "readings_count": stats.readings or 0,
            "total_kwh": round(float(stats.total_kwh or 0), 2),
            "avg_kwh": round(float(stats.avg_kwh or 0), 2),
            "peak_kwh": round(float(stats.peak_kwh or 0), 2),
            "avg_voltage": round(float(stats.avg_voltage or 0), 1),
            "avg_power_factor": round(float(stats.avg_pf or 0), 2),
            "meters": [m.to_dict() for m in meters],
            "recent_readings": [r.to_dict() for r in recent_readings]
        })

        return jsonify({"branch": b_dict})
    finally:
        db.close()

