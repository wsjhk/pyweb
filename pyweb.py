# -*- coding: utf-8 -*-

import re, datetime, json, hashlib, time, traceback
from six.moves import http_client
from six.moves import urllib
from wsgiref.headers import Headers
from wsgi_server import WSGIServer
from middleware import TestMiddle, get_validate


class UppercaseMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        for data in self.app(environ, start_response):
            yield data.upper()


class Request(object):
    def __init__(self, environ):
        self.environ = environ

    @property
    def path(self):
        return self.environ['PATH_INFO']

    @property
    def args(self):
        """ 把查询参数转成字典形式 """
        get_arguments = urllib.parse.parse_qs(self.environ['QUERY_STRING'])
        return {k: v[0] for k, v in get_arguments.items()}

    @property
    def header(self):
        return self.environ['headers']


class Response(object):
    def __init__(self, response=None, status=200, charset='utf-8', content_type='text/html'):
        self.response = [] if response is None else response
        self.charset = charset
        self.headers = Headers([])
        content_type = '{content_type}; charset={charset}'.format(content_type=content_type, charset=charset)
        self.headers.add_header('content-type', content_type)
        self._status = status

    @property
    def status(self):
        status_string = http_client.responses.get(self._status, 'UNKNOWN')
        return '{status} {status_string}'.format(status=self._status, status_string=status_string)

    def __iter__(self):
        for val in self.response:
            if isinstance(val, bytes):
                yield val
            else:
                yield val.encode(self.charset)


# 试试结合了 Resquest 和 Response 的新 application:
def request_response_application(func):
    def application(environ, start_response):
        request = Request(environ)
        response = func(request)
        start_response(
            response.status,
            response.headers.items()
        )
        return iter(response)
    return application


class NotFoundError(Exception):
    """ url pattern not found """
    pass

def token(request, user):
    try:
        username = user
        passwd = hashlib.md5(username).hexdigest()
        if not (username and passwd):
            return json.dumps({'code': 1, 'errmsg': "Need username!!!"})
        result = {'username': 'wsjhk', 'password': '3a61696d7bf61c7e15a6652a431b55ab', 'is_lock': 0}
        if username != result['username']:
            return json.dumps({'code': 1, 'errmsg': "%s is not exist!!!" % user})
        if result['is_lock'] == 1:
            return json.dumps({'code': 1, 'errmsg': "%s is Locked!!!" % user})

        if passwd == result['password']:
            token = get_validate(result['username'], 'passport_key')
            return json.dumps({'code': 0, 'authorization': token})
        else:
            return json.dumps({'code': 1, 'errmsg': "The password is error!!!"})
    except:
        return json.dumps({'code': 1, 'errmsg': "Login Failed!!!"})

class DecoratorRouter:
    def __init__(self):
        self.token_api_pattern = r'/api/token/(.*)/$'
        self.token_api_func = token
        self.routing_table = [(self.token_api_pattern, self.token_api_func)]    # 保存 url pattern 和 可调用对象

    def match(self, path):
        for (pattern, callback) in self.routing_table:
            m = re.match(pattern, path)
            if m:
                return (callback, m.groups())
        raise NotFoundError()

    def __call__(self, pattern):
        def _(func):
            self.routing_table.append((pattern, func))
        return _


class Application(object):
    def __init__(self):
        self.routers = DecoratorRouter()

    def router(self, pattern):
        return self.routers(pattern)

    def generate_server(self, address, application):
        server = WSGIServer(address)
        server.set_application(TestMiddle(application))
        return server

    def run(self, host='127.0.0.1', port=8000):
        httpd = self.generate_server((host, port), app)
        print 'RAPOWSGI Server Serving HTTP service on \'{}:{}\''.format(host, port)
        print '{0}'.format(datetime.datetime.now().
                           strftime('%a, %d %b %Y %H:%M:%S GMT'))
        httpd.run()

    def __call__(self, environ, start_response):
        try:
            request = Request(environ)
            callback, args = self.routers.match(request.path)
            response = callback(request, *args)
            if not isinstance(response, Response):
                response = Response(response)
        except NotFoundError:
            response = Response("<h1>Not found</h1>", status=404)
        start_response(response.status, response.headers.items())

        return iter(response)

app = Application()

