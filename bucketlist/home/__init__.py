from flask import Blueprint, request
from flask import current_app as app
from . import views


def add_cors_headers(response):
    response.headers.add(
        'Access-Control-Allow-Origin', '*')
    if request.method == 'OPTIONS':
        response.headers[
            'Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response


home = Blueprint('home', __name__)
home.after_request(add_cors_headers)

bucketlist_view = views.BucketlistAPI.as_view('bucketlist_api')
bucketlist_items_view = views.BucketListItemsAPI.as_view(
    'bucketlist_items_api')

home.add_url_rule(
    '/v1/bucketlist/',
    view_func=bucketlist_view,
    methods=['POST', 'GET']
)
home.add_url_rule(
    '/v1/bucketlist/<int:id>',
    view_func=bucketlist_view,
    methods=['PUT', 'DELETE', 'GET']
)
home.add_url_rule(
    '/v1/bucketlist/<int:id>/items/',
    view_func=bucketlist_items_view,
    methods=['POST']
)
home.add_url_rule(
    '/v1/bucketlist/<int:id>/items/<int:item_id>/',
    view_func=bucketlist_items_view,
    methods=['GET', 'PUT', 'DELETE']
)
home.add_url_rule(
    '/v1/bucketlist/<int:id>/items/',
    view_func=bucketlist_items_view,
    methods=['GET']
)
