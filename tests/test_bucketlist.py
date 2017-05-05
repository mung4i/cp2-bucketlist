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
        query_user = db.session.query(User).filter_by(
            email='test@bucket.com').first()
        self.test_token = self.test_user.encode_auth_token(query_user.email)
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
        self.test_token_a = self.test_user_a.encode_auth_token(user_id.email)

        def tear_down(self):
            db.session.remove()
            db.drop_all()


class RegistrationLoginTestCase(BaseTestCase):

    payload = {
        'first_name': 'Martin',
        'last_name': 'Mungai',
        'username': 'jailbre3k',
        'email': 'jailbre3k@gmail.com',
        'password': 'password'
    }

    login_payload = {
        'email': 'jailbre3k@gmail.com',
        'password': 'password'
    }

    wrong_pass_payload = {
        'email': 'jailbre3k@gmail.com',
        'password': 'swordpas'
    }

    def register_user(self, payload):
        return self.client.post("/v1/auth/register",
                                data=json.dumps(payload),
                                content_type='application/json')

    def login_user(self, payload):
        return self.client.post("/v1/auth/login",
                                data=json.dumps(payload),
                                content_type='application/json')

    def test_encode_auth_token(self):
        """
        Test token encoding functionality
        """
        with self.client:
            test_user = db.session.query(User).filter_by(
                email='test@bucket.com').first()
            auth_token = test_user.encode_auth_token(test_user.email)
            self.assertTrue(isinstance(auth_token, str))

    def test_decode_auth_token(self):
        """
        Test token decoding functionality
        """
        with self.client:
            auth_token = self.test_user.encode_auth_token(self.test_user.email)
            decoded_token = self.test_user.decode_auth_token(auth_token)
            self.assertTrue(isinstance(auth_token, str))
            self.assertTrue(isinstance(decoded_token, str))

    def test_register_endpoint(self):
        """
        Test if a user is able to register
        """
        with self.client:

            response = self.register_user(self.payload)

            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "Success")
            self.assertTrue(data["message"] == "Successfully registered")
            self.assertTrue(data["auth_token"])
            self.assertEqual(response.status_code, 201,
                             msg=data["message"])

    def test_register_endpoint_for_existing_users(self):
        """
        Test if existing users can register
        """

        with self.client:

            response = self.register_user(self.payload)

            new_response = self.register_user(self.payload)

            data = json.loads(response.data.decode())
            duplicate_data = json.loads(new_response.data.decode())

            self.assertEqual(response.status_code, 201, msg=data["message"])
            self.assertTrue(data['message'] == 'Successfully registered')
            self.assertEqual(new_response.status_code, 202,
                             msg=duplicate_data["message"])
            self.assertTrue(duplicate_data['message'] == 'User already exists')

    def test_login_endpoint(self):
        """
        Test if a registered user can login
        """
        with self.client:
            register = self.register_user(self.payload)
            register_response = json.loads(register.data.decode())
            self.assertTrue(register_response['message'] ==
                            "Successfully registered")
            self.assertEqual(register.status_code, 201)

            # Login
            response = self.login_user(self.login_payload)

            data = json.loads(response.data.decode())
            self.assertTrue(data['auth_token'])
            self.assertTrue(data['message'] == 'Successfully logged in')
            self.assertEqual(response.status_code, 200,
                             msg=data["message"])

    def test_login_endpoint_for_non_registered(self):
        """
        Test if a non registered user is able to login
        """
        with self.client:
            response = self.login_user(self.login_payload)
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == 'Failed')
            self.assertTrue(data["message"] == 'User is not registered')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_login_endpoint_for_wrong_password(self):
        """
        Test if a user logins with wrong credentials
        """
        with self.client:
            register = self.register_user(self.payload)
            register_response = json.loads(register.data.decode())
            self.assertTrue(register_response['message'] ==
                            "Successfully registered")
            self.assertEqual(register.status_code, 201)

            # Login
            response = self.login_user(self.wrong_pass_payload)

            data = json.loads(response.data.decode())
            self.assertTrue(
                data['message'] == 'User password combination failed to match')
            self.assertEqual(response.status_code, 400,
                             msg=data["message"])


