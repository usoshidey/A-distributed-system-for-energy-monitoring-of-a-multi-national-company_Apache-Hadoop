"""
Big Data & Advanced Analytics Routes:
Interfaces with Apache Hadoop MapReduce and Apache Hive analytical engines.
"""

from flask import Blueprint, jsonify, request
from backend.database import SessionLocal
from backend.models import HadoopJobLog
from backend.services.hive_service import execute_hive_analytics, get_hive_status
from backend.services.hadoop_service import run_mapreduce_job, get_hadoop_status

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@analytics_bp.route("/country", methods=["GET"])
def get_country_analytics():
    results = execute_hive_analytics("country")
    return jsonify({
        "engine": results["engine"],
        "is_live_hive": results["is_live_hive"],
        "country_wise": results["country_wise"],
        "expenditure": results["expenditure"]
    })


@analytics_bp.route("/branch", methods=["GET"])
def get_branch_analytics():
    results = execute_hive_analytics("branch")
    return jsonify({
        "engine": results["engine"],
        "is_live_hive": results["is_live_hive"],
        "branch_wise": results["branch_wise"],
        "highest_consuming_branch": results["highest_consuming_branch"]
    })


@analytics_bp.route("/monthly", methods=["GET"])
def get_monthly_analytics():
    results = execute_hive_analytics("monthly")
    return jsonify({
        "engine": results["engine"],
        "is_live_hive": results["is_live_hive"],
        "monthly_trends": results["monthly_trends"],
        "daily_trends": results["daily_trends"]
    })


@analytics_bp.route("/all", methods=["GET"])
def get_all_analytics():
    results = execute_hive_analytics("all")
    return jsonify(results)


@analytics_bp.route("/mapreduce/run", methods=["POST"])
def trigger_mapreduce():
    try:
        job_result = run_mapreduce_job()
        return jsonify({
            "success": True,
            "message": "MapReduce job executed successfully",
            "job": job_result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_bp.route("/hive/run", methods=["POST"])
def trigger_hive_query():
    try:
        results = execute_hive_analytics("all")
        return jsonify({
            "success": True,
            "message": "Hive analytics queries executed successfully",
            "results": results
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_bp.route("/jobs", methods=["GET"])
def get_job_history():
    db = SessionLocal()
    try:
        logs = db.query(HadoopJobLog).order_by(HadoopJobLog.created_at.desc()).limit(20).all()
        return jsonify({"jobs": [j.to_dict() for j in logs]})
    finally:
        db.close()

