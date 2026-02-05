from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from src.services.auth_service import AuthService
from src.core.constants import UserRole

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("user.dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = request.form.get("remember", False)

        success, message, user = AuthService.login_user_service(
            email, password, remember
        )

        if success and user:
            flash(message, "success")
            if user.is_admin():
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("user.dashboard"))
        else:
            flash(message, "danger")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("user.dashboard"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template("auth/register.html")

        success, message, user = AuthService.register_user(name, email, phone, password)

        if success:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash(message, "danger")

    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    AuthService.logout_user_service()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
