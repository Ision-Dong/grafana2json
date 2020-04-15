import json
import time

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
    evetlist = ['online','offline']
    # for event in g.getDCMEvenList():
    #     evetlist.append(eval(event)['event'])
    return jsonify(evetlist)


@blue.route('/api/query',methods=['POST'])
def query():

    g = GetEventer()

    print(json.loads(request.get_data())['targets'][0]['target'])
    if json.loads(request.get_data())['targets'][0]['target'] == 'online' :
        return jsonify(
            [
                {
                    "target": "online",
                    "datapoints": [
                            [g.getDCMcount()[0], time.time()*1000],
                    ]
                }
            ]
        )
    elif json.loads(request.get_data())['targets'][0]['target'] == 'offline':
        return jsonify(
            [
                {
                    "target": "offline",
                    "datapoints": [
                            [g.getDCMcount()[1], time.time()*1000],
                    ]
                }
            ]
        )

