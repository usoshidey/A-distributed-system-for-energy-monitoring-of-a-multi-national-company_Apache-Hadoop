"""
Energy Alert Routes: Anomaly monitoring, filtering, and acknowledgment.
"""

from flask import Blueprint, request, jsonify, session
from backend.database import SessionLocal
from backend.models import EnergyAlert
from backend.services.anomaly_service import acknowledge_alert, scan_all_readings_for_anomalies

alert_bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")


@alert_bp.route("", methods=["GET"])
def get_alerts():
    status = request.args.get("status")  # 'Pending', 'Acknowledged', or None (all)
    severity = request.args.get("severity")  # 'Critical', 'High', 'Warning'
    country = request.args.get("country")
    limit = min(int(request.args.get("limit", 100)), 500)

    db = SessionLocal()
    try:
        query = db.query(EnergyAlert)
        if status and status != "All":
            query = query.filter_by(status=status)
        if severity and severity != "All":
            query = query.filter_by(severity=severity)
        if country and country != "All":
            query = query.filter_by(country_name=country)

        total = query.count()
        alerts = query.order_by(EnergyAlert.timestamp.desc()).limit(limit).all()

        pending_count = db.query(EnergyAlert).filter_by(status="Pending").count()
        acknowledged_count = db.query(EnergyAlert).filter_by(status="Acknowledged").count()

        return jsonify({
            "total": total,
            "pending_count": pending_count,
            "acknowledged_count": acknowledged_count,
            "alerts": [a.to_dict() for a in alerts]
        })
    finally:
        db.close()


@alert_bp.route("/acknowledge", methods=["POST"])
def acknowledge():
    data = request.get_json(silent=True) or {}
    alert_id = data.get("alert_id")
    if not alert_id:
        return jsonify({"error": "alert_id is required"}), 400

    username = session.get("username") or data.get("acknowledged_by") or "System Administrator"

    updated_alert, error = acknowledge_alert(alert_id, username)
    if error:
        return jsonify({"error": error}), 404

    return jsonify({
        "success": True,
        "message": f"Alert #{alert_id} successfully acknowledged by {username}",
        "alert": updated_alert
    })


@alert_bp.route("/scan", methods=["POST"])
def trigger_anomaly_scan():
    try:
        result = scan_all_readings_for_anomalies()
        return jsonify({
            "success": True,
            "message": "Anomaly detection batch scan completed",
            "result": result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

