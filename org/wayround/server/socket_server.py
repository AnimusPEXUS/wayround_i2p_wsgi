
"""
I don't like socketserver realization in PSL, so here is My version
"""

import socket
import threading
import logging
import datetime


# class SocketServerFuncWrapper:

#    def __init__(self, func):
#        return

def _ssfw(
        func,
        transaction_id,
        serv,
        serv_stop_event,
        sock,
        addr
        ):
    func(
        transaction_id,
        serv,
        serv_stop_event,
        sock,
        addr
        )
    print("SS callable exited")
    sock.shutdown(socket.SHUT_WR)
    print("shutt down")
    return


class SocketServer:

    def __init__(
            self,
            sock,
            func,
            unique_transaction_id_generator=datetime.datetime.utcnow
            ):
        """
        The socket must be bound to an address and listening for connections

        func - must be callable and accept arguments:
            utc_datetime - probably taken from datetime.utcnow()
                (utc_datetime is meant to be used as unique transaction
                 identifier, and ought to be passed to http (or any other
                 server) and from there to other functionalities which might
                 require such a thing)
                 (I don't like time zone gradations: I think they are only
                  adding trash to information field. life can be mutch easier
                  if everybody will use utc. so this is default.
                  but You can specify `unique_transaction_id_generator'
                  to override this.
                  )
            serv - for this server instance
            serv_stop_event - threading.Event for server stop
            sock - for new socket
            addr - for remote address
        """

        if not callable(func):
            raise ValueError("`func' must be callable")

        self.sock = sock

        self._func = func

        self._trans_id_gen = unique_transaction_id_generator

        self._server_stop_flag = threading.Event()
        self._server_stop_flag.clear()

        self._acceptor_thread = None

        return

    def start(self):
        self._server_stop_flag.clear()
        if self._acceptor_thread is None:
            self._acceptor_thread = threading.Thread(
                target=self._acceptor_thread_method
                )
            self._acceptor_thread.start()
        return

    def wait(self):
        self._acceptor_thread.join()
        return

    def stop(self):
        self._server_stop_flag.stop()
        return

    def _acceptor_thread_method(self):
        while True:
            if self._server_stop_flag.is_set():
                break
            res = self.sock.accept()
            thr = threading.Thread(
                target=_ssfw,
                args=(
                    self._func,
                    self._trans_id_gen(),
                    self,
                    self._server_stop_flag,
                    res[0],
                    res[1])
                )
            thr.start()

        self._acceptor_thread = None
        return
