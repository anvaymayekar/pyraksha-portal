from flask import Blueprint, request, jsonify
from src.api.decorators import token_required
from src.services.complaint_service import ComplaintService

api_complaints = Blueprint("api_complaints", __name__, url_prefix="/api/complaints")


@api_complaints.route("/file", methods=["POST"])
@token_required
def file_complaint(current_user):
    data = request.get_json()

    complaint_id = data.get("complaint_id")
    title = data.get("title")
    description = data.get("description")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not complaint_id:
        return jsonify({"success": False, "message": "Complaint ID is required"}), 400

    success, message, complaint = ComplaintService.create_complaint(
        current_user.id, complaint_id, title, description, latitude, longitude
    )

    if success and complaint:
        return (
            jsonify(
                {"success": True, "message": message, "complaint": complaint.to_dict()}
            ),
            201,
        )
    else:
        return jsonify({"success": False, "message": message}), 400


@api_complaints.route("/list", methods=["GET"])
@token_required
def list_complaints(current_user):
    status = request.args.get("status")

    if current_user.is_admin():
        user_id = request.args.get("user_id", type=int)
        if user_id:
            complaints = ComplaintService.get_user_complaints(user_id, status)
        else:
            complaints = ComplaintService.get_all_complaints(status)
    else:
        complaints = ComplaintService.get_user_complaints(current_user.id, status)

    return (
        jsonify({"success": True, "complaints": [c.to_dict() for c in complaints]}),
        200,
    )


@api_complaints.route("/<complaint_id>", methods=["GET"])
@token_required
def get_complaint(current_user, complaint_id):
    complaint = ComplaintService.get_complaint_by_id(complaint_id)

    if not complaint:
        return jsonify({"success": False, "message": "Complaint not found"}), 404

    if complaint.user_id != current_user.id and not current_user.is_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    return jsonify({"success": True, "complaint": complaint.to_dict()}), 200


@api_complaints.route("/<complaint_id>/status", methods=["PUT"])
@token_required
def update_complaint_status(current_user, complaint_id):
    if not current_user.is_admin():
        return jsonify({"success": False, "message": "Admin access required"}), 403

    data = request.get_json()
    new_status = data.get("status")
    notes = data.get("notes")

    if not new_status:
        return jsonify({"success": False, "message": "Status is required"}), 400

    success, message = ComplaintService.update_complaint_status(
        complaint_id, new_status, current_user.id, notes
    )

    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "message": message}), 400


@api_complaints.route("/search", methods=["GET"])
@token_required
def search_complaints(current_user):
    query = request.args.get("q", "")

    if not query:
        return jsonify({"success": False, "message": "Search query is required"}), 400

    if current_user.is_admin():
        complaints = ComplaintService.search_complaints(query)
    else:
        complaints = ComplaintService.search_complaints(query, current_user.id)

    return (
        jsonify({"success": True, "complaints": [c.to_dict() for c in complaints]}),
        200,
    )
