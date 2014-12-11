
import pprint

import org.wayround.wsgi.server


def a(e, s):

    s(
        200,
        [('Content-type', 'text/plain')]
        )

    res = "{}".format(pprint.pformat(e))

    return [bytes(res, 'utf-8')]

s = org.wayround.wsgi.server.CompleteServer(
    a
    )


s.start()
