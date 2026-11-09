"""
Routes Package Initialization.
Registers all blueprints for the energy monitoring API.
"""

from backend.routes.auth_routes import auth_bp
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.country_routes import country_bp
from backend.routes.branch_routes import branch_bp
from backend.routes.energy_routes import energy_bp
from backend.routes.analytics_routes import analytics_bp
from backend.routes.alert_routes import alert_bp
from backend.routes.report_routes import report_bp
from backend.routes.settings_routes import settings_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(country_bp)
    app.register_blueprint(branch_bp)
    app.register_blueprint(energy_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(alert_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(settings_bp)

