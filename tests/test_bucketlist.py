import datetime
import json
import unittest

from bucketlist import create_app, db
from bucketlist.models import User


class BaseTestCase(unittest.TestCase):

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

        self.test_user_a = User(
            email='test_a@bucket.com',
            username='theatester',
            first_name='test_a',
            last_name='user',
            password='password'
        )
        db.session.add(self.test_user_a)
        db.session.commit()
        user_id = db.session.query(User).filter_by(
            email='test_a@bucket.com').first()
        self.test_token_a = self.test_user_a.encode_auth_token(user_id.id)


class RegistrationLoginTestCase(BaseTestCase):

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
                       'username': 'jailbre3k',
                       'email': 'jailbre3k@gmail.com',
                       'password': 'password'}
            response = self.client.post("/v1/auth/register",
                                        data=json.dumps(payload),
                                        content_type='application/json')
            self.assertEqual(response.status_code, 201,
                             msg='Server not found')

    def test_existing_users_cannot_be_registered(self):
        with self.client:
            payload = {'first_name': 'Martin',
                       'last_name': 'Mungai',
                       'username': 'jailbre3k',
                       'email': 'jailbre3k@gmail.com',
                       'password': 'password'}
            response = self.client.post("/v1/auth/register",
                                        data=json.dumps(payload),
                                        content_type='application/json')
            # data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 202)
            # self.assertTrue(data['message'] == 'User already exists')

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

    def test_non_registered_user_can_login(self):
        with self.client:
            payload = {
                'email': 'danielwangai@gmail.com',
                'password': 'swordpas'
            }
            response = self.client.post("/v1/auth/login",
                                        data=json.dumps(payload),
                                        content_type='application/json')
            self.assertEqual(response.status_code, 401,
                             msg='User not registered')

    def tear_down(self):
        db.session.remove()
        db.drop_all()