class BucketListAPITestCase(BaseTestCase):

    payload = {'title': '2017'}
    now = datetime.datetime.now()

    update_payload = {'title': '2018',
                      'date_modified': now.isoformat()}

    def create_bucketlist(self, payload):
        return self.client.post("v1/bucketlists/",
                                data=json.dumps(payload),
                                headers={
                                    'Content-Type': 'application/json',
                                    'Authorization': self.test_token
                                })

    def test_create_bucketlist(self):
        """
        Test if a user can create a bucketlist
        """
        with self.client:
            response = self.create_bucketlist(self.payload)
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "Success")
            self.assertTrue(data["message"] == "Bucketlist has been created")
            self.assertEqual(response.status_code, 201)

    def test_update_bucketlist(self):
        """
        Test if a user can update their bucketlist
        """
        with self.client:

            response = self.create_bucketlist(self.payload)
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "Success")
            self.assertTrue(data["message"] == "Bucketlist has been created")
            self.assertEqual(response.status_code, 201)

            update_response = self.client.put("v1/bucketlists/1",
                                              data=json.dumps(
                                                  self.update_payload),
                                              headers={
                                                  'Content-Type':
                                                  'application/json',
                                                  'Authorization':
                                                  self.test_token
                                              })
            update_data = json.loads(update_response.data.decode())
            self.assertTrue(update_data["status"] == "Success")
            self.assertTrue(
                update_data["message"] == "Bucketlist has been updated")
            self.assertEqual(update_response.status_code, 200)

    def test_update_bucketlist_by_other_users(self):
        """
        Test if a user can update another users bucketlist
        """
        with self.client:
            response = self.create_bucketlist(self.payload)
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "Success")
            self.assertTrue(data["message"] == "Bucketlist has been created")
            self.assertEqual(response.status_code, 201)

            update_payload = {'title': '2018',
                              'date_modified': self.now.isoformat()}
            response = self.client.put("v1/bucketlists/1",
                                       data=json.dumps(update_payload),
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': self.test_token_a})
            response_data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "Success")
            self.assertTrue(
                response_data['message'] ==
                "You are not authorized to update these resources")
            self.assertEqual(response.status_code, 401)

    def test_get_bucketlist(self):
        """
        Test if a user can get all their bucketlist
        """
        with self.client:
            create_response = self.create_bucketlist(self.payload)
            data = json.loads(create_response.data.decode())
            self.assertTrue(data["message"] == "Bucketlist has been created")
            self.assertTrue(data["status"] == "Success")
            self.assertEqual(create_response.status_code, 201)

            get_response = self.client.get("v1/bucketlists/",
                                           headers={
                                               'Content-Type':
                                               'application/json',
                                               'Authorization': self.test_token
                                           })
            self.assertEqual(get_response.status_code, 200)

    def test_get_single_bucketlist(self):
        """
        Test if a user can get a single item in their bucketlist
        """
        with self.client:
            create_response = self.create_bucketlist(self.payload)
            created_data = json.loads(create_response.data.decode())
            self.assertTrue(
                created_data["message"] == "Bucketlist has been created")

            response = self.client.get("v1/bucketlists/1",
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': self.test_token
                                       })
            self.assertEqual(response.status_code, 200)

    def test_delete_bucketlist(self):
        """
        Test if a user can delete a bucketlist
        """
        with self.client:
            create_response = self.create_bucketlist(self.payload)
            created_data = json.loads(create_response.data.decode())
            self.assertTrue(
                created_data["message"] == "Bucketlist has been created")

            response = self.client.delete("/v1/bucketlists/1",
                                          headers={
                                              'Content-Type':
                                              'application/json',
                                              'Authorization': self.test_token
                                          })
            self.assertEqual(response.status_code, 204)


