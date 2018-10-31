# -*- coding: utf-8 -*-

from pyweb import app, Response
from middleware import token_auth
from templates import PyTpl

@app.router(r'/login/(.*)/$')
@token_auth
def login(request, name):
    return Response("<h1>Welcome, {name}!</h1>".format(name=name))

@app.router(r'/hello/(.*)/$')
def hello(request, name):
    tpl = PyTpl(filepath="./test.html")
    data = []
    data.append({"id": 1, "name": "name1", "array": [2,4,6,8,10]})
    data.append({"id": 2, "name": "name2", "array": [1,3,5,7,9]})

    tpl.assign("title", name)
    tpl.assign("data", data)

    return tpl.render()

@app.router(r'/logout/(.*)/$')
@token_auth
def logout(request, name):
    return "<h1>Logout, {name}!</h1>".format(name=name)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8001)