class BucketListAPITestCase(BaseTestCase):

    def test_if_user_can_create_a_bucketlist(self):
        with self.client:
            now = datetime.datetime.now()
            payload = {'title': '2017',
                       'date_created': now.isoformat(),
                       'date_modified': now.isoformat(),
                       'users_email': 'test@bucket.com'}
            response = self.client.post("v1/bucketlists/",
                                        data=json.dumps(payload),
                                        headers={
                                            'Content-Type': 'application/json',
                                            'Authorization': self.test_token
                                        })
            self.assertEqual(response.status_code, 201)

    def test_if_user_can_update_another_users_bucketlist(self):
        with self.client:
            now = datetime.datetime.now()
            update_payload = {'title': '2018',
                              'date_created': now.isoformat(),
                              'date_modified': now.isoformat(),
                              'users_email': 'test_a@bucket.com'
                              }
            response = self.client.put("v1/bucketlists/1",
                                       data=json.dumps(update_payload),
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': self.test_token})

            self.assertEqual(response.status_code, 405)

    def test_if_user_can_get_a_list_of_bucketlist(self):
        with self.client:
            response = self.client.get("v1/bucketlists",
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': self.test_token
                                       })
            self.assertEqual(response.status_code, 200)

    def test_if_user_can_get_a_single_bucketlist(self):
        with self.client:
            payload = {'title': '2017'}
            response = self.client.get("v1/bucketlists/1",
                                       data=json.dumps(payload),
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': self.test_token
                                       })
            self.assertEqual(response.status_code, 200)

    def test_if_user_can_create_a_bucketlist_item(self):
        with self.client:
            now = datetime.datetime.now()
            payload = {'name': 'Visit New York',
                       'date_created': now.isoformat(),
                       'date_modified': now.isoformat(),
                       'done': False,
                       'bucketlist_id': 1}
            response = self.client.post("v1/bucketlists/1/items/",
                                        data=json.dumps(payload),
                                        headers={
                                            'Content-Type': 'application/json',
                                            'Authorization': self.test_token
                                        })
            self.assertEqual(response.status_code, 201)

    def test_if_user_can_update_a_bucketlist_item(self):
        with self.client:
            now = datetime.datetime.now()
            # Create a bucket list
            payload = {'title': '2010',
                       'date_created': now.isoformat(),
                       'date_modified': now.isoformat(),
                       'users_email': 'test@bucket.com'
                       }
            self.client.post("v1/bucketlists/", data=json.dumps(payload),
                             headers={
                'Content-Type': 'application/json',
                'Authorization': self.test_token
            })
            # Create a bucket list item
            item_payload = {'name': 'Visit Paris',
                            'date_created': now.isoformat(),
                            'date_modified': now.isoformat(),
                            'done': False,
                            'bucketlist_id': 2
                            }
            self.client.post("v1/bucketlists/2/items",
                             data=json.dumps(item_payload),
                             headers={
                                 'Content-Type': 'application/json',
                                 'Authorization': self.test_token
                             })
            # edit the bucket list
            update_payload = {'name': 'Visit Kampala',
                              'date_modified': now.isoformat(),
                              'done': False,
                              'bucketlist_id': 2
                              }
            rv = self.client.put("v1/bucketlists/2/items/1",
                                 data=json.dumps(update_payload),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'Authorization': self.test_token
                                 })
            self.assertEqual(rv.status_code, 200)

    def test_if_user_can_delete_a_bucketlist_item(self):
        with self.client:
            now = datetime.datetime.now()
            payload = {'name': 'Visit Addis Ababa',
                       'date_created': now.isoformat(),
                       'date_modified': now.isoformat(),
                       'done': False,
                       'bucketlist_id': 1}

            rv = self.client.post("v1/bucketlists/1/items",
                                  data=json.dumps(payload),
                                  headers={
                                      'Content-Type': 'application/json',
                                      'Authorization': self.test_token
                                  })

            response = self.client.delete("v1/bucketlists/1/items/3",
                                          data=json.dumps(payload),
                                          headers={
                                              'Content-Type':
                                              'application/json',
                                              'Authorization': self.test_token
                                          })

            self.assertEqual(rv.status_code, 201)
            self.assertEqual(response.status_code, 204)

    def test_if_a_user_can_delete_a_bucketlist(self):
        with self.client:
            response = self.client.delete("/v1/bucketlists/1",
                                          headers={
                                              'Content-Type':
                                              'application/json',
                                              'Authorization': self.test_token
                                          })
            self.assertEqual(response.status_code, 204)

    def tear_down(self):
        db.session.remove()
        db.drop_all()


