import datetime

from flask import request, make_response, jsonify
from flask.views import MethodView

from bucketlist import db
from bucketlist.models import User, Bucketlist, Items


class BucketlistAPI(MethodView):

    """
        All things buckelist(Create, Get, Update, Delete)
    """

    now = datetime.datetime.now()

    def post(self):
        data = request.get_json()
        headers = request.headers.get('Authorization')
        bucketlist = Bucketlist.query.filter_by(
            title=data.get('title')).first()

        if not bucketlist:
            try:
                email = User.decode_auth_token(headers)
                user = User.query.filter_by(email=email).first()
                create = Bucketlist(
                    title=data.get('title'),
                    date_created=self.now,
                    date_modified=self.now,
                    users_email=user.email)

                db.session.add(create)
                db.session.commit()

                response = {
                    'status': 'Success',
                    'message': 'Bucketlist has been created'
                }

                return make_response(jsonify(response)), 201
            except Exception as e:
                print(e)
                response = {
                    'status': 'Fail',
                    'message': 'Some error occurred.'
                }
                return make_response(jsonify(response)), 400
        else:
            response = {
                'status': 'Fail',
                'message': 'Bucketlist already exists.'
            }
            return make_response(jsonify(response)), 403

    def get(self, id=None):

        headers = request.headers.get('Authorization')
        if headers:
            try:
                email = User.decode_auth_token(headers)
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
                        response = {
                            'id': bucketlist.id,
                            'title': bucketlist.title,
                            'date_created': bucketlist.date_created,
                            'date_modified': bucketlist.date_modified
                        }
                        return make_response(jsonify(response)), 200
                else:
                    all_bucketlists = []
                    bucketlists = Bucketlist.query.filter_by(
                        users_email=user.email).all()
                    if not bucketlists:
                        response = {
                            'status': 'Fail',
                            'message': 'You do not have bucketlists'
                        }
                        return make_response(jsonify(response)), 404
                    for bucketlist in bucketlists:
                        if user.email == bucketlist.users_email:
                            response = {
                                'id': bucketlist.id,
                                'title': bucketlist.title,
                                'date_created': bucketlist.date_created,
                                'date_modified': bucketlist.date_modified
                            }
                            all_bucketlists.append(response)
                    return make_response(jsonify(all_bucketlists)), 200

            except Exception as e:
                print(e)
                response = {
                    'status': 'Fail',
                    'message': 'Some error occurred.'
                }
                return make_response(jsonify(response)), 400
        else:
            response = {
                'status': 'Fail',
                'message': 'You are not authorized to view these resources'
            }
            return make_response(jsonify(response)), 401

    def delete(self, id):
        headers = request.headers.get('Authorization')
        if headers:
            try:
                email = User.decode_auth_token(headers)
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

            except:
                response = {
                    'status': 'Fail',
                    'message': 'Some error occurred'
                }
                return make_response(jsonify(response)), 400
        else:
            response = {
                'status': 'Fail',
                'message': 'You are not authorized to delete these resources'
            }
            return make_response(jsonify(response)), 401

    def put(self, id):
        data = request.get_json()
        headers = request.headers.get('Authorization')
        if headers:
            try:
                email = User.decode_auth_token(headers)
                user = User.query.filter_by(email=email).first()
                bucketlists = Bucketlist.query.filter_by(
                    users_email=user.email).all()

                for bucketlist in bucketlists:
                    if user.email == bucketlist.users_email:
                        bucketlist.title = data.get('title')
                        bucketlist.date_modified = self.now
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

            except:
                response = {
                    'status': 'Fail',
                    'message': 'Some error occured.'
                }
                return make_response(jsonify(response)), 400


class BucketListItemsAPI(MethodView):
    """
    Create, Get, Update, Delete BucketListItems
    """
    now = datetime.datetime.now()

    def post(self, id):
        data = request.get_json()
        headers = request.headers.get('Authorization')
        items = Items.query.filter_by(
            name=data.get('name')).first()
        if headers:
            if not items:
                email = User.decode_auth_token(headers)
                user = User.query.filter_by(email=email).first()
                if User.decode_auth_token(user.email):
                    create = Items(
                        name=data.get('name'),
                        date_created=self.now,
                        date_modified=self.now,
                        done=False,
                        bucketlist_id=id)
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
                return make_response(jsonify(response)), 403

        else:
            response = {
                'status': 'Fail',
                'message': 'You are not authorized to view these resources'
            }
            return make_response(jsonify(response)), 401

    def get(self, id, item_id=None):
        headers = request.headers.get('Authorization')
        if headers:
            try:
                email = User.decode_auth_token(headers)
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
                        print(response)
                        return make_response(jsonify(response)), 200
                if id:
                    all_items = []
                    items = Items.query.filter_by(
                        bucketlist_id=id).all()
                    print(items)
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
            except Exception as e:
                print(e)
                response = {
                    'status': 'Fail',
                    'message': 'Some error occurred.'
                }
                return make_response(jsonify(response)), 400

        else:
            response = {
                'status': 'Fail',
                'message': 'You are not authorized to view these resources'
            }
            return make_response(jsonify(response)), 401

    def put(self, id=None, item_id=None):
        data = request.get_json()
        headers = request.headers.get('Authorization')
        if headers:
            try:
                email = User.decode_auth_token(headers)
                user = User.query.filter_by(email=email).first()
                item = Items.query.filter_by(
                    id=item_id).first()
                if item.bucketlist_id == id:
                    item.name = data.get('name')
                    item.date_modified = self.now
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

            except:
                response = {
                    'status': 'Fail',
                    'message': 'Some error occured.'
                }
                return make_response(jsonify(response)), 400
