import functools

from flask import request, jsonify


def check_args(func):
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        print(request.form)
        if request.form.get('user') == '' and request.form.get('password') == '':
            return jsonify(err="use or password is wrong!!!")
        else:
            return func(*args, **kwargs)
    return wrapper