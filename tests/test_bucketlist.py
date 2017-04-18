import datetime
import json
import unittest

from app import create_app, db
from app.models import User


class TestBucketListAPI(unittest.TestCase):

    def setUp(self):
        create_app('testing').app_context().push()
        db.drop_all()
        db.create_all()
        self.client = create_app('testing').test_client()
        self.test_user = User(email='test@bucket.com',
                              username='thetester',
                              first_name='test',
                              last_name='user',
                              password='password')
        db.session.add(self.test_user)
        db.session.commit()
        rv = db.session.query(User).filter_by(
            email='test@bucket.com').first()
        self.test_token = self.test_user.encode_auth_token(rv.id)

    def tear_down(self):
        db.session.remove()
        db.drop_all()

    def test_encode_auth_token(self):
        with self.client:
            test_user = db.session.query(User).filter_by(
                email='test@bucket.com').first()
            auth_token = test_user.encode_auth_token(test_user.id)
            self.assertTrue(isinstance(auth_token, bytes))

    def test_if_a_user_can_register(self):
        with self.client:
            payload = {'first_name': 'Martin',
                       'last_name': 'Mungai',
                       'email': 'jailbre3k@gmail.com',
                       'password': 'password'}
            response = self.client.post("/v1/auth/register",
                                        data=json.dumps(payload),
                                        content_type='application/json')
            self.assertEqual(response.status_code, 201,
                             msg='Server not found')

    def test_if_a_user_can_login(self):
        with self.client:
            payload = {
                'email': 'jailbre3k@gmail.com',
                'password': 'password'
            }
            response = self.client.post("/v1/auth/login",
                                        data=json.dumps(payload),
                                        content_type='application/json')
            self.assertEqual(response.status_code, 200,
                             msg='Server not found')

    def test_non_registered_user_login(self):
        pass

    def test_if_user_can_create_a_bucketlist(self):
        with self.client:
            now = datetime.datetime.now()
            payload = {'title': '2017',
                       'date_created': now.isoformat(),
                       'date_modified': now.isoformat()}
            response = self.client.post("v1/bucketlists/",
                                        data=json.dumps(payload),
                                        headers={
                                            'Content-Type': 'application/json',
                                            'Authorization': self.test_token
                                        })
            self.assertEqual(response.status_code, 201)

    def test_if_user_can_create_a_bucketlist_item(self):
        with self.client:
            now = datetime.datetime.now()
            payload = {'name': 'Visit New York',
                       'date_created': now.isoformat(),
                       'date_modified': now.isoformat(),
                       'done': False}
            response = self.client.post("v1/bucketlists/<id>/items/",
                                        data=json.dumps(payload),
                                        headers={
                                            'Content-Type': 'application/json',
                                            'Authorization': self.test_token
                                        })
            self.assertEqual(response.status_code, 201)