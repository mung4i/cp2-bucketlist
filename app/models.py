from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


from app import db, login_manager


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), index=True, unique=True)
    username = db.Column(db.String(25), index=True, unique=True)
    first_name = db.Column(db.String(25), index=True)
    last_name = db.Column(db.String(25), index=True)
    password_hash = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)


@property
def password(self):
    raise AttributeError('Access denied')


@password.setter
def password(self):
    self.password_hash = generate_password_hash


def verify_password(self):
    return check_password_hash(self.password_hash, password)


def __repr__(self):
    return "{0}: {1} {2}".format(self.username, self.first_name, self.last_name)


@login_manager.user_loader
def load_user(users_id):
    return User.query.get(int(users_id))


class Bucketlist(db.Model):
    __tablename__ = 'bucketlist'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(25))
    date_created = db.Column(db.DateTime)
    date_modified = db.Column(db.DateTime)
    users_email = db.Column(db.String(255), db.ForeignKey('users.email'))
    user = db.relationship("User", backref='users', lazy="dynamic")

    def __repr__(self):
        return 'Bucketlist: {}'.format(self.title)


class Items(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime)
    date_modified = db.Column(db.DateTime)
    done = db.Column(db.Boolean, default=False)
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlist.id'))
    bucketlist = db.relationship('Bucketlist', backref="bucketlist", lazy='dynamic')

    def __repr__(self):
        return 'Item: {}'.format(self.name)
