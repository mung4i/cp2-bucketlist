from functools import wraps
from flask import request, jsonify, make_response


def validate_user_credentials(func):
    '''
    Validate data posted by the user
    '''

    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.get_json()
        response = {
            "status": "Failed",
            "message": "Bad request"
        }
        if not data:
            return make_response(jsonify(response)), 400
        elif "first_name" not in data or "last_name" not in data or\
                "email" not in data or "password" not in data:
            return make_response(jsonify(response)), 400
        elif data["first_name"] == "" or data["last_name"] == "" \
                or data["email"] == "" or data["password"] == "":
            return make_response(jsonify(response)), 400
        elif "@" not in data["email"] or ".com" not in data["email"]:
            error = {
                "status": "Fail",
                "message": "Invalid email address"
            }
            return make_response(jsonify(error)), 400
        return func(*args, **kwargs)
    return wrapper


def validate_bucketlist_data(func):
    '''
    Validates data posted to bucketlists
    '''

    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.get_json()
        response = {
            'status': "Bad request",
            'message': "Required fields are empty."
        }
        if not data:
            return make_response(jsonify(response)), 400
        elif "title" not in data or data["title"] == "":
            return make_response(jsonify(response)), 400
        return func(*args, **kwargs)
    return wrapper


def validate_bucketlist_data_items(func):
    '''
    Validates data posted to bucketlist items
    '''

    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.get_json()
        response = {
            'status': "Bad request",
            'message': "Required fields are empty."
        }
        if not data:
            return make_response(jsonify(response)), 400
        elif "name" not in data or data["name"] == "":
            return make_response(jsonify(response)), 400
        return func(*args, **kwargs)
    return wrapper
