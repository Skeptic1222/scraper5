from flask import jsonify


def success(**kwargs):
    return jsonify({"success": True, **kwargs})


def fail(message: str = "", status: int | None = None, **kwargs):
    payload = {"success": False, "error": message}
    payload.update(kwargs)
    resp = jsonify(payload)
    if status:
        resp.status_code = status
    return resp
