"""
Settings Routes: Tariff management and Big Data cluster diagnostics.
"""

from flask import Blueprint, request, jsonify
from backend.database import SessionLocal
from backend.models import Country, ElectricityTariff
from backend.services.hadoop_service import get_hadoop_status
from backend.services.hive_service import get_hive_status

settings_bp = Blueprint("settings", __name__, url_prefix="/api/settings")


@settings_bp.route("/tariffs", methods=["GET"])
def get_tariffs():
    db = SessionLocal()
    try:
        tariffs = db.query(ElectricityTariff).filter_by(is_active=True).all()
        return jsonify({
            "tariffs": [t.to_dict() for t in tariffs],
            "disclaimer": "All tariff configurations represent sample illustrative rates for academic demonstration."
        })
    finally:
        db.close()


@settings_bp.route("/tariffs", methods=["POST", "PUT"])
def update_tariff():
    data = request.get_json(silent=True) or {}
    country_name = data.get("country_name")
    new_rate = data.get("tariff_rate")

    if not country_name or new_rate is None:
        return jsonify({"error": "country_name and tariff_rate are required"}), 400

    try:
        new_rate = float(new_rate)
        if new_rate < 0:
            return jsonify({"error": "Tariff rate cannot be negative"}), 400
    except ValueError:
        return jsonify({"error": "Invalid tariff rate"}), 400

    db = SessionLocal()
    try:
        country = db.query(Country).filter_by(name=country_name).first()
        if not country:
            return jsonify({"error": f"Country '{country_name}' not found"}), 404

        # Update active tariff
        tariff = db.query(ElectricityTariff).filter_by(country_id=country.id, is_active=True).first()
        if tariff:
            tariff.tariff_rate = new_rate
        else:
            tariff = ElectricityTariff(
                country_id=country.id,
                tariff_rate=new_rate,
                currency_code=country.currency_code,
                currency_symbol=country.currency_symbol,
                is_active=True
            )
            db.add(tariff)
        db.commit()

        return jsonify({
            "success": True,
            "message": f"Tariff for {country_name} updated to {country.currency_symbol} {new_rate} / kWh",
            "tariff": tariff.to_dict()
        })
    finally:
        db.close()


@settings_bp.route("/hadoop-status", methods=["GET"])
def get_cluster_status():
    hadoop_status = get_hadoop_status()
    hive_status = get_hive_status()
    return jsonify({
        "hadoop": hadoop_status,
        "hive": hive_status,
        "cluster_mode": "Pseudo-distributed / Containerized / Local Fallback",
        "supported_nodes": [
            {"node": "Namenode", "port": 9870, "protocol": "HDFS IPC / WebHDFS"},
            {"node": "ResourceManager", "port": 8088, "protocol": "YARN Web UI"},
            {"node": "Datanode", "port": 9864, "protocol": "HDFS Block Storage"},
            {"node": "HiveServer2", "port": 10000, "protocol": "JDBC / Thrift"}
        ]
    })