class BucketListAPIEdgeTestCase(BaseTestCase):

    def test_if_can_view_bucketlists_when_none_exist(self):
        with self.client:
            response = self.client.get("v1/bucketlists/",
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': self.test_token
                                       })

            self.assertEqual(response.status_code, 204)

    def test_if_a_user_can_view_non_existent_bucketlist(self):
        with self.client:
            response = self.client.get("v1/bucketlists/10",
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': self.test_token
                                       })

            self.assertEqual(response.status_code, 204)

    def test_if_user_can_update_non_existing_bucketlist(self):
        with self.client:
            now = datetime.datetime.now()
            update_payload = {'name': 'Visit Kampala',
                              'date_modified': now.isoformat(),
                              'done': False,
                              'bucketlist_id': 2
                              }

            rv = self.client.put("v1/bucketlists/2/items/1",
                                 data=json.dumps(update_payload),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'Authorization': self.test_token
                                 })
            self.assertEqual(rv.status_code, 204)

    def test_if_a_user_can_create_existing_bucketlist(self):
        with self.client:
            now = datetime.datetime.now()
            payload = {'title': '2017',
                       'date_created': now.isoformat(),
                       'date_modified': now.isoformat(),
                       'users_email': 'test@bucket.com'}
            response = self.client.post("v1/bucketlists/",
                                        data=json.dumps(payload),
                                        headers={
                                            'Content-Type': 'application/json',
                                            'Authorization': self.test_token
                                        })
            rv = self.client.post("v1/bucketlists/",
                                  data=json.dumps(payload),
                                  headers={
                                      'Content-Type': 'application/json',
                                      'Authorization': self.test_token
                                  })
            self.assertEqual(response.status_code, 201)
            self.assertEqual(rv.status_code, 204)

    def test_if_a_bucketlist_with_no_name_can_be_created(self):
        with self.client:
            now = datetime.datetime.now()
            payload = {'date_created': now.isoformat(),
                       'date_modified': now.isoformat(),
                       'users_email': 'test@bucket.com'
                       }

            response = self.client.post("v1/bucketlists/",
                                        data=json.dumps(payload),
                                        headers={
                                            'Content-Type': 'application/json',
                                            'Authorization': self.test_token
                                        })
            self.assertEqual(response.status_code, 409)

    def test_if_a_bucketlist_without_authentication_can_be_created(self):
        with self.client:
            now = datetime.datetime.now()
            payload = {'title': '2017',
                       'date_created': now.isoformat(),
                       'date_modified': now.isoformat(),
                       'users_email': 'test@bucket.com'
                       }

            response = self.client.post("v1/bucketlists/",
                                        data=json.dumps(payload),
                                        headers={
                                            'Content-Type': 'application/json'
                                        })
            self.assertEqual(response.status_code, 401)

    def test_if_a_user_can_create_existing_bucketlist_items(self):
        with self.client:
            now = datetime.datetime.now()
            payload = {'name': 'Visit New York',
                       'date_created': now.isoformat(),
                       'date_modified': now.isoformat(),
                       'done': False}
            response = self.client.post("v1/bucketlists/1/items/",
                                        data=json.dumps(payload),
                                        headers={
                                            'Content-Type': 'application/json',
                                            'Authorization': self.test_token
                                        })

            rv = self.client.post("v1/bucketlists/1/items/",
                                  data=json.dumps(payload),
                                  headers={
                                      'Content-Type': 'application/json',
                                      'Authorization': self.test_token
                                  })

            self.assertEqual(response.status_code, 201)
            self.assertEqual(rv.status_code, 403)

    def test_if_a_user_can_update_bucketlist_items_without_auth(self):
        with self.client:
            now = datetime.datetime.now()
            update_payload = {'name': 'Visit Boston',
                              'date_created': now.isoformat(),
                              'date_modified': now.isoformat(),
                              'done': False,
                              'bucketlist_id': 1
                              }

            rv = self.client.put("v1/bucketlists/1/items/1",
                                 data=json.dumps(update_payload),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'Authorization': self.test_token
                                 })
            self.assertEqual(rv.status_code, 204)

    def test_if_a_user_can_create_bucketlist_items_without_name(self):
        with self.client:
            now = datetime.datetime.now()
            payload = {'date_created': now.isoformat(),
                       'date_modified': now.isoformat(),
                       'users_email': 'test@bucket.com'}
            response = self.client.post("v1/bucketlists/1/items",
                                        data=json.dumps(payload),
                                        headers={
                                            'Content-Type': 'application/json',
                                            'Authorization': self.test_token
                                        })

            self.assertEqual(response.status_code, 403)

    def test_if_a_user_can_create_bucketlist_items_without_auth(self):
        with self.client:
            now = datetime.datetime.now()
            payload = {
                'name': 'Visit Pretoria',
                'date_created': now.isoformat(),
                'date_modified': now.isoformat(),
                'done': False
            }
            response = self.client.post("v1/bucketlists/1/items",
                                        data=json.dumps(payload),
                                        headers={
                                            'Content-Type': 'application/json',
                                            'Authorization': self.test_token
                                        })
            self.assertEqual(response.status_code, 401)

    def test_if_user_can_get_bucketlists_without_auth(self):
        with self.client:
            response = self.client.get("v1/bucketlists",
                                       headers={
                                           'Content-Type': 'application/json'
                                       })
            self.assertEqual(response.status_code, 401)
