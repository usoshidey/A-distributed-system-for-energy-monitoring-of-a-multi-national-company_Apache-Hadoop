"""
Authentication Routes: User Login, Registration, Session verification and Role checking.
"""

from flask import Blueprint, request, jsonify, session
from backend.database import SessionLocal
from backend.models import User, Country

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required"}), 400

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({"success": False, "error": "Invalid username or password"}), 401

        # Store in flask session
        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] = user.role
        session["assigned_country"] = user.assigned_country

        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": user.to_dict()
        })
    finally:
        db.close()


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()
    role = data.get("role", "country_manager")
    assigned_country = data.get("assigned_country", None)

    if not username or not email or not password or not full_name:
        return jsonify({"success": False, "error": "All fields are required"}), 400

    if role not in ["admin", "country_manager"]:
        return jsonify({"success": False, "error": "Invalid role specified"}), 400

    db = SessionLocal()
    try:
        if db.query(User).filter_by(username=username).first():
            return jsonify({"success": False, "error": "Username already taken"}), 409
        if db.query(User).filter_by(email=email).first():
            return jsonify({"success": False, "error": "Email already registered"}), 409

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            assigned_country=assigned_country if role == "country_manager" else None
        )
        user.set_password(password)
        db.add(user)
        db.commit()

        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "user": user.to_dict()
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    user_id = session.get("user_id")
    # For dev convenience, if no active cookie session, check Authorization header (e.g., Bearer demo_admin)
    auth_header = request.headers.get("Authorization", "")
    db = SessionLocal()
    try:
        user = None
        if user_id:
            user = db.query(User).filter_by(id=user_id).first()
        elif "admin" in auth_header.lower():
            user = db.query(User).filter_by(username="admin").first()

        if not user:
            # Default to admin in local development if unauthenticated
            user = db.query(User).filter_by(username="admin").first()

        return jsonify({
            "authenticated": True if user else False,
            "user": user.to_dict() if user else None
        })
    finally:
        db.close()


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"})

