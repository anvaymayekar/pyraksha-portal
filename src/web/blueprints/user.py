from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.services.complaint_service import ComplaintService
from src.services.sos_service import SOSService
from src.services.location_service import LocationService

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.before_request
@login_required
def require_login():
    if current_user.is_admin():
        return redirect(url_for("admin.dashboard"))


@user_bp.route("/dashboard")
def dashboard():
    complaints = ComplaintService.get_user_complaints(current_user.id, limit=5)
    sos_events = SOSService.get_user_sos_history(current_user.id, limit=5)
    active_sos = SOSService.get_active_sos_events()
    active_sos = [sos for sos in active_sos if sos.user_id == current_user.id]

    return render_template(
        "user/dashboard.html",
        complaints=complaints,
        sos_events=sos_events,
        active_sos=active_sos[0] if active_sos else None,
    )


@user_bp.route("/complaints")
def complaints():
    status_filter = request.args.get("status")
    user_complaints = ComplaintService.get_user_complaints(
        current_user.id, status_filter
    )

    return render_template("user/complaints.html", complaints=user_complaints)


@user_bp.route("/complaints/new", methods=["GET", "POST"])
def new_complaint():
    if request.method == "POST":
        import uuid

        title = request.form.get("title")
        description = request.form.get("description")
        latitude = request.form.get("latitude", type=float)
        longitude = request.form.get("longitude", type=float)

        complaint_id = str(uuid.uuid4())
        success, message, complaint = ComplaintService.create_complaint(
            current_user.id, complaint_id, title, description, latitude, longitude
        )

        if success:
            flash(message, "success")
            return redirect(url_for("user.complaints"))
        else:
            flash(message, "danger")

    return render_template("user/new_complaint.html")


@user_bp.route("/sos-history")
def sos_history():
    sos_events = SOSService.get_user_sos_history(current_user.id)
    return render_template("user/sos_history.html", sos_events=sos_events)


@user_bp.route("/profile")
def profile():
    return render_template("user/profile.html")


@user_bp.route("/map")
def map_view():
    locations = LocationService.get_user_locations(current_user.id, limit=100)
    return render_template("user/map.html", locations=locations)
