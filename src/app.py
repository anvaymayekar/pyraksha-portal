from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from config import get_config
from src.core.extensions import init_extensions
import os
import uuid


def create_app(config_name="default"):
    app = Flask(__name__, template_folder="web/templates", static_folder="web/static")

    app.config.from_object(get_config(config_name))

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    init_extensions(app)

    with app.app_context():
        from src.core.extensions import db
        from src.models import User, Location, SOS, Complaint

        db.create_all()

        # AUTO-CREATE ADMIN USER
        _create_default_admin()

    from src.api.auth import api_auth
    from src.api.sos import api_sos
    from src.api.complaints import api_complaints

    app.register_blueprint(api_auth)
    app.register_blueprint(api_sos)
    app.register_blueprint(api_complaints)

    from src.web.blueprints.auth import auth_bp
    from src.web.blueprints.user import user_bp
    from src.web.blueprints.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            if current_user.is_admin():
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("user.dashboard"))
        return redirect(url_for("auth.login"))

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app


def _create_default_admin():
    """
    Create default admin user if none exists.
    Credentials can be set via environment variables.
    """
    from src.models import User
    from src.core.extensions import db

    # Check if any admin exists
    admin = User.query.filter_by(role="admin").first()

    if admin:
        print("Admin user already exists")
        return

    # Get credentials from environment variables (for Railway/production)
    admin_name = os.getenv("ADMIN_NAME", "Admin")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@pyraksha.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "Admin@2024")
    admin_phone = os.getenv("ADMIN_PHONE", "+919876543210")

    # Create admin user
    admin_user = User(
        user_id=str(uuid.uuid4()),  # <-- add this
        name=admin_name,
        email=admin_email,
        phone=admin_phone,
        role="admin",
    )

    # Set password (assuming your User model has set_password method)
    admin_user.set_password(admin_password)

    try:
        db.session.add(admin_user)
        db.session.commit()

        print("Default admin user created successfully!")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        print(f"   Phone: {admin_phone}")
        print("\nIMPORTANT: Change the password after first login!")

    except Exception as e:
        db.session.rollback()
        print(f"Failed to create admin user: {e}")
