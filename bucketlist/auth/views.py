from flask import request, make_response, jsonify
from flask.views import MethodView

from bucketlist import db
from bucketlist.models import User


class RegisterAPI(MethodView):

    def post(self):
        data = request.get_json()

        user = User.query.filter_by(email=data.get('email')).first()
        if not user:
            try:
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
                response = {
                    'status': 'Success',
                    'message': 'Successfully registered',
                    'auth_token': auth_token.decode()
                }
                return make_response(jsonify(response)), 201
            except Exception as e:
                print(e)
                response = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.',
                }
                return make_response(jsonify(response)), 401
        else:
            response = {
                'status': 'fail',
                'message': 'User already exists'
            }
            return make_response(jsonify(response)), 202


class LoginAPI(MethodView):

    def post(self):
        data = request.get_json()
        try:
            user = User.query.filter_by(email=data.get('email')).first()
            if not user:
                response = {
                    'status': 'Failed',
                    'message': "User is not registered "
                }
                return make_response(jsonify(response), 401)
            auth_token = user.encode_auth_token(user.id)
            if auth_token:
                response = {
                    'status': "Success",
                    'message': "Successfully logged in",
                    "auth_token": auth_token.decode()
                }
                return make_response(jsonify(response)), 200
        except Exception as e:
            print(e)
            response = {
                'status': 'Failed',
                'message': 'User password combination failed to match.'
            }
            return make_response(jsonify(response)), 500
