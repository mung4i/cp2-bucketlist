from flask import Blueprint


home = Blueprint('home', __name__)


from . import views


bucketlist_view = views.BucketlistAPI.as_view('bucketlist_api')

home.add_url_rule(
    '/v1/bucketlists/',
    view_func=bucketlist_view,
    methods=['POST', 'GET']
)
home.add_url_rule(
    '/v1/bucketlists/<int:id>',
    view_func=bucketlist_view,
    methods=['PUT', 'DELETE', 'GET']
)
