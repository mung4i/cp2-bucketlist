import os

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt


from bucketlist import db, login_manager


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), index=True, unique=True)
    username = db.Column(db.String(25), index=True, unique=True)
    first_name = db.Column(db.String(25), index=True)
    last_name = db.Column(db.String(25), index=True)
    password_hash = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)
    bucketlists = db.relationship('Bucketlist', backref='user', lazy='dynamic')

    def __init__(self, email, username, first_name, last_name, password=[]):
        self.email = email
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.password = password

    def encode_auth_token(self, email):
        """
        Generates auth token
        """
        try:
            payload = {
                'iat': datetime.utcnow(),
                'nbf': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(days=1),
                'email': email
            }
            token = jwt.encode(
                payload,
                os.getenv('SECRET_KEY'),
                algorithm='HS256'
            )
            decoded_token = token.decode()
            return "JWT " + decoded_token
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes auth token
        """
        try:
            auth_token = auth_token.replace("JWT ", '', 1)
            payload = jwt.decode(auth_token, os.getenv('SECRET_KEY'),
                                 algorithms=['HS256'])
            return payload['email']
        except jwt.ExpiredSignatureError:
            return 'Token has expired. Please log in to continue.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Log in to continue.'

    @property
    def password(self):
        raise AttributeError('Access denied')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def authenticate(email, password):
        user = User.query.filter_by(email).first()
        if user.verify_password(password):
            return user

    def identity(payload):
        email = payload['email']
        return email

    def __repr__(self):
        return "{0}: {1} {2}".format(self.username, self.first_name,
                                     self.last_name)

    @login_manager.user_loader
    def load_user(email):
        return User.query.get(email=email)


class Bucketlist(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(25))
    date_created = db.Column(db.DateTime)
    date_modified = db.Column(db.DateTime)
    users_email = db.Column(db.String(255), db.ForeignKey('user.email'))
    items = db.relationship('Items', backref='bucketlist',
                            lazy='dynamic')

    def __repr__(self):
        return 'Bucketlist: {}'.format(self.title)


class Items(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime)
    date_modified = db.Column(db.DateTime)
    done = db.Column(db.Boolean, default=False)
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlist.id'))

    def __repr__(self):
        return 'Item: {}'.format(self.name)
