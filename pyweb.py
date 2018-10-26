# -*- coding: utf-8 -*-

import re, datetime, json, hashlib, time, traceback
from wsgi_server import WSGIServer
from middleware import TestMiddle, get_validate
from urls import URLpattern


HTTP_STATUS_CODE = {
    100: 'Continue',
    101: 'Switching Protocols',

    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',

    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    306: '(Unused)',
    307: 'Temporary Redirect',

    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request-URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Requested Range Not Satisfiable',
    417: 'Expectation Failed',

    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
}

def routers():
    return URLpattern

class Headers:
    def __init__(self,headers):
        if type(headers) is not list:
            raise TypeError("Headers must be a list of name/value tuples")
        self._headers = headers
        self.tspecials = re.compile(r'[ \(\)<>@,;:\\"/\[\]\?=]')

    def _formatparam(self, param, value=None, quote=1):
        """Convenience function to format and return a key=value pair.

        This will quote the value if needed or if quote is true.
        """
        if value is not None and len(value) > 0:
            if quote or self.tspecials.search(value):
                value = value.replace('\\', '\\\\').replace('"', r'\"')
                return '%s="%s"' % (param, value)
            else:
                return '%s=%s' % (param, value)
        else:
            return param

    def items(self):
        return self._headers[:]

    def add_header(self, _name, _value, **_params):
        parts = []
        if _value is not None:
            parts.append(_value)
        for k, v in _params.items():
            if v is None:
                parts.append(k.replace('_', '-'))
            else:
                parts.append(self._formatparam(k.replace('_', '-'), v))
        self._headers.append((_name, "; ".join(parts)))


class Request(object):
    def __init__(self, environ):
        self.environ = environ

    @property
    def path(self):
        return self.environ['PATH_INFO']

    @property
    def args(self):
        return self.environ

    @property
    def header(self):
        return self.environ['headers']

    @property
    def method(self):
        return self.environ['REQUEST_METHOD']


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
        status_string = HTTP_STATUS_CODE.get(self._status, 'UNKNOWN')
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
        self.routing_table = [(self.token_api_pattern, self.token_api_func)]    # 保存初始化FBC的url pattern和可调用对象
        # 添加CBV的url pattern和可调用对象
        for cbv_url in routers():
            self.routing_table.append(cbv_url)

    def match(self, path):
        for (pattern, callback) in self.routing_table:
            m = re.match(pattern, path)
            if m:
                return (callback, m.groups())
        raise NotFoundError()

    # 实现FBV路由的添加
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

