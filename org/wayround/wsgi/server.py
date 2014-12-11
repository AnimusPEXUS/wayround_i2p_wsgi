
import pprint
import logging
import urllib.parse
import socket
import sys

import org.wayround.http.message
import org.wayround.http.server
import org.wayround.utils.socket_server


class WSGIHTTPSession:

    def __init__(self, http_request):

        if not isinstance(http_request, org.wayround.http.message.HTTPRequest):
            raise TypeError("invalid `http_request' type")

        self._http_request = http_request

        self.status = None
        self.response_headers = None
        self.exc_info = None

        return

    def format_environ(self):

        parsed_requesttarget = urllib.parse.urlparse(
            self._http_request.requesttarget
            )

        serv_name = parsed_requesttarget.netloc
        sockaddr = self._http_request.sock.getsockname()
        hostname = sockaddr[0]
        hostport = str(sockaddr[1])

        input_ = self._http_request.sock.makefile('br')

        ret = {
            'REQUEST_METHOD': self._http_request.method,
            'SCRIPT_NAME': '',  # TODO
            'PATH_INFO': parsed_requesttarget.path,
            'QUERY_STRING': parsed_requesttarget.query,
            'CONTENT_TYPE': '',  # TODO
            'SERVER_NAME': hostname,
            'SERVER_PORT': hostport,
            'SERVER_PROTOCOL': self._http_request.httpversion,
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': parsed_requesttarget.scheme,
            'wsgi.input': input_,
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': True,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            }

        for k, v in self._http_request.get_decoded_header_fields():
            ret['HTTP_{}'.format(k.upper())] = v

        if 'HTTP_CONTENT-LENGTH' in ret:
            ret['CONTENT_LENGTH'] = ret['HTTP_CONTENT-LENGTH']

        return ret

    def start_response(
            self,
            status,
            response_headers,
            exc_info=None
            ):

        self.status = status
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

    def __init__(self, func=None):

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

        resp = org.wayround.http.message.HTTPResponse(
            whs.status,
            whs.response_headers,
            iterator
            )

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
        sock.bind(address)
        sock.listen(listen_number)

        self.sock = sock

        ws = WSGIServer(wsgi_application)

        self.wsgi_server = ws

        hs = org.wayround.http.server.HTTPServer(
            ws.callable_for_http_server
            )

        self.http_server = hs

        ss = org.wayround.utils.socket_server.SocketServer(
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
        self.socket_server.stop()
        return