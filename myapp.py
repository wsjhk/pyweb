# -*- coding: utf-8 -*-

from pyweb import app, Response
from middleware import token_auth


@app.router(r'/login/(.*)/$')
@token_auth
def login(request, name):
    return Response("<h1>Welcome, {name}!</h1>".format(name=name))

@app.router(r'/hello/(.*)/$')
def hello(request, name):
    return "<h1>hello, {name}!</h1>".format(name=name)

@app.router(r'/logout/(.*)/$')
@token_auth
def logout(request, name):
    return Response("<h1>Logout, {name}!</h1>".format(name=name))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8001)
    
