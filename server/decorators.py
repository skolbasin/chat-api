from functools import wraps

from flask import jsonify, request

from server.src.config import auth_key
from server.src.log_config import client_log
from server.src.models import User, session


def check_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("api-key")
        if api_key != auth_key:
            client_log.warn("Попытка входа неавторизованного пользователя")
            return (
                jsonify({"error": "Данный пользователь не авторизован в системе"}),
                401,
            )
        return func(*args, **kwargs)

    return wrapper


def check_user_exists(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.json.get("user_id")
        check_user = session.query(User).filter_by(id=user_id).first()
        if check_user is None:
            return jsonify(
                {
                    "result": False,
                    "error": "Пользователь с данным ID не существует в системе",
                }
            )
        return func(*args, **kwargs)

    return wrapper
