import datetime
from urllib.parse import urljoin

from flask import request, make_response, jsonify, url_for
from flask.views import MethodView
from flask_jwt import jwt_required
from flask_restful import reqparse


from bucketlist import db
from bucketlist.models import User, Bucketlist, Items
from ..decorators import\
    validate_bucketlist_data, validate_bucketlist_data_items


class BucketlistAPI(MethodView):

    """
        All things buckelist(Create, Get, Update, Delete)
    """

    @jwt_required()
    @validate_bucketlist_data
    def post(self):
        data = request.get_json()
        token = request.headers.get('Authorization')
        bucketlist = Bucketlist.query.filter_by(
            title=data.get('title')).first()

        if not bucketlist:
            email = User.decode_auth_token(token)
            user = User.query.filter_by(email=email).first()
            create = Bucketlist(
                title=data.get('title'),
                date_created=datetime.datetime.now(),
                date_modified=datetime.datetime.now(),
                users_email=user.email)

            db.session.add(create)
            db.session.commit()

            response = {
                'status': 'Success',
                'message': 'Bucketlist has been created'
            }

            return make_response(jsonify(response)), 201
        else:
            response = {
                'status': 'Fail',
                'message': 'Bucketlist already exists.'
            }
            return make_response(jsonify(response)), 409

    @jwt_required()
    def get(self, id=None):

        token = request.headers.get('Authorization')
        # Search and Query params
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int, required=False, location='args')
        parser.add_argument('q', type=str, required=False, location='args')
        parser.add_argument(
            'page', type=int, required=False, location='args')
        args = parser.parse_args()

        email = User.decode_auth_token(token)
        user = User.query.filter_by(email=email).first()

        if id:

            bucketlist = Bucketlist.query.filter_by(id=id).first()
            if not bucketlist:
                response = {
                    'status': 'Fail',
                    'message': 'The bucketlist does not exist'
                }
                return make_response(jsonify(response)), 404
            if user.email == bucketlist.users_email:
                all_items = []
                for item in bucketlist.items:
                    item_response = {
                        'id': item.id,
                        'name': item.name,
                        'date_created': item.date_created,
                        'date_modified': item.date_modified,
                        'done': item.done
                    }
                    all_items.append(item_response)
                response = {
                    'id': bucketlist.id,
                    'title': bucketlist.title,
                    'items': all_items,
                    'date_created': bucketlist.date_created,
                    'date_modified': bucketlist.date_modified
                }
                return make_response(jsonify(response)), 200

        else:
            all_bucketlists = []

            page = args["page"] or 1
            limit = args["limit"] or 1
            query = args["q"] or None

            if query:
                bucketlists = Bucketlist.query.filter(
                    Bucketlist.title.ilike('%{}%'.format(query))).filter_by(
                    users_email=user.email).paginate(
                    page=page, per_page=limit, error_out=True)
            else:
                bucketlists = Bucketlist.query.filter_by(
                    users_email=user.email).paginate(
                    page=page, per_page=limit, error_out=True)

            if not bucketlists.items:
                response = {
                    'status': 'Fail',
                    'message': 'You do not have bucketlists'
                }
                return make_response(jsonify(response)), 404
            for bucketlist in bucketlists.items:
                response = {
                    'id': bucketlist.id,
                    'title': bucketlist.title,
                    'date_created': bucketlist.date_created,
                    'date_modified': bucketlist.date_modified
                }
                all_bucketlists.append(response)

            if bucketlists.has_next:
                next_url = (urljoin(
                    "http://127.0.0.1:5000/v1/bucketlists/",
                    url_for(request.endpoint,
                            q=query,
                            page=bucketlists.next_num,
                            limit=bucketlists.per_page)))
            else:
                next_url = None
            if bucketlists.has_prev:
                prev_url = (urljoin(
                    "http://127.0.0.1:5000/v1/bucketlists/",
                    url_for(request.endpoint,
                            page=bucketlists.prev_num,
                            limit=bucketlists.per_page)))
            else:
                prev_url = None

            response = {
                "page": bucketlists.page,
                "pages": bucketlists.pages,
                "limit": 20,
                "next_url": next_url,
                "prev_url": prev_url,
                "bucketlists": all_bucketlists
            }

            return make_response(jsonify(response)), 200

    @jwt_required()
    def delete(self, id):
        token = request.headers.get('Authorization')
        if token:
            email = User.decode_auth_token(token)
            user = User.query.filter_by(email=email).first()
            bucketlists = Bucketlist.query.filter_by(
                users_email=user.email).all()
            for bucketlist in bucketlists:
                if id == bucketlist.id:
                    db.session.delete(bucketlist)
                    db.session.commit()
            response = {
                'status': "Success",
                'message': 'Deleted'
            }
            return make_response(jsonify(response)), 204
        else:
            response = {
                'status': 'Fail',
                'message': 'You are not authorized to delete these resources'
            }
            return make_response(jsonify(response)), 401

    @jwt_required()
    @validate_bucketlist_data
    def put(self, id):
        data = request.get_json()
        token = request.headers.get('Authorization')
        email = User.decode_auth_token(token)
        user = User.query.filter_by(email=email).first()
        bucketlist = Bucketlist.query.filter_by(
            id=id).first()

        if token and user.email == bucketlist.users_email:
            bucketlist.title = data.get('title')
            bucketlist.date_modified = datetime.datetime.now()

            db.session.commit()

            response = {
                'status': "Success",
                'message': "Bucketlist has been updated"
            }
            return make_response(jsonify(response)), 200
        else:
            response = {
                'status': 'Fail',
                'message':
                'You are not authorized to update these resources'
            }
            return make_response(jsonify(response)), 401


