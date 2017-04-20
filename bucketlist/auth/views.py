from flask import request, make_response, jsonify
from flask.views import MethodView

from bucketlist import db
from bucketlist.models import User
# from .auth import auth as auth


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
                response = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                return make_response(jsonify(response)), 401
        else:
            response = {
                'status': 'fail',
                'message': 'User already exists'
            }
            return make_response(jsonify(response)), 202
