from flask import Blueprint
from flask_restful import Api


auth = Blueprint('auth', __name__)
api = Api(auth)


from . import views

auth.add_url_rule(
    '/v1/auth/register',
    view_func=views.RegisterAPI.as_view('register_api'),
    methods=['POST']
)

auth.add_url_rule(
    '/v1/auth/login',
    view_func=views.LoginAPI.as_view('login_api'),
    methods=['POST']
)
