import datetime

from flask import request, make_response, jsonify
# from flask_login import login_required'
from flask.views import MethodView

from bucketlist import db
from bucketlist.models import User


class RegisterAPI(MethodView):

    """
        Register users
    """

    def post(self):
        data = request.get_json()

        user = User.query.filter_by(email=data.get('email')).first()
        if not user:
            user = User(
                email=data.get('email'),
                username=data.get('username'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                password=data.get('password')
            )

            db.session.add(user)
            db.session.commit()

            auth_token = user.encode_auth_token(user.id)
            print(auth_token, type(auth_token))
            response = {
                'status': 'Success',
                'message': 'Successfully registered',
                'auth_token': auth_token
            }
            return make_response(jsonify(response)), 201
        else:
            response = {
                'status': 'fail',
                'message': 'User already exists'
            }
            return make_response(jsonify(response)), 202


class LoginAPI(MethodView):
    """
        Login users
    """
    now = datetime.datetime.now()

    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data.get('email')).first()
        if not user:
            response = {
                'status': 'Failed',
                'message': "User is not registered"
            }
            return make_response(jsonify(response), 400)
        password = data.get('password')
        if user.verify_password(password):
            auth_token = user.encode_auth_token(user.email)
            response = {
                'status': "Success",
                'message': "Successfully logged in",
                "auth_token": auth_token
            }
            return make_response(jsonify(response)), 200
        else:
            response = {
                'status': "Failed",
                'message': "User password combination failed to match"
            }
            return make_response(jsonify(response)), 400
