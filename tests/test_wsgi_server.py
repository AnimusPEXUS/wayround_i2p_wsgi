
import pprint
import urllib.parse

import wayround_i2p.wsgi.server


def a(e, s):

    s(
        '200',
        [('Content-Type', 'text/plain;charset=UTF8')]
        )

    res = """\
e:
{}
pi:
{}
qs:
{}
""".format(
        pprint.pformat(e),
        urllib.parse.unquote(e['PATH_INFO']),
        urllib.parse.parse_qs(urllib.parse.unquote(e['QUERY_STRING']))
        )

    print(res)

    return [bytes(res, 'utf-8')]

s = wayround_i2p.wsgi.server.CompleteServer(
    a
    )


s.start()
