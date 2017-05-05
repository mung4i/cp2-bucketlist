from flask import Blueprint

from . import views

home = Blueprint('home', __name__)

bucketlist_view = views.BucketlistAPI.as_view('bucketlist_api')
bucketlist_items_view = views.BucketListItemsAPI.as_view(
    'bucketlist_items_api')

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
home.add_url_rule(
    '/v1/bucketlists/<int:id>/items/',
    view_func=bucketlist_items_view,
    methods=['POST']
)
home.add_url_rule(
    '/v1/bucketlists/<int:id>/items/<int:item_id>',
    view_func=bucketlist_items_view,
    methods=['GET', 'PUT', 'DELETE']
)
home.add_url_rule(
    '/v1/bucketlists/<int:id>/items',
    view_func=bucketlist_items_view,
    methods=['GET']
)
