from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from datetime import datetime
from flask_login import login_required, current_user
from src.services.complaint_service import ComplaintService
from src.services.sos_service import SOSService
from src.services.analytics_service import AnalyticsService
from src.services.location_service import LocationService
from src.models.user import User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.before_request
@login_required
def require_admin():
    if not current_user.is_admin():
        flash("Admin access required", "danger")
        return redirect(url_for("user.dashboard"))


@admin_bp.route("/dashboard")
def dashboard():
    metrics = AnalyticsService.get_dashboard_metrics()
    active_sos = SOSService.get_active_sos_events()
    recent_complaints = ComplaintService.get_all_complaints(limit=5)
    recent_activities = AnalyticsService.get_recent_activities(limit=10)

    return render_template(
        "admin/dashboard.html",
        metrics=metrics,
        active_sos=active_sos,
        recent_complaints=recent_complaints,
        recent_activities=recent_activities,
    )


@admin_bp.route("/sos")
def sos_list():
    status_filter = request.args.get("status")
    sos_events = SOSService.get_all_sos_events(status_filter, limit=100)

    return render_template("admin/sos_list.html", sos_events=sos_events)


@admin_bp.route("/sos/<sos_id>")
def sos_detail(sos_id):
    sos = SOSService.get_sos_by_id(sos_id)
    if not sos:
        flash("SOS not found", "danger")
        return redirect(url_for("admin.sos_list"))

    return render_template("admin/sos_detail.html", sos=sos)


@admin_bp.route("/sos/<sos_id>/resolve", methods=["POST"])
def resolve_sos(sos_id):
    notes = request.form.get("notes")
    success, message = SOSService.resolve_sos(sos_id, current_user.id, notes)

    if success:
        flash(message, "success")
    else:
        flash(message, "danger")

    return redirect(url_for("admin.sos_detail", sos_id=sos_id))


@admin_bp.route("/complaints")
def complaints_list():
    status_filter = request.args.get("status")
    complaints = ComplaintService.get_all_complaints(status_filter, limit=100)

    return render_template("admin/complaints_list.html", complaints=complaints)


@admin_bp.route("/complaints/<complaint_id>")
def complaint_detail(complaint_id):
    complaint = ComplaintService.get_complaint_by_id(complaint_id)
    if not complaint:
        flash("Complaint not found", "danger")
        return redirect(url_for("admin.complaints_list"))

    return render_template("admin/complaint_detail.html", complaint=complaint)


@admin_bp.route("/complaints/<complaint_id>/update-status", methods=["POST"])
def update_complaint_status(complaint_id):
    new_status = request.form.get("status")
    notes = request.form.get("notes")

    success, message = ComplaintService.update_complaint_status(
        complaint_id, new_status, current_user.id, notes
    )

    if success:
        flash(message, "success")
    else:
        flash(message, "danger")

    return redirect(url_for("admin.complaint_detail", complaint_id=complaint_id))


@admin_bp.route("/users")
def users_list():
    users = User.query.all()
    return render_template("admin/users_list.html", users=users)


@admin_bp.route("/users/<int:user_id>")
def user_detail(user_id):
    user_activity = AnalyticsService.get_user_activity(user_id)
    if not user_activity:
        flash("User not found", "danger")
        return redirect(url_for("admin.users_list"))

    user = user_activity.get("user")

    # SAFETY: convert created_at to datetime if it's a string
    if user and isinstance(user.get("created_at"), str):
        try:
            user["created_at"] = datetime.fromisoformat(user["created_at"])
        except ValueError:
            user["created_at"] = None

    return render_template("admin/user_detail.html", activity=user_activity)


@admin_bp.route("/map")
def map_view():
    active_locations = LocationService.get_all_active_user_locations()
    return render_template("admin/map.html", active_locations=active_locations)


@admin_bp.route("/analytics")
def analytics():
    metrics = AnalyticsService.get_dashboard_metrics()
    sos_trends = AnalyticsService.get_sos_trends(days=30)
    complaint_trends = AnalyticsService.get_complaint_trends(days=30)
    status_distribution = AnalyticsService.get_complaint_status_distribution()

    return render_template(
        "admin/analytics.html",
        metrics=metrics,
        sos_trends=sos_trends,
        complaint_trends=complaint_trends,
        status_distribution=status_distribution,
    )