class BucketListItemsTestCase(BaseTestCase):

    create_payload = {'title': '2017'}
    payload = {'name': 'Visit New York'}
    now = datetime.datetime.now()

    def create_bucketlist(self, payload):
        return self.client.post("v1/bucketlists/",
                                data=json.dumps(payload),
                                headers={
                                    'Content-Type': 'application/json',
                                    'Authorization': self.test_token
                                })

    def create_bucketlist_item(self, payload):
        return self.client.post("v1/bucketlists/1/items/",
                                data=json.dumps(payload),
                                headers={
                                    'Content-Type': 'application/json',
                                    'Authorization': self.test_token
                                })

    def test_create_bucketlist_item(self):
        """
        Test if a user can create a bucketlist item
        """
        with self.client:
            create_response = self.create_bucketlist(self.create_payload)
            data = json.loads(create_response.data.decode())
            self.assertTrue(data["message"] == "Bucketlist has been created")
            self.assertTrue(data["status"] == "Success")
            self.assertEqual(create_response.status_code, 201)

            response = self.create_bucketlist_item(self.payload)
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "Success")
            self.assertTrue(
                data["message"] == "Bucketlist item has been created")
            self.assertEqual(response.status_code, 201)

    def test_get_bucketlist_items(self):
        """
        Test if a user can get bucketlist items
        """
        with self.client:
            create_response = self.create_bucketlist(self.payload)
            data = json.loads(create_response.data.decode())
            self.assertTrue(data["message"] == "Bucketlist has been created")
            self.assertEqual(create_response.status_code, 201)

            response = self.create_bucketlist_item(self.payload)
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "Success")
            self.assertEqual(response.status_code, 201)

            get_response = self.client.get("v1/bucketlists/1/items/1",
                                           headers={
                                               'Content-Type':
                                               'application/json',
                                               'Authorization': self.test_token
                                           })
            self.assertEqual(get_response.status_code, 200)

    def test_delete_bucketlist_item(self):
        """
        Test if a user can delete a bucketlist item
        """
        with self.client:
            create_response = self.create_bucketlist(self.payload)
            data = json.loads(create_response.data.decode())
            self.assertTrue(data["message"] == "Bucketlist has been created")
            self.assertTrue(data["status"] == "Success")
            self.assertEqual(create_response.status_code, 201)

            create_response = self.create_bucketlist_item(self.payload)
            data = json.loads(create_response.data.decode())
            self.assertTrue(data["status"] == "Success")
            self.assertTrue(
                data["message"] == "Bucketlist item has been created")
            self.assertEqual(create_response.status_code, 201)

            response = self.client.delete("v1/bucketlists/1/items/1",
                                          data=json.dumps(self.payload),
                                          headers={
                                              'Content-Type':
                                              'application/json',
                                              'Authorization': self.test_token
                                          })
            self.assertEqual(response.status_code, 204)

    def test_update_bucketlist_item(self):
        """
        Test if a user can update a bucketlist item
        """
        with self.client:
            create_response = self.create_bucketlist(self.payload)
            data = json.loads(create_response.data.decode())
            self.assertTrue(data["message"] == "Bucketlist has been created")
            self.assertTrue(data["status"] == "Success")
            self.assertEqual(create_response.status_code, 201)

            # Create a bucket list item
            response = self.create_bucketlist_item(self.payload)
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "Success")
            self.assertTrue(
                data["message"] == "Bucketlist item has been created")
            self.assertEqual(response.status_code, 201)

            # Edit the bucket list
            update_payload = {'name': 'Visit Kampala',
                              'bucketlist_id': 2}
            update_response = self.client.put("v1/bucketlists/1/items/1",
                                              data=json.dumps(update_payload),
                                              headers={
                                                  'Content-Type':
                                                  'application/json',
                                                  'Authorization':
                                                  self.test_token
                                              })
            self.assertEqual(update_response.status_code, 200)


