from flask import Blueprint, request
from flask_restful import Api


def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    if request.method == 'OPTIONS':
        response.headers[
            'Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response


auth = Blueprint('auth', __name__)
auth.after_request(add_cors_headers)
api = Api(auth)


from . import views

auth.add_url_rule(
    '/v1/auth/register/',
    view_func=views.RegisterAPI.as_view('register_api'),
    methods=['POST']
)

auth.add_url_rule(
    '/v1/auth/login/',
    view_func=views.LoginAPI.as_view('login_api'),
    methods=['POST']
)
