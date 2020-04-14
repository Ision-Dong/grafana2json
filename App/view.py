from flask import Blueprint, render_template, request,jsonify

from App.models import Employer, User
from Tools.Tools import check_args
from ext import db

from ext.EventScript import GetEventer
from ext.dcm import DataHandler


blue = Blueprint('first_blue', __name__)


# @blue.route('/', methods=['POST','GET'])
# def login():
#     return render_template('login.html')
#
# @blue.route('/index/', methods=['POST','GET'])
# @check_args
# def index():
#     if request.method == 'POST':
#         return render_template('index.html',user=request.form.get('user'),
#                                password=request.form.get('password'))
#     else:
#         return render_template('index.html')
#
# @blue.route('/add/',methods=['POST','GET'])
# def add():
#     if request.method == 'GET':
#         return render_template('add.html')
#     else:
#         db.create_all()
#         t = []
#         for i in request.form.values():
#             t.append(i)
#         user,password,fullname,sex,phone,role,department,post=t
#         en = Employer(fullname,sex,phone,role,department,post)
#         us = User(user,password)
#         db.session.add(en)
#         db.session.add(us)
#         db.session.commit()
#         return 'ok'


@blue.route('/api', methods=['GET'])
def index():

    return jsonify('OK')


@blue.route('/api/search',methods=['POST','GET'])
def search():
    g = GetEventer()
    g.getDCMcount()
    evetlist = ['assetTag','eventType','description']
    # for event in g.getDCMEvenList():
    #     evetlist.append(eval(event)['event'])
    return jsonify(evetlist)


@blue.route('/api/query',methods=['POST'])
def query():
    return jsonify(
        [
            {
                     "target": "assetTag",
                "datapoints": [
                                  [818389658, 1586835015000],
                ]
            },
            {
                "target": "eventType",
                "datapoints": [
                    ["DEVICE_COMPONENT_FAULT", 1586835015000],
                ]
            },
            {
                "target": "description",
                "datapoints": [
                    ["'Status: Abnormal; Name: POWER_SUPPLY; Detail: PSU_Redundant:Re", 1586835015000],
                ]
            }
        ]
    )