class BucketListAPIEdgeTestCase(BaseTestCase):

    create_payload = {'title': '2017'}
    payload = {'name': 'Visit New York'}
    now = datetime.datetime.now()

    def create_bucketlist(self, payload):
        return self.client.post("v1/bucketlists/",
                                data=json.dumps(payload),
                                headers={
                                    'Content-Type': 'application/json',
                                    'Authorization': self.test_token
                                })

    def create_bucketlist_items(self, payload):
        return self.client.post("v1/bucketlists/1/items/",
                                data=json.dumps(payload),
                                headers={
                                    'Content-Type': 'application/json',
                                    'Authorization': self.test_token
                                })

    def test_get_nonexistent_bucket_lists(self):
        """
        Test if a user can get a list of bucketlists when none exist.
        """
        with self.client:
            response = self.client.get("v1/bucketlists/",
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': self.test_token
                                       })

            self.assertEqual(response.status_code, 404)

    def test_get_nonexistent_bucketlist(self):
        """
        Test if a user can get a bucketlist which does not exist.
        """
        with self.client:
            response = self.client.get("v1/bucketlists/10",
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': self.test_token
                                       })

            self.assertEqual(response.status_code, 404)

    def test_get_bucketlists_without_auth(self):
        """
        Test if a user can get bucketlist items without authentication
        """
        with self.client:
            response = self.client.get("v1/bucketlists/",
                                       headers={
                                           'Content-Type': 'application/json'
                                       })
            self.assertEqual(response.status_code, 401)

    def test_create_bucketlist_items_without_auth(self):
        """
        Test if a user can create a bucketlist items without an authentication
        """
        with self.client:
            payload = {'name': 'Visit Pretoria'}
            create_response = self.create_bucketlist(self.payload)
            data = json.loads(create_response.data.decode())
            self.assertTrue(data["message"] == "Bucketlist has been created")
            self.assertTrue(data["status"] == "Success")
            self.assertEqual(create_response.status_code, 201)

            response = self.client.post("v1/bucketlists/1/items/",
                                        data=json.dumps(payload),
                                        headers={'Content-Type':
                                                 'application/json'})
            self.assertEqual(response.status_code, 401)

    def test_create_existing_bucketlist(self):
        """
        Test if a user can create existing bucketlists
        """
        with self.client:
            create_response = self.create_bucketlist(self.payload)
            data = json.loads(create_response.data.decode())
            self.assertTrue(data["message"] == "Bucketlist has been created")
            self.assertTrue(data["status"] == "Success")
            self.assertEqual(create_response.status_code, 201)

            response = self.create_bucketlist(self.payload)
            self.assertEqual(response.status_code, 403)

    def test_create_existing_bucketlist_items(self):
        """
        Test if a user can create existing bucketlist items
        """
        with self.client:
            payload = {'name': 'Visit New York'}

            create_response = self.create_bucketlist(self.payload)
            data = json.loads(create_response.data.decode())
            self.assertTrue(data["message"] == "Bucketlist has been created")
            self.assertTrue(data["status"] == "Success")
            self.assertEqual(create_response.status_code, 201)

            response = self.client.post("v1/bucketlists/1/items/",
                                        data=json.dumps(payload),
                                        headers={
                                            'Content-Type': 'application/json',
                                            'Authorization': self.test_token
                                        })

            self.assertEqual(response.status_code, 201)

            response = self.client.post("v1/bucketlists/1/items/",
                                        data=json.dumps(payload),
                                        headers={
                                            'Content-Type': 'application/json',
                                            'Authorization': self.test_token
                                        })
            self.assertEqual(response.status_code, 403)

    def test_create_bucketlist_without_name(self):
        """
        Test if a user can create a bucketlist without a name
        """
        with self.client:
            payload = {"title": ''}
            response = self.create_bucketlist(payload)
            self.assertEqual(response.status_code, 400)

    def test_create_bucketlist_items_without_name(self):
        """
        Test if a user can create a bucketlist item without a name
        """
        with self.client:
            create_payload = {"title": ''}
            payload = {"name": ''}

            create_response = self.create_bucketlist(create_payload)
            data = json.loads(create_response.data.decode())
            print(create_response.status_code)
            self.assertTrue(data["message"] == "Bucketlist name is missing")
            self.assertTrue(data["status"] == "Fail")
            self.assertEqual(create_response.status_code, 400)

            response = self.create_bucketlist_items(payload)
            self.assertEqual(response.status_code, 400)

    def test_create_bucketlist_without_authentication(self):
        """
        Test if a user can create a bucketlist without authentication
        """
        with self.client:
            response = self.client.post("v1/bucketlists/",
                                        data=json.dumps(self.payload),
                                        headers={
                                            'Content-Type': 'application/json'
                                        })
            self.assertEqual(response.status_code, 401)

    def test_update_non_existing_bucketlist(self):
        """
        Test if a user can update a bucketlist item which does not exist
        """
        with self.client:
            update_payload = {'name': 'Visit Kampala',
                              'done': False}

            response = self.client.put("v1/bucketlists/2/items/1",
                                       data=json.dumps(update_payload),
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': self.test_token
                                       })
            self.assertEqual(response.status_code, 400)

    def test_update_bucketlist_items_without_auth(self):
        """
        Test if a user can update a bucketlist without an authentication token
        """
        with self.client:
            payload = {'name': 'Visit New York'}

            create_response = self.create_bucketlist(self.payload)
            data = json.loads(create_response.data.decode())
            self.assertTrue(data["message"] == "Bucketlist has been created")
            self.assertTrue(data["status"] == "Success")
            self.assertEqual(create_response.status_code, 201)

            response = self.create_bucketlist_items(payload)

            self.assertEqual(response.status_code, 201)

            update_payload = {'name': 'Visit Boston'}

            response = self.client.put("v1/bucketlists/1/items/1",
                                       data=json.dumps(update_payload),
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': ''
                                       })
            self.assertEqual(response.status_code, 401)
