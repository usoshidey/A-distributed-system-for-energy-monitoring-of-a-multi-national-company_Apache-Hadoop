"""
Energy Reading Routes: Query historical readings and ingest live meter data with automated anomaly check.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy import desc
from backend.database import SessionLocal
from backend.models import Branch, Country, EnergyMeter, EnergyReading
from backend.services.anomaly_service import evaluate_reading_for_anomaly, get_branch_averages

energy_bp = Blueprint("energy", __name__, url_prefix="/api/energy")


@energy_bp.route("/readings", methods=["GET"])
def get_readings():
    country = request.args.get("country")
    branch_name = request.args.get("branch")
    limit = min(int(request.args.get("limit", 50)), 500)
    offset = int(request.args.get("offset", 0))

    db = SessionLocal()
    try:
        query = db.query(EnergyReading).join(Branch, EnergyReading.branch_id == Branch.id) \
                                      .join(Country, Branch.country_id == Country.id)

        if country and country != "All":
            query = query.filter(Country.name == country)
        if branch_name and branch_name != "All":
            query = query.filter(Branch.name == branch_name)

        total_count = query.count()
        readings = query.order_by(desc(EnergyReading.timestamp)) \
                        .offset(offset).limit(limit).all()

        return jsonify({
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "readings": [r.to_dict() for r in readings]
        })
    finally:
        db.close()


@energy_bp.route("/readings", methods=["POST"])
def add_reading():
    data = request.get_json(silent=True) or {}
    
    branch_name = data.get("branch_name", "").strip()
    meter_code = data.get("meter_code", "").strip()
    timestamp_str = data.get("timestamp")
    energy_kwh = data.get("energy_kwh")
    voltage = data.get("voltage", 230.0)
    current = data.get("current")
    power_factor = data.get("power_factor", 0.92)

    # Validation
    if not branch_name or not meter_code or energy_kwh is None:
        return jsonify({"error": "branch_name, meter_code, and energy_kwh are required"}), 400

    try:
        energy_kwh = float(energy_kwh)
        voltage = float(voltage)
        power_factor = float(power_factor)
        if current is not None:
            current = float(current)
        else:
            # Auto compute current if omitted
            current = round((energy_kwh * 1000.0) / (voltage * power_factor), 2)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid numerical values provided"}), 400

    ts = datetime.utcnow()
    if timestamp_str:
        try:
            ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
            except ValueError:
                ts = datetime.utcnow()

    db = SessionLocal()
    try:
        branch = db.query(Branch).filter_by(name=branch_name).first()
        if not branch:
            return jsonify({"error": f"Branch '{branch_name}' not found"}), 404

        meter = db.query(EnergyMeter).filter_by(meter_code=meter_code).first()
        if not meter:
            # Create meter under this branch if it's new
            meter = EnergyMeter(meter_code=meter_code, branch_id=branch.id)
            db.add(meter)
            db.flush()

        reading_id = f"R-LIVE-{int(datetime.utcnow().timestamp()*1000)}"

        reading = EnergyReading(
            reading_id=reading_id,
            meter_id=meter.id,
            branch_id=branch.id,
            timestamp=ts,
            energy_kwh=energy_kwh,
            voltage=voltage,
            current=current,
            power_factor=power_factor
        )
        db.add(reading)
        db.commit()

        # Check for anomaly against branch average
        branch_baselines = get_branch_averages(db)
        b_avg = branch_baselines.get(branch.id, {}).get("avg_kwh", 200.0)

        alert_created = None
        alert_obj = evaluate_reading_for_anomaly(reading, b_avg, db)
        if alert_obj:
            alert_created = alert_obj.to_dict()

        return jsonify({
            "success": True,
            "message": "Energy reading successfully recorded and analyzed",
            "reading": reading.to_dict(),
            "anomaly_detected": alert_created is not None,
            "alert": alert_created
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

