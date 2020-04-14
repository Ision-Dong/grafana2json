
from ext import db


class Employer(db.Model):

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    fullname = db.Column(db.String(80),unique=True)
    sex = db.Column(db.String(80))
    phone = db.Column(db.String(80))
    role = db.Column(db.String(80))
    department = db.Column(db.String(80))
    post = db.Column(db.String(80))

    def __init__(self,fullname,sex,phone,role,department,post):
        self.fullname = fullname
        self.sex = sex
        self.phone = phone
        self.role = role
        self.department = department
        self.post = post

    def __repr__(self):
        return 'This is a db models'


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    user = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))

    def __init__(self, user, password):
        self.user = user
        self.password = password



