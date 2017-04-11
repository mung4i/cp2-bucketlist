import datetime
import json
import unittest

from app import create_app, db
from app.models import User, Bucketlist, Items


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

    def tear_down(self):
        db.session.remove()
        db.drop_all()

    def test_if_user_can_create_a_bucketlist(self):
        now = datetime.datetime.now()
        self.bucketlist = Bucketlist(title="2017",
                                     date_created=now,
                                     date_modified=now,
                                     users_email='test@bucket.com',
                                     user=self.test_user)
        db.session.add(self.bucketlist)
        db.session.commit()
        data = db.session.query(Bucketlist).filter_by(title="2017").first()
        self.assertEqual(data, self.bucketlist)

    def test_if_user_can_create_a_bucketlist_item(self):
        now = datetime.datetime.now()
        data = db.session.query(Bucketlist).filter_by(title="2017").first()
        item = Items(name="Visit New York",
                     date_created=now,
                     date_modified=now,
                     done=False,
                     bucketlist_id=1,
                     bucketlist=data)
        db.session.add(item)
        db.session.commit()
        search = db.session.query(Items).filter_by(name="Visit New York"
                                                   ).first()
        self.assertEqual(search, item)

    def test_user_api_registration(self):
        payload = {"first_name": "Sharon", "last_name": "Njihia",
                   "email": "sharonkarendi5@gmail.com", "password": "password"}
        response = self.client.post("/v1/auth/register", data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201, msg="Server not found")
