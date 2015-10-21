
import pprint
import logging
import urllib.parse
import socket
import sys
import time

import wayround_org.http.message
import wayround_org.http.server
import wayround_org.socketserver.server


class WSGIHTTPSession:

    def __init__(self, http_request, encoding='utf-8'):

        if not isinstance(http_request, wayround_org.http.message.HTTPRequest):
            raise TypeError("invalid `http_request' type")

        self._http_request = http_request

        self.status = None
        self.response_headers = None
        self.exc_info = None

        self._encoding = encoding

        self._input_ = http_request.sock.makefile('br')

        self.start_response(
            '500 Error',
            [
                ('Content-Type', 'text/plain;codepage=UTF-8')
                ]
            )

        return

    def format_environ(self):

        parsed_requesttarget = urllib.parse.urlparse(
            self._http_request.requesttarget
            )

        serv_name = parsed_requesttarget.netloc
        sockaddr = self._http_request.sock.getsockname()
        hostname = sockaddr[0]
        hostport = str(sockaddr[1])

        input_ = self._input_
        #input_ = None

        ret = {
            'REQUEST_METHOD': str(self._http_request.method, self._encoding),
            'SCRIPT_NAME': '',  # TODO
            'PATH_INFO': str(parsed_requesttarget.path, self._encoding),
            'QUERY_STRING': str(parsed_requesttarget.query, self._encoding),
            'CONTENT_TYPE': '',  # TODO
            'SERVER_NAME': hostname,
            'SERVER_PORT': hostport,
            'SERVER_PROTOCOL': str(
                self._http_request.httpversion,
                self._encoding
                ),
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': str(parsed_requesttarget.scheme, self._encoding),
            'wsgi.input': input_,
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': True,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            }

        for k, v in self._http_request.get_decoded_header_fields():
            ret['HTTP_{}'.format(k.upper().replace('-', '_'))] = v

        if 'HTTP_CONTENT_LENGTH' in ret:
            ret['CONTENT_LENGTH'] = ret['HTTP_CONTENT_LENGTH']

        if ret['CONTENT_TYPE'] == '':
            del ret['CONTENT_TYPE']

        return ret

    def start_response(
            self,
            status,
            response_headers,
            exc_info=None
            ):

        if not isinstance(status, str):
            raise TypeError("response `status' must be str")

        status_split = status.strip().split(' ')

        if len(status_split) < 2:
            raise ValueError(
                "`status' must be in form of 'code_number reason text'"
                " (now it is `{}')".format(status)
                )

        status_code = int(status_split[0])
        status_reason = ' '.join(status_split[1:])

        self.status = status_code
        self.status_reason = status_reason
        self.response_headers = response_headers
        self.exc_info = exc_info

        return self._deprecated_callback_returned_by_start_response

    @staticmethod
    def _deprecated_callback_returned_by_start_response(value):
        raise Exception(
            "This callable is deprecated by WSGI. "
            "Don't use it. "
            "(Please read PEP-3333)"
            )
        return


class WSGIServer:

    def __init__(self, func):

        if not callable(func):
            raise ValueError("`func' must be callable")

        self._func = func

        return

    def callable_for_http_server(self, http_request):

        whs = WSGIHTTPSession(http_request)

        iterator = self._func(
            whs.format_environ(),
            whs.start_response
            )

        resp = wayround_org.http.message.HTTPResponse(
            whs.status,
            whs.response_headers,
            iterator,
            reasonphrase=whs.status_reason
            )

        whs._input_.close()

        return resp


class CompleteServer:

    def __init__(
            self,
            wsgi_application,
            address=None,
            listen_number=5
            ):

        if address is None:
            address = ('127.0.0.1', 8080)

        sock = socket.socket()
        sock.setblocking(False)
        try:
            sock.bind(address)
        except OSError as err:
            if err.args[0] == 98:
                print("Tryed to use address: {}".format(address))
            raise

        sock.listen(listen_number)

        self.sock = sock

        ws = WSGIServer(wsgi_application)

        self.wsgi_server = ws

        hs = wayround_org.http.server.HTTPServer(
            ws.callable_for_http_server
            )

        self.http_server = hs

        ss = wayround_org.socketserver.server.SocketServer(
            sock,
            hs.callable_for_socket_server
            )

        self.socket_server = ss

        return

    def start(self):
        self.socket_server.start()
        return

    def wait(self):
        self.socket_server.wait()
        return

    def stop(self):
        self.sock.shutdown(socket.SHUT_WR)
        self.sock.close()
        self.socket_server.stop()
        return

    def wait_for_shutdown(self):
        print("Waiting for user to press CTRL+C to start shutdown")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("CTRL+C pressed - shutting down.. please wait..")
        self.stop()
        self.wait()
        return
