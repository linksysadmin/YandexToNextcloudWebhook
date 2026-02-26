from flask import Blueprint, request, jsonify


bp = Blueprint("webhook", __name__)


def create_routes(booking_service):
    @bp.route("/webhook", methods=["POST"])
    def webhook():

        data = request.json

        if not data or "params" not in data:
            return "Bad request", 400

        uids = booking_service.process_form(data["params"])

        if not uids:
            return "Не удалось создать ни одного события", 500

        return jsonify({"status": "ok", "uids": uids})

    return bp