class BucketListItemsAPI(MethodView):
    """
    Create, Get, Update, Delete BucketListItems
    """

    @jwt_required()
    @validate_bucketlist_data_items
    def post(self, id):
        data = request.get_json()
        token = request.headers.get('Authorization')
        items = Items.query.filter_by(
            name=data.get('name')).first()
        bucketlist = Bucketlist.query.filter_by(id=id).first()

        if not items:
            email = User.decode_auth_token(token)
            user = User.query.filter_by(email=email).first()
            if User.decode_auth_token(user.email):
                create = Items(
                    name=data.get('name'),
                    date_created=datetime.datetime.now(),
                    date_modified=datetime.datetime.now(),
                    done=False,
                    bucketlist_id=bucketlist.id)
                db.session.add(create)
                db.session.commit()

            response = {
                'status': 'Success',
                'message': 'Bucketlist item has been created'
            }

            return make_response(jsonify(response)), 201

        else:
            response = {
                'status': 'Fail',
                'message': 'Bucketlist already exists.'
            }
            return make_response(jsonify(response)), 409

    @jwt_required()
    def get(self, id, item_id=None):
        token = request.headers.get('Authorization')
        email = User.decode_auth_token(token)
        user = User.query.filter_by(email=email).first()
        if item_id:
            item = Items.query.filter_by(
                id=item_id).first()
            if not item:
                response = {
                    'status': 'Fail',
                    'message': 'The bucketlist item does not exist'
                }
                return make_response(jsonify(response)), 404
            if item and user:
                response = {
                    'name': item.name,
                    'date_created': item.date_created,
                    'date_modified': item.date_modified,
                    'done': item.done,
                    'bucketlist_id': item.bucketlist_id
                }
                return make_response(jsonify(response)), 200
        if id:
            all_items = []
            items = Items.query.filter_by(
                bucketlist_id=id).all()
            if not items:
                response = {
                    "status": "Fail",
                    "message": "You do not have any bucketlist items"
                }
                return make_response(jsonify(response)), 404
            for item in items:
                response = {
                    "name": item.name,
                    "date_created": item.date_created,
                    "date_modified": item.date_modified,
                    "done": item.done,
                    "bucketlist_id": item.bucketlist_id,
                    "item_id": item.id
                }
                all_items.append(response)
            return make_response(jsonify(all_items)), 200
        else:
            response = {
                'status': 'Fail',
                'message': 'You are not authorized to view these resources'
            }
            return make_response(jsonify(response)), 401

    @jwt_required()
    @validate_bucketlist_data_items
    def put(self, id=None, item_id=None):
        data = request.get_json()
        item = Items.query.filter_by(
            id=item_id).first()
        if item:
            item.name = data.get('name')
            item.date_modified = datetime.datetime.now()
            db.session.commit()
            response = {
                'status': "Success",
                'message': "Bucketlist has been updated"
            }
            return make_response(jsonify(response)), 200

        else:
            response = {
                'status': 'Fail',
                'message':
                'The resources you want to update do not exist.'
            }
            return make_response(jsonify(response)), 400

    @jwt_required()
    def delete(self, id=None, item_id=None):
        item = Items.query.filter_by(
            id=item_id).first()
        if item.bucketlist_id == id:
            db.session.delete(item)
            db.session.commit()
            response = {
                'status': "Success",
                'message': 'Deleted'
            }
            return make_response(jsonify(response)), 204
        else:
            response = {
                'status': 'Fail',
                'message': 'You are not authorized to delete these resources'
            }
            return make_response(jsonify(response)), 401
