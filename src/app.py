from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from config import get_config
from src.core.extensions import init_extensions
import os


def create_app(config_name="default"):
    app = Flask(__name__, template_folder="web/templates", static_folder="web/static")

    app.config.from_object(get_config(config_name))

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    init_extensions(app)

    with app.app_context():
        from src.core.extensions import db
        from src.models import User, Location, SOS, Complaint

        db.create_all()

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
