# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json, time, traceback, hashlib, base64, os, logging, logging.config

class TestMiddle(object):
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        if 'postman' in environ.get('USER_AGENT'):
            start_response('403 Not Allowed', [])
            return ['not allowed!']
        return self.application(environ, start_response)

def token_auth(func):
    def wrapper(*arg, **kwargs):
        try:
            request = arg[0]
            authorization = request.header.get('authorization', 'None')
            res = validate(authorization, 'passport_key')
            res = json.loads(res)
            if int(res['code']) == 1:
                return json.dumps({'code': 1, 'errmsg': '%s' % res['errmsg']})
        except:
            return json.dumps({'code': 1, 'errmsg': 'validate token exception!!!'})
        return func(*arg, **kwargs)
    # wrapper.__name__ = '%s_wrapper' % func.__name__
    return wrapper

def get_validate(username, fix_pwd):
    t = int(time.time())
    validate_key = hashlib.md5('%s%s%s' % (username, t, fix_pwd)).hexdigest()
    return base64.b64encode('%s|%s|%s' % (username, t, validate_key)).strip()

def validate(key, fix_pwd):
    t = int(time.time())
    key = base64.b64decode(key)
    x = key.split('|')
    if len(x) != 3:
        return json.dumps({'code':1,'errmsg':'token insufficient parameters!!!'})

    if t > int(x[1]) + 24*60*60:
        return json.dumps({'code':1,'errmsg':'token expired!!!'})
    validate_key = hashlib.md5('%s%s%s' % (x[0], x[1], fix_pwd)).hexdigest()
    if validate_key == x[2]:
        return json.dumps({'code':0,'username':x[0]})
    else:
        return json.dumps({'code':1,'errmsg':'password incorrect!!!'})

def write_log(loggername):
    work_dir = os.path.dirname(os.path.realpath(__file__))
    log_conf= os.path.join(work_dir, 'conf/logger.conf')
    logging.config.fileConfig(log_conf)
    logger = logging.getLogger(loggername)
    return logger
    # write_log('api').warning("Validate error: %s" % traceback.format_exc())

    
