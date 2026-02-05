from flask import Blueprint, request, jsonify
from src.api.decorators import token_required
from src.services.sos_service import SOSService
from src.core.extensions import socketio

api_sos = Blueprint("api_sos", __name__, url_prefix="/api/sos")


@api_sos.route("/trigger", methods=["POST"])
@token_required
def trigger_sos(current_user):
    data = request.get_json()

    sos_id = data.get("sos_id")
    initial_location = data.get("location")

    if not sos_id:
        return jsonify({"success": False, "message": "SOS ID is required"}), 400

    success, message, sos = SOSService.create_sos(
        current_user.id, sos_id, initial_location
    )

    if success and sos:
        socketio.emit(
            "sos_triggered",
            {
                "sos": sos.to_dict(include_locations=True),
                "user": current_user.to_dict(),
            },
            broadcast=True,
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": message,
                    "sos": sos.to_dict(include_locations=True),
                }
            ),
            201,
        )
    else:
        return jsonify({"success": False, "message": message}), 400


@api_sos.route("/update_location", methods=["POST"])
@token_required
def update_location(current_user):
    data = request.get_json()

    sos_id = data.get("sos_id")
    location = data.get("location")

    if not sos_id or not location:
        return (
            jsonify({"success": False, "message": "SOS ID and location are required"}),
            400,
        )

    success, message = SOSService.add_location_update(sos_id, location)

    if success:
        sos = SOSService.get_sos_by_id(sos_id)
        socketio.emit(
            "sos_location_update",
            {"sos_id": sos_id, "location": location, "user_id": current_user.id},
            broadcast=True,
        )

        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "message": message}), 400


@api_sos.route("/resolve", methods=["POST"])
@token_required
def resolve_sos(current_user):
    data = request.get_json()

    sos_id = data.get("sos_id")
    notes = data.get("notes")

    if not sos_id:
        return jsonify({"success": False, "message": "SOS ID is required"}), 400

    sos = SOSService.get_sos_by_id(sos_id)
    if not sos:
        return jsonify({"success": False, "message": "SOS not found"}), 404

    if sos.user_id != current_user.id and not current_user.is_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    success, message = SOSService.resolve_sos(
        sos_id, current_user.id if current_user.is_admin() else None, notes
    )

    if success:
        socketio.emit(
            "sos_resolved",
            {"sos_id": sos_id, "resolved_by": current_user.id},
            broadcast=True,
        )

        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "message": message}), 400


@api_sos.route("/active", methods=["GET"])
@token_required
def get_active_sos(current_user):
    if current_user.is_admin():
        sos_events = SOSService.get_active_sos_events()
    else:
        sos_events = [
            sos
            for sos in SOSService.get_active_sos_events()
            if sos.user_id == current_user.id
        ]

    return (
        jsonify(
            {
                "success": True,
                "sos_events": [
                    sos.to_dict(include_locations=True) for sos in sos_events
                ],
            }
        ),
        200,
    )


@api_sos.route("/history", methods=["GET"])
@token_required
def get_sos_history(current_user):
    if current_user.is_admin():
        user_id = request.args.get("user_id", type=int)
        if user_id:
            sos_events = SOSService.get_user_sos_history(user_id)
        else:
            sos_events = SOSService.get_all_sos_events(limit=100)
    else:
        sos_events = SOSService.get_user_sos_history(current_user.id)

    return (
        jsonify({"success": True, "sos_events": [sos.to_dict() for sos in sos_events]}),
        200,
    )


@api_sos.route("/<sos_id>", methods=["GET"])
@token_required
def get_sos_details(current_user, sos_id):
    sos = SOSService.get_sos_by_id(sos_id)

    if not sos:
        return jsonify({"success": False, "message": "SOS not found"}), 404

    if sos.user_id != current_user.id and not current_user.is_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    return jsonify({"success": True, "sos": sos.to_dict(include_locations=True)}), 200
