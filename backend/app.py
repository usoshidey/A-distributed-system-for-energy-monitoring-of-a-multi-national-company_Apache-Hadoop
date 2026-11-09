"""
Flask Backend Application Entrypoint.
Distributed Energy Monitoring System for a Multinational Company Using Apache Hadoop.
"""

import os
import sys

# Ensure root directory is on Python path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from backend.routes import register_blueprints
from backend.database import engine, Base
from backend.init_db import init_database

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

def create_app():
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "supersecret-distributed-energy-key-2026")

    # Enable CORS for all API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Register API Blueprints
    register_blueprints(app)

    # Auto-initialize database schema if database file does not exist
    db_file = os.path.join(BASE_DIR, "energy_monitoring.db")
    if not os.path.exists(db_file):
        print(f"Database file not detected at {db_file}. Initializing database...")
        init_database(load_readings=True)

    # -------------------------------------------------------------------------
    # Frontend Page Serving Routes
    # -------------------------------------------------------------------------
    @app.route("/")
    def index_page():
        return send_from_directory(FRONTEND_DIR, "dashboard.html")

    @app.route("/login")
    def login_page():
        return send_from_directory(FRONTEND_DIR, "login.html")

    @app.route("/dashboard")
    def dashboard_page():
        return send_from_directory(FRONTEND_DIR, "dashboard.html")

    @app.route("/countries")
    def countries_page():
        return send_from_directory(FRONTEND_DIR, "countries.html")

    @app.route("/branches")
    def branches_page():
        return send_from_directory(FRONTEND_DIR, "branches.html")

    @app.route("/energy-monitoring")
    def energy_monitoring_page():
        return send_from_directory(FRONTEND_DIR, "energy-monitoring.html")

    @app.route("/analytics")
    def analytics_page():
        return send_from_directory(FRONTEND_DIR, "analytics.html")

    @app.route("/alerts")
    def alerts_page():
        return send_from_directory(FRONTEND_DIR, "alerts.html")

    @app.route("/reports")
    def reports_page():
        return send_from_directory(FRONTEND_DIR, "reports.html")

    @app.route("/settings")
    def settings_page():
        return send_from_directory(FRONTEND_DIR, "settings.html")

    # Serve static frontend files (CSS, JS, images)
    @app.route("/<path:path>")
    def static_proxy(path):
        return send_from_directory(FRONTEND_DIR, path)

    # Health check
    @app.route("/api/health")
    def health_check():
        return jsonify({
            "status": "healthy",
            "system": "Distributed Energy Monitoring System",
            "version": "2.0.0"
        })

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource or endpoint not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error occurred", "details": str(e)}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Distributed Energy Monitoring System on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)

