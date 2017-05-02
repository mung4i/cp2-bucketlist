import datetime

from flask import request, make_response, jsonify
from flask.views import MethodView

from bucketlist import db
from bucketlist.models import User, Bucketlist


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
        print('first')
        print(id)

        headers = request.headers.get('Authorization')
        if headers:
            try:
                email = User.decode_auth_token(headers)
                user = User.query.filter_by(email=email).first()

                if id:
                    bucketlist = Bucketlist.query.filter_by(id=id).first()
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


class BucketListItems(MethodView):
    pass
