# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import StringIO
import datetime
import socket
import sys
import os
import time
import traceback
import errno
import signal
import platform
from threading import Thread
# from middleware import TestMiddle
# from myapp import app

class Worker(object):
    def __init__(self, host, port, sock , app):
        self.socket = sock
        self.application = app
        self.host = host
        self.port = port

    def accept(self):
        self.client, addr = self.socket.accept()
        # self.client.setblocking(True)
        self.handle_request()

    # def serve_forever(self):
    #     while 1:
    #         self.connection, client_address = self.socket.accept()
    #         self.handle_request()

    def init_process(self):
        # self.socket.setblocking(False)
        while True:
            try:
                time.sleep(1)
                self.accept()
                continue
            except Exception as e:
                msg = traceback.format_exc()
                with open("sub_" + str(os.getpid()) + ".txt","a") as f:
                    f.write(msg+"\n")
                if hasattr(e, "errno"):
                    if e.errno not in (errno.EAGAIN, errno.ECONNABORTED, errno.EWOULDBLOCK):
                        msg = traceback.format_exc()
                else:
                    raise

    def handle_request(self):
        self.request_data = self.client.recv(1024)
        self.request_lines = self.request_data.splitlines()
        try:
            self.get_url_parameter()
            env = self.get_environ()
            app_data = self.application(env, self.start_response)
            self.finish_response(app_data)
            print '[{0}] "{1}" {2}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                           self.request_lines[0], self.status)
        except Exception, e:
            pass

    def get_url_parameter(self):
        self.request_dict = {'Path': self.request_lines[0]}
        for itm in self.request_lines[1:]:
            if ':' in itm:
                self.request_dict[itm.split(':')[0]] = itm.split(':')[1]
        self.request_method, self.path, self.request_version = self.request_dict.get('Path').split()

    def get_environ(self):
        env = {
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': StringIO.StringIO(self.request_data),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'REQUEST_METHOD': self.request_method,
            'PATH_INFO': self.path,
            'SERVER_NAME': self.host,
            'SERVER_PORT': self.port,
            'USER_AGENT': self.request_dict.get('User-Agent'),
            'headers': self.request_dict
        }
        return env

    def start_response(self, status, response_headers):
        headers = [
            ('Date', datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')),
            ('Server', 'RAPOWSGI0.1'),
        ]
        self.headers = response_headers + headers
        self.status = status

    def finish_response(self, app_data):
        try:
            response = 'HTTP/1.1 {status}\r\n'.format(status=self.status)
            for header in self.headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in app_data:
                response += data
            self.client.sendall(response)
        finally:
            self.client.close()


class WSGIServer(object):
    socket_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 10

    def __init__(self, address):
        self.socket = socket.socket(self.socket_family, self.socket_type)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(address)
        self.socket.listen(self.request_queue_size)
        host, port = self.socket.getsockname()[:2]
        self.host = host
        self.port = port
        self.WORKERS = {}

        # self.sysstr = platform.system()
        # if (self.sysstr == "Windows"):
        #     self.WNOHANG = os.WNOHANG
        #     self.SIGTTIN = signal.SIGTTIN
        #     self.SIGTTOU = signal.SIGTTOU
        #     self.SIGKILL = signal.SIGKILL
        # elif (self.sysstr == "Linux"):
        #     self.WNOHANG = os.WNOHANG
        #     self.SIGTTIN = signal.SIGTTIN
        #     self.SIGTTOU = signal.SIGTTOU
        #     self.SIGKILL = signal.SIGKILL
        # else:
        #     pass

    def set_application(self, application):
        self.application = application

    def run(self):
        # self.init_signals()
        for i in range(2):
            self.spawn_worker()

        # while True:
        #     import time
        #     time.sleep(3)
        #     try:
        #         pid, status = os.waitpid(-1, os.WNOHANG)
        #         print("kill  pid: {}, status: {}".format(pid, status))
        #     except os.error:
        #         print("error")

    # def init_signals(self):
    #     signal.signal(signal.SIGTTIN, self.incr_one)
    #     signal.signal(signal.SIGTTOU, self.decr_one)

    # def incr_one(self, signo, frame):
    #     self.spawn_worker()
    #     for k in self.WORKERS:
    #         print(k, self.WORKERS[k])

    # def decr_one(self, signo, frame):
    #     for k in self.WORKERS:
    #         os.kill(k, signal.SIGKILL)
    #         break

    def spawn_worker(self):
        worker = Worker(self.host, self.port, self.socket, self.application)

        # pid = os.fork()
        # if pid != 0:
        #     worker.pid = pid
        #     self.WORKERS[pid] = worker
        #     return pid
        #
        # worker.pid = os.getpid()
        # worker.init_process()
        # sys.exit(0)
        work = Thread(target=worker.init_process)
        work.start()


# if __name__ == '__main__':
#     host = ''
#     port = 8888
#
#     def generate_server(address, application):
#         server = WSGIServer(address)
#         server.set_application(TestMiddle(application))
#         return server
#
#     httpd = generate_server((host, port), app)
#     print 'RAPOWSGI Server Serving HTTP service on port \'{0}:{1}\''.format(host, port)
#     print '{0}'.format(datetime.datetime.now().
#                        strftime('%a, %d %b %Y %H:%M:%S GMT'))
#     httpd.run()

