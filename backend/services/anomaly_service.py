"""
Abnormal Energy Consumption Anomaly Detection Service.
Detects surges and spikes exceeding 1.5x of a branch's historical average consumption.
"""

from datetime import datetime
from sqlalchemy import func
from backend.database import SessionLocal
from backend.models import Branch, EnergyReading, EnergyAlert


def get_branch_averages(db_session=None):
    """Calculate baseline average consumption (kWh) for every branch."""
    close_at_end = False
    if db_session is None:
        db_session = SessionLocal()
        close_at_end = True

    try:
        results = db_session.query(
            Branch.id,
            Branch.name,
            func.avg(EnergyReading.energy_kwh).label("avg_kwh")
        ).join(EnergyReading, EnergyReading.branch_id == Branch.id) \
         .group_by(Branch.id, Branch.name).all()

        averages = {row.id: {"name": row.name, "avg_kwh": float(row.avg_kwh or 0.0)} for row in results}
        return averages
    finally:
        if close_at_end:
            db_session.close()


def evaluate_reading_for_anomaly(reading_obj, branch_avg, db_session=None):
    """
    Evaluates an EnergyReading object against the 1.5x branch average threshold.
    Creates and saves EnergyAlert if threshold exceeded.
    """
    if not branch_avg or branch_avg <= 0:
        return None

    threshold = 1.5 * branch_avg
    kwh = reading_obj.energy_kwh

    if kwh > threshold:
        ratio = kwh / branch_avg
        if ratio >= 2.0:
            severity = "Critical"
        elif ratio >= 1.75:
            severity = "High"
        else:
            severity = "Warning"

        close_at_end = False
        if db_session is None:
            db_session = SessionLocal()
            close_at_end = True

        try:
            alert = EnergyAlert(
                reading_id=reading_obj.reading_id,
                branch_id=reading_obj.branch_id,
                country_name=reading_obj.branch_rel.country_rel.name if reading_obj.branch_rel and reading_obj.branch_rel.country_rel else "Global",
                current_kwh=kwh,
                average_kwh=branch_avg,
                ratio=ratio,
                severity=severity,
                status="Pending",
                timestamp=reading_obj.timestamp
            )
            db_session.add(alert)
            db_session.commit()
            return alert
        finally:
            if close_at_end:
                db_session.close()

    return None


def acknowledge_alert(alert_id, acknowledged_by_username):
    """Acknowledge an anomaly alert."""
    db = SessionLocal()
    try:
        alert = db.query(EnergyAlert).filter_by(id=alert_id).first()
        if not alert:
            return None, "Alert not found"

        alert.status = "Acknowledged"
        alert.acknowledged_by = acknowledged_by_username
        alert.acknowledged_at = datetime.utcnow()
        db.commit()
        return alert.to_dict(), None
    except Exception as e:
        db.rollback()
        return None, str(e)
    finally:
        db.close()


def scan_all_readings_for_anomalies():
    """Batch scan historical readings against branch baselines."""
    db = SessionLocal()
    try:
        branch_avgs = get_branch_averages(db)
        readings = db.query(EnergyReading).all()
        created_count = 0

        existing_alert_reading_ids = set(
            row[0] for row in db.query(EnergyAlert.reading_id).filter(EnergyAlert.reading_id.isnot(None)).all()
        )

        new_alerts = []
        for r in readings:
            if r.reading_id in existing_alert_reading_ids:
                continue

            b_info = branch_avgs.get(r.branch_id)
            if not b_info or b_info["avg_kwh"] <= 0:
                continue

            avg_kwh = b_info["avg_kwh"]
            if r.energy_kwh > 1.5 * avg_kwh:
                ratio = r.energy_kwh / avg_kwh
                severity = "Critical" if ratio >= 2.0 else ("High" if ratio >= 1.75 else "Warning")
                alert = EnergyAlert(
                    reading_id=r.reading_id,
                    branch_id=r.branch_id,
                    country_name=r.branch_rel.country_rel.name if r.branch_rel and r.branch_rel.country_rel else "Global",
                    current_kwh=r.energy_kwh,
                    average_kwh=avg_kwh,
                    ratio=ratio,
                    severity=severity,
                    status="Pending",
                    timestamp=r.timestamp
                )
                new_alerts.append(alert)
                existing_alert_reading_ids.add(r.reading_id)
                created_count += 1

        if new_alerts:
            db.bulk_save_objects(new_alerts)
            db.commit()

        return {"scanned_readings": len(readings), "new_alerts_created": created_count}
    finally:
        db.close()

