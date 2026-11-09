"""
Reporting Routes: Query custom energy consumption reports and stream CSV file exports.
"""

from flask import Blueprint, request, jsonify, Response
from backend.services.report_service import generate_consumption_report, export_report_csv

report_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@report_bp.route("", methods=["GET"])
def get_report():
    country = request.args.get("country")
    branch_name = request.args.get("branch")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    limit = min(int(request.args.get("limit", 200)), 2000)

    try:
        report = generate_consumption_report(country, branch_name, start_date, end_date, limit=limit)
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@report_bp.route("/export", methods=["GET"])
def export_csv():
    country = request.args.get("country")
    branch_name = request.args.get("branch")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    try:
        csv_data = export_report_csv(country, branch_name, start_date, end_date)
        filename = f"energy_consumption_report_{country or 'global'}.csv"
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@report_bp.route("/summary", methods=["GET"])
def get_summary_report():
    country = request.args.get("country")
    branch_name = request.args.get("branch")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    try:
        report = generate_consumption_report(country, branch_name, start_date, end_date, limit=1)
        return jsonify({"summary": report["summary"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

