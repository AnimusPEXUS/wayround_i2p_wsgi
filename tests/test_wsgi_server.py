
import org.wayround.wsgi.server


def a(e, s):

    s(
        200,
        [('Content-type', 'text/plain')]
        )

    return [b'test']

s = org.wayround.wsgi.server.CompleteServer(
    a
    )


s.start